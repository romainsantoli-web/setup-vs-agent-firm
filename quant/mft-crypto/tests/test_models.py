import datetime as dt

import pytest
from pydantic import ValidationError

from mft.fees import BINANCE_UM, SCHEDULES, get_schedule
from mft.models import BacktestConfig, DownloadRequest, FeeSchedule, FeeTier, StudyConfig


def test_fee_schedules_valid_and_lookup():
    assert set(SCHEDULES) == {"kraken_futures", "kraken_futures_consumer", "binance_um", "bybit", "hyperliquid"}
    k = get_schedule("kraken_futures")
    assert k.verified and k.tier_for_volume(0).name == "K0" and k.tier_for_volume(150e6).name == "K5"
    assert k.tiers[-1].taker_bps == 1.35 and k.tiers[-1].maker_bps == -0.6  # maker rebate
    c = get_schedule("kraken_futures_consumer")
    assert c.tiers[0].maker_bps == c.tiers[0].taker_bps == 25.0
    assert get_schedule("binance_um") is BINANCE_UM
    assert BINANCE_UM.tier_for_volume(0).name == "VIP0"
    assert BINANCE_UM.tier_for_volume(15e6).name == "VIP1"
    assert BINANCE_UM.tier_for_volume(1e12).name == "VIP9"


def test_unknown_venue_rejected():
    with pytest.raises(ValueError):
        get_schedule("ftx")


def test_schedule_must_start_at_zero_and_be_monotone():
    t0 = FeeTier(name="A", min_volume_usd=0, maker_bps=2, taker_bps=5)
    with pytest.raises(ValidationError):
        FeeSchedule(venue="x", window_days=30, as_of="2025", tiers=(FeeTier(name="A", min_volume_usd=1, maker_bps=2, taker_bps=5),))
    with pytest.raises(ValidationError):  # fees going up with tier
        FeeSchedule(venue="x", window_days=30, as_of="2025", tiers=(t0, FeeTier(name="B", min_volume_usd=10, maker_bps=2, taker_bps=6)))
    with pytest.raises(ValidationError):  # thresholds not increasing
        FeeSchedule(venue="x", window_days=30, as_of="2025", tiers=(t0, FeeTier(name="B", min_volume_usd=0, maker_bps=1, taker_bps=4)))
    with pytest.raises(ValidationError):  # bad slug
        FeeSchedule(venue="Bad Venue", window_days=30, as_of="2025", tiers=(t0,))


def test_backtest_config_bands():
    assert BacktestConfig(k_in=2, k_out=0.5).k_out == 0.5
    with pytest.raises(ValidationError):
        BacktestConfig(k_in=1, k_out=1)
    with pytest.raises(ValidationError):
        BacktestConfig(min_hold_bars=10, max_hold_bars=5)
    with pytest.raises(ValidationError):
        BacktestConfig(unknown=1)


def test_download_request_validation():
    ok = DownloadRequest(venue="binance_um", dataset="aggTrades", symbol="BTCUSDT",
                         start=dt.date(2025, 1, 1), end=dt.date(2025, 1, 2), out_dir="data/raw")
    assert ok.symbol == "BTCUSDT"
    base = dict(venue="binance_um", dataset="aggTrades", symbol="BTCUSDT", start=dt.date(2025, 1, 1),
                end=dt.date(2025, 1, 2), out_dir="data")
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "out_dir": "../etc"})
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "out_dir": "a\\..\\b"})
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "out_dir": "a\x00b"})
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "symbol": "btc/usdt"})
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "end": dt.date(2024, 12, 31)})
    with pytest.raises(ValidationError):
        DownloadRequest(**{**base, "end": dt.date(2029, 1, 1)})


def test_study_config():
    c = StudyConfig(horizons=(15, 1, 5, 5))
    assert c.horizons == (1, 5, 15)
    assert StudyConfig().funding_interval_h == 1
    with pytest.raises(ValidationError):
        StudyConfig(funding_interval_h=0)
    with pytest.raises(ValidationError):
        StudyConfig(horizons=(0,))
    with pytest.raises(ValidationError):
        StudyConfig(out_path="../../x.md")
