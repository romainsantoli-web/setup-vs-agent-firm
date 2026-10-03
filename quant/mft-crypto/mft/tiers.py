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
                      window_days: int = 30) -> dict[str, float]:
    passive_legs = {"taker": 0, "maker_entry": 1, "maker_both": 2}[execution]
    cost = _rt_fees(t, execution) + _spread_cost(spread_bps, execution) + passive_legs * adverse_bps
    sig = em.sigma_h_bps(annual_vol, horizon_s)
    best = em.best_threshold(ic, sig, cost, horizon_s, n_independent)
    # passive entries that never fill lose trades (and their volume) proportionally
    eff_rate = fill_rate if passive_legs else 1.0
    notional = capital_usd * gross_leverage / n_symbols  # per-symbol slot (peak gross = cap*lev)
    trades_per_year_book = best["trade_prob"] * (em.SECONDS_PER_YEAR / horizon_s) * n_symbols * eff_rate
    vol_window = trades_per_year_book * 2 * notional * window_days / 365.0
    pnl_year = trades_per_year_book * best["net_edge_bps"] / 1e4 * notional
    sharpe = best["sharpe"] * np.sqrt(eff_rate)
    return {
        "tier": t.name, "rt_cost_bps": cost, "k": best["k"], "gross_edge_bps": best["gross_edge_bps"],
        "net_edge_bps": best["net_edge_bps"], "trades_per_day": trades_per_year_book / 365.0,
        "volume_window_usd": vol_window, "tier_min_volume": t.min_volume_usd,
        "self_sustaining": vol_window >= t.min_volume_usd, "pnl_year_usd": pnl_year,
        "return_on_capital": pnl_year / capital_usd, "sharpe": sharpe,
        "breakeven_ic_at_k1": em.breakeven_ic(sig, cost, 1.0),
    }


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
    return {"table": table, "reached": tier.name, "path": path}


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
