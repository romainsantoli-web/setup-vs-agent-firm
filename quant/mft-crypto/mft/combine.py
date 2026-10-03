"""Signal combination with walk-forward fitting, purging and sign constraints.

The combination is where weak signals become a tradeable forecast (combined IC ~ sqrt(sum IC^2)
for decorrelated signals). It is also the easiest place to overfit, hence:
  * strictly walk-forward (fit on the past only, embargo >= label horizon),
  * ridge shrinkage toward zero,
  * weights whose sign contradicts the pre-registered sign are zeroed, not flipped.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _time_key(index: pd.Index) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(index.get_level_values(0) if isinstance(index, pd.MultiIndex) else index)


def standardize_expanding(x: pd.DataFrame, min_periods: int = 500, clip: float = 5.0) -> pd.DataFrame:
    """Point-in-time z-score per column using only past data (expanding mean/std), clipped."""
    m = x.expanding(min_periods=min_periods).mean().shift(1)
    s = x.expanding(min_periods=min_periods).std().shift(1)
    return ((x - m) / s).clip(-clip, clip)


def fit_ridge(X: np.ndarray, y: np.ndarray, alpha: float, signs: np.ndarray | None = None) -> np.ndarray:
    m = np.isfinite(X).all(1) & np.isfinite(y)
    X, y = X[m], y[m]
    if len(y) < X.shape[1] + 2:
        return np.zeros(X.shape[1])
    n = len(y)
    w = np.linalg.solve(X.T @ X / n + alpha * np.eye(X.shape[1]), X.T @ y / n)
    if signs is not None:
        w = np.where(np.sign(w) == signs, w, 0.0)
    return w


def walk_forward_forecast(X: pd.DataFrame, y: pd.Series, train_days: int, test_days: int,
                          embargo_bars: int, alpha: float = 1.0,
                          signs: np.ndarray | None = None) -> tuple[pd.Series, pd.DataFrame]:
    """Out-of-sample forecast built block by block (rolling train window, purged + embargoed).

    X rows must be point-in-time features, y the forward label at the same timestamp. Training
    rows whose label window overlaps the test block are purged by dropping the last
    `embargo_bars` distinct timestamps of the training window.
    Returns (forecast aligned to X.index, weights per test block).
    """
    t = _time_key(X.index)
    days = t.floor("D")
    udays = np.array(sorted(days.unique()))
    fc = np.full(len(X), np.nan)
    weights = []
    start = train_days
    while start < len(udays):
        tr_days = udays[start - train_days:start]
        te_days = udays[start:start + test_days]
        tr = np.isin(days, tr_days)
        te = np.isin(days, te_days)
        tr_ts = np.unique(t[tr])
        if embargo_bars > 0 and len(tr_ts) > embargo_bars:
            cutoff = tr_ts[-embargo_bars]
            tr = tr & (t < cutoff)
        w = fit_ridge(X.values[tr], y.values[tr], alpha, signs)
        fc[te] = np.nan_to_num(X.values[te]) @ w
        weights.append(pd.Series(w, index=X.columns, name=pd.Timestamp(te_days[0])))
        start += test_days
    return pd.Series(fc, index=X.index), pd.DataFrame(weights)


def signal_correlation(X: pd.DataFrame) -> pd.DataFrame:
    return X.corr(method="spearman")
