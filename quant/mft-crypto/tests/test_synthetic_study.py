import numpy as np
import pytest

import mft.features as feats
from mft.backtest import summarize  # noqa: F401
from mft.fees import BINANCE_UM
from mft.features import SignalSpec
from mft.models import BacktestConfig, StudyConfig
from mft.study import backtest_book, combined_forecast, panel_label, signal_report, tier_study
from mft.synthetic import generate_market
from mft.validation import daily_ic, ic_summary


def test_generator_is_deterministic_and_complete(planted_market):
    again = generate_market(StudyConfig(n_symbols=3, n_days=16, bars_per_day=288, seed=5, planted=True))
    df = planted_market["ALT01USDT"]
    assert np.allclose(df["close"], again["ALT01USDT"]["close"])
    assert (df["high"] >= df[["open", "close"]].max(axis=1) - 1e-9).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-9).all()
    assert df["is_funding"].sum() == 16 * 24  # Kraken: hourly funding


def test_report_recovers_planted_and_rejects_null(planted_market, null_market):
    rep, corr = signal_report(planted_market, (1, 3))
    keep = set(rep.loc[rep.verdict == "KEEP", "signal"])
    assert {"lead_lag", "informed_flow"} <= keep
    rep0, _ = signal_report(null_market, (1, 3))
    assert (rep0.verdict != "KEEP").all()
    assert corr.shape[0] == len(feats.SIGNALS)


def test_leaky_signal_is_flagged(planted_market, monkeypatch):
    leaky = SignalSpec(lambda d: d["close"].shift(-1) / d["close"] - 1, +1, "the future", (1, 1))
    monkeypatch.setattr(feats, "SIGNALS", {"leaky": leaky})
    import mft.study as st
    monkeypatch.setattr(st, "SIGNALS", {"leaky": leaky})
    rep, _ = signal_report(planted_market, (1,))
    assert rep["verdict"].tolist() == ["LEAK"]


def test_combination_backtest_and_tiers(planted_market):
    keep = ["lead_lag", "btc_lead", "informed_flow", "flow_imbalance"]
    fc, w = combined_forecast(planted_market, keep, h=3, train_days=6, test_days=2)
    y = panel_label(planted_market, 3).reindex(fc.index)
    assert ic_summary(daily_ic(fc, y))["ic"] > 0.02
    assert (w.values >= 0).all()  # all pre-registered signs are +1
    cfg = BacktestConfig(k_in=1.5, k_out=0.3, max_hold_bars=9, min_hold_bars=3, bars_per_day=288)
    s = backtest_book(planted_market, fc, cfg, BINANCE_UM.tiers[-1])
    assert s["trades"] > 10
    res = tier_study(planted_market, fc, cfg, BINANCE_UM, scale=100.0)
    assert res["path"][0] == "VIP0" and len(res["table"]) == len(BINANCE_UM.tiers)
    assert res["table"][-1]["pnl_per_day"] >= res["table"][0]["pnl_per_day"] - 1e-9


@pytest.mark.parametrize("planted", [True, False])
def test_small_configs(planted):
    m = generate_market(StudyConfig(n_symbols=1, n_days=2, bars_per_day=96, planted=planted))
    assert list(m) == ["BTCUSDT"]
