"""Fee-tier economics: the book's own volume decides its tier, and its tier decides its edge.

Two views:
  * `analytic_book` — closed form (edge_math) for planning: given a combined IC, horizon,
    breadth, capital and leverage, iterate volume -> tier -> optimal threshold -> volume until
    the tier is self-consistent. Also returns the full per-tier table so we see the PnL at every
    tier and which ones the book can reach by itself.
  * `simulated_tier_table` — same fixed point but each evaluation is a full backtest
    (`run_fn(tier) -> summary dict` with `volume_per_day`, `pnl_per_day`, `sharpe`).
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from . import edge_math as em
from .models import FeeSchedule, FeeTier


def _rt_fees(t: FeeTier, execution: str) -> float:
    if execution == "taker":
        return 2 * t.taker_bps
    if execution == "maker_entry":
        return t.maker_bps + t.taker_bps
    if execution == "maker_both":
        return 2 * t.maker_bps
    raise ValueError(f"unknown execution {execution!r}")


def _spread_cost(spread_bps: float, execution: str) -> float:
    # taker legs pay half the spread each; maker legs earn it back but suffer selection, which is
    # captured separately by `adverse_bps` per passive leg.
    legs = {"taker": 2, "maker_entry": 1, "maker_both": 0}[execution]
    return legs * spread_bps / 2


def analytic_tier_row(t: FeeTier, *, ic: float, horizon_s: float, annual_vol: float, n_symbols: int,
                      n_independent: float, capital_usd: float, gross_leverage: float, execution: str,
                      spread_bps: float, adverse_bps: float = 0.0, fill_rate: float = 1.0,
                      window_days: int = 30, impact_coef: float = 0.2, adv_usd: float = 3e8) -> dict[str, float]:
    passive_legs = {"taker": 0, "maker_entry": 1, "maker_both": 2}[execution]
    notional = capital_usd * gross_leverage / n_symbols  # per-symbol slot (peak gross = cap*lev)
    daily_vol_bps = annual_vol / np.sqrt(365.0) * 1e4
    impact = impact_coef * daily_vol_bps * np.sqrt(notional / adv_usd)  # per taker leg
    taker_legs = 2 - passive_legs
    cost = (_rt_fees(t, execution) + _spread_cost(spread_bps, execution)
            + passive_legs * adverse_bps + taker_legs * impact)
    sig = em.sigma_h_bps(annual_vol, horizon_s)
    best = em.best_threshold(ic, sig, cost, horizon_s, n_independent)
    # passive entries that never fill lose trades (and their volume) proportionally
    eff_rate = fill_rate if passive_legs else 1.0
    trades_per_year_book = best["trade_prob"] * (em.SECONDS_PER_YEAR / horizon_s) * n_symbols * eff_rate
    vol_window = trades_per_year_book * 2 * notional * window_days / 365.0
    pnl_year = trades_per_year_book * best["net_edge_bps"] / 1e4 * notional
    sharpe = best["sharpe"] * np.sqrt(eff_rate)
    return {
        "tier": t.name, "rt_cost_bps": cost, "impact_bps_leg": impact, "k": best["k"], "gross_edge_bps": best["gross_edge_bps"],
        "net_edge_bps": best["net_edge_bps"], "trades_per_day": trades_per_year_book / 365.0,
        "volume_window_usd": vol_window, "tier_min_volume": t.min_volume_usd,
        "self_sustaining": vol_window >= t.min_volume_usd, "pnl_year_usd": pnl_year,
        "return_on_capital": pnl_year / capital_usd, "sharpe": sharpe,
        "breakeven_ic_at_k1": em.breakeven_ic(sig, cost, 1.0),
        "notional_usd": notional, "nonfee_cost_bps": cost - _rt_fees(t, execution),
        "execution": execution,
    }


def bootstrap_ramp(schedule: FeeSchedule, row: dict) -> dict[str, float]:
    """Run tier T's policy from zero history, paying each day the tier the trailing volume
    actually gives (venues re-tier daily on the rolling window). Returns days to reach T and the
    PnL accumulated during the ramp (negative = the price of buying the tier)."""
    target = next(t for t in schedule.tiers if t.name == row["tier"])
    daily_vol = row["volume_window_usd"] / schedule.window_days
    if daily_vol <= 0:
        return {"days": float("nan"), "ramp_pnl_usd": float("nan")}
    trades_day = row["trades_per_day"]
    rolling = pnl = 0.0
    day = 0
    while schedule.tier_for_volume(rolling).min_volume_usd < target.min_volume_usd and day < schedule.window_days:
        t = schedule.tier_for_volume(rolling)
        net = row["gross_edge_bps"] - row["nonfee_cost_bps"] - _rt_fees(t, row["execution"])
        pnl += trades_day * net / 1e4 * row["notional_usd"]
        rolling += daily_vol
        day += 1
    return {"days": float(day), "ramp_pnl_usd": pnl}


def analytic_book(schedule: FeeSchedule, max_iter: int = 20, **kw) -> dict:
    """Per-tier table + self-consistent tier reached starting from the bottom tier."""
    kw.setdefault("window_days", schedule.window_days)
    table = [analytic_tier_row(t, **kw) for t in schedule.tiers]
    tier = schedule.tiers[0]
    path = [tier.name]
    for _ in range(max_iter):
        row = next(r for r in table if r["tier"] == tier.name)
        nxt = schedule.tier_for_volume(row["volume_window_usd"])
        if nxt.name == tier.name:
            break
        tier = nxt
        path.append(tier.name)
    # Best tier the book can *sustain* once there, and what it costs to get there from zero.
    sustain = [r for r in table if r["self_sustaining"] and r["pnl_year_usd"] > 0]
    best = max(sustain, key=lambda r: r["pnl_year_usd"], default=None)
    boot = None
    if best is not None:
        ramp = bootstrap_ramp(schedule, best)
        daily = best["pnl_year_usd"] / 365.0
        payback = max(-ramp["ramp_pnl_usd"], 0.0) / daily if daily > 0 else float("nan")
        boot = {"tier": best["tier"], **ramp, "payback_days": payback}
    return {"table": table, "reached": tier.name, "path": path, "bootstrap": boot}


def simulated_tier_table(schedule: FeeSchedule, run_fn: Callable[[FeeTier], dict],
                         scale: float = 1.0, max_iter: int = 10) -> dict:
    """Backtest-driven version. `scale` converts backtest notional to deployed notional."""
    cache: dict[str, dict] = {}

    def ev(t: FeeTier) -> dict:
        if t.name not in cache:
            s = dict(run_fn(t))
            vol_w = s["volume_per_day"] * scale * schedule.window_days
            s.update({"tier": t.name, "volume_window_usd": vol_w, "tier_min_volume": t.min_volume_usd,
                      "self_sustaining": vol_w >= t.min_volume_usd,
                      "pnl_per_day_scaled": s["pnl_per_day"] * scale})
            cache[t.name] = s
        return cache[t.name]

    table = [ev(t) for t in schedule.tiers]
    tier = schedule.tiers[0]
    path = [tier.name]
    for _ in range(max_iter):
        nxt = schedule.tier_for_volume(ev(tier)["volume_window_usd"])
        if nxt.name == tier.name:
            break
        tier = nxt
        path.append(tier.name)
    return {"table": table, "reached": tier.name, "path": path}


def ic_required_for_sharpe(schedule: FeeSchedule, target_sharpe: float, hi: float = 0.5, **kw) -> dict:
    """Smallest combined IC for which the *self-consistent* book reaches `target_sharpe`.

    Bisection over IC; at each IC the tier is the one the book's own volume reaches.
    """
    def reached_sharpe(ic: float) -> tuple[float, str]:
        res = analytic_book(schedule, ic=ic, **kw)
        row = next(r for r in res["table"] if r["tier"] == res["reached"])
        return row["sharpe"], res["reached"]

    if reached_sharpe(hi)[0] < target_sharpe:
        return {"ic": float("nan"), "tier": None}
    lo = 0.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if reached_sharpe(mid)[0] >= target_sharpe:
            hi = mid
        else:
            lo = mid
    return {"ic": hi, "tier": reached_sharpe(hi)[1]}
