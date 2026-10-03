"""Signal library: weak, mechanism-backed, point-in-time features for MFT (10 s – 1 h).

Every signal is a pure function of bars at times <= t (checked by
`validation.point_in_time_violations`). Each entry in `SIGNALS` pre-registers:
  * the expected sign (set *before* looking at data — a wrong-sign IC kills the signal,
    it is never silently flipped),
  * the counterparty we expect to earn from,
  * the horizon where the mechanism should live.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

EPS = 1e-12


def _ret(close: pd.Series, w: int) -> pd.Series:
    return np.log(close / close.shift(w))


def _vol(close: pd.Series, w: int = 60) -> pd.Series:
    r = np.log(close / close.shift(1))
    return r.rolling(w, min_periods=max(5, w // 4)).std()


def rolling_z(x: pd.Series, w: int, min_periods: int | None = None) -> pd.Series:
    mp = min_periods or max(10, w // 4)
    m = x.rolling(w, min_periods=mp).mean()
    s = x.rolling(w, min_periods=mp).std()
    return (x - m) / (s + EPS)


# --- signals ---------------------------------------------------------------------------------

def lead_lag(df: pd.DataFrame, w: int = 1) -> pd.Series:
    """Leader-venue return minus own return over w bars, in own-vol units."""
    gap = _ret(df["close_ref"], w) - _ret(df["close"], w)
    return gap / (_vol(df["close"]) * np.sqrt(w) + EPS)


def btc_lead(df: pd.DataFrame, w: int = 1, beta_w: int = 240) -> pd.Series:
    """Beta-scaled BTC move over w bars, in alt-vol units. Zero for BTC itself.

    Deliberately NOT `beta*r_btc - r_alt`: that gap mixes in the alt's own short-term
    reversal (a different exposure, measured by `short_term_reversal`); on the synthetic bench
    the mixed version showed a strong wrong-sign IC coming entirely from own-return dynamics.
    """
    r_alt = np.log(df["close"] / df["close"].shift(1))
    r_btc = np.log(df["close_btc"] / df["close_btc"].shift(1))
    if np.allclose(df["close"].values, df["close_btc"].values):
        return pd.Series(0.0, index=df.index)
    mp = 60
    cov = (r_alt * r_btc).rolling(beta_w, min_periods=mp).mean() - r_alt.rolling(beta_w, min_periods=mp).mean() * r_btc.rolling(beta_w, min_periods=mp).mean()
    beta = cov / (r_btc.rolling(beta_w, min_periods=mp).var() + EPS)
    return beta * _ret(df["close_btc"], w) / (_vol(df["close"]) * np.sqrt(w) + EPS)


def flow_imbalance(df: pd.DataFrame, w: int = 15) -> pd.Series:
    """Aggressor imbalance (all trades) over w bars."""
    b = df["buy_volume"].rolling(w, min_periods=1).sum()
    s = df["sell_volume"].rolling(w, min_periods=1).sum()
    return (b - s) / (b + s + EPS)


def informed_flow(df: pd.DataFrame, w: int = 15) -> pd.Series:
    """Large-trade imbalance minus small-trade imbalance: informed vs retail aggressors."""
    lb = df["large_buy_volume"].rolling(w, min_periods=1).sum()
    ls = df["large_sell_volume"].rolling(w, min_periods=1).sum()
    sb = (df["buy_volume"] - df["large_buy_volume"]).rolling(w, min_periods=1).sum()
    ss = (df["sell_volume"] - df["large_sell_volume"]).rolling(w, min_periods=1).sum()
    return (lb - ls) / (lb + ls + EPS) - 0.5 * (sb - ss) / (sb + ss + EPS)


def liquidation_reversal(df: pd.DataFrame, w: int = 10) -> pd.Series:
    """Net long liquidations (forced sells) over w bars, scaled by volume -> expect bounce."""
    net = (df["liq_long_usd"] - df["liq_short_usd"]).rolling(w, min_periods=1).sum()
    vol = df["volume"].rolling(w * 6, min_periods=1).sum() / 6
    return net / (vol + EPS)


def short_term_reversal(df: pd.DataFrame, w: int = 5) -> pd.Series:
    """Minus vol-scaled return over w bars: liquidity provision to impatient flow."""
    return -_ret(df["close"], w) / (_vol(df["close"]) * np.sqrt(w) + EPS)


def momentum(df: pd.DataFrame, w: int = 240) -> pd.Series:
    """Vol-scaled return over a long window (1-4 h trend persistence)."""
    return _ret(df["close"], w) / (_vol(df["close"], 240) * np.sqrt(w) + EPS)


def funding_crowding(df: pd.DataFrame, w: int = 1440 * 3) -> pd.Series:
    """Minus z-scored predicted funding: crowded leveraged longs pay and underperform."""
    return -rolling_z(df["funding_rate_bps"], w, min_periods=60)


def premium_reversion(df: pd.DataFrame, w: int = 240) -> pd.Series:
    """Minus z-scored perp-index premium (smoothed): basis mean-reverts through the perp."""
    p = df["premium_bps"].ewm(span=10, adjust=False).mean()
    return -rolling_z(p, w)


def oi_divergence(df: pd.DataFrame, w: int = 60) -> pd.Series:
    """Price up with OI up = fresh leveraged longs (fragile) -> expect giveback."""
    d_oi = np.log(df["oi_usd"] / df["oi_usd"].shift(w))
    d_px = _ret(df["close"], w)
    return -rolling_z(d_oi * np.sign(d_px), 1440)


@dataclass(frozen=True)
class SignalSpec:
    fn: Callable[..., pd.Series]
    expected_sign: int
    counterparty: str
    horizon_bars: tuple[int, int]
    params: dict = field(default_factory=dict)
    sparse: bool = False  # event-driven: validate with an event study, not rank IC


SIGNALS: dict[str, SignalSpec] = {
    "lead_lag": SignalSpec(lead_lag, +1, "latency/capital-constrained cross-venue arbitrage", (1, 5)),
    "btc_lead": SignalSpec(btc_lead, +1, "alt books repricing slowly after BTC moves", (1, 15)),
    "flow_imbalance": SignalSpec(flow_imbalance, +1, "order-flow persistence (split meta-orders)", (5, 60)),
    "informed_flow": SignalSpec(informed_flow, +1, "retail aggressors vs informed size", (5, 60)),
    "liquidation_reversal": SignalSpec(liquidation_reversal, +1, "forced liquidations of leveraged retail", (5, 60), sparse=True),
    "short_term_reversal": SignalSpec(short_term_reversal, +1, "impatient flow paying for immediacy", (1, 30)),
    "momentum": SignalSpec(momentum, +1, "slow information diffusion / trend followers", (30, 240)),
    "funding_crowding": SignalSpec(funding_crowding, +1, "crowded leveraged longs paying carry", (60, 480)),
    "premium_reversion": SignalSpec(premium_reversion, +1, "basis arbitrageurs constrained by capital", (15, 240)),
    "oi_divergence": SignalSpec(oi_divergence, +1, "fresh leverage unwinding", (30, 240)),
}


def compute_features(df: pd.DataFrame, names: list[str] | None = None) -> pd.DataFrame:
    names = list(SIGNALS) if names is None else names
    unknown = set(names) - set(SIGNALS)
    if unknown:
        raise ValueError(f"unknown signals: {sorted(unknown)}")
    cols = {}
    for name in names:
        spec = SIGNALS[name]
        cols[name] = spec.fn(df, **spec.params).astype(float)
    return pd.DataFrame(cols, index=df.index).replace([np.inf, -np.inf], np.nan)


def forward_return_bps(close: pd.Series, h: int) -> pd.Series:
    """Label: log return from close_t to close_{t+h}, in bps. Uses the future by design."""
    return np.log(close.shift(-h) / close) * 1e4
