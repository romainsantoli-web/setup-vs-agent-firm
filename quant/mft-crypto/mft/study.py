"""End-to-end research run: features -> leakage check -> IC decay -> verdicts -> walk-forward
combination -> execution-mode backtests -> fee-tier fixed point. Works on any
{symbol: bars DataFrame} dict (synthetic today, recorded/archived data tomorrow).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .backtest import run_backtest, summarize
from .combine import signal_correlation, standardize_expanding, walk_forward_forecast
from .features import SIGNALS, compute_features, forward_return_bps
from .models import BacktestConfig, CostParams, FeeSchedule, FeeTier
from .tiers import simulated_tier_table
from scipy.stats import norm

from .validation import (daily_ic, event_study, ic_summary, point_in_time_violations,
                         signal_verdict, split_half_ic)


def panel_features(market: dict[str, pd.DataFrame], names: list[str]) -> pd.DataFrame:
    frames = []
    for sym, df in market.items():
        f = standardize_expanding(compute_features(df, names), min_periods=min(500, len(df) // 4))
        f["symbol"] = sym
        frames.append(f)
    return pd.concat(frames).set_index("symbol", append=True).sort_index()


def panel_label(market: dict[str, pd.DataFrame], h: int) -> pd.Series:
    parts = []
    for sym, df in market.items():
        y = forward_return_bps(df["close"], h)
        y.index = pd.MultiIndex.from_arrays([df.index, [sym] * len(df)])
        parts.append(y)
    return pd.concat(parts).sort_index()


def signal_report(market: dict[str, pd.DataFrame], horizons: tuple[int, ...]) -> tuple[pd.DataFrame, pd.DataFrame]:
    names = list(SIGNALS)
    X = panel_features(market, names)
    labels = {h: panel_label(market, h).reindex(X.index) for h in horizons}
    probe = next(iter(market.values()))
    n_tests = len(names) * len(horizons)
    rows = []
    for name in names:
        spec = SIGNALS[name]
        pit = point_in_time_violations(lambda d, fn=spec.fn: fn(d, **spec.params), probe.iloc[:3000])
        for h in horizons:
            s = ic_summary(daily_ic(X[name], labels[h]))
            halves = split_half_ic(X[name], labels[h])
            ev = event_study(X[name], labels[h], threshold=3.0, min_gap=h) if spec.sparse else {}
            if pit:
                verdict = "LEAK"
            elif spec.sparse:
                hurdle = 2.0 if n_tests <= 1 else float(norm.ppf(1 - 0.025 / n_tests))
                ok = np.isfinite(ev["t"]) and np.sign(ev["mean_bps"]) == spec.expected_sign
                verdict = "KEEP" if ok and abs(ev["t"]) >= hurdle else ("WEAK" if ok and abs(ev["t"]) >= 2 else "KILL")
            else:
                verdict = signal_verdict(s, spec.expected_sign, n_tests, halves)
            rows.append({"signal": name, "h": h, **s, "ic_h1": halves[0], "ic_h2": halves[1],
                         "event_n": ev.get("n_events", np.nan), "event_bps": ev.get("mean_bps", np.nan),
                         "event_t": ev.get("t", np.nan), "pit_violations": pit, "verdict": verdict})
    return pd.DataFrame(rows), signal_correlation(X)


def combined_forecast(market: dict[str, pd.DataFrame], keep: list[str], h: int, train_days: int,
                      test_days: int = 1, alpha: float = 1.0) -> tuple[pd.Series, pd.DataFrame]:
    X = panel_features(market, keep)
    y = panel_label(market, h).reindex(X.index)
    signs = np.array([SIGNALS[k].expected_sign for k in keep], dtype=float)
    fc, w = walk_forward_forecast(X, y, train_days, test_days, embargo_bars=h, alpha=alpha, signs=signs)
    return fc, w


def backtest_book(market: dict[str, pd.DataFrame], forecast: pd.Series, cfg: BacktestConfig,
                  tier: FeeTier) -> dict[str, float]:
    res = {}
    for sym, df in market.items():
        f = forecast.xs(sym, level=1)
        z = f / f.expanding(min_periods=200).std().shift(1)  # point-in-time scaling
        cost = CostParams(half_spread_bps=float(df["spread_bps"].iloc[0]) / 2)
        res[sym] = run_backtest(df, z, cfg, tier, cost)
    return summarize(res)


def tier_study(market: dict[str, pd.DataFrame], forecast: pd.Series, cfg: BacktestConfig,
               schedule: FeeSchedule, scale: float) -> dict:
    return simulated_tier_table(schedule, lambda t: backtest_book(market, forecast, cfg, t), scale=scale)
