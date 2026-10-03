import math

import pytest

from mft import kraken_costs as kc


def test_impact_interpolation_and_clamp():
    assert kc.impact_bps("PF_XBTUSD", 75_000) == pytest.approx(0.80)
    assert 0.41 < kc.impact_bps("PF_XBTUSD", 50_000) < 0.80
    assert kc.impact_bps("PF_XBTUSD", 1_000) == pytest.approx(0.41)  # clamped, no extrapolation
    with pytest.raises(ValueError):
        kc.impact_bps("PF_DOGEUSD", 25_000)


def test_round_trip_costs():
    assert kc.round_trip_bps("PF_XBTUSD", 75_000) == pytest.approx(10 + 1.6)
    assert kc.round_trip_bps("PF_XBTUSD", 75_000, "maker_entry") == pytest.approx(2 + 1.5 + 5 + 0.8)
    with pytest.raises(ValueError):
        kc.round_trip_bps("PF_XBTUSD", 75_000, "maker_both")


def test_required_ic_falls_with_horizon():
    one_h = kc.required_ic("PF_XBTUSD", 75_000, 3600, 0.5)
    day = kc.required_ic("PF_XBTUSD", 75_000, 86_400, 0.5)
    assert day["breakeven_ic_k1"] < one_h["breakeven_ic_k1"] / 4
    assert math.isfinite(one_h["ic_for_sharpe"]) and one_h["ic_for_sharpe"] > one_h["breakeven_ic_k1"] * 0.5
