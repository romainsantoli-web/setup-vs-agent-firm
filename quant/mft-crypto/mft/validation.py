"""Validation toolkit: IC with honest t-stats, decay, regimes, leakage, multiple testing.

A signal survives only if: (i) daily IC t-stat clears the bar *after* correcting for the number
of things we tried, (ii) the sign matches the pre-registered one, (iii) it is point-in-time,
(iv) it holds in more than one volatility regime and in both halves of the sample.
"""

from __future__ import annotations

import itertools
import math
from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

EULER_GAMMA = 0.5772156649015329


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 10 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return np.nan
    return float(spearmanr(a[m], b[m]).statistic)


def _days(index: pd.Index) -> pd.DatetimeIndex:
    ts = index.get_level_values(0) if isinstance(index, pd.MultiIndex) else index
    return pd.DatetimeIndex(ts).floor("D")


def _gauss_rank(x: pd.Series) -> pd.Series:
    r = x.rank(method="average")
    return pd.Series(norm.ppf((r - 0.5) / len(r)), index=x.index)


def intraday_ic(signal: pd.Series, fwd: pd.Series) -> pd.Series:
    """Spearman IC recomputed *within* each day. BIASED for time-series signals whose window
    is a sizeable fraction of a day (per-day demeaning of overlapping windows manufactures
    negative IC on a pure random walk). Kept only to document that bias; use `daily_ic`."""
    df = pd.DataFrame({"s": signal, "f": fwd}).dropna()
    return df.groupby(_days(df.index)).apply(lambda g: _spearman(g["s"].values, g["f"].values)).dropna()


def daily_ic(signal: pd.Series, fwd: pd.Series) -> pd.Series:
    """Daily contributions to the pooled rank IC.

    Signal and label are Gaussian-rank transformed with *global* moments, then the product is
    averaged per UTC day: mean(daily) = pooled rank IC, and each day is one observation for the
    t-stat (robust to the autocorrelation of overlapping intraday labels).
    """
    df = pd.DataFrame({"s": signal, "f": fwd}).dropna()
    if len(df) < 10:
        return pd.Series(dtype=float)
    prod = _gauss_rank(df["s"]) * _gauss_rank(df["f"])
    return prod.groupby(_days(df.index)).mean()


def _deoverlap(values: np.ndarray, threshold: float, min_gap: int) -> np.ndarray:
    keep, last = [], -10**12
    for i in np.flatnonzero(np.abs(values) > threshold):
        if i - last >= min_gap:
            keep.append(i)
            last = i
    return np.asarray(keep, dtype=int)


def event_study(signal: pd.Series, fwd: pd.Series, threshold: float, min_gap: int = 1) -> dict[str, float]:
    """Mean signed forward return (bps) after sparse events |signal| > threshold.

    Rank IC is the wrong metric for signals that are zero most of the time (liquidations):
    measure the conditional mean move per event instead. Events are de-overlapped *per symbol*
    in bars (`min_gap`), then events sharing a timestamp across symbols (market-wide cascades)
    are averaged into one cluster before the t-stat — otherwise one cascade counts N times.
    """
    df = pd.DataFrame({"s": signal, "f": fwd}).dropna()
    groups = df.groupby(level=1, sort=False) if isinstance(df.index, pd.MultiIndex) else [(None, df)]
    ts_list, vals = [], []
    for _, g in groups:
        idx = _deoverlap(g["s"].to_numpy(), threshold, min_gap)
        if len(idx):
            ts = g.index.get_level_values(0) if isinstance(g.index, pd.MultiIndex) else g.index
            ts_list.append(np.asarray(ts)[idx])
            vals.append(np.sign(g["s"].to_numpy()[idx]) * g["f"].to_numpy()[idx])
    if not vals:
        return {"n_events": 0, "mean_bps": np.nan, "t": np.nan}
    clusters = pd.Series(np.concatenate(vals)).groupby(np.concatenate(ts_list)).mean().to_numpy()
    n = len(clusters)
    if n < 3:
        return {"n_events": n, "mean_bps": np.nan, "t": np.nan}
    sd = clusters.std(ddof=1)
    return {"n_events": n, "mean_bps": float(clusters.mean()),
            "t": float(clusters.mean() / sd * math.sqrt(n)) if sd > 0 else np.nan}


def ic_summary(ic: pd.Series) -> dict[str, float]:
    n = len(ic)
    mean = float(ic.mean()) if n else np.nan
    sd = float(ic.std(ddof=1)) if n > 1 else np.nan
    t = mean / sd * math.sqrt(n) if n > 1 and sd > 0 else np.nan
    return {"ic": mean, "ic_sd": sd, "t": t, "days": n, "pos_frac": float((ic > 0).mean()) if n else np.nan}


def ic_decay(signal: pd.Series, close_by_key: Callable[[int], pd.Series], horizons: list[int]) -> pd.DataFrame:
    rows = []
    for h in horizons:
        s = ic_summary(daily_ic(signal, close_by_key(h)))
        rows.append({"h": h, **s})
    return pd.DataFrame(rows).set_index("h")


