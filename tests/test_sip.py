"""Known-answer tests for desk.sip."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from desk import calc, sip


def sessions(start="2020-01-01", end="2022-12-31"):
    return pd.bdate_range(start, end)


def test_flat_market_returns_zero():
    idx = sessions()
    p = sip.Panel.from_nav(pd.Series(100.0, index=idx))
    k = p.starts(12)
    assert np.allclose(p.value(k, 11), 12.0)                      # 12 instalments of ₹1, no growth
    assert np.allclose(p.xirr(k, 12), 0.0, atol=1e-9)


def test_units_and_value_by_hand():
    # NAV 10 in month 1, 20 in month 2 (constant within each month), then 20
    idx = sessions("2021-01-01", "2021-03-31")
    nav = pd.Series(np.where(idx.month == 1, 10.0, 20.0), index=idx)
    p = sip.Panel.from_nav(nav)
    assert p.units(0, 1) == pytest.approx(1 / 10 + 1 / 20)       # 0.15 units for ₹2
    assert p.value(0, 1) == pytest.approx(0.15 * 20)              # ₹3 at the end of month 2
    assert p.value(0, 0) == pytest.approx(0.1 * 10)               # month 1 ends at 10


def test_xirr_matches_scalar_calc():
    idx = sessions("2015-01-01", "2020-12-31")
    rng = np.random.default_rng(1)
    nav = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, len(idx)))), index=idx)
    p = sip.Panel.from_nav(nav)
    k = 3
    v = p.xirr(np.array([k]), 36)[0]
    flows = [(pd.Timestamp(p.buy_date[k + i]).date(), -1.0) for i in range(36)]
    flows.append((pd.Timestamp(p.end_date[k + 35]).date(), float(p.value(k, 35))))
    assert v == pytest.approx(calc.xirr(flows), abs=1e-7)


def test_expense_ratio_costs_about_its_rate():
    idx = sessions("2010-01-01", "2020-12-31")
    level = pd.Series(100 * 1.10 ** ((idx - idx[0]).days / 365.0), index=idx)   # 10% a year exactly
    gross = sip.Panel.from_nav(sip.nav_after_costs(level, 0.0))
    net = sip.Panel.from_nav(sip.nav_after_costs(level, 0.01))
    k = gross.starts(120)
    g, n = gross.xirr(k, 120), net.xirr(k, 120)
    assert np.allclose(g, 0.10, atol=2e-4)
    assert np.allclose(g - n, 0.011, atol=5e-4)                  # 1.10 * 0.99 = 1.089: 1.1 points


def test_partial_last_month_dropped():
    idx = sessions("2021-01-01", "2021-03-10")
    p = sip.Panel.from_nav(pd.Series(1.0, index=idx))
    assert str(p.months[-1]) == "2021-02"


def test_xirr_vec_nan_when_no_sign_change():
    out = sip.xirr_vec(np.array([[0.0, 1.0]]), np.array([[-1.0, -1.0]]))
    assert np.isnan(out[0])
