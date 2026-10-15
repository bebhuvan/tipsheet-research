"""Known-answer tests for desk.calc: hand-worked cases and published examples."""

from datetime import date

import numpy as np
import pytest

from desk import calc


def test_simple_return_and_cagr():
    assert calc.simple_return(100, 125) == pytest.approx(0.25)
    assert calc.cagr(100, 200, 10) == pytest.approx(2 ** 0.1 - 1)          # doubling in 10 years: 7.18% a year
    with pytest.raises(ValueError):
        calc.cagr(0, 100, 1)


def test_xirr_one_year_leap():
    # 366 days at 10% total: (1.1) ** (365 / 366) - 1
    r = calc.xirr([(date(2020, 1, 1), -1000), (date(2021, 1, 1), 1100)])
    assert r == pytest.approx(1.1 ** (365 / 366) - 1, abs=1e-9)


def test_xirr_microsoft_published_example():
    # Microsoft's documented XIRR example (support.microsoft.com, XIRR function): 0.373362535
    flows = [(date(2008, 1, 1), -10000), (date(2008, 3, 1), 2750), (date(2008, 10, 30), 4250),
             (date(2009, 2, 15), 3250), (date(2009, 4, 1), 2750)]
    assert calc.xirr(flows) == pytest.approx(0.373362535, abs=1e-6)


def test_xirr_monthly_sip_zero_growth():
    # ₹1,000 a month for 12 months, redeemed at exactly what was put in: 0% return
    flows = [(date(2024, m, 1), -1000) for m in range(1, 13)] + [(date(2025, 1, 1), 12000)]
    assert calc.xirr(flows) == pytest.approx(0.0, abs=1e-8)


def test_welch_hand_worked():
    w = calc.welch([1, 2, 3, 4], [2, 4, 6, 8])
    # var_a/n = 1.6667/4, var_b/n = 6.6667/4; t = -2.5 / sqrt(2.08333) = -1.7320508
    assert w["t"] == pytest.approx(-1.7320508, abs=1e-6)
    assert w["diff"] == pytest.approx(-2.5)
    assert 0 < w["p"] < 1


def test_holm():
    out = calc.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert out == {"a": True, "c": False, "b": False}


def test_independent_periods():
    assert calc.independent_periods(120, 12) == 10
    assert calc.independent_periods(119, 12) == 9


def test_bootstrap_brackets_estimate():
    x = np.arange(100, dtype=float)
    est, lo, hi = calc.bootstrap_ci(x, np.median)
    assert est == 49.5 and lo < est < hi


def test_block_bootstrap_wider_for_overlapping_windows():
    # Rolling 12-row sums of white noise overlap heavily; the block bootstrap must give a wider band than iid.
    rng = np.random.default_rng(0)
    noise = rng.normal(size=600)
    rolling = np.convolve(noise, np.ones(12), mode="valid")
    _, lo_i, hi_i = calc.bootstrap_ci(rolling, np.mean)
    _, lo_b, hi_b = calc.block_bootstrap_ci(rolling, block=12)
    assert (hi_b - lo_b) > 1.5 * (hi_i - lo_i)