def regime_ic(signal: pd.Series, fwd: pd.Series, regime: pd.Series, n_bins: int = 3) -> pd.DataFrame:
    """IC within regime buckets (e.g. realized-vol terciles computed point-in-time)."""
    df = pd.DataFrame({"s": signal, "f": fwd, "r": regime}).dropna()
    df["bucket"] = pd.qcut(df["r"], n_bins, labels=False, duplicates="drop")
    rows = []
    for b, g in df.groupby("bucket"):
        rows.append({"bucket": int(b), **ic_summary(daily_ic(g["s"], g["f"]))})
    return pd.DataFrame(rows).set_index("bucket")


def split_half_ic(signal: pd.Series, fwd: pd.Series) -> tuple[float, float]:
    ic = daily_ic(signal, fwd)
    h = len(ic) // 2
    return float(ic.iloc[:h].mean()), float(ic.iloc[h:].mean())


def point_in_time_violations(fn: Callable[[pd.DataFrame], pd.Series], df: pd.DataFrame,
                             n_cuts: int = 5, tol: float = 1e-9) -> int:
    """Number of cut points where the feature at t changes when data after t is removed.

    Any non-zero result means the feature peeks at the future (centered windows, full-sample
    normalisation, bfill, ...). This must be 0 for every signal before it enters research.
    """
    full = fn(df)
    bad = 0
    for cut in np.linspace(len(df) * 0.3, len(df) - 1, n_cuts).astype(int):
        part = fn(df.iloc[: cut + 1])
        a, b = full.iloc[: cut + 1].values, part.values
        m = np.isfinite(a) | np.isfinite(b)
        if not np.allclose(np.nan_to_num(a[m], nan=1e300), np.nan_to_num(b[m], nan=1e300), atol=tol, rtol=1e-7):
            bad += 1
    return bad


def sharpe_annual(daily_pnl: pd.Series, periods: float = 365.0) -> float:
    x = daily_pnl.dropna()
    if len(x) < 2 or x.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / x.std(ddof=1) * math.sqrt(periods))


def expected_max_sharpe(n_trials: int, var_sr: float) -> float:
    """Expected maximum of n_trials Sharpe estimates under the null (Bailey & López de Prado)."""
    if n_trials <= 1:
        return 0.0
    a = (1 - EULER_GAMMA) * norm.ppf(1 - 1.0 / n_trials)
    b = EULER_GAMMA * norm.ppf(1 - 1.0 / (n_trials * math.e))
    return math.sqrt(var_sr) * (a + b)


def deflated_sharpe(sr: float, n_obs: int, n_trials: int, var_sr: float,
                    skew: float = 0.0, kurt: float = 3.0) -> float:
    """Probability that the true (per-period) Sharpe > 0 after selecting the best of n_trials.

    `sr` and `var_sr` are per-observation (not annualised) Sharpe ratios.
    """
    sr0 = expected_max_sharpe(n_trials, var_sr)
    denom = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr**2, 1e-12))
    return float(norm.cdf((sr - sr0) * math.sqrt(n_obs - 1) / denom))


def pbo_cscv(perf: np.ndarray, n_blocks: int = 8) -> float:
    """Probability of Backtest Overfitting via combinatorially symmetric cross-validation.

    perf: (T, N) matrix of per-period returns of N strategy variants. Returns the fraction of
    IS/OOS splits where the IS-best variant ranks below the OOS median.
    """
    t, n = perf.shape
    if n < 2 or n_blocks % 2 or t < n_blocks:
        raise ValueError("need >=2 variants, an even number of blocks and T >= n_blocks")
    blocks = np.array_split(np.arange(t), n_blocks)
    logits = []
    for is_ids in itertools.combinations(range(n_blocks), n_blocks // 2):
        is_idx = np.concatenate([blocks[i] for i in is_ids])
        oos_idx = np.concatenate([blocks[i] for i in range(n_blocks) if i not in is_ids])

        def _sr(m: np.ndarray) -> np.ndarray:
            return m.mean(0) / (m.std(0, ddof=1) + 1e-12)
        best = int(np.argmax(_sr(perf[is_idx])))
        oos = _sr(perf[oos_idx])
        rank = (oos < oos[best]).sum() + 1  # 1..n
        w = rank / (n + 1)
        logits.append(math.log(w / (1 - w)))
    return float(np.mean(np.array(logits) <= 0))


def signal_verdict(summary: dict[str, float], expected_sign: int, n_tests: int,
                   halves: tuple[float, float], min_abs_ic: float = 0.01) -> str:
    """KEEP / WEAK / KILL with a Bonferroni-style hurdle on |t| for the number of tests run."""
    hurdle = norm.ppf(1 - 0.025 / max(n_tests, 1))
    ic, t = summary["ic"], summary["t"]
    if not np.isfinite(t) or np.sign(ic) != expected_sign:
        return "KILL"
    same_sign_halves = np.sign(halves[0]) == np.sign(halves[1]) == expected_sign
    if abs(t) >= hurdle and abs(ic) >= min_abs_ic and same_sign_halves:
        return "KEEP"
    if abs(t) >= 2.0 and same_sign_halves:
        return "WEAK"
    return "KILL"
