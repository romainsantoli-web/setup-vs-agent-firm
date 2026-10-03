import numpy as np
import pandas as pd
import pytest

from mft import combine as c
from mft.features import SIGNALS, btc_lead, compute_features, forward_return_bps, rolling_z
from mft.validation import point_in_time_violations


def test_every_signal_is_point_in_time(planted_market):
    df = planted_market["ALT01USDT"].iloc[:1500]
    for name, spec in SIGNALS.items():
        assert point_in_time_violations(lambda d, s=spec: s.fn(d, **s.params), df, n_cuts=3) == 0, name


def test_compute_features_and_errors(planted_market):
    df = planted_market["BTCUSDT"]
    f = compute_features(df)
    assert list(f.columns) == list(SIGNALS)
    assert (btc_lead(df) == 0).all()
    with pytest.raises(ValueError):
        compute_features(df, ["nope"])


def test_label_and_rolling_z():
    close = pd.Series([100.0, 101.0, 102.0])
    y = forward_return_bps(close, 1)
    assert y.iloc[0] == pytest.approx(np.log(1.01) * 1e4) and np.isnan(y.iloc[-1])
    z = rolling_z(pd.Series(np.arange(100.0)), 20)
    assert np.isfinite(z.iloc[-1])


def test_standardize_expanding_is_point_in_time():
    x = pd.DataFrame({"a": np.random.default_rng(0).standard_normal(800)})
    assert point_in_time_violations(lambda d: c.standardize_expanding(d, 100)["a"], x) == 0


def test_ridge_sign_constraint_and_small_sample():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((2000, 2))
    y = 0.5 * X[:, 0] - 0.5 * X[:, 1] + rng.standard_normal(2000)
    w = c.fit_ridge(X, y, 0.1)
    assert w[0] > 0 and w[1] < 0
    w_s = c.fit_ridge(X, y, 0.1, signs=np.array([1.0, 1.0]))
    assert w_s[1] == 0 and w_s[0] > 0
    assert (c.fit_ridge(X[:2], y[:2], 0.1) == 0).all()


def test_walk_forward_is_out_of_sample():
    rng = np.random.default_rng(1)
    idx = pd.date_range("2025-01-01", periods=288 * 12, freq="5min", tz="UTC")
    X = pd.DataFrame({"a": rng.standard_normal(len(idx)), "b": rng.standard_normal(len(idx))}, index=idx)
    y = pd.Series(0.3 * X["a"] + rng.standard_normal(len(idx)), index=idx)
    fc, w = c.walk_forward_forecast(X, y, train_days=4, test_days=2, embargo_bars=3)
    first_test = idx[0].floor("D") + pd.Timedelta(days=4)
    assert fc[idx < first_test].isna().all() and fc[idx >= first_test].notna().all()
    assert (w["a"] > 0).all() and len(w) == 4
    assert np.corrcoef(fc.dropna(), y[fc.notna()])[0, 1] > 0.2
    assert c.signal_correlation(X).shape == (2, 2)
