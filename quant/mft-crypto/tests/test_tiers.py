import math

import pytest

from mft.fees import BINANCE_UM
from mft.tiers import (_rt_fees, analytic_book, analytic_tier_row, bootstrap_ramp,
                       ic_required_for_sharpe, simulated_tier_table)

KW = dict(horizon_s=3600, annual_vol=0.7, n_symbols=20, n_independent=6, capital_usd=1e6,
          gross_leverage=3, execution="maker_both", spread_bps=1.0, adverse_bps=0.5, fill_rate=0.6)


def test_zero_ic_never_trades():
    res = analytic_book(BINANCE_UM, ic=0.0, **KW)
    assert res["reached"] == "VIP0" and res["bootstrap"] is None
    assert all(r["pnl_year_usd"] == 0 for r in res["table"])


def test_strong_ic_climbs_tiers_and_tables_are_consistent():
    res = analytic_book(BINANCE_UM, ic=0.06, **KW)
    assert res["path"][0] == "VIP0" and len(res["path"]) > 1
    sharpes = [r["sharpe"] for r in res["table"]]
    assert sharpes == sorted(sharpes)  # lower fees never hurt
    reached = next(r for r in res["table"] if r["tier"] == res["reached"])
    assert reached["self_sustaining"]


def test_bootstrap_ramp():
    row = analytic_tier_row(BINANCE_UM.tiers[3], ic=0.06, window_days=30, **KW)
    ramp = bootstrap_ramp(BINANCE_UM, row)
    assert 0 < ramp["days"] <= 30
    dead = dict(row, volume_window_usd=0.0)
    assert math.isnan(bootstrap_ramp(BINANCE_UM, dead)["days"])


def test_rt_fees_and_bad_execution():
    t = BINANCE_UM.tiers[0]
    assert _rt_fees(t, "taker") == 10 and _rt_fees(t, "maker_entry") == 7 and _rt_fees(t, "maker_both") == 4
    with pytest.raises(ValueError):
        _rt_fees(t, "iceberg")


def test_ic_required_for_sharpe():
    r = ic_required_for_sharpe(BINANCE_UM, 2.0, **KW)
    assert 0 < r["ic"] < 0.2 and r["tier"] is not None
    assert math.isnan(ic_required_for_sharpe(BINANCE_UM, 1e6, hi=0.01, **KW)["ic"])


def test_simulated_tier_table_fixed_point():
    def run_fn(tier):  # fake book: lower fees -> more volume
        vol = {"VIP0": 1e6, "VIP1": 3e6}.get(tier.name, 5e6)
        return {"volume_per_day": vol, "pnl_per_day": 100.0 - tier.taker_bps, "sharpe": 1.0}
    res = simulated_tier_table(BINANCE_UM, run_fn, scale=1.0)
    assert res["path"][:2] == ["VIP0", "VIP1"]
    assert res["reached"] == "VIP3"  # 5M/day * 30 = 150M
    assert len(res["table"]) == len(BINANCE_UM.tiers)
