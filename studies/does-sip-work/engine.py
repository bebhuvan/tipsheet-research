"""Path simulations for does-sip-work: mixes, FD accounts with transfers, stopping and lever strategies, tax.

Everything works per start month on a common monthly grid: month t buys on its first session and is
valued on its last. Amounts are rupees (₹10,000 a month unless stated).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from desk.sip import Panel, xirr_vec

AMT = 10_000.0
ST_RATE, LT_RATE, LT_EXEMPT = 0.20, 0.125, 125_000.0


# ---------------------------------------------------------------- an FD account that can pay out

class FDAccount:
    """A deposit account: daily growth at the FD's rate, interest taxed each 31 March and at closure."""

    def __init__(self, fd, start: pd.Timestamp):
        self.fd, self.t, self.bal, self.interest = fd, pd.Timestamp(start).normalize(), 0.0, 0.0
        self.taxed = fd.taxed

    def _grow(self, to: pd.Timestamp) -> None:
        if to > self.t:
            g = self.fd.growth(self.t, to)
            self.interest += self.bal * (g - 1)
            self.bal *= g
            self.t = to

    def roll(self, to: pd.Timestamp) -> None:
        """Accrue to `to`, taxing the year's interest at every 31 March on the way (including `to` itself)."""
        to = pd.Timestamp(to).normalize()
        while True:
            fy_end = pd.Timestamp(year=self.t.year, month=3, day=31)
            if fy_end <= self.t:
                fy_end = pd.Timestamp(year=self.t.year + 1, month=3, day=31)
            if fy_end > to:
                self._grow(to)
                return
            self._grow(fy_end)
            self._tax()
            if fy_end == to:
                return

    def _tax(self) -> None:
        if self.taxed:
            self.bal -= self.interest * 0.30 * 1.04
        self.interest = 0.0

    def deposit(self, when, amount: float) -> None:
        self.roll(when)
        self.bal += amount

    def withdraw(self, when, amount: float) -> float:
        self.roll(when)
        amount = min(amount, self.bal)
        self.bal -= amount
        return amount

    def close(self, when) -> float:
        self.roll(when)
        self._tax()
        out, self.bal = self.bal, 0.0
        return out


# ---------------------------------------------------------------- aligned monthly grids

def aligned(panels: dict[str, Panel], assets: list[str], from_month: pd.Period) -> dict:
    """Buy and end NAVs of several assets on their common months from `from_month`."""
    months = None
    for a in assets:
        m = panels[a].months
        months = m if months is None else months.intersection(m)
    months = months[months >= from_month]
    out = {"months": months}
    for a in assets:
        p = panels[a]
        pos = p.months.get_indexer(months)
        out[a] = {"buy": p.buy_nav[pos], "end": p.end_nav[pos], "buy_date": p.buy_date[pos], "end_date": p.end_date[pos]}
    out["buy_date"] = out[assets[0]]["buy_date"]
    out["end_date"] = out[assets[0]]["end_date"]
    return out


def mix_path(grid: dict, weights: dict[str, float], k: int, h: int, rebalance_months=(4,)) -> np.ndarray:
    """Month-end values of a SIP of ₹AMT a month into a mix, start k, h months. Each instalment is split at the
    target weights; in each month listed in rebalance_months (calendar month numbers), holdings are reset to the
    targets at that month's first session before the instalment. Before tax and trading costs."""
    assets = list(weights)
    w = np.array([weights[a] for a in assets])
    units = np.zeros(len(assets))
    vals = np.empty(h)
    for j in range(h):
        t = k + j
        buy = np.array([grid[a]["buy"][t] for a in assets])
        if j > 0 and grid["months"][t].month in rebalance_months:
            total = float((units * buy).sum())
            units = total * w / buy
        units = units + AMT * w / buy
        end = np.array([grid[a]["end"][t] for a in assets])
        vals[j] = float((units * end).sum())
    return vals


def single_path(p: Panel, k: int, h: int) -> np.ndarray:
    return AMT * p.value(np.full(h, k), np.arange(h))


def red_stats(values: np.ndarray, invested: np.ndarray) -> tuple[float, int, bool]:
    """(deepest fall below money put in, longest run of red month-ends, ever red)."""
    rel = values / invested - 1
    red = rel < 0
    longest, run = 0, 0
    for r in red:
        run = run + 1 if r else 0
        longest = max(longest, run)
    return float(rel.min()), longest, bool(red.any())


def xirr_flows(dates_list, amounts_list, end_dates, finals) -> np.ndarray:
    """XIRR of many cash-flow sets of different lengths (padded with zero flows)."""
    n = len(dates_list)
    m = max(len(d) for d in dates_list) + 1
    T = np.zeros((n, m))
    F = np.zeros((n, m))
    for i, (ds, am, e, v) in enumerate(zip(dates_list, amounts_list, end_dates, finals)):
        d0 = np.datetime64(ds[0])
        t = (np.array(ds, dtype="datetime64[ns]") - d0) / np.timedelta64(1, "D") / 365.0
        T[i, :len(t)] = t
        F[i, :len(t)] = -np.asarray(am, float)
        T[i, -1] = (np.datetime64(e) - d0) / np.timedelta64(1, "D") / 365.0
        F[i, -1] = v
    return xirr_vec(T, F)


# ---------------------------------------------------------------- tax on redeeming a SIP in full

def redemption_tax(buy_dates, units, buy_nav, end_date, end_nav, load: float = 0.0) -> dict:
    """Today's rules: short-term (held under a year) gains at 20%, long-term gains at 12.5% above ₹1.25 lakh;
    a short-term loss offsets either; a long-term loss only long-term gains. Optional exit load on short-term units."""
    held = (np.datetime64(end_date) - np.asarray(buy_dates, dtype="datetime64[ns]")) / np.timedelta64(1, "D")
    st = held < 365
    value_units = units * end_nav
    cost = units * buy_nav
    load_amt = load * value_units[st].sum()
    gain = value_units - cost
    g_st, g_lt = gain[st].sum() - load_amt, gain[~st].sum()
    if g_st < 0:
        g_lt += g_st
        g_st = 0.0
    tax = ST_RATE * max(g_st, 0.0) + LT_RATE * max(g_lt - LT_EXEMPT, 0.0)
    return {"value": float(value_units.sum()), "tax": float(tax), "load": float(load_amt),
            "st_units_share": float(st.mean()), "gain": float(gain.sum()), "st_gain": float(gain[st].sum())}
