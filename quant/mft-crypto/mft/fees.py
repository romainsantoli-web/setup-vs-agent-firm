"""Fee-tier schedules for perpetual futures venues.

EXECUTION VENUE = Kraken Futures (Binance perps are not available to French residents).
Binance / Bybit schedules are kept only for comparison; their market data stays useful as
information (lead-lag), not as a place to trade.

WARNING: these are snapshots reconstructed from public fee pages as known to the author
(`verified=False`). Thresholds and rates change (and Binance also conditions some tiers on BNB
holdings). Re-check every value on the venue's fee page before any sizing decision; the tier
economics in `tiers.py` only depend on the schedule object, so updating it is a one-line change.
"""

from __future__ import annotations

from .models import FeeSchedule, FeeTier

_M = 1e6
_B = 1e9

# Binance USDⓈ-M futures, 30-day rolling futures volume (USD). Rates in bps (0.02 % = 2 bps).
BINANCE_UM = FeeSchedule(
    venue="binance_um",
    window_days=30,
    as_of="2025-snapshot",
    tiers=(
        FeeTier(name="VIP0", min_volume_usd=0, maker_bps=2.0, taker_bps=5.0),
        FeeTier(name="VIP1", min_volume_usd=15 * _M, maker_bps=1.6, taker_bps=4.0),
        FeeTier(name="VIP2", min_volume_usd=50 * _M, maker_bps=1.4, taker_bps=3.5),
        FeeTier(name="VIP3", min_volume_usd=100 * _M, maker_bps=1.2, taker_bps=3.2),
        FeeTier(name="VIP4", min_volume_usd=600 * _M, maker_bps=1.0, taker_bps=3.0),
        FeeTier(name="VIP5", min_volume_usd=1 * _B, maker_bps=0.8, taker_bps=2.7),
        FeeTier(name="VIP6", min_volume_usd=2.5 * _B, maker_bps=0.6, taker_bps=2.5),
        FeeTier(name="VIP7", min_volume_usd=5 * _B, maker_bps=0.4, taker_bps=2.2),
        FeeTier(name="VIP8", min_volume_usd=12.5 * _B, maker_bps=0.2, taker_bps=2.0),
        FeeTier(name="VIP9", min_volume_usd=25 * _B, maker_bps=0.0, taker_bps=1.7),
    ),
)

# Bybit derivatives, 30-day volume. Approximate; Bybit also uses asset-balance criteria.
BYBIT = FeeSchedule(
    venue="bybit",
    window_days=30,
    as_of="2025-snapshot",
    tiers=(
        FeeTier(name="VIP0", min_volume_usd=0, maker_bps=2.0, taker_bps=5.5),
        FeeTier(name="VIP1", min_volume_usd=10 * _M, maker_bps=1.8, taker_bps=4.0),
        FeeTier(name="VIP2", min_volume_usd=25 * _M, maker_bps=1.6, taker_bps=3.75),
        FeeTier(name="VIP3", min_volume_usd=50 * _M, maker_bps=1.4, taker_bps=3.5),
        FeeTier(name="VIP4", min_volume_usd=100 * _M, maker_bps=1.2, taker_bps=3.2),
        FeeTier(name="VIP5", min_volume_usd=250 * _M, maker_bps=1.0, taker_bps=3.2),
        FeeTier(name="SVIP", min_volume_usd=1 * _B, maker_bps=0.0, taker_bps=3.0),
    ),
)

# Hyperliquid perps, 14-day weighted volume. Maker rebates from maker-volume share not modelled.
HYPERLIQUID = FeeSchedule(
    venue="hyperliquid",
    window_days=14,
    as_of="2025-snapshot",
    tiers=(
        FeeTier(name="T0", min_volume_usd=0, maker_bps=1.5, taker_bps=4.5),
        FeeTier(name="T1", min_volume_usd=5 * _M, maker_bps=1.2, taker_bps=4.0),
        FeeTier(name="T2", min_volume_usd=25 * _M, maker_bps=0.8, taker_bps=3.5),
        FeeTier(name="T3", min_volume_usd=100 * _M, maker_bps=0.4, taker_bps=3.0),
        FeeTier(name="T4", min_volume_usd=500 * _M, maker_bps=0.0, taker_bps=2.8),
        FeeTier(name="T5", min_volume_usd=2 * _B, maker_bps=0.0, taker_bps=2.6),
        FeeTier(name="T6", min_volume_usd=7 * _B, maker_bps=0.0, taker_bps=2.4),
    ),
)

