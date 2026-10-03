"""Measured Kraken Futures execution costs (desk calibration, design window <= 2026-10-08).

Source: desk files kraken_calib/out/ (calib_p1_now.json, impact_final_p1_now.json), relayed by
Romain on 2026-10-03, plus the fee rate read from Romain's own fills (private `fills` stream of the
v10 test runs: 86 maker at 2.000 bp, 86 taker at 5.000 bp -> standard schedule, tier K0).

`impact_bps` = median cost of an aggressive clip versus mid, fees excluded (it already contains the
half-spread actually crossed), so a taker round trip = 2 x taker fee + 2 x impact.
Passive fills (87 real maker fills): markout vs fill price -0.66 / -1.03 / -1.77 / -1.05 bp at
+1 s / +10 s / +1 min / +5 min -> adverse selection ~1.5 bp per passive leg, i.e. ~-3 bp net of the
2 bp maker fee. Those were market-making fills; signal-gated directional entries are untested.
"""

from __future__ import annotations

import numpy as np

from . import edge_math as em

TAKER_FEE_BPS = 5.0  # measured on Romain's account (standard schedule, K0)
MAKER_FEE_BPS = 2.0
PASSIVE_ADVERSE_BPS = 1.5  # measured MM markout, 10 s - 1 min

# symbol: (median spread bps, ADV usd, {clip_usd: median impact bps}) — impact None = not measured
MEASURED: dict[str, tuple[float, float, dict[int, float] | None]] = {
    "PF_XBTUSD": (0.12, 636e6, {25_000: 0.41, 75_000: 0.80, 150_000: 1.09}),
    "PF_ETHUSD": (0.37, 107e6, {25_000: 1.13, 75_000: 1.74, 150_000: 2.18}),
    "PF_SOLUSD": (0.85, 60e6, {25_000: 3.07, 75_000: 4.08, 150_000: 4.87}),
    "PF_XRPUSD": (1.29, 34e6, {25_000: 4.21, 75_000: 5.67, 150_000: 6.62}),
    "PF_DOGEUSD": (2.05, 11e6, None),
    "PF_ADAUSD": (4.37, 5.6e6, None),
    "PF_LINKUSD": (2.85, 10e6, None),
    "PF_LTCUSD": (2.98, 2.7e6, None),
    "PF_SUIUSD": (3.38, 13e6, None),
    "PF_ZECUSD": (5.05, 44e6, None),
}


def impact_bps(symbol: str, clip_usd: float) -> float:
    """Measured impact, log-log interpolated between measured clip sizes (clamped at the ends)."""
    spread, _adv, table = MEASURED[symbol]
    if table is None:
        raise ValueError(f"no measured book depth for {symbol}")
    sizes = np.array(sorted(table), dtype=float)
    vals = np.array([table[int(s)] for s in sizes])
    x = np.clip(np.log(clip_usd), np.log(sizes[0]), np.log(sizes[-1]))
    return float(np.exp(np.interp(x, np.log(sizes), np.log(vals))))


def round_trip_bps(symbol: str, clip_usd: float, execution: str = "taker") -> float:
    """All-in round-trip cost (fees + impact/selection) for one clip."""
    imp = impact_bps(symbol, clip_usd)
    if execution == "taker":
        return 2 * TAKER_FEE_BPS + 2 * imp
    if execution == "maker_entry":
        return MAKER_FEE_BPS + PASSIVE_ADVERSE_BPS + TAKER_FEE_BPS + imp
    raise ValueError("execution must be 'taker' or 'maker_entry'")


def required_ic(symbol: str, clip_usd: float, horizon_s: float, annual_vol: float,
                execution: str = "taker", target_sharpe: float = 2.0,
                n_independent: float = 1.0) -> dict[str, float]:
    sig = em.sigma_h_bps(annual_vol, horizon_s)
    cost = round_trip_bps(symbol, clip_usd, execution)
    return {"rt_cost_bps": cost, "sigma_h_bps": sig,
            "breakeven_ic_k1": em.breakeven_ic(sig, cost, 1.0),
            "ic_for_sharpe": em.ic_for_sharpe(target_sharpe, sig, cost, horizon_s, n_independent)}
