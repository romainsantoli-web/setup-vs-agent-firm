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

# Kraken Futures (multi-collateral perps PF_*), 30-day futures volume (USD). Note how LOW the
# thresholds are vs Binance: the top tier (0 / 1 bp) needs only 100 M$/30 d — a book of our size
# can own it. These are the global Kraken Futures rates; the EU (MiFID) offering may differ.
# Do NOT confuse with Kraken *spot* fees (16-40 bps), which make spot useless for MFT.
KRAKEN_FUTURES = FeeSchedule(
    venue="kraken_futures",
    window_days=30,
    as_of="2025-snapshot",
    tiers=(
        FeeTier(name="K0", min_volume_usd=0, maker_bps=2.0, taker_bps=5.0),
        FeeTier(name="K1", min_volume_usd=100e3, maker_bps=1.5, taker_bps=4.0),
        FeeTier(name="K2", min_volume_usd=1 * _M, maker_bps=1.25, taker_bps=3.0),
        FeeTier(name="K3", min_volume_usd=5 * _M, maker_bps=1.0, taker_bps=2.5),
        FeeTier(name="K4", min_volume_usd=10 * _M, maker_bps=0.75, taker_bps=2.0),
        FeeTier(name="K5", min_volume_usd=20 * _M, maker_bps=0.5, taker_bps=1.5),
        FeeTier(name="K6", min_volume_usd=50 * _M, maker_bps=0.25, taker_bps=1.25),
        FeeTier(name="K7", min_volume_usd=100 * _M, maker_bps=0.0, taker_bps=1.0),
    ),
)

EXECUTION_VENUE = "kraken_futures"

SCHEDULES: dict[str, FeeSchedule] = {s.venue: s for s in (KRAKEN_FUTURES, BINANCE_UM, BYBIT, HYPERLIQUID)}


def get_schedule(venue: str) -> FeeSchedule:
    try:
        return SCHEDULES[venue]
    except KeyError:
        raise ValueError(f"unknown venue {venue!r}; known: {sorted(SCHEDULES)}") from None
