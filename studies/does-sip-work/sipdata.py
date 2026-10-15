"""Inputs for does-sip-work, built once and shared by compute.py: asset NAVs, the FD and CPI.

Every input is read through desk.data (fingerprinted) or from reference/ (public RBI table, with its
source line). Conventions are the plan's "Common conventions".
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from desk import checks, data
from desk.sip import Panel, nav_after_costs

HERE = Path(__file__).resolve().parent
EXPENSE = {"equity": 0.0020, "Gold": 0.0050, "G-sec 5-year": 0.0030}
EQUITY = ["Nifty 500", "Nifty 50", "Nifty Midcap 150", "Nifty Smallcap 250"]
MENU_ASSETS = EQUITY + ["Gold", "G-sec 5-year"]
MIXES = {"60/40": {"Nifty 500": 0.6, "G-sec 5-year": 0.4},
         "60/20/20": {"Nifty 500": 0.6, "G-sec 5-year": 0.2, "Gold": 0.2},
         "Equal thirds": {"Nifty 500": 1 / 3, "G-sec 5-year": 1 / 3, "Gold": 1 / 3}}
MENU_START = pd.Period("2005-04", "M")
TAX_FD = 0.30 * 1.04
RETRIEVED_LAST_RATE = pd.Timestamp("2026-10-08")   # the Handbook's provisional latest row (see reference CSV)


@dataclass
class Inputs:
    levels: pd.DataFrame                    # total-return levels on NSE sessions
    navs: dict[str, pd.Series]              # after expense ratio
    panels: dict[str, Panel]
    deposit_rate: pd.Series                 # % a year, daily (calendar days)
    cpi: pd.Series                          # monthly, PeriodIndex
    pe: pd.DataFrame                        # daily trailing P/E, columns NIFTY_50, NIFTY_500
    amfi: pd.DataFrame                      # monthly AMFI SIP series
    notes: list[str] = field(default_factory=list)


def _deposit_rate(R, column: str = "dep_1_3y_high") -> pd.Series:
    path = HERE / "reference" / "rbi_deposit_rates_1_3y.csv"
    rows = list(csv.DictReader(line for line in path.read_text().splitlines() if not line.startswith("#")))
    pts = {}
    for r in rows:
        y = int(r["as_at_year"])
        d = RETRIEVED_LAST_RATE if r["fy"] == rows[-1]["fy"] else pd.Timestamp(f"{y}-03-31")
        pts[d] = float(r[column])
    s = pd.Series(pts).sort_index()
    days = pd.date_range(s.index[0], RETRIEVED_LAST_RATE + pd.Timedelta(days=400), freq="D")
    daily = s.reindex(days.union(s.index)).interpolate(method="time").reindex(days).ffill()
    if R is not None:
        R.input(f"reference:{path.name}", data.fingerprint(path))
    return daily


def load(R=None) -> Inputs:
    lv = data.load("portal:asset_tri_daily", R).set_index("d").sort_index()
    lv.index = pd.to_datetime(lv.index)
    if R is not None:
        checks.no_duplicates(lv.reset_index(), ["d"], R)
    sessions = lv.index[lv["Nifty 500"].notna()]
    lv = lv.loc[sessions]
    navs, panels = {}, {}
    for a in MENU_ASSETS:
        er = EXPENSE.get(a, EXPENSE["equity"])
        s = lv[a].dropna()
        if R is not None:
            daily = s.pct_change().dropna()
            checks.in_range(daily, -0.25, 0.25, R, name=f"input_daily_move[{a}]")
        navs[a] = nav_after_costs(s, er)
        panels[a] = Panel.from_nav(navs[a])

    cpi = data.load("portal:macro_cpi_monthly", R, columns=["d", "cpi_combined_index"]).dropna()
    cpi = cpi.set_index(pd.to_datetime(cpi["d"]).dt.to_period("M"))["cpi_combined_index"].sort_index()
    if R is not None:
        checks.in_range(cpi.pct_change().dropna(), -0.05, 0.08, R, name="input_cpi_monthly_change")

    v = data.load("databank:nifty_index_valuations", R, columns=["index_code", "date", "valuation_metric", "value"])
    v = v[(v.valuation_metric == "pe_ratio") & v.index_code.isin(["NIFTY_50", "NIFTY_500"])]
    pe = v.pivot_table(index="date", columns="index_code", values="value", aggfunc="last")
    pe.index = pd.to_datetime(pe.index)

    idh = data.path_of("databank:india_data_hub_series", R)
    import duckdb
    codes = ("CMMFSIPFLO11M:IND", "CMMFSIPNEW11M:IND", "CMMFSIPCLO11M:IND", "CMMFSIPACC11M:IND")
    a = duckdb.connect().execute(
        f"select series_id, observation_date, value, vintage_date from read_parquet('{idh}') where series_id in {codes}").df()
    a = a.sort_values("vintage_date").drop_duplicates(["series_id", "observation_date"], keep="last")
    amfi = a.pivot(index="observation_date", columns="series_id", values="value")
    amfi.index = pd.to_datetime(amfi.index).to_period("M")
    amfi = amfi.rename(columns={"CMMFSIPFLO11M:IND": "inflow", "CMMFSIPNEW11M:IND": "new",
                                "CMMFSIPCLO11M:IND": "closed", "CMMFSIPACC11M:IND": "outstanding"}).sort_index()

    return Inputs(lv, navs, panels, _deposit_rate(R), cpi, pe, amfi)


# ---------------------------------------------------------------- the FD

class FD:
    """Fixed deposits at the daily deposit rate, interest taxed at each 31 March (plan: Common conventions)."""

    def __init__(self, rate: pd.Series, taxed: bool = True, bump: float = 0.0, bump_from: str | None = None):
        r = rate.copy()
        if bump:
            r.loc[pd.Timestamp(bump_from):] = r.loc[pd.Timestamp(bump_from):] + bump
        g = np.log1p(r.to_numpy() / 100) / 365.0
        self.days = r.index
        self.logcum = pd.Series(np.concatenate([[0.0], np.cumsum(g)[:-1]]), index=r.index)   # growth up to day t
        self.taxed = taxed

    def growth(self, t1: pd.Timestamp, t2: pd.Timestamp) -> float:
        return float(np.exp(self.logcum.at[t2.normalize()] - self.logcum.at[t1.normalize()]))

    def value(self, dates, amounts, end: pd.Timestamp) -> float:
        """Final value at `end` of deposits (dates, amounts), interest taxed each 31 March."""
        events = sorted([(pd.Timestamp(d).normalize(), float(a)) for d, a in zip(dates, amounts)])
        end = pd.Timestamp(end).normalize()
        if not events:
            return 0.0
        fy_ends = [pd.Timestamp(f"{y}-03-31") for y in range(events[0][0].year, end.year + 1)]
        timeline = sorted([(d, "dep", a) for d, a in events] + [(d, "tax", 0.0) for d in fy_ends
                          if events[0][0] < d < end] + [(end, "end", 0.0)], key=lambda x: (x[0], x[1] != "dep"))
        bal, interest, t = 0.0, 0.0, timeline[0][0]
        for d, kind, a in timeline:
            if d > t:
                gr = self.growth(t, d)
                interest += bal * (gr - 1)
                bal *= gr
                t = d
            if kind == "dep":
                bal += a
            elif kind == "tax" and self.taxed:
                bal -= interest * TAX_FD
                interest = 0.0
            elif kind == "end":
                if self.taxed:
                    bal -= interest * TAX_FD
                return bal
        return bal


def deflator(cpi: pd.Series, dates) -> np.ndarray:
    """CPI level for each date's month; months after the latest CPI print use the latest (recorded in notes)."""
    per = pd.DatetimeIndex(dates).to_period("M")
    s = cpi.reindex(cpi.index.union(per)).sort_index().ffill()
    return s.reindex(per).to_numpy(float)
