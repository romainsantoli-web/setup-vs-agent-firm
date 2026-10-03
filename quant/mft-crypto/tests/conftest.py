import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mft.models import StudyConfig  # noqa: E402
from mft.synthetic import generate_market  # noqa: E402


@pytest.fixture(scope="session")
def planted_market():
    return generate_market(StudyConfig(n_symbols=3, n_days=16, bars_per_day=288, seed=5, planted=True))


@pytest.fixture(scope="session")
def null_market():
    return generate_market(StudyConfig(n_symbols=3, n_days=16, bars_per_day=288, seed=5, planted=False))


def make_bars(close, spread_bps=2.0, funding_bps=0.0, funding_every=None, wick=0.0, freq="1min"):
    close = np.asarray(close, dtype=float)
    idx = pd.date_range("2025-01-01", periods=len(close), freq=freq, tz="UTC")
    is_f = np.zeros(len(close), bool)
    if funding_every:
        is_f[::funding_every] = True
        is_f[0] = False
    return pd.DataFrame({
        "close": close, "high": close * (1 + wick), "low": close * (1 - wick),
        "spread_bps": spread_bps, "funding_rate_bps": funding_bps, "is_funding": is_f,
    }, index=idx)
