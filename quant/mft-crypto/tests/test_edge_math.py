import math

import numpy as np
import pytest

from mft import edge_math as em


def test_sigma_and_tail_moments():
    assert em.sigma_h_bps(0.5, em.SECONDS_PER_YEAR) == pytest.approx(5000)
    assert em.mean_abs_s_given_trade(0.0) == pytest.approx(math.sqrt(2 / math.pi))
    assert em.trade_prob(0.0) == pytest.approx(1.0)
    assert em.mean_abs_s_given_trade(50.0) == 50.0  # tail underflow guard


def test_breakeven_ic_zeroes_net_edge():
    sig, cost, k = 30.0, 8.0, 1.2
    ic = em.breakeven_ic(sig, cost, k)
    assert em.gross_edge_bps(ic, sig, k) == pytest.approx(cost)
    assert em.round_trip_cost_bps(5, 5, 1, 0.5) == pytest.approx(12)


def test_no_edge_means_no_trade():
    best = em.best_threshold(0.0, 30.0, 5.0, 900)
    assert best["trade_prob"] == 0 and best["sharpe"] == 0 and math.isinf(best["k"])


def test_positive_edge_trades_and_sharpe_matches_monte_carlo():
    ic, sig, cost, k, h = 0.1, 20.0, 1.0, 1.0, 3600
    st = em.policy_stats(ic, sig, k, cost, h)
    rng = np.random.default_rng(0)
    n = 400_000
    s = rng.standard_normal(n)
    r = ic * sig * s + sig * math.sqrt(1 - ic**2) * rng.standard_normal(n)
    tr = np.abs(s) > k
    pnl = np.sign(s[tr]) * r[tr] - cost
    assert pnl.mean() == pytest.approx(st["net_edge_bps"], abs=0.15)
    assert tr.mean() == pytest.approx(st["trade_prob"], abs=0.005)


def test_combined_ic():
    assert em.combined_ic([0.03, 0.04]) == pytest.approx(0.05)
    corr = np.array([[1, 0.8], [0.8, 1]])
    assert em.combined_ic([0.03, 0.03], corr) < em.combined_ic([0.03, 0.03])


def test_ic_for_sharpe():
    ic = em.ic_for_sharpe(2.0, 40.0, 6.0, 3600, n_independent=4)
    assert 0 < ic < 0.2
    assert em.best_threshold(ic, 40.0, 6.0, 3600, 4)["sharpe"] >= 2.0
    assert math.isnan(em.ic_for_sharpe(1e9, 40.0, 6.0, 3600))
