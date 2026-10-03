import math

import numpy as np
import pandas as pd
import pytest

from mft import validation as v


def _ts(n, freq="5min"):
    return pd.date_range("2025-01-01", periods=n, freq=freq, tz="UTC")


def test_daily_ic_recovers_planted_and_rejects_noise():
    rng = np.random.default_rng(1)
    n = 288 * 40
    s = pd.Series(rng.standard_normal(n), index=_ts(n))
    f = 0.05 * s + rng.standard_normal(n)
    ic = v.ic_summary(v.daily_ic(s, f))
    assert ic["ic"] == pytest.approx(0.05, abs=0.02) and ic["t"] > 3
    noise = v.ic_summary(v.daily_ic(s, pd.Series(rng.standard_normal(n), index=s.index)))
    assert abs(noise["t"]) < 3


def test_intraday_ic_bias_on_random_walk_is_documented():
    """Long trailing-return signal vs forward return on a pure random walk: the within-day IC
    is biased negative, the pooled estimator is not. This is the bug the null test caught."""
    rng = np.random.default_rng(2)
    n = 1440 * 30
    px = pd.Series(np.exp(np.cumsum(rng.standard_normal(n) * 1e-3)), index=_ts(n, "1min"))
    sig = np.log(px / px.shift(240))
    fwd = np.log(px.shift(-60) / px)
    biased = v.ic_summary(v.intraday_ic(sig, fwd))
    pooled = v.ic_summary(v.daily_ic(sig, fwd))
    assert biased["ic"] < -0.03
    assert abs(pooled["ic"]) < abs(biased["ic"]) / 2


def test_event_study():
    rng = np.random.default_rng(3)
    n = 20_000
    s = np.zeros(n)
    ev = rng.choice(n, 400, replace=False)
    s[ev] = rng.choice([-1, 1], 400) * 5
    f = rng.standard_normal(n) * 10
    f[ev] += np.sign(s[ev]) * 4
    res = v.event_study(pd.Series(s), pd.Series(f), threshold=1, min_gap=1)
    assert res["n_events"] == 400 and res["mean_bps"] > 2 and res["t"] > 4
    few = v.event_study(pd.Series(np.zeros(100)), pd.Series(np.ones(100)), threshold=1)
    assert few["n_events"] == 0 and math.isnan(few["t"])
    two = v.event_study(pd.Series([5.0, 0, 0, 5.0]), pd.Series([1.0, 0, 0, 2.0]), threshold=1)
    assert two["n_events"] == 2 and math.isnan(two["t"])


def test_event_study_panel_deoverlaps_per_symbol_and_clusters_cascades():
    """Regression: on an interleaved (ts, symbol) panel the gap must count bars of the same
    symbol, and simultaneous events across symbols are one cluster (null test caught t=4.4)."""
    ts = pd.date_range("2025-01-01", periods=200, freq="1min", tz="UTC")
    syms = ["A", "B", "C"]
    idx = pd.MultiIndex.from_product([ts, syms])
    s = pd.Series(0.0, index=idx)
    f = pd.Series(np.random.default_rng(0).standard_normal(len(idx)), index=idx)
    for k in range(0, 200, 20):  # market-wide cascade every 20 bars, lasting 10 bars, all symbols
        for j in range(10):
            s.loc[(ts[k + j], slice(None))] = 5.0
    res = v.event_study(s, f, threshold=1, min_gap=15)
    assert res["n_events"] == 10  # 10 cascades, not 10 x 3 symbols x several rows


def test_point_in_time_detection():
    df = pd.DataFrame({"x": np.random.default_rng(0).standard_normal(500)})
    assert v.point_in_time_violations(lambda d: d["x"].rolling(10).mean(), df) == 0
    assert v.point_in_time_violations(lambda d: d["x"].rolling(10, center=True).mean(), df) > 0
    assert v.point_in_time_violations(lambda d: (d["x"] - d["x"].mean()), df) > 0


def test_regime_and_halves():
    rng = np.random.default_rng(4)
    n = 288 * 20
    s = pd.Series(rng.standard_normal(n), index=_ts(n))
    f = 0.1 * s + rng.standard_normal(n)
    reg = v.regime_ic(s, f, pd.Series(rng.random(n), index=s.index))
    assert len(reg) == 3 and (reg["ic"] > 0).all()
    h1, h2 = v.split_half_ic(s, f)
    assert h1 > 0 and h2 > 0
    assert v.daily_ic(s.iloc[:5], f.iloc[:5]).empty
    assert math.isnan(v.ic_summary(pd.Series(dtype=float))["ic"])


def test_sharpe_dsr_pbo():
    rng = np.random.default_rng(5)
    pnl = pd.Series(rng.normal(0.1, 1, 365))
    assert v.sharpe_annual(pnl) > 0
    assert v.sharpe_annual(pd.Series([1.0])) == 0.0
    assert v.expected_max_sharpe(1, 0.01) == 0.0
    d1 = v.deflated_sharpe(0.1, 365, 1, 0.003)
    d100 = v.deflated_sharpe(0.1, 365, 100, 0.003)
    assert d100 < d1
    noise = rng.standard_normal((400, 20))
    # one noise draw gives a very noisy PBO (the 70 splits are dependent): average over draws
    pbos = [v.pbo_cscv(np.random.default_rng(k).standard_normal((400, 20)), 8) for k in range(12)]
    assert 0.3 < float(np.mean(pbos)) < 0.7
    good = noise.copy()
    good[:, 0] += 0.5
    assert v.pbo_cscv(good, 8) < 0.1
    with pytest.raises(ValueError):
        v.pbo_cscv(noise[:, :1], 8)
    with pytest.raises(ValueError):
        v.pbo_cscv(noise, 7)


def test_signal_verdict():
    good = {"ic": 0.03, "t": 6.0}
    assert v.signal_verdict(good, +1, 40, (0.02, 0.03)) == "KEEP"
    assert v.signal_verdict(good, -1, 40, (0.02, 0.03)) == "KILL"  # wrong pre-registered sign
    assert v.signal_verdict({"ic": 0.03, "t": 2.5}, +1, 40, (0.02, 0.03)) == "WEAK"
    assert v.signal_verdict(good, +1, 40, (-0.01, 0.05)) == "KILL"  # unstable across halves
    assert v.signal_verdict({"ic": 0.03, "t": float("nan")}, +1, 40, (0.1, 0.1)) == "KILL"