# Kraken Futures perps (PF_*), standard schedule, 30-day volume (USD).
# VERIFIED 2026-10-03 by the desk from the VPS (public GET /derivatives/api/v3/feeschedules).
# Negative maker = rebate. Kraken also publishes "Incentive" schedules (rebates up to -1 bp
# above 1 B$) and "Consumer" schedules at 25 bp maker AND taker (see KRAKEN_FUTURES_CONSUMER):
# which one applies to Romain's account is only visible through the private API.
# Do NOT confuse with Kraken *spot* fees (16-40 bps), which make spot useless for MFT.
KRAKEN_FUTURES = FeeSchedule(
    venue="kraken_futures",
    window_days=30,
    as_of="2026-10-03 API",
    verified=True,
    tiers=(
        FeeTier(name="K0", min_volume_usd=0, maker_bps=2.0, taker_bps=5.0),
        FeeTier(name="K1", min_volume_usd=5 * _M, maker_bps=1.75, taker_bps=4.5),
        FeeTier(name="K2", min_volume_usd=10 * _M, maker_bps=1.5, taker_bps=4.0),
        FeeTier(name="K3", min_volume_usd=25 * _M, maker_bps=1.0, taker_bps=3.0),
        FeeTier(name="K4", min_volume_usd=50 * _M, maker_bps=0.5, taker_bps=2.5),
        FeeTier(name="K5", min_volume_usd=100 * _M, maker_bps=0.0, taker_bps=2.0),
        FeeTier(name="K6", min_volume_usd=250 * _M, maker_bps=-0.3, taker_bps=1.75),
        FeeTier(name="K7", min_volume_usd=1 * _B, maker_bps=-0.6, taker_bps=1.35),
    ),
)

# Kraken "Consumer" perp schedule (flat 25 bp maker and taker). If the account sits on it,
# no MFT book is viable: the break-even IC exceeds anything public-flow signals can deliver.
KRAKEN_FUTURES_CONSUMER = FeeSchedule(
    venue="kraken_futures_consumer",
    window_days=30,
    as_of="2026-10-03 API",
    verified=True,
    tiers=(FeeTier(name="C0", min_volume_usd=0, maker_bps=25.0, taker_bps=25.0),),
)

EXECUTION_VENUE = "kraken_futures"

SCHEDULES: dict[str, FeeSchedule] = {s.venue: s for s in (KRAKEN_FUTURES, KRAKEN_FUTURES_CONSUMER, BINANCE_UM, BYBIT, HYPERLIQUID)}


def get_schedule(venue: str) -> FeeSchedule:
    try:
        return SCHEDULES[venue]
    except KeyError:
        raise ValueError(f"unknown venue {venue!r}; known: {sorted(SCHEDULES)}") from None


# Kraken derivatives margin schedule for EEA clients (MiFID II), checked 2026-10-03 on Kraken's
# support pages ("Derivatives margin schedule and maximum leverage for EEA clients"):
# tier -> (initial margin, maintenance margin). Leverage falls as the position grows; the tier
# thresholds depend on the asset class (class A: tier II only above ~30 M$ of position), and
# class F contracts START at tier II (5x max). The 50-100x offered elsewhere is NOT available
# from France. Retail and professional clients share this schedule.
KRAKEN_EEA_MARGIN_TIERS: dict[str, tuple[float, float]] = {
    "I": (0.10, 0.05),
    "II": (0.20, 0.10),
    "III": (0.30, 0.15),
    "IV": (0.50, 0.25),
}


def kraken_eea_max_leverage(asset_class: str = "A", tier: str = "I") -> float:
    """Max leverage for an EEA client: 1 / initial margin; class F starts at tier II."""
    if asset_class.upper() == "F" and tier == "I":
        tier = "II"
    if tier not in KRAKEN_EEA_MARGIN_TIERS:
        raise ValueError(f"unknown margin tier {tier!r}")
    return round(1.0 / KRAKEN_EEA_MARGIN_TIERS[tier][0], 2)
