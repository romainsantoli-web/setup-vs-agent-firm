"""Closed-form economics of a threshold policy on a Gaussian forecast.

Model: standardized forecast s ~ N(0, 1) observed every h; forward return over h is
    r = IC * sigma_h * s + eps,   eps ~ N(0, sigma_h^2 (1 - IC^2)).
Policy: trade (round trip) when |s| > k, direction sign(s), hold h.

These formulas give the *break-even IC* per fee tier and horizon and the trade-count / edge
trade-off that drives the choice of threshold. They are the analytic backbone that the
simulator (`backtest.py`) is checked against.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

SECONDS_PER_YEAR = 365.0 * 86_400.0


def sigma_h_bps(annual_vol: float, horizon_s: float) -> float:
    """Return volatility (bps) over a horizon, from annualized vol (e.g. 0.5 = 50 %)."""
    return annual_vol * math.sqrt(horizon_s / SECONDS_PER_YEAR) * 1e4


def mean_abs_s_given_trade(k: float) -> float:
    """E[|s| | |s| > k] for s ~ N(0,1)."""
    tail = 1.0 - norm.cdf(k)
    return float(norm.pdf(k) / tail) if tail > 0 else float(k)


def trade_prob(k: float) -> float:
    return float(2.0 * (1.0 - norm.cdf(k)))


def gross_edge_bps(ic: float, sig_h_bps: float, k: float) -> float:
    return ic * sig_h_bps * mean_abs_s_given_trade(k)


def round_trip_cost_bps(entry_fee_bps: float, exit_fee_bps: float, spread_cost_bps: float = 0.0,
                        impact_bps: float = 0.0) -> float:
    """Fees on both legs + spread actually crossed + impact (all in bps of notional)."""
    return entry_fee_bps + exit_fee_bps + spread_cost_bps + 2.0 * impact_bps


def policy_stats(ic: float, sig_h_bps: float, k: float, cost_rt_bps: float, horizon_s: float,
                 n_independent: float = 1.0) -> dict[str, float]:
    """Per-trade net edge, trades/year and annualized Sharpe of the threshold policy.

    `n_independent` = effective number of independent instruments (breadth multiplier).
    """
    p = trade_prob(k)
    decisions_per_year = SECONDS_PER_YEAR / horizon_s
    trades_per_year = p * decisions_per_year * n_independent
    edge = gross_edge_bps(ic, sig_h_bps, k)
    net = edge - cost_rt_bps
    # per-trade PnL std ~ sigma_h (IC small); Sharpe of the sum of independent trades
    sharpe = net / sig_h_bps * math.sqrt(trades_per_year) if trades_per_year > 0 else 0.0
    return {"k": k, "trade_prob": p, "gross_edge_bps": edge, "net_edge_bps": net,
            "trades_per_year": trades_per_year, "sharpe": sharpe}


def best_threshold(ic: float, sig_h_bps: float, cost_rt_bps: float, horizon_s: float,
                   n_independent: float = 1.0, grid: np.ndarray | None = None) -> dict[str, float]:
    """Threshold maximizing annualized Sharpe; if no threshold is profitable, do not trade."""
    grid = np.linspace(0.0, 4.0, 161) if grid is None else grid
    best = {"k": float("inf"), "trade_prob": 0.0, "gross_edge_bps": 0.0, "net_edge_bps": 0.0,
            "trades_per_year": 0.0, "sharpe": 0.0}
    for k in grid:
        st = policy_stats(ic, sig_h_bps, float(k), cost_rt_bps, horizon_s, n_independent)
        if st["sharpe"] > best["sharpe"] + 1e-12:
            best = st
    return best


def ic_for_sharpe(target_sharpe: float, sig_h_bps: float, cost_rt_bps: float, horizon_s: float,
                  n_independent: float = 1.0, hi: float = 1.0) -> float:
    """Smallest combined IC whose optimal threshold policy reaches `target_sharpe` (bisection)."""
    lo = 0.0
    if best_threshold(hi, sig_h_bps, cost_rt_bps, horizon_s, n_independent)["sharpe"] < target_sharpe:
        return float("nan")
    for _ in range(40):
        mid = (lo + hi) / 2
        if best_threshold(mid, sig_h_bps, cost_rt_bps, horizon_s, n_independent)["sharpe"] >= target_sharpe:
            hi = mid
        else:
            lo = mid
    return hi


def breakeven_ic(sig_h_bps: float, cost_rt_bps: float, k: float) -> float:
    """IC at which the gross edge at threshold k exactly pays the round-trip cost."""
    return cost_rt_bps / (sig_h_bps * mean_abs_s_given_trade(k))


def combined_ic(ics: list[float], corr: np.ndarray | None = None) -> float:
    """IC of the optimal linear combination of signals (Grinold).

    With signal correlation matrix C and IC vector g, the best combined IC is sqrt(g' C^-1 g).
    Orthogonal signals: sqrt(sum IC^2) — the reason funds stack many weak, decorrelated signals.
    """
    g = np.asarray(ics, dtype=float)
    c = np.eye(len(g)) if corr is None else np.asarray(corr, dtype=float)
    return float(math.sqrt(max(g @ np.linalg.solve(c, g), 0.0)))
