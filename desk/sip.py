"""A monthly SIP engine for every start month at once, with tests in tests/test_sip.py.

Conventions (a study may change them, and says so in its plan):
- an instalment buys on the first session of each month, at that session's NAV;
- the statement value of month j is units held x the NAV on the last session of month j;
- NAV is the total-return level less a yearly expense ratio charged daily: level x (1 - er) ** (days / 365).

`Panel` precomputes cumulative units per rupee, so the value of any SIP (start month k, age j months)
is two lookups. `xirr_vec` solves many XIRRs at once by bisection.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def nav_after_costs(level: pd.Series, expense_ratio: float) -> pd.Series:
    """Total-return level less a yearly expense ratio charged daily."""
    level = level.dropna()
    days = (level.index - level.index[0]).days.to_numpy()
    return level * (1 - expense_ratio) ** (days / 365.0)


def month_sessions(index: pd.DatetimeIndex) -> pd.DataFrame:
    """For each calendar month in a session index: its first and last session."""
    s = pd.Series(index, index=index)
    g = s.groupby(index.to_period("M"))
    out = pd.DataFrame({"first": g.min(), "last": g.max()})
    out.index.name = "month"
    return out


@dataclass
class Panel:
    """Monthly buy and value prices of one NAV series. Month k buys at buy_nav[k], is valued at end_nav[k]."""
    months: pd.PeriodIndex
    buy_date: np.ndarray        # datetime64, first session of each month
    end_date: np.ndarray        # datetime64, last session of each month
    buy_nav: np.ndarray
    end_nav: np.ndarray
    cum_units: np.ndarray       # cum_units[k] = sum of 1/buy_nav[0:k]  (length n + 1)

    @classmethod
    def from_nav(cls, nav: pd.Series, drop_partial_last: bool = True) -> "Panel":
        nav = nav.dropna()
        ms = month_sessions(nav.index)
        if drop_partial_last and len(ms) > 1:
            # the latest month is incomplete unless its last session is the month's last weekday
            last = ms.index[-1]
            if ms["last"].iloc[-1] < (last.to_timestamp(how="end") - pd.offsets.BDay(1)).normalize():
                ms = ms.iloc[:-1]
        buy = nav.loc[ms["first"]].to_numpy(float)
        end = nav.loc[ms["last"]].to_numpy(float)
        return cls(ms.index, ms["first"].to_numpy(), ms["last"].to_numpy(), buy, end,
                   np.concatenate([[0.0], np.cumsum(1.0 / buy)]))

    def __len__(self) -> int:
        return len(self.months)

    def units(self, k: np.ndarray | int, j: np.ndarray | int) -> np.ndarray:
        """Units per ₹1 a month held after the instalment of month k + j, for a SIP started in month k."""
        k, j = np.asarray(k), np.asarray(j)
        return self.cum_units[k + j + 1] - self.cum_units[k]

    def value(self, k, j) -> np.ndarray:
        """Statement value per ₹1 a month at the end of month k + j (age j + 1 instalments)."""
        k, j = np.asarray(k), np.asarray(j)
        return self.units(k, j) * self.end_nav[k + j]

    def starts(self, horizon_months: int) -> np.ndarray:
        """Start months with a full horizon of data after them."""
        return np.arange(0, len(self) - horizon_months + 1)

    def xirr(self, starts: np.ndarray, horizon_months: int, amounts: np.ndarray | None = None) -> np.ndarray:
        """XIRR of each SIP of `horizon_months` instalments, valued at the end of its last month."""
        starts = np.asarray(starts)
        h = horizon_months
        idx = starts[:, None] + np.arange(h)[None, :]
        amt = np.ones_like(idx, float) if amounts is None else np.broadcast_to(amounts, idx.shape).astype(float)
        units = (amt / self.buy_nav[idx]).sum(axis=1)
        final = units * self.end_nav[starts + h - 1]
        t0 = self.buy_date[starts]
        times = (self.buy_date[idx] - t0[:, None]) / np.timedelta64(1, "D") / 365.0
        t_end = (self.end_date[starts + h - 1] - t0) / np.timedelta64(1, "D") / 365.0
        flows = np.concatenate([-amt, final[:, None]], axis=1)
        all_t = np.concatenate([times, t_end[:, None]], axis=1)
        return xirr_vec(all_t, flows)


def xirr_vec(times: np.ndarray, flows: np.ndarray, lo: float = -0.9999, hi: float = 10.0, iters: int = 200) -> np.ndarray:
    """XIRR for each row of (times in years, flows), by bisection. Rows whose flows don't change sign get NaN."""
    times, flows = np.atleast_2d(times).astype(float), np.atleast_2d(flows).astype(float)
    n = len(times)
    a, b = np.full(n, lo), np.full(n, hi)

    def npv(r):
        return (flows * np.power(1.0 + r[:, None], -times)).sum(axis=1)

    fa = npv(a)
    fb = npv(b)
    ok = (fa * fb) <= 0
    for _ in range(iters):
        m = (a + b) / 2
        fm = npv(m)
        left = (fa * fm) <= 0
        b = np.where(left, m, b)
        fb = np.where(left, fm, fb)
        a = np.where(left, a, m)
        fa = np.where(left, fa, fm)
    out = (a + b) / 2
    out[~ok] = np.nan
    return out
