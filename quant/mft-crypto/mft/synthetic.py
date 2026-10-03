"""Synthetic perp market with *known* planted inefficiencies — the pipeline's test bench.

Why: a research pipeline is only trustworthy if (1) it recovers effects we planted, with the
right sign and decay, and (2) it finds nothing (and loses money net of costs) on a market where
nothing is planted. Real data cannot give that ground truth.

Planted mechanisms (planted=True), each mapped to a real crypto counterparty:
  * lead_lag      — own venue absorbs only `lam` of the leader-venue move this bar, the rest the
                    next bar (fragmentation; arbitrageurs constrained by latency/capital).
  * informed flow — latent AR(1) alpha drives drift; large-trade imbalance observes it noisily,
                    small (retail) flow is mostly contemporaneous noise.
  * liquidations  — forced-flow jumps that partially revert over ~tau bars (leveraged retail).
  * funding       — crowded longs (high funding) slightly underperform (carry/crowding).
  * premium       — perp-index basis mean-reverts and drags perp price toward index.
Decoys (never predictive): open-interest changes, contemporaneous small-trade flow.
In null mode every feature keeps the same marginal behaviour (incl. contemporaneous correlation
with returns) but has zero predictive link.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import lfilter

from .models import StudyConfig


def _ar1(rng: np.random.Generator, n: int, phi: float, sd: float = 1.0) -> np.ndarray:
    """Stationary AR(1) with unit-free stationary std `sd`."""
    e = rng.standard_normal(n) * sd * np.sqrt(1.0 - phi**2)
    x = lfilter([1.0], [1.0, -phi], e)
    x[0] = rng.standard_normal() * sd
    return x


def _decay_kernel_conv(impulses: np.ndarray, tau: float) -> np.ndarray:
    """Drift at t from impulses at s<t with exponential kernel normalised to sum to 1."""
    phi = np.exp(-1.0 / tau)
    shifted = np.concatenate([[0.0], impulses[:-1]])  # only strictly-past events act
    return lfilter([1.0 - phi], [1.0, -phi], shifted)


def generate_market(cfg: StudyConfig) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    bpd = cfg.bars_per_day
    n = cfg.n_days * bpd
    bar_s = 86_400 / bpd
    idx = pd.date_range("2025-01-01", periods=n, freq=pd.Timedelta(seconds=bar_s), tz="UTC")
    P = 1.0 if cfg.planted else 0.0

    sigma_bar = 0.6 / np.sqrt(365 * bpd)  # 60 % annual vol, in log-return units
    log_vol = _ar1(rng, n, np.exp(-1.0 / (bpd / 2)), 0.35)
    mkt = rng.standard_normal(n)  # common factor shocks (unit)
    funding_clock = (idx.hour % cfg.funding_interval_h == 0) & (idx.minute == 0) & (idx.second == 0)

    out: dict[str, pd.DataFrame] = {}
    for i in range(cfg.n_symbols):
        sym = "BTCUSDT" if i == 0 else f"ALT{i:02d}USDT"
        beta = 1.0 if i == 0 else rng.uniform(0.8, 1.3)
        idio_w = 0.3 if i == 0 else rng.uniform(0.6, 0.9)
        vol = sigma_bar * np.exp(log_vol + _ar1(rng, n, np.exp(-1.0 / bpd), 0.15))

        alpha = _ar1(rng, n, np.exp(-1.0 / 20.0))  # informed-flow state, unit variance
        # bps per funding interval (scaled from an 8h-equivalent level: Kraken pays hourly)
        funding = (1.0 + _ar1(rng, n, np.exp(-1.0 / bpd), 3.0)) * cfg.funding_interval_h / 8.0
        premium = _ar1(rng, n, np.exp(-1.0 / 60.0), 4.0)  # bps

        # liquidation cascades: jumps with partial reversal
        ev = rng.random(n) < 4.0 / bpd
        side = np.where(rng.random(n) < 0.6, -1.0, 1.0)  # -1 = longs liquidated (price down)
        jump = ev * side * rng.uniform(3.0, 8.0, n) * vol
        reversal = -0.3 * P * _decay_kernel_conv(jump, tau=30.0)

        drift = P * vol * (0.035 * alpha - 0.01 * (funding * 8.0 / cfg.funding_interval_h - 1.0) / 3.0 - 0.01 * premium / 4.0) + reversal
        shock = vol * (beta * mkt * (1.0 / np.sqrt(beta**2 + idio_w**2)) * 1.0
                       + idio_w * rng.standard_normal(n) / np.sqrt(beta**2 + idio_w**2))
        r_eff = drift + shock + jump

        lam = 0.93 if cfg.planted else 1.0
        r_own = lam * r_eff + (1.0 - lam) * np.concatenate([[0.0], r_eff[:-1]])
        r_ref = r_eff + 0.02 * vol * rng.standard_normal(n)

        log_px = np.log(100.0 * (1 + i)) + np.cumsum(r_own)
        close = np.exp(log_px)
        open_ = np.exp(np.concatenate([[log_px[0]], log_px[:-1]]))
        # exact Brownian-bridge extremes between open and close: no free mean-reverting wicks
        x = r_own
        u = rng.random((2, n))
        hi_ex = (x + np.sqrt(x**2 - 2 * vol**2 * np.log(u[0]))) / 2
        lo_ex = (x - np.sqrt(x**2 - 2 * vol**2 * np.log(u[1]))) / 2
        high = open_ * np.exp(np.maximum(hi_ex, np.maximum(x, 0)))
        low = open_ * np.exp(np.minimum(lo_ex, np.minimum(x, 0)))

        z_now = r_own / vol
        volume = 2e5 * (1 + i) * np.exp(log_vol) * rng.lognormal(0.0, 0.5, n) * (1 + 2 * ev)
        small_imb = np.tanh(0.6 * z_now + 0.8 * rng.standard_normal(n))
        large_imb = np.tanh(0.4 * z_now + 0.8 * P * alpha + 1.0 * rng.standard_normal(n))
        large_share = 0.3
        large_buy = volume * large_share * (1 + large_imb) / 2
        large_sell = volume * large_share * (1 - large_imb) / 2
        small_buy = volume * (1 - large_share) * (1 + small_imb) / 2
        small_sell = volume * (1 - large_share) * (1 - small_imb) / 2

        liq_usd = np.abs(jump) / vol * volume * 0.05 * ev
        liq_long = np.where(side < 0, liq_usd, 0.0)
        liq_short = np.where(side > 0, liq_usd, 0.0)

        oi = 1e8 * (1 + i) * np.exp(np.cumsum(0.0005 * rng.standard_normal(n) + 0.0002 * np.abs(small_imb) - 0.0001))

        out[sym] = pd.DataFrame({
            "open": open_, "high": high, "low": low, "close": close,
            "close_ref": close * np.exp(np.cumsum(r_ref - r_own)),
            "volume": volume,
            "buy_volume": large_buy + small_buy, "sell_volume": large_sell + small_sell,
            "large_buy_volume": large_buy, "large_sell_volume": large_sell,
            "liq_long_usd": liq_long, "liq_short_usd": liq_short,
            "funding_rate_bps": funding, "premium_bps": premium + 2.0 * z_now,
            "oi_usd": oi, "spread_bps": np.full(n, 1.0 if i == 0 else 2.5),
            "is_funding": funding_clock,
        }, index=idx)
    btc = out["BTCUSDT"]["close"]
    for df in out.values():
        df["close_btc"] = btc.values
    return out
