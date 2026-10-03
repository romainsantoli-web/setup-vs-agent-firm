import numpy as np
import pandas as pd
import pytest

from conftest import make_bars
from mft.backtest import impact_bps, run_backtest, summarize
from mft.models import BacktestConfig, CostParams, FeeTier

TIER = FeeTier(name="T", min_volume_usd=0, maker_bps=1.0, taker_bps=4.0)
FREE = FeeTier(name="F", min_volume_usd=0, maker_bps=0.0, taker_bps=0.0)
NO_IMPACT = CostParams(half_spread_bps=1.0, impact_coef=0.0)


def _fc(df, values):
    return pd.Series(values, index=df.index, dtype=float)


def test_taker_round_trip_costs_are_exact_on_flat_price():
    df = make_bars([100.0] * 10, spread_bps=2.0)
    z = [0, 3, 3, 0, 0, 0, 0, 0, 0, 0]
    cfg = BacktestConfig(k_in=1, k_out=0.5, max_hold_bars=50, min_hold_bars=1, notional_usd=10_000)
    r = run_backtest(df, _fc(df, z), cfg, TIER, NO_IMPACT)
    assert len(r.trades) == 1
    # half-spread 1 bp each leg + 4 bp taker each leg = 10 bp of 10k = 10 USD
    assert r.equity.iloc[-1] == pytest.approx(-10.0, rel=1e-3)
    assert r.volume_usd == pytest.approx(20_000, rel=1e-3)
    assert r.trades["hold_bars"].iloc[0] == 2
    assert np.isnan(r.maker_fill_rate)


def test_signal_with_edge_makes_money_and_summary():
    df = make_bars(np.linspace(100, 110, 50), spread_bps=0.0)
    cfg = BacktestConfig(k_in=1, k_out=0.0, max_hold_bars=100, notional_usd=10_000)
    r = run_backtest(df, _fc(df, [2.0] * 50), cfg, FREE, CostParams(half_spread_bps=0, impact_coef=0))
    assert r.equity.iloc[-1] > 900
    s = summarize({"A": r})
    assert s["trades"] == 0 and s["pnl_usd"] == pytest.approx(r.equity.iloc[-1])  # still open
    assert r.volume_per_day > 0


def test_max_hold_and_flip_reverse():
    df = make_bars([100.0] * 12, spread_bps=0.0)
    cfg = BacktestConfig(k_in=1, k_out=0.0, max_hold_bars=3, notional_usd=1000)
    r = run_backtest(df, _fc(df, [2] * 12), cfg, FREE, CostParams(half_spread_bps=0, impact_coef=0))
    assert (r.trades["hold_bars"] == 3).all()
    z = [2, 2, -2, -2, -2, 0, 0, 0]
    df2 = make_bars([100.0] * 8, spread_bps=0.0)
    r2 = run_backtest(df2, _fc(df2, z), BacktestConfig(k_in=1, k_out=0.5, max_hold_bars=50), FREE,
                      CostParams(half_spread_bps=0, impact_coef=0))
    assert list(r2.trades["side"]) == [1, -1]


def test_passive_fill_requires_trade_through_and_pays_adverse():
    # bar 2 trades through the bid placed at bar 1 close
    close = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
    df = make_bars(close, spread_bps=2.0)
    df.loc[df.index[2], "low"] = 99.0
    z = [0, 3, 3, 3, 0, 0]
    cfg = BacktestConfig(k_in=1, k_out=0.5, execution="maker_entry", fill_window_bars=2, notional_usd=10_000)
    r = run_backtest(df, _fc(df, z), cfg, TIER, CostParams(half_spread_bps=1, impact_coef=0))
    t = r.trades.iloc[0]
    assert bool(t["entry_maker"]) and not bool(t["exit_maker"])
    # limit 100*(1-1bp) then adverse = half-spread (1bp) -> filled at mid
    assert t["entry_px"] == pytest.approx(100.0, rel=1e-6)
    assert r.maker_fill_rate == 1.0
    # explicit adverse override
    r2 = run_backtest(df, _fc(df, z), cfg, TIER, CostParams(half_spread_bps=1, impact_coef=0, adverse_bps=0))
    assert r2.trades.iloc[0]["entry_px"] == pytest.approx(99.99, rel=1e-6)


def test_unfilled_passive_cancel_or_chase():
    df = make_bars([100.0] * 8, spread_bps=2.0)  # low == close: never trades through
    z = [0, 3, 3, 3, 3, 3, 0, 0]
    base = dict(k_in=1, k_out=0.5, execution="maker_entry", fill_window_bars=2)
    r = run_backtest(df, _fc(df, z), BacktestConfig(**base), TIER, NO_IMPACT)
    assert r.trades.empty and r.maker_fill_rate == 0.0
    r2 = run_backtest(df, _fc(df, z), BacktestConfig(**base, chase_unfilled=True), TIER, NO_IMPACT)
    assert len(r2.trades) == 1 and not bool(r2.trades.iloc[0]["entry_maker"])


def test_maker_both_exit_falls_back_to_taker_and_funding_sign():
    df = make_bars([100.0] * 10, spread_bps=2.0, funding_bps=10.0, funding_every=2)
    z = [3, 3, 3, 0, 0, 0, 0, 0, 0, 0]
    cfg = BacktestConfig(k_in=1, k_out=0.5, execution="maker_both", fill_window_bars=1, chase_unfilled=True)
    r = run_backtest(df, _fc(df, z), cfg, TIER, NO_IMPACT)
    assert len(r.trades) == 1
    assert not bool(r.trades.iloc[0]["exit_maker"])
    assert r.funding_usd < 0  # long pays positive funding


def test_flip_with_passive_execution_reposts_entry():
    df = make_bars([100.0] * 8, spread_bps=0.0, wick=0.01)
    z = [2, 2, -2, -2, -2, 0, 0, 0]
    cfg = BacktestConfig(k_in=1, k_out=0.5, execution="maker_entry", fill_window_bars=1)
    r = run_backtest(df, _fc(df, z), cfg, FREE, CostParams(half_spread_bps=0, impact_coef=0))
    assert list(r.trades["side"])[:2] == [1, -1]


def test_impact_and_null_forecast_loses(null_market):
    assert impact_bps(CostParams(half_spread_bps=1, impact_coef=0.1, daily_vol_bps=300, adv_usd=1e8), 1e6) == pytest.approx(3.0)
    df = null_market["ALT01USDT"]
    rng = np.random.default_rng(0)
    r = run_backtest(df, pd.Series(rng.standard_normal(len(df)) * 2, index=df.index),
                     BacktestConfig(k_in=1.5, k_out=0.2, max_hold_bars=12), TIER, NO_IMPACT)
    assert r.equity.iloc[-1] < 0 and r.fees_usd > 0
    assert summarize({"a": r})["net_bps_per_trade"] < 0
