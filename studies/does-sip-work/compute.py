"""does-sip-work: compute every question in plan.md (frozen at the commit in freeze.json).

Run from the repo root:  uv run python studies/does-sip-work/compute.py
Inputs and conventions: sipdata.py; path simulations: engine.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine as E          # noqa: E402
import sipdata as SD        # noqa: E402
from desk.results import Results  # noqa: E402
from desk.sip import Panel, nav_after_costs  # noqa: E402

HORIZONS = [1, 3, 5, 7, 10, 15, 20]
AMT = E.AMT
R: Results
I: SD.Inputs
FDT: SD.FD          # taxed FD at the top of RBI's range (the plan's FD)


# ---------------------------------------------------------------- helpers

def q(x, p):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return float(np.quantile(x, p)) if len(x) else float("nan")


def med(x):
    return q(x, 0.5)


def episodes(flags: np.ndarray) -> int:
    """Runs of consecutive True start months."""
    f = np.asarray(flags, bool)
    return int(((f[1:] & ~f[:-1]).sum()) + (1 if len(f) and f[0] else 0))


def indep(p: Panel, months: int) -> float:
    return round(len(p) / months, 1)


def windows(asset: str, years: int, start_from: pd.Period | None = None) -> dict:
    p = I.panels[asset]
    h = 12 * years
    k = p.starts(h)
    if start_from is not None:
        k = k[p.months[k] >= start_from]
    inv = AMT * h
    final = AMT * p.value(k, h - 1)
    return {"p": p, "k": k, "h": h, "inv": inv, "final": final, "xirr": p.xirr(k, h),
            "start": p.months[k], "end_date": p.end_date[k + h - 1]}


def fd_finals(p: Panel, k: np.ndarray, h: int, fd: SD.FD = None) -> np.ndarray:
    fd = fd or FDT
    return np.array([fd.value(p.buy_date[i:i + h], [AMT] * h, pd.Timestamp(p.end_date[i + h - 1])) for i in k])


def real_xirr(p: Panel, k: np.ndarray, h: int) -> np.ndarray:
    out = []
    for i in k:
        bd = p.buy_date[i:i + h]
        c0 = SD.deflator(I.cpi, [bd[0]])[0]
        defl = c0 / SD.deflator(I.cpi, bd)
        fin = AMT * p.value(i, h - 1) * c0 / SD.deflator(I.cpi, [p.end_date[i + h - 1]])[0]
        out.append((bd, AMT * defl, p.end_date[i + h - 1], fin))
    return E.xirr_flows([o[0] for o in out], [o[1] for o in out], [o[2] for o in out], [o[3] for o in out])


def after_tax_final(p: Panel, i: int, h: int, load: float = 0.0, amt: float = AMT) -> dict:
    bd = p.buy_date[i:i + h]
    units = amt / p.buy_nav[i:i + h]
    return E.redemption_tax(bd, units, p.buy_nav[i:i + h], p.end_date[i + h - 1], p.end_nav[i + h - 1], load)


def era_mask(starts: pd.PeriodIndex) -> tuple[np.ndarray, np.ndarray]:
    early = np.asarray(starts < pd.Period("2005-01", "M"))
    return early, ~early


def pct_fact(key, frac, note="", exploratory=False):
    R.fact(key, frac, "fraction", note, exploratory)


# ================================================================= Chapter 1

def q1():
    rows = []
    n500 = I.panels["Nifty 500"]
    for y in HORIZONS:
        w = windows("Nifty 500", y)
        fdv = fd_finals(n500, w["k"], w["h"])
        rx = real_xirr(n500, w["k"], w["h"])
        tax = np.array([after_tax_final(n500, i, w["h"])["tax"] for i in w["k"]])
        after = w["final"] - tax
        lost, lost_at = w["final"] < w["inv"], after < w["inv"]
        below_fd, below_fd_at = w["final"] < fdv, after < fdv
        below_inf = rx < 0
        pct_fact(f"q1_n500_{y}y_lost", lost.mean(), "before tax")
        pct_fact(f"q1_n500_{y}y_lost_after_tax", lost_at.mean())
        pct_fact(f"q1_n500_{y}y_below_fd", below_fd.mean(), "before tax on the SIP; FD after tax")
        pct_fact(f"q1_n500_{y}y_below_fd_after_tax", below_fd_at.mean())
        pct_fact(f"q1_n500_{y}y_below_inflation", below_inf.mean())
        R.fact(f"q1_n500_{y}y_starts", len(w["k"]), "count")
        R.fact(f"q1_n500_{y}y_independent", indep(n500, w["h"]), "plain")
        R.fact(f"q1_n500_{y}y_loss_episodes", episodes(lost), "count")
        e, l = era_mask(w["start"])
        rows.append({"horizon": y, "lost": lost.mean(), "below_fd": below_fd.mean(), "below_inflation": below_inf.mean(),
                     "lost_after_tax": lost_at.mean(), "below_fd_after_tax": below_fd_at.mean(),
                     "independent": indep(n500, w["h"]), "starts": len(w["k"]),
                     "below_fd_early": below_fd[e].mean() if e.any() else None,
                     "below_fd_late": below_fd[l].mean() if l.any() else None})
        if y in (5, 10):
            fd_low = SD.FD(I.deposit_rate_low)
            fdl = fd_finals(n500, w["k"], w["h"], fd_low)
            pct_fact(f"q1_n500_{y}y_below_fd_low", (w["final"] < fdl).mean(), "FD at the bottom of RBI's range")
            for era, m in (("1995_2004", e), ("2005_on", l)):
                if m.any():
                    pct_fact(f"q1_n500_{y}y_below_fd_{era}", below_fd[m].mean())
                    pct_fact(f"q1_n500_{y}y_lost_{era}", lost[m].mean())
    R.chart("q1_by_horizon", rows)
    # shortest horizon (whole years) after which no start month lost money
    last_loss = 0
    for y in range(1, 21):
        w = windows("Nifty 500", y)
        if (w["final"] < w["inv"]).any():
            last_loss = y
    R.fact("q1_n500_no_loss_from_years", last_loss + 1, "years")
    R.check("era_split", True, "below-FD and loss shares split at 2005 starts recorded for 5 and 10 years", "q1")
    R.check("robustness", True, "FD at the bottom of RBI's range and after-tax versions recorded", "q1")
    # the menu at 5 and 10 years
    menu = []
    for y in (5, 10):
        for a in SD.MENU_ASSETS:
            w = windows(a, y, SD.MENU_START)
            fdv = fd_finals(w["p"], w["k"], w["h"])
            menu.append({"asset": a, "horizon": y, "lost": float((w["final"] < w["inv"]).mean()),
                         "below_fd": float((w["final"] < fdv).mean()), "starts": len(w["k"])})
    R.chart("q1_menu", menu)


def q2():
    n500 = I.panels["Nifty 500"]
    fan, values = [], []
    latest_cpi = float(I.cpi.iloc[-1])
    for y in HORIZONS:
        w = windows("Nifty 500", y)
        x = w["xirr"]
        row = {"horizon": y, **{f"p{int(p * 100)}": q(x, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)},
               "worst": float(np.nanmin(x)), "best": float(np.nanmax(x))}
        fan.append(row)
        for p_ in (0.05, 0.5, 0.95):
            R.fact(f"q2_n500_{y}y_p{int(p_ * 100)}", q(x, p_), "fraction")
        R.fact(f"q2_n500_{y}y_worst", row["worst"], "fraction")
        R.fact(f"q2_n500_{y}y_best", row["best"], "fraction")
        if y in (10, 15, 20):
            today = w["final"] * latest_cpi / SD.deflator(I.cpi, w["end_date"])
            for p_ in (0.05, 0.5, 0.95):
                R.fact(f"q2_n500_{y}y_value_p{int(p_ * 100)}", q(w["final"], p_), "rupees")
                R.fact(f"q2_n500_{y}y_value_today_p{int(p_ * 100)}", q(today, p_), "rupees", "in today's rupees (CPI)")
            R.fact(f"q2_n500_{y}y_invested", w["inv"], "rupees")
            values.append({"horizon": y, "invested": w["inv"], "p5": q(w["final"], .05), "p50": med(w["final"]),
                           "p95": q(w["final"], .95), "today_p50": med(today)})
    R.chart("q2_fan", fan)
    R.chart("q2_values", values)
    # the calculator's 12%
    R.context("calculator_rate_pct", 12)
    w = windows("Nifty 500", 10)
    pct_fact("q2_n500_10y_share_below_12pct", float((w["xirr"] < 0.12).mean()))
    e, l = era_mask(w["start"])
    R.fact("q2_n500_10y_median_1995_2004", med(w["xirr"][e]), "fraction")
    R.fact("q2_n500_10y_median_2005_on", med(w["xirr"][l]), "fraction")
    R.check("era_split", True, "10-year medians by era recorded", "q2")
    w50 = windows("Nifty 50", 10)
    R.fact("q2_n50_10y_p50", med(w50["xirr"]), "fraction")
    R.fact("q2_n50_10y_worst", float(np.nanmin(w50["xirr"])), "fraction")
    R.fact("q2_n50_10y_best", float(np.nanmax(w50["xirr"])), "fraction")
    R.check("robustness", True, "Nifty 50 from 1999 recorded", "q2")


def q3():
    n500 = I.panels["Nifty 500"]
    rows = []
    for y in (5, 10, 15, 20):
        w = windows("Nifty 500", y)
        rx = real_xirr(n500, w["k"], w["h"])
        rows.append({"horizon": y, "nominal_p5": q(w["xirr"], .05), "nominal_p50": med(w["xirr"]), "nominal_p95": q(w["xirr"], .95),
                     "real_p5": q(rx, .05), "real_p50": med(rx), "real_p95": q(rx, .95)})
        R.fact(f"q3_n500_{y}y_real_p50", med(rx), "fraction")
        R.fact(f"q3_n500_{y}y_real_p5", q(rx, .05), "fraction")
        pct_fact(f"q3_n500_{y}y_real_below_zero", float((rx < 0).mean()))
        if y == 10:
            e, l = era_mask(w["start"])
            R.fact("q3_n500_10y_real_p50_1995_2004", med(rx[e]), "fraction")
            R.fact("q3_n500_10y_real_p50_2005_on", med(rx[l]), "fraction")
    R.chart("q3_real_nominal", rows)
    # whole-period index returns, nominal and real, and the FD's
    for a, key in (("Nifty 500", "n500"), ("Nifty 50", "n50")):
        s = I.levels[a].dropna()
        t0, t1 = s.index[0], s.index[-1]
        yrs = (t1 - t0).days / 365.0
        nom = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
        c0, c1 = SD.deflator(I.cpi, [t0, t1])
        real = ((s.iloc[-1] / s.iloc[0]) * c0 / c1) ** (1 / yrs) - 1
        R.fact(f"q3_{key}_index_nominal", nom, "fraction", f"total return, {t0.date()} to {t1.date()}")
        R.fact(f"q3_{key}_index_real", real, "fraction")
        acct = E.FDAccount(FDT, t0)
        acct.deposit(t0, 1.0)
        fdv = acct.close(t1)
        R.fact(f"q3_{key}_fd_nominal", fdv ** (1 / yrs) - 1, "fraction", "FD after tax, same dates")
        R.fact(f"q3_{key}_fd_real", (fdv * c0 / c1) ** (1 / yrs) - 1, "fraction")
        R.label(f"q3_{key}_from", t0.strftime("%B %Y"))
    R.check("era_split", True, "real 10-year medians by era recorded", "q3")


# ================================================================= Chapter 2

GRID = None


def mix_windows(name: str, years: int, rebalance=(4,)) -> dict:
    weights = SD.MIXES[name]
    h = 12 * years
    n = len(GRID["months"])
    ks = np.arange(0, n - h + 1)
    paths = [E.mix_path(GRID, weights, k, h, rebalance) for k in ks]
    final = np.array([pth[-1] for pth in paths])
    dates = [GRID["buy_date"][k:k + h] for k in ks]
    ends = [GRID["end_date"][k + h - 1] for k in ks]
    x = E.xirr_flows(dates, [[AMT] * h] * len(ks), ends, final)
    inv = AMT * np.arange(1, h + 1)
    rs = [E.red_stats(pth, inv) for pth in paths]
    return {"k": ks, "h": h, "final": final, "xirr": x, "deep": np.array([r[0] for r in rs]),
            "longest": np.array([r[1] for r in rs]), "paths": paths, "start": GRID["months"][ks]}


def single_menu_windows(asset: str, years: int) -> dict:
    """A single asset on the menu's months (so it pairs start-for-start with the mixes)."""
    p = I.panels[asset]
    h = 12 * years
    n = len(GRID["months"])
    ks = np.arange(0, n - h + 1)
    pk = p.months.get_indexer(GRID["months"][ks])
    paths = [E.single_path(p, int(i), h) for i in pk]
    inv = AMT * np.arange(1, h + 1)
    rs = [E.red_stats(pth, inv) for pth in paths]
    return {"k": ks, "h": h, "final": np.array([pth[-1] for pth in paths]), "xirr": p.xirr(pk, h),
            "deep": np.array([r[0] for r in rs]), "longest": np.array([r[1] for r in rs]), "pk": pk, "p": p,
            "start": GRID["months"][ks], "paths": paths}


def q4():
    rows = []
    for y in (5, 10):
        for a in SD.MENU_ASSETS:
            w = single_menu_windows(a, y)
            fdv = fd_finals(w["p"], w["pk"], w["h"])
            key = a.lower().replace("nifty ", "").replace(" ", "").replace("-", "").replace("/", "")
            r = {"asset": a, "horizon": y, "median": med(w["xirr"]), "p5": q(w["xirr"], .05), "worst": float(np.nanmin(w["xirr"])),
                 "below_fd": float((w["final"] < fdv).mean()), "deepest_median": med(w["deep"]), "deepest_worst": float(w["deep"].min()),
                 "longest_median": med(w["longest"]), "longest_max": int(w["longest"].max()), "starts": len(w["k"])}
            rows.append(r)
            R.fact(f"q4_{key}_{y}y_p50", r["median"], "fraction")
            R.fact(f"q4_{key}_{y}y_p5", r["p5"], "fraction")
            R.fact(f"q4_{key}_{y}y_worst", r["worst"], "fraction")
            pct_fact(f"q4_{key}_{y}y_below_fd", r["below_fd"])
            R.fact(f"q4_{key}_{y}y_deepest_worst", r["deepest_worst"], "fraction")
            R.fact(f"q4_{key}_{y}y_longest_red_max", r["longest_max"], "months")
    R.fact("q4_menu_10y_starts", rows[-1]["starts"], "count")
    R.fact("q4_menu_10y_independent", round(len(GRID["months"]) / 120, 1), "plain")
    R.chart("q4_assets", rows)
    R.check("era_split", True, "not possible within the menu's 2005 window; back-calculated mid/small-cap history flagged instead", "q4")
    R.check("robustness", True, "Nifty 50 recorded as the large-cap line beside the Nifty 500", "q4")


MIXW = {}


def q5():
    out = []
    for y in (5, 10, 15):
        base = single_menu_windows("Nifty 500", y)
        R.fact(f"q5_n500_{y}y_p50", med(base["xirr"]), "fraction")
        R.fact(f"q5_n500_{y}y_p5", q(base["xirr"], .05), "fraction")
        R.fact(f"q5_n500_{y}y_worst", float(np.nanmin(base["xirr"])), "fraction")
        R.fact(f"q5_n500_{y}y_deepest_worst", float(base["deep"].min()), "fraction")
        for name in SD.MIXES:
            m = mix_windows(name, y)
            MIXW[(name, y)] = m
            key = {"60/40": "m6040", "60/20/20": "m602020", "Equal thirds": "mthirds"}[name]
            given_up = med(base["final"]) - med(m["final"])
            gained_p5 = q(m["final"], .05) - q(base["final"], .05)
            gained_worst = float(m["final"].min() - base["final"].min())
            inv = AMT * 12 * y
            # the deepest fall in rupees, at its worst start month, for each
            def worst_hole(w):
                return min(float(np.min(pth - AMT * np.arange(1, len(pth) + 1))) for pth in w["paths"])
            hole_base, hole_mix = worst_hole(base), worst_hole(m)
            R.fact(f"q5_{key}_{y}y_p50", med(m["xirr"]), "fraction")
            R.fact(f"q5_{key}_{y}y_p5", q(m["xirr"], .05), "fraction")
            R.fact(f"q5_{key}_{y}y_worst", float(np.nanmin(m["xirr"])), "fraction")
            R.fact(f"q5_{key}_{y}y_deepest_worst", float(m["deep"].min()), "fraction")
            R.fact(f"q5_{key}_{y}y_given_up_median", given_up, "rupees", "median final value, Nifty 500 minus mix")
            R.fact(f"q5_{key}_{y}y_gained_p5", gained_p5, "rupees", "5th-percentile final value, mix minus Nifty 500")
            R.fact(f"q5_{key}_{y}y_gained_worst", gained_worst, "rupees")
            R.fact(f"q5_{key}_{y}y_hole_reduction", hole_mix - hole_base, "rupees", "worst rupee shortfall below money put in, mix less deep by")
            out.append({"mix": name, "horizon": y, "given_up_median": given_up, "gained_p5": gained_p5, "gained_worst": gained_worst,
                        "hole_base": hole_base, "hole_mix": hole_mix, "invested": inv, "starts": len(m["k"]),
                        "median_xirr": med(m["xirr"]), "p5_xirr": q(m["xirr"], .05), "deepest_median": med(m["deep"])})
    R.chart("q5_price_of_protection", out)
    r10 = [o for o in out if o["mix"] == "60/20/20" and o["horizon"] == 10][0]
    r5 = [o for o in out if o["mix"] == "60/20/20" and o["horizon"] == 5][0]
    R.fact("q5_P5_holds", bool(r10["given_up_median"] > r10["gained_p5"] and r5["given_up_median"] < r5["gained_p5"]), "text")
    # robustness: no rebalancing for 60/20/20 at 10 years
    m = mix_windows("60/20/20", 10, rebalance=())
    R.fact("q5_m602020_10y_p50_norebal", med(m["xirr"]), "fraction")
    R.check("robustness", True, "60/40 and equal thirds recorded beside 60/20/20; 60/20/20 without rebalancing recorded", "q5")


def q6():
    rows = []
    for name, key in (("60/20/20", "m602020"), ("60/40", "m6040")):
        for y, reb2 in ((10, (4, 10)), (15, (4, 10))):
            on = MIXW.get((name, y)) or mix_windows(name, y)
            off = mix_windows(name, y, rebalance=())
            d = on["xirr"] - off["xirr"]
            semi = mix_windows(name, y, rebalance=reb2)
            d2 = semi["xirr"] - off["xirr"]
            R.fact(f"q6_{key}_{y}y_diff_p50", med(d), "fraction", "rebalanced each April minus never, paired by start month")
            R.fact(f"q6_{key}_{y}y_diff_p10", q(d, .1), "fraction")
            R.fact(f"q6_{key}_{y}y_diff_p90", q(d, .9), "fraction")
            R.fact(f"q6_{key}_{y}y_deep_on_p50", med(on["deep"]), "fraction")
            R.fact(f"q6_{key}_{y}y_deep_off_p50", med(off["deep"]), "fraction")
            R.fact(f"q6_{key}_{y}y_semi_diff_p50", med(d2), "fraction", "rebalanced April and October minus never")
            rows += [{"mix": name, "horizon": y, "start": str(s), "diff": float(v)} for s, v in zip(on["start"], d)]
            if name == "60/20/20" and y == 10:
                R.fact("q6_P6_holds", bool(abs(med(d)) <= 0.005 and med(on["deep"]) > med(off["deep"])), "text")
    R.chart("q6_paired", rows)
    R.check("robustness", True, "six-monthly rebalancing and 15-year windows recorded", "q6")


# ================================================================= Chapter 3

def q7():
    rows = []
    for y in (5, 10, 15, 20):
        w = windows("Nifty 500", y)
        mult = w["final"] / w["inv"]
        rng = q(w["xirr"], .95) - q(w["xirr"], .05)
        mrng = q(mult, .95) - q(mult, .05)
        R.fact(f"q7_n500_{y}y_xirr_range", rng, "fraction", "95th minus 5th percentile")
        R.fact(f"q7_n500_{y}y_multiple_range", mrng, "ratio")
        R.fact(f"q7_n500_{y}y_multiple_p5", q(mult, .05), "ratio")
        R.fact(f"q7_n500_{y}y_multiple_p95", q(mult, .95), "ratio")
        rows.append({"horizon": y, "xirr_p5": q(w["xirr"], .05), "xirr_p95": q(w["xirr"], .95), "mult_p5": q(mult, .05),
                     "mult_p95": q(mult, .95), "independent": indep(w["p"], w["h"])})
        if y == 10:
            e, l = era_mask(w["start"])
            R.fact("q7_n500_10y_xirr_range_1995_2004", q(w["xirr"][e], .95) - q(w["xirr"][e], .05), "fraction")
            R.fact("q7_n500_10y_xirr_range_2005_on", q(w["xirr"][l], .95) - q(w["xirr"][l], .05), "fraction")
    R.chart("q7_ranges", rows)
    R.check("era_split", True, "10-year ranges by era recorded", "q7")


def q8():
    w = windows("Nifty 500", 10)
    yr = pd.Series(w["xirr"], index=[s.year for s in w["start"]])
    by = yr.groupby(level=0).median()
    R.chart("q8_by_start_year", [{"year": int(k), "median": float(v), "n": int((yr.index == k).sum())} for k, v in by.items()])
    R.fact("q8_n500_10y_best_year_median", float(by.max()), "fraction")
    R.label("q8_best_year", str(int(by.idxmax())))
    R.fact("q8_n500_10y_worst_year_median", float(by.min()), "fraction")
    R.label("q8_worst_year", str(int(by.idxmin())))
    R.fact("q8_n500_10y_year_spread", float(by.max() - by.min()), "fraction")
    lv = I.levels["Nifty 500"]
    peak = lv.cummax()
    below = 1 - lv / peak
    p = w["p"]
    dist = below.reindex(pd.DatetimeIndex(p.buy_date[w["k"]])).to_numpy()
    bands = {"within 2%": dist <= 0.02, "2-10% below": (dist > 0.02) & (dist <= 0.10), "over 10% below": dist > 0.10}
    rows = []
    for name, m in bands.items():
        key = {"within 2%": "near_high", "2-10% below": "mid", "over 10% below": "far"}[name]
        R.fact(f"q8_n500_10y_{key}_p50", med(w["xirr"][m]), "fraction")
        R.fact(f"q8_n500_10y_{key}_n", int(m.sum()), "count")
        rows.append({"band": name, "median": med(w["xirr"][m]), "p5": q(w["xirr"][m], .05), "p95": q(w["xirr"][m], .95), "n": int(m.sum())})
    R.chart("q8_bands", rows)
    e, l = era_mask(w["start"])
    for era, m in (("1995_2004", e), ("2005_on", l)):
        R.fact(f"q8_n500_10y_near_high_p50_{era}", med(w["xirr"][m & bands["within 2%"]]), "fraction")
        R.fact(f"q8_n500_10y_far_p50_{era}", med(w["xirr"][m & bands["over 10% below"]]), "fraction")
    R.check("era_split", True, "band medians by era recorded", "q8")


def glide(p: Panel, k: int, h: int, steps: int, fd: SD.FD) -> float:
    """SIP into equity, switching the corpus to the FD in equal monthly steps over the last `steps` months;
    instalments in those months go to the FD. Before tax on the equity side."""
    units = 0.0
    acct = E.FDAccount(fd, pd.Timestamp(p.buy_date[k]))
    switch_from = h - steps
    for j in range(h):
        t = k + j
        d = pd.Timestamp(p.buy_date[t])
        if j >= switch_from:
            remaining = h - j
            sell = units / remaining
            units -= sell
            acct.deposit(d, sell * p.buy_nav[t])
            acct.deposit(d, AMT)
        else:
            units += AMT / p.buy_nav[t]
    end = pd.Timestamp(p.end_date[k + h - 1])
    return units * p.end_nav[k + h - 1] + acct.close(end)


def q9():
    w = windows("Nifty 500", 15)
    p, h = w["p"], w["h"]
    first5 = np.array([AMT * p.units(i, 59) * p.end_nav[i + h - 1] for i in w["k"]]) / w["final"]
    last5 = np.array([AMT * (p.units(i, h - 1) - p.units(i, h - 61)) * p.end_nav[i + h - 1] for i in w["k"]]) / w["final"]
    pct_fact("q9_n500_15y_first5_share_p50", med(first5), "share of final value from the first five years' instalments")
    pct_fact("q9_n500_15y_last5_share_p50", med(last5))
    first3 = p.buy_nav[w["k"] + 36] / p.buy_nav[w["k"]] - 1
    last3 = p.end_nav[w["k"] + h - 1] / p.buy_nav[w["k"] + h - 36] - 1
    R.fact("q9_n500_15y_corr_first3", float(spearmanr(w["xirr"], first3).statistic), "ratio")
    R.fact("q9_n500_15y_corr_last3", float(spearmanr(w["xirr"], last3).statistic), "ratio")
    R.fact("q9_n500_15y_starts", len(w["k"]), "count")
    R.fact("q9_n500_15y_independent", indep(p, h), "plain")
    R.chart("q9_value_by_year", [{"year": y + 1, "share": med(np.array([AMT * (p.units(i, 12 * y + 11) - (p.units(i, 12 * y - 1) if y else 0)) * p.end_nav[i + h - 1] for i in w["k"]]) / w["final"])} for y in range(15)])
    # the glide to the FD
    res = {}
    for steps, fd, tag in ((36, FDT, "g36"), (12, FDT, "g12"), (36, SD.FD(I.deposit_rate_low), "g36_low")):
        gv = np.array([glide(p, int(i), h, steps, fd) for i in w["k"]])
        res[tag] = gv
        R.fact(f"q9_{tag}_p50", med(gv), "rupees")
        R.fact(f"q9_{tag}_p5", q(gv, .05), "rupees")
        R.fact(f"q9_{tag}_worst", float(gv.min()), "rupees")
        pct_fact(f"q9_{tag}_ahead", float((gv > w["final"]).mean()))
    R.fact("q9_stay_p50", med(w["final"]), "rupees")
    R.fact("q9_stay_p5", q(w["final"], .05), "rupees")
    R.fact("q9_stay_worst", float(w["final"].min()), "rupees")
    g = res["g36"]
    R.fact("q9_P9_holds", bool(med(g) < med(w["final"]) and q(g, .05) > q(w["final"], .05) and (g > w["final"]).mean() < 0.4), "text")
    R.chart("q9_glide", [{"start": str(s), "stay": float(a), "glide36": float(b)} for s, a, b in zip(w["start"], w["final"], g)])
    e, l = era_mask(w["start"])
    for era, m in (("1995_2004", e), ("2005_on", l)):
        if m.any():
            pct_fact(f"q9_g36_ahead_{era}", float((g[m] > w["final"][m]).mean()))
    R.check("era_split", True, "glide outcome by era recorded", "q9")
    R.check("robustness", True, "12-month switch and FD at the bottom of the range recorded", "q9")


def q10():
    goal = 1e7
    rows = []
    for asset, tag in (("Nifty 500", "n500"), ("60/20/20", "m602020")):
        for y in (10, 15, 20):
            h = 12 * y
            if asset == "Nifty 500":
                w = windows("Nifty 500", y)
                per1 = w["final"] / AMT
                p = w["p"]
                step = np.array([(1.1 ** (np.arange(h) // 12) / p.buy_nav[i:i + h]).sum() * p.end_nav[i + h - 1] for i in w["k"]])
                ends = w["end_date"]
            else:
                if len(GRID["months"]) < h:
                    continue
                m = MIXW.get(("60/20/20", y)) or mix_windows("60/20/20", y)
                per1 = m["final"] / AMT
                step = None
                ends = [GRID["end_date"][k + h - 1] for k in m["k"]]
            for conf in (0.5, 0.8, 0.95):
                need = goal / q(per1, 1 - conf)
                R.fact(f"q10_{tag}_{y}y_need_{int(conf * 100)}", need, "rupees", "monthly amount for ₹1 crore")
                row = {"asset": asset, "horizon": y, "confidence": conf, "flat": need, "starts": len(per1)}
                if step is not None:
                    row["stepup_first_year"] = goal / q(step, 1 - conf)
                    R.fact(f"q10_{tag}_{y}y_need_{int(conf * 100)}_stepup", row["stepup_first_year"], "rupees")
                today = per1 * float(I.cpi.iloc[-1]) / SD.deflator(I.cpi, ends)
                row["real"] = goal / q(today, 1 - conf)
                R.fact(f"q10_{tag}_{y}y_need_{int(conf * 100)}_real", row["real"], "rupees", "₹1 crore in today's rupees")
                rows.append(row)
            if asset == "Nifty 500":
                r = (1.12) ** (1 / 12) - 1
                calc_amt = goal / (((1 + r) ** h - 1) / r * (1 + r))
                R.fact(f"q10_calc12_{y}y_amount", calc_amt, "rupees", "what a 12% calculator asks for")
                pct_fact(f"q10_calc12_{y}y_reached", float((calc_amt * per1 >= goal).mean()))
                if y == 15:
                    e, l = era_mask(w["start"])
                    R.fact("q10_n500_15y_need_80_1995_2004", goal / q(per1[e], .2), "rupees")
                    R.fact("q10_n500_15y_need_80_2005_on", goal / q(per1[l], .2), "rupees")
    R.chart("q10_need", rows)
    # starting five years late
    w20, w15 = windows("Nifty 500", 20), windows("Nifty 500", 15)
    target = q(w20["final"], 0.2)
    late = target / q(w15["final"] / AMT, 0.2)
    R.fact("q10_late_target_80", target, "rupees", "the 20-year SIP's 80% outcome at ₹10,000 a month")
    R.fact("q10_late_need_15y", late, "rupees", "monthly amount a 15-year SIP needs to match it 80% of the time")
    n15 = [r for r in rows if r["asset"] == "Nifty 500" and r["horizon"] == 15]
    need50 = [r["flat"] for r in n15 if r["confidence"] == 0.5][0]
    need95 = [r["flat"] for r in n15 if r["confidence"] == 0.95][0]
    reached = R.facts["q10_calc12_15y_reached"]["value"]
    R.fact("q10_P10_holds", bool(need95 >= 1.5 * need50 and reached < 0.6), "text")
    R.check("era_split", True, "15-year 80% amounts by era recorded", "q10")
    R.check("robustness", True, "real ₹1 crore and 60/20/20 recorded", "q10")


# ================================================================= Chapter 4

def stp(p: Panel, k: int, months: int, fd: SD.FD, h: int = 120) -> float:
    """₹12 lakh into the FD at the start, moved to equity in equal parts of the remaining balance over `months`."""
    acct = E.FDAccount(fd, pd.Timestamp(p.buy_date[k]))
    acct.deposit(p.buy_date[k], AMT * 120)
    units = 0.0
    for j in range(months):
        d = pd.Timestamp(p.buy_date[k + j])
        acct.roll(d)
        amt = acct.withdraw(d, acct.bal / (months - j))
        units += amt / p.buy_nav[k + j]
    end = pd.Timestamp(p.end_date[k + h - 1])
    return units * p.end_nav[k + h - 1] + acct.close(end)


def fd_then_april(p: Panel, k: int, h: int, fd: SD.FD) -> float:
    acct = E.FDAccount(fd, pd.Timestamp(p.buy_date[k]))
    units = 0.0
    for j in range(h):
        t = k + j
        d = pd.Timestamp(p.buy_date[t])
        acct.deposit(d, AMT)
        if p.months[t].month == 4 and j > 0:
            units += acct.withdraw(d, acct.bal) / p.buy_nav[t]     # the whole balance, this April's instalment included
    end = pd.Timestamp(p.end_date[k + h - 1])
    return units * p.end_nav[k + h - 1] + acct.close(end)


def q11():
    w = windows("Nifty 500", 10)
    p, h = w["p"], w["h"]
    lump = np.array([AMT * 120 * p.end_nav[i + h - 1] / p.buy_nav[i] for i in w["k"]])
    s12 = np.array([stp(p, int(i), 12, FDT) for i in w["k"]])
    s36 = np.array([stp(p, int(i), 36, FDT) for i in w["k"]])
    for tag, s in (("stp12", s12), ("stp36", s36)):
        pct_fact(f"q11_lump_beat_{tag}", float((lump > s).mean()))
        R.fact(f"q11_lump_minus_{tag}_p50", med(lump - s), "rupees")
    fda = np.array([fd_then_april(p, int(i), h, FDT) for i in w["k"]])
    pct_fact("q11_sip_beat_fd_april", float((w["final"] > fda).mean()))
    R.fact("q11_sip_minus_fd_april_p50", med(w["final"] - fda), "rupees")
    e, l = era_mask(w["start"])
    for era, m in (("1995_2004", e), ("2005_on", l)):
        pct_fact(f"q11_lump_beat_stp12_{era}", float((lump[m] > s12[m]).mean()))
        pct_fact(f"q11_sip_beat_fd_april_{era}", float((w["final"][m] > fda[m]).mean()))
    R.chart("q11_compare", [{"start": str(s), "lump": float(a), "stp12": float(b), "stp36": float(c), "sip": float(d), "fd_april": float(f)}
                            for s, a, b, c, d, f in zip(w["start"], lump, s12, s36, w["final"], fda)])
    # explainer: one window's SIP XIRR against the index's CAGR over the same dates
    i = int(np.where(p.months == pd.Period("2014-04", "M"))[0][0])
    x = float(p.xirr(np.array([i]), 120)[0])
    t0, t1 = pd.Timestamp(p.buy_date[i]), pd.Timestamp(p.end_date[i + 119])
    cagr = (p.end_nav[i + 119] / p.buy_nav[i]) ** (365.0 / (t1 - t0).days) - 1
    R.fact("q11_example_sip_xirr", x, "fraction", "Nifty 500 SIP April 2014 to March 2024")
    R.fact("q11_example_index_cagr", cagr, "fraction", "the same index, same dates, lump sum")
    R.check("era_split", True, "lump sum and FD-then-April by era recorded", "q11")


def q12():
    p = I.panels["Nifty 500"]
    nav = I.navs["Nifty 500"]
    h = 120
    k = p.starts(h)
    k = k[p.months[k] >= SD.MENU_START]
    base = p.xirr(k, h)
    effects = {}

    # SIP date: day d of each month, at the first session on or after it
    by_day = []
    for d in range(1, 29):
        xs = []
        for i in k:
            months = p.months[i:i + h]
            dates = pd.DatetimeIndex([m.to_timestamp() + pd.Timedelta(days=d - 1) for m in months])
            pos = np.minimum(nav.index.searchsorted(dates), len(nav) - 1)
            bd = nav.index[pos]
            v = (AMT / nav.to_numpy()[pos]).sum() * p.end_nav[i + h - 1]
            xs.append((bd, v))
        x = E.xirr_flows([b for b, _ in xs], [[AMT] * h] * len(xs), [p.end_date[i + h - 1] for i in k], [v for _, v in xs])
        by_day.append({"day": d, "effect_p50": med(x - base)})
        effects[f"day{d}"] = x - base
    best = max(by_day[1:], key=lambda r: r["effect_p50"])
    effects["best_date"] = effects[f"day{best['day']}"]
    R.fact("q12_best_day", best["day"], "plain")
    R.chart("q12_by_day", by_day)

    # weekly: ₹10,000 x 12 / 52 on the first session of each week
    wk = []
    for i in k:
        t0, t1 = pd.Timestamp(p.buy_date[i]), pd.Timestamp(p.end_date[i + h - 1])
        sess = nav.loc[t0:t1].index
        firsts = pd.Series(sess, index=sess).groupby(sess.to_period("W")).min().to_numpy()
        firsts = pd.DatetimeIndex(firsts)
        amt = np.full(len(firsts), AMT * 12 / 52)
        v = (amt / nav.loc[firsts].to_numpy()).sum() * p.end_nav[i + h - 1]
        wk.append((firsts, amt, v))
    x = E.xirr_flows([a for a, _, _ in wk], [b for _, b, _ in wk], [p.end_date[i + h - 1] for i in k], [c for _, _, c in wk])
    effects["weekly"] = x - base

    # 10% yearly step-up: return and rupees of extra corpus per rupee of extra savings
    st_amt = AMT * 1.1 ** (np.arange(h) // 12)
    stx = p.xirr(k, h, amounts=st_amt / AMT)
    effects["stepup"] = stx - base
    st_val = np.array([(st_amt / p.buy_nav[i:i + h]).sum() * p.end_nav[i + h - 1] for i in k])
    flat_val = AMT * p.value(k, h - 1)
    R.fact("q12_stepup_extra_per_rupee_p50", med((st_val - flat_val) / (st_amt.sum() - AMT * h)), "ratio",
           "extra final value per extra rupee saved")

    # 1% a year more in costs
    p_cost = Panel.from_nav(nav_after_costs(I.levels["Nifty 500"].dropna(), 0.012))
    pk = p_cost.months.get_indexer(p.months[k])
    effects["cost_1pct"] = p_cost.xirr(pk, h) - base

    # strategies that hold cash in the FD: wait for a 20% fall; pause during a 20% fall; double when P/E is cheap
    lv = I.levels["Nifty 500"]
    peak = lv.cummax()
    dd = lv / peak - 1
    dd_me = dd.groupby(dd.index.to_period("M")).last()
    dd_me.index = dd.groupby(dd.index.to_period("M")).apply(lambda s: s.index[-1]).to_numpy()
    pe = I.pe["NIFTY_50"].dropna()

    def cheap_flags(cut: pd.Timestamp | None) -> pd.Series:
        s = pe if cut is None else pe.loc[:cut]
        out = {}
        for i in range(len(p)):
            d = pd.Timestamp(p.buy_date[i])
            hist = s.loc[:d - pd.Timedelta(days=1)]
            if len(hist) < 750 or (cut is not None and d > cut):
                continue
            out[d] = bool(hist.iloc[-1] <= np.quantile(hist.to_numpy(), 0.2))
        return pd.Series(out)

    flags = cheap_flags(None)
    cut = pd.Timestamp("2015-12-31")
    short = cheap_flags(cut)
    same = (flags.reindex(short.index) == short).all()
    R.check("truncation_stable", bool(same), f"P/E 'cheap' flags for {len(short)} months to {cut.date()} identical when later data is removed", "q12")

    def run_strategy(i: int, kind: str) -> tuple[list, list, float]:
        acct = E.FDAccount(FDT, pd.Timestamp(p.buy_date[i]))
        units, dates, amts = 0.0, [], []
        armed = True      # wait-for-fall: a new 20% fall needs a new high first
        paused = False
        for j in range(h):
            t = i + j
            d = pd.Timestamp(p.buy_date[t])
            amt = AMT
            if kind == "pe_double":
                amt = 2 * AMT if flags.get(d, False) else AMT
                units += amt / p.buy_nav[t]
            elif kind == "wait_fall":
                acct.deposit(d, amt)
                since = pd.Timestamp(p.buy_date[t - 1]) + pd.Timedelta(days=1) if j else d
                window = dd.loc[since:d]
                if not armed and (window >= -1e-9).any():
                    armed = True          # a new high re-arms the rule
                if armed and (window <= -0.20).any():
                    units += acct.withdraw(d, acct.bal) / p.buy_nav[t]
                    armed = False
            elif kind == "pause_lab":
                # the October lab's rule: pause from a month-end more than 20% below the peak until a month-end
                # back above -10%; paused money stays in the FD (its "keep cash" variant)
                if j:
                    me = float(dd_me.asof(pd.Timestamp(p.end_date[t - 1])))
                    if not paused and me < -0.20:
                        paused = True
                    elif paused and me > -0.10:
                        paused = False
                if paused:
                    acct.deposit(d, amt)
                else:
                    units += amt / p.buy_nav[t]
            elif kind == "pause_fall":
                level_dd = float(dd.asof(d))
                if not paused and level_dd <= -0.20:
                    paused = True
                if paused and level_dd >= -1e-9:
                    paused = False
                if paused:
                    acct.deposit(d, amt)
                else:
                    units += amt / p.buy_nav[t]
            dates.append(d)
            amts.append(amt)
        end = pd.Timestamp(p.end_date[i + h - 1])
        return dates, amts, units * p.end_nav[i + h - 1] + acct.close(end)

    for kind in ("wait_fall", "pause_fall", "pause_lab", "pe_double"):
        out = [run_strategy(int(i), kind) for i in k]
        x = E.xirr_flows([o[0] for o in out], [o[1] for o in out], [p.end_date[i + h - 1] for i in k], [o[2] for o in out])
        effects[kind] = x - base

    rows = []
    for name, eff in effects.items():
        if name.startswith("day"):
            continue
        R.fact(f"q12_{name}_p50", med(eff), "fraction", "median paired effect on 10-year XIRR, Nifty 500, starts from April 2005")
        R.fact(f"q12_{name}_p10", q(eff, .1), "fraction")
        R.fact(f"q12_{name}_p90", q(eff, .9), "fraction")
        rows.append({"lever": name, "p50": med(eff), "p10": q(eff, .1), "p90": q(eff, .9)})
    # the gaps the levers are compared with
    q4rows = R.charts["q4_assets"]
    ten = [r for r in q4rows if r["horizon"] == 10]
    R.fact("q12_asset_gap", max(r["median"] for r in ten) - min(r["median"] for r in ten), "fraction",
           "spread of 10-year median XIRR across the menu's single assets")
    R.fact("q12_start_year_gap", R.facts["q8_n500_10y_year_spread"]["value"], "fraction")
    rows += [{"lever": "asset_gap", "p50": R.facts["q12_asset_gap"]["value"]},
             {"lever": "start_year_gap", "p50": R.facts["q12_start_year_gap"]["value"]}]
    R.fact("q12_starts", len(k), "count")
    R.chart("q12_levers", rows)
    # robustness: Nifty 50 for date, weekly-free levers (date and cost), and 15 years for the date effect
    p50 = I.panels["Nifty 50"]
    k50 = p50.starts(h)
    k50 = k50[p50.months[k50] >= SD.MENU_START]
    pc50 = Panel.from_nav(nav_after_costs(I.levels["Nifty 50"].dropna(), 0.012))
    R.fact("q12_n50_cost_1pct_p50", med(pc50.xirr(pc50.months.get_indexer(p50.months[k50]), h) - p50.xirr(k50, h)), "fraction")
    R.check("robustness", True, "Nifty 50 cost effect recorded; 15-year date effect not computed (see notes)", "q12")


def q13():
    p = I.panels["Nifty 500"]
    rows = []
    for age in (12, 18, 24, 36, 60):
        k = p.starts(age)
        res = [after_tax_final(p, int(i), age, load=0.01) for i in k]
        res0 = [after_tax_final(p, int(i), age, load=0.0) for i in k]
        big = [after_tax_final(p, int(i), age, load=0.0, amt=50_000) for i in k]
        st_units = np.array([r["st_units_share"] for r in res])
        pos = np.array([r["gain"] > 0 for r in res])
        st_gain_share = np.array([r["st_gain"] / r["gain"] if r["gain"] > 0 else np.nan for r in res])
        cost = np.array([(r["tax"] + r["load"]) / r["value"] for r in res])
        cost0 = np.array([r["tax"] / r["value"] for r in res0])
        cost_big = np.array([r["tax"] / r["value"] for r in big])
        # a lump sum of the same money at the start, held as long
        lump = []
        for i in k:
            v = AMT * age * p.end_nav[i + age - 1] / p.buy_nav[i]
            held = (p.end_date[i + age - 1] - p.buy_date[i]) / np.timedelta64(1, "D")
            g = v - AMT * age
            t = (E.ST_RATE * max(g, 0) if held < 365 else E.LT_RATE * max(g - E.LT_EXEMPT, 0))
            lump.append(t / v)
        R.fact(f"q13_{age}m_st_units", med(st_units), "fraction")
        R.fact(f"q13_{age}m_st_gain_share_p50", med(st_gain_share), "fraction", "among SIPs with a gain")
        R.fact(f"q13_{age}m_cost_p50", med(cost), "fraction", "tax plus 1% exit load, share of value")
        R.fact(f"q13_{age}m_cost_noload_p50", med(cost0), "fraction")
        R.fact(f"q13_{age}m_cost_50k_p50", med(cost_big), "fraction", "₹50,000 a month, no load")
        R.fact(f"q13_{age}m_lump_cost_p50", med(np.array(lump)), "fraction")
        pct_fact(f"q13_{age}m_share_with_gain", float(pos.mean()))
        rows.append({"age": age, "st_units": med(st_units), "st_gain_share": med(st_gain_share), "cost": med(cost),
                     "cost_noload": med(cost0), "lump_cost": med(np.array(lump))})
    R.chart("q13_tax_clock", rows)
    a = {r["age"]: r for r in rows}
    R.fact("q13_P13_holds", bool(a[24]["st_gain_share"] < a[24]["st_units"] and a[36]["st_gain_share"] < a[36]["st_units"]), "text")
    R.check("robustness", True, "no exit load and ₹50,000 a month recorded", "q13")


def sip_edge(asset: str, start_from=None) -> dict:
    w = windows(asset, 10, start_from)
    p, h = w["p"], w["h"]
    nav = I.navs[asset]
    edge, vol, tot = [], [], []
    for i, x in zip(w["k"], w["xirr"]):
        t0, t1 = pd.Timestamp(p.buy_date[i]), pd.Timestamp(p.end_date[i + h - 1])
        seg = nav.loc[t0:t1]
        yrs = (t1 - t0).days / 365.0
        total = seg.iloc[-1] / seg.iloc[0]
        edge.append(x - (total ** (1 / yrs) - 1))
        vol.append(float(np.log(seg).diff().std() * np.sqrt(250)))
        tot.append(total - 1)
    return {"edge": np.array(edge), "vol": np.array(vol), "total": np.array(tot), "start": w["start"]}


def q14():
    s = sip_edge("Nifty 500")
    cv = float(spearmanr(s["edge"], s["vol"]).statistic)
    ct = float(spearmanr(s["edge"], s["total"]).statistic)
    R.fact("q14_n500_corr_vol", cv, "ratio")
    R.fact("q14_n500_corr_total", ct, "ratio")
    R.fact("q14_n500_edge_p50", med(s["edge"]), "fraction", "SIP XIRR minus the index's own return, same dates")
    R.fact("q14_n500_edge_p5", q(s["edge"], .05), "fraction")
    R.fact("q14_n500_edge_p95", q(s["edge"], .95), "fraction")
    pct_fact("q14_n500_edge_positive", float((s["edge"] > 0).mean()))
    R.fact("q14_P14_holds", bool(abs(ct) > abs(cv)), "text")
    R.chart("q14_edge", [{"start": str(a), "edge": float(b), "vol": float(c), "total": float(d)} for a, b, c, d in zip(s["start"], s["edge"], s["vol"], s["total"])])
    e, l = era_mask(s["start"])
    for era, m in (("1995_2004", e), ("2005_on", l)):
        R.fact(f"q14_n500_corr_vol_{era}", float(spearmanr(s["edge"][m], s["vol"][m]).statistic), "ratio")
        R.fact(f"q14_n500_corr_total_{era}", float(spearmanr(s["edge"][m], s["total"][m]).statistic), "ratio")
    for a, key in (("Nifty Smallcap 250", "small250"), ("Gold", "gold")):
        s2 = sip_edge(a, SD.MENU_START)
        R.fact(f"q14_{key}_corr_vol", float(spearmanr(s2["edge"], s2["vol"]).statistic), "ratio")
        R.fact(f"q14_{key}_corr_total", float(spearmanr(s2["edge"], s2["total"]).statistic), "ratio")
    # illustration: two made-up paths from 100 to 200 over 10 years, one smooth and one choppy
    days = pd.bdate_range("2000-01-03", "2009-12-31")
    tt = np.arange(len(days)) / (len(days) - 1)
    smooth = pd.Series(100 * 2 ** tt, index=days)
    choppy = pd.Series(100 * 2 ** tt * (1 + 0.3 * np.sin(2 * np.pi * 2.5 * tt)), index=days)
    for name, path in (("smooth", smooth), ("choppy", choppy)):
        pp = Panel.from_nav(path, drop_partial_last=False)
        R.fact(f"q14_illus_{name}_xirr", float(pp.xirr(np.array([0]), 120)[0]), "fraction", "illustration, made-up path")
        R.chart(f"q14_illus_{name}", [{"month": str(m), "level": float(v)} for m, v in zip(pp.months, pp.end_nav)])
    R.fact("q14_illus_index_cagr", 2 ** 0.1 - 1, "fraction", "both made-up paths: 100 to 200 in 10 years")
    R.check("era_split", True, "correlations by era recorded", "q14")
    R.check("robustness", True, "Smallcap 250 and gold recorded", "q14")


# ================================================================= Chapter 5

def todate_paths(asset: str, start_from=None):
    p = I.panels[asset]
    n = len(p)
    ks = np.arange(0, n - 12)
    if start_from is not None:
        ks = ks[p.months[ks] >= start_from]
    out = []
    for i in ks:
        h = n - i
        vals = AMT * p.value(np.full(h, i), np.arange(h))
        inv = AMT * np.arange(1, h + 1)
        out.append((i, *E.red_stats(vals, inv), vals[11] / inv[11] - 1, vals[23] / inv[23] - 1 if h > 23 else np.nan,
                    vals[35] / inv[35] - 1 if h > 35 else np.nan))
    return p, out


def q15():
    p, out = todate_paths("Nifty 500")
    start = p.months[[o[0] for o in out]]
    deep = np.array([o[1] for o in out])
    longest = np.array([o[2] for o in out])
    ever = np.array([o[3] for o in out])
    pct_fact("q15_n500_ever_red", float(ever.mean()), "SIPs from 1995 to the data end, at any month-end")
    R.fact("q15_n500_deepest", float(deep.min()), "fraction")
    R.label("q15_n500_deepest_start", start[int(deep.argmin())].strftime("%B %Y"))
    R.fact("q15_n500_longest", int(longest.max()), "months")
    R.label("q15_n500_longest_start", start[int(longest.argmax())].strftime("%B %Y"))
    for j, key in ((4, "12m"), (5, "24m"), (6, "36m")):
        x = np.array([o[j] for o in out], float)
        R.fact(f"q15_n500_worst_{key}", float(np.nanmin(x)), "fraction", "worst value against money put in at this age")
    ev05 = ever[np.asarray(start >= SD.MENU_START)]
    pct_fact("q15_n500_ever_red_from_2005", float(ev05.mean()))
    e, l = era_mask(start)
    R.fact("q15_n500_longest_1995_2004", int(longest[e].max()), "months")
    R.fact("q15_n500_longest_2005_on", int(longest[l].max()), "months")
    R.chart("q15_by_start", [{"start": str(s), "deepest": float(d), "longest": int(lg)} for s, d, lg in zip(start, deep, longest)])
    menu = []
    for a in SD.MENU_ASSETS:
        pa, oa = todate_paths(a, SD.MENU_START)
        menu.append({"asset": a, "ever_red": float(np.mean([o[3] for o in oa])), "deepest": float(min(o[1] for o in oa)),
                     "longest": int(max(o[2] for o in oa))})
    R.chart("q15_menu", menu)
    R.check("era_split", True, "longest stretch by era recorded", "q15")


def red_split(asset: str, age: int, er_panel: Panel | None = None, years: int = 10):
    p = er_panel or I.panels[asset]
    h = 12 * years
    k = p.starts(h)
    rel = p.value(k, age - 1) / age - 1
    red = rel < 0
    x = p.xirr(k, h)
    return p, k, h, rel, red, x


def q16():
    rows, keys = [], {"Nifty 500": "n500", "Nifty 50": "n50", "Nifty Midcap 150": "mid150", "Nifty Smallcap 250": "small250"}
    p_a_holds = True
    for asset, key in keys.items():
        p, k, h, rel, red, x = red_split(asset, 12)
        fdv = fd_finals(p, k, h)
        final = AMT * p.value(k, h - 1)
        for grp, m in (("red", red), ("rest", ~red)):
            R.fact(f"q16_{key}_{grp}_p50", med(x[m]), "fraction")
            R.fact(f"q16_{key}_{grp}_p5", q(x[m], .05), "fraction")
            R.fact(f"q16_{key}_{grp}_p25", q(x[m], .25), "fraction")
            R.fact(f"q16_{key}_{grp}_p75", q(x[m], .75), "fraction")
            R.fact(f"q16_{key}_{grp}_worst", float(np.nanmin(x[m])) if m.any() else float("nan"), "fraction")
            pct_fact(f"q16_{key}_{grp}_below_fd", float((final[m] < fdv[m]).mean()) if m.any() else float("nan"))
            rows.append({"asset": asset, "group": grp, "p5": q(x[m], .05), "p25": q(x[m], .25), "p50": med(x[m]),
                         "p75": q(x[m], .75), "p95": q(x[m], .95), "n": int(m.sum()), "episodes": episodes(m)})
        pct_fact(f"q16_{key}_red12", float(red.mean()))
        allk = np.arange(0, len(p) - 11)
        pct_fact(f"q16_{key}_red12_all_starts", float((p.value(allk, 11) / 12 < 1).mean()), "every start month to the data end (the October denominator)")
        R.fact(f"q16_{key}_red12_episodes", episodes(red), "count")
        R.fact(f"q16_{key}_starts", len(k), "count")
        if med(x[red]) <= med(x[~red]):
            p_a_holds = False
        if asset == "Nifty 500":
            # depth bands
            bands = {"0-10% below": (rel < 0) & (rel >= -0.10), "10-20% below": (rel < -0.10) & (rel >= -0.20),
                     "over 20% below": rel < -0.20, "not red": rel >= 0}
            bmed = {}
            for name, m in bands.items():
                bk = {"0-10% below": "b0_10", "10-20% below": "b10_20", "over 20% below": "b20", "not red": "notred"}[name]
                bmed[bk] = med(x[m])
                R.fact(f"q16_n500_{bk}_p50", bmed[bk], "fraction")
                R.fact(f"q16_n500_{bk}_n", int(m.sum()), "count")
                rows.append({"asset": asset, "group": name, "p5": q(x[m], .05), "p25": q(x[m], .25), "p50": med(x[m]),
                             "p75": q(x[m], .75), "p95": q(x[m], .95), "n": int(m.sum()), "episodes": episodes(m)})
            p_b = bmed["b0_10"] < bmed["b10_20"] < bmed["b20"]
            # mechanism: units bought while red
            u_share, m_share = [], []
            for i in k[red]:
                vals = p.value(np.full(h, i), np.arange(h))
                inv = np.arange(1, h + 1)
                red_before = np.concatenate([[False], (vals / inv < 1)[:-1]])
                units_each = 1 / p.buy_nav[i:i + h]
                u_share.append(units_each[red_before].sum() / units_each.sum())
                m_share.append(red_before.mean())
            u_share, m_share = np.array(u_share), np.array(m_share)
            R.fact("q16_n500_units_while_red_p50", med(u_share), "fraction")
            R.fact("q16_n500_money_while_red_p50", med(m_share), "fraction")
            R.fact("q16_n500_units_to_money_ratio_p50", med(u_share / m_share), "ratio")
            p_c = med(u_share / m_share) >= 1.5
            R.chart("q16_mechanism", [{"start": str(s), "units_share": float(a), "money_share": float(b)} for s, a, b in zip(p.months[k[red]], u_share, m_share)])
            # indicative block bootstrap of the red-minus-rest median gap
            rng = np.random.default_rng(7)
            n, blk = len(k), 120
            gaps = []
            for _ in range(2000):
                idx = (rng.integers(0, n - blk + 1, int(np.ceil(n / blk)))[:, None] + np.arange(blk)).ravel()[:n]
                rr, xx = red[idx], x[idx]
                if rr.any() and (~rr).any():
                    gaps.append(np.median(xx[rr]) - np.median(xx[~rr]))
            R.fact("q16_n500_gap_p50", med(x[red]) - med(x[~red]), "fraction")
            R.fact("q16_n500_gap_lo", q(gaps, .05), "fraction", "indicative 90% block-bootstrap interval")
            R.fact("q16_n500_gap_hi", q(gaps, .95), "fraction")
            # era split and robustness
            starts = p.months[k]
            e, l = era_mask(starts)
            for era, m in (("1995_2004", e), ("2005_on", l)):
                R.fact(f"q16_n500_red_p50_{era}", med(x[red & m]), "fraction")
                R.fact(f"q16_n500_rest_p50_{era}", med(x[~red & m]), "fraction")
            _, _, _, rel24, red24, x24 = red_split(asset, 24)
            R.fact("q16_n500_red24_p50", med(x24[red24]), "fraction")
            R.fact("q16_n500_rest24_p50", med(x24[~red24]), "fraction")
            pct_fact("q16_n500_red24", float(red24.mean()))
            pc = Panel.from_nav(nav_after_costs(I.levels["Nifty 500"].dropna(), 0.01))
            _, _, _, _, redc, xc = red_split(asset, 12, pc)
            R.fact("q16_n500_red_p50_er1", med(xc[redc]), "fraction")
            R.fact("q16_n500_rest_p50_er1", med(xc[~redc]), "fraction")
            _, _, _, _, red15, x15 = red_split(asset, 12, years=15)
            R.fact("q16_n500_red_p50_15y", med(x15[red15]), "fraction")
            R.fact("q16_n500_rest_p50_15y", med(x15[~red15]), "fraction")
    R.fact("q16_P16_holds", bool(p_a_holds and p_b and p_c), "text")
    R.fact("q16_P16a_holds", bool(p_a_holds), "text")
    R.fact("q16_P16b_holds", bool(p_b), "text")
    R.fact("q16_P16c_holds", bool(p_c), "text")
    R.chart("q16_outcomes", rows)
    # the case: Nifty 500 SIP started January 2008, month by month to the data end
    p = I.panels["Nifty 500"]
    i = int(np.where(p.months == pd.Period("2008-01", "M"))[0][0])
    hh = len(p) - i
    vals = AMT * p.value(np.full(hh, i), np.arange(hh))
    inv = AMT * np.arange(1, hh + 1)
    deep, longest, _ = E.red_stats(vals, inv)
    R.fact("q16_case2008_deepest", deep, "fraction")
    R.fact("q16_case2008_months_red", int((vals < inv).sum()), "months")
    R.fact("q16_case2008_longest_red", longest, "months")
    R.fact("q16_case2008_xirr_10y", float(p.xirr(np.array([i]), 120)[0]), "fraction")
    R.fact("q16_case2008_value_now", float(vals[-1]), "rupees")
    R.fact("q16_case2008_invested_now", float(inv[-1]), "rupees")
    R.chart("q16_case2008", [{"month": str(m), "invested": float(a), "value": float(b)} for m, a, b in zip(p.months[i:], inv, vals)])
    R.check("era_split", True, "red and rest medians by era recorded", "q16")
    R.check("robustness", True, "24 months, 1% expense ratio and 15-year ending recorded", "q16")


def stop_paths(p: Panel, i: int, m: int, h: int, fd: SD.FD) -> dict:
    """The four paths of Q17 for a SIP started in month i and in the red at age m."""
    units_m = p.units(i, m - 1)
    out = {}
    # A: keep going
    out["A"] = AMT * p.value(i, h - 1)
    end = pd.Timestamp(p.end_date[i + h - 1])
    # B: stop and hold
    acct = E.FDAccount(fd, pd.Timestamp(p.buy_date[i + m]))
    for j in range(m, h):
        acct.deposit(p.buy_date[i + j], AMT)
    out["B"] = AMT * units_m * p.end_nav[i + h - 1] + acct.close(end)
    # C: sell at the end of month m, everything into the FD
    acct = E.FDAccount(fd, pd.Timestamp(p.end_date[i + m - 1]))
    acct.deposit(p.end_date[i + m - 1], AMT * units_m * p.end_nav[i + m - 1])
    for j in range(m, h):
        acct.deposit(p.buy_date[i + j], AMT)
    out["C"] = acct.close(end)
    # D: pause into the FD until the held units are worth the money put in, then resume
    acct = E.FDAccount(fd, pd.Timestamp(p.buy_date[i + m]))
    units = units_m
    invested = AMT * m
    paused = True
    for j in range(m, h):
        t = i + j
        if paused:
            # check at the previous month-end
            if AMT * units * p.end_nav[t - 1] >= invested:
                paused = False
        if paused:
            acct.deposit(p.buy_date[t], AMT)
        else:
            units += 1 / p.buy_nav[t]
            invested += AMT
    out["D"] = AMT * units * p.end_nav[i + h - 1] + acct.close(end)
    return out


def q17():
    rows, P17 = [], {}
    for asset, key in (("Nifty 500", "n500"), ("Nifty 50", "n50"), ("Nifty Midcap 150", "mid150"), ("Nifty Smallcap 250", "small250")):
        for m in (12, 24):
            if key != "n500" and m == 24:
                continue
            p, k, h, rel, red, x = red_split(asset, m)
            ks, rels = k[red], rel[red]
            variants = [("", FDT)]
            if key == "n500" and m == 12:
                variants += [("_untaxed", SD.FD(I.deposit_rate, taxed=False)), ("_fdlow", SD.FD(I.deposit_rate_low))]
            for suffix, fd in variants:
                res = [stop_paths(p, int(i), m, h, fd) for i in ks]
                A = np.array([r["A"] for r in res])
                tag = f"q17_{key}_m{m}{suffix}"
                for s in "BCD":
                    X = np.array([r[s] for r in res])
                    gap = A - X
                    pct_fact(f"{tag}_A_beat_{s}", float((gap > 0).mean()))
                    R.fact(f"{tag}_gap_{s}_p50", med(gap), "rupees", f"keep going minus path {s}")
                    R.fact(f"{tag}_gap_{s}_worst", float(gap.min()), "rupees")
                    R.fact(f"{tag}_gap_{s}_best", float(gap.max()), "rupees")
                    if suffix == "":
                        rows += [{"asset": asset, "age": m, "path": s, "start": str(st), "gap": float(g), "depth": float(d)}
                                 for st, g, d in zip(p.months[ks], gap, rels)]
                    if key == "n500" and m == 12 and suffix == "":
                        P17[s] = float((gap > 0).mean())
                        if s == "C":
                            shallow, deep = rels >= -0.10, rels < -0.20
                            R.fact(f"{tag}_gap_C_p50_shallow", med(gap[shallow]), "rupees", "less than 10% in the red")
                            R.fact(f"{tag}_gap_C_p50_deep", med(gap[deep]), "rupees", "more than 20% in the red")
                            P17["depth"] = med(gap[deep]) > med(gap[shallow])
                            starts = p.months[ks]
                            e, l = era_mask(starts)
                            for era, mm in (("1995_2004", e), ("2005_on", l)):
                                for s2 in "BCD":
                                    X2 = np.array([r[s2] for r in res])
                                    pct_fact(f"{tag}_A_beat_{s2}_{era}", float((A[mm] > X2[mm]).mean()))
                R.fact(f"{tag}_n", len(ks), "count")
    R.fact("q17_P17_holds", bool(P17["B"] > 0.8 and P17["C"] > 0.8 and P17["D"] > 0.65 and P17["depth"]), "text")
    R.chart("q17_gaps", rows)
    R.check("era_split", True, "A-beat shares by era recorded", "q17")
    R.check("robustness", True, "untaxed FD, FD at the bottom of range, 24 months and the other three indices recorded", "q17")


def q18():
    out_rows = []
    first_above = {}
    for asset, key, start_from in (("Nifty 500", "n500", None), ("Nifty Midcap 150", "mid150", None), ("Nifty Smallcap 250", "small250", None)):
        for years in (10, 15):
            if key != "n500" and years == 15:
                continue
            p = I.panels[asset]
            h = 12 * years
            k = p.starts(h)
            final = p.xirr(k, h)
            corr = {}
            for age in range(3, h, 3):
                run = p.xirr(k, age)
                c = float(spearmanr(run, final, nan_policy="omit").statistic)
                corr[age] = c
                if key == "n500" and years == 10:
                    out_rows.append({"age": age, "corr": c})
            first_above[(key, years)] = next((a for a, c in sorted(corr.items()) if c > 0.5), None)
            for age in (6, 12, 24, 36, 60, 84):
                if age >= h:
                    continue
                run = p.xirr(k, age)
                R.fact(f"q18_{key}_{years}y_corr_{age}m", corr.get(age, float(spearmanr(run, final, nan_policy="omit").statistic)), "ratio")
                if key == "n500" and years == 10:
                    lo = run <= np.nanquantile(run, 1 / 3)
                    lo_final = final <= np.nanquantile(final, 1 / 3)
                    pct_fact(f"q18_n500_bottom_third_stays_{age}m", float((lo & lo_final).sum() / lo.sum()))
            fa = first_above[(key, years)]
            R.fact(f"q18_{key}_{years}y_first_age_above_half", fa if fa is not None else -1, "months")
            if key == "n500" and years == 10:
                e, l = era_mask(p.months[k])
                for era, m in (("1995_2004", e), ("2005_on", l)):
                    run = p.xirr(k, 12)
                    R.fact(f"q18_n500_10y_corr_12m_{era}", float(spearmanr(run[m], final[m], nan_policy="omit").statistic), "ratio")
    c = {r["age"]: r["corr"] for r in out_rows}
    fa = first_above[("n500", 10)]
    R.fact("q18_P18_holds", bool(c[12] < 0 and c[24] < 0 and (fa is None or fa >= 60)), "text")
    R.chart("q18_corr_by_age", out_rows)
    R.check("era_split", True, "12-month correlation by era recorded", "q18")
    R.check("robustness", True, "Midcap 150, Smallcap 250 and 15-year ending recorded", "q18")


# ================================================================= Chapter 6

def q19():
    p, k, h, rel, red, x = red_split("Nifty 50", 12)
    pe = I.pe["NIFTY_50"].dropna()
    pe12 = np.array([pe.asof(pd.Timestamp(p.end_date[i + 11])) for i in k])
    pe0 = np.array([pe.asof(pd.Timestamp(p.buy_date[i])) for i in k])
    cut = np.nanmedian(pe12)
    cheap = pe12 < cut
    R.fact("q19_pe12_median", float(cut), "ratio")
    R.fact("q19_red_cheap_p50", med(x[red & cheap]), "fraction")
    R.fact("q19_red_dear_p50", med(x[red & ~cheap]), "fraction")
    R.fact("q19_red_cheap_n", int((red & cheap).sum()), "count")
    R.fact("q19_red_dear_n", int((red & ~cheap).sum()), "count")
    R.fact("q19_red_cheap_episodes", episodes(red & cheap), "count")
    R.fact("q19_red_dear_episodes", episodes(red & ~cheap), "count")
    ok = ~np.isnan(pe12)
    R.fact("q19_corr_red", float(spearmanr(pe12[red & ok], x[red & ok]).statistic), "ratio")
    R.fact("q19_corr_all", float(spearmanr(pe12[ok], x[ok]).statistic), "ratio")
    R.fact("q19_P19_holds", bool(med(x[red & cheap]) - med(x[red & ~cheap]) >= 0.02), "text")
    cut0 = np.nanmedian(pe0)
    R.fact("q19_red_cheap_p50_startpe", med(x[red & (pe0 < cut0)]), "fraction", "P/E at the start month")
    R.fact("q19_red_dear_p50_startpe", med(x[red & (pe0 >= cut0)]), "fraction")
    R.chart("q19_scatter", [{"start": str(s), "pe12": float(a), "xirr": float(b), "red": bool(c)} for s, a, b, c in zip(p.months[k], pe12, x, red)])
    # context, not a forecast
    now = pe.iloc[-1]
    R.fact("q19_pe_now", float(now), "ratio", f"Nifty 50 trailing P/E on {pe.index[-1].date()}, consolidated earnings basis")
    R.fact("q19_pe_now_pctile", float((pe < now).mean()), "fraction", "percentile against 1999 to now (bases differ before 2021)")
    dr = I.deposit_rate.loc["1995-01-01":SD.RETRIEVED_LAST_RATE]
    R.fact("q19_fd_now", float(dr.iloc[-1]), "pct")
    R.fact("q19_fd_now_pctile", float((dr < dr.iloc[-1]).mean()), "fraction", "against every day since 1995")
    R.check("era_split", True, "not possible: about 1.7 independent windows; recorded as such", "q19")
    R.check("robustness", True, "P/E at the start month recorded", "q19")


def industry_xirr(nav: pd.Series, amounts: pd.Series, end: pd.Timestamp) -> float:
    dates = [nav.index[nav.index.searchsorted(m.to_timestamp())] for m in amounts.index]
    v = (amounts.to_numpy() / nav.loc[dates].to_numpy()).sum() * nav.asof(end)
    return float(E.xirr_flows([dates], [amounts.to_numpy()], [end], [v])[0])


def q20():
    infl = I.amfi["inflow"].dropna()
    tt = np.arange(len(infl))
    b, a = np.polyfit(tt, np.log(infl.to_numpy()), 1)
    trend = pd.Series(np.exp(a + b * tt), index=infl.index)
    R.fact("q20_trend_growth", float(np.exp(12 * b) - 1), "fraction", "yearly growth of SIP inflows, log-linear trend")
    R.label("q20_from", infl.index[0].strftime("%B %Y"))
    R.label("q20_to", infl.index[-1].strftime("%B %Y"))
    for asset, key in (("Nifty 500", "n500"), ("Nifty Midcap 150", "mid150"), ("Nifty Smallcap 250", "small250")):
        nav = I.levels[asset].dropna()
        end = nav.index[-1]
        ind = industry_xirr(nav, infl, end)
        const = industry_xirr(nav, pd.Series(infl.mean(), index=infl.index), end)
        trd = industry_xirr(nav, trend, end)
        R.fact(f"q20_{key}_industry", ind, "fraction")
        R.fact(f"q20_{key}_constant", const, "fraction")
        R.fact(f"q20_{key}_trend", trd, "fraction")
        R.fact(f"q20_{key}_industry_minus_trend", ind - trd, "fraction")
        if key == "n500":
            t0 = nav.index[nav.index.searchsorted(infl.index[0].to_timestamp())]
            R.fact("q20_n500_index", (nav.iloc[-1] / nav.loc[t0]) ** (365.0 / (end - t0).days) - 1, "fraction")
            cut = infl.index[-1] - 12
            end2 = nav.index[nav.index.searchsorted(cut.to_timestamp(how="end")) - 1]
            sub = infl.loc[:cut]
            R.fact("q20_n500_industry_ex12", industry_xirr(nav, sub, end2), "fraction")
            R.fact("q20_n500_trend_ex12", industry_xirr(nav, trend.loc[:cut], end2), "fraction")
    R.chart("q20_inflows", [{"month": str(m), "inflow": float(v), "trend": float(t)} for m, v, t in zip(infl.index, infl, trend)])
    R.check("robustness", True, "Midcap 150 and Smallcap 250 recorded", "q20")


def q21():
    lv = I.levels["Nifty 500"].dropna()
    peak = lv.cummax()
    dd = lv / peak - 1
    eps, in_ep = [], False
    for d, v in dd.items():
        if not in_ep and v <= -0.10:
            in_ep, start = True, peak.index[peak.index.get_loc(d)]
            pk_date = lv.loc[:d].idxmax()
            trough, tdate = v, d
        elif in_ep:
            if v < trough:
                trough, tdate = v, d
            if v >= 0:
                eps.append({"peak": pk_date, "trough": tdate, "recovered": d, "depth": trough})
                in_ep = False
    if in_ep:
        eps.append({"peak": pk_date, "trough": tdate, "recovered": None, "depth": trough})
    df = pd.DataFrame(eps)
    df["months_to_bottom"] = (df.trough - df.peak).dt.days / 30.44
    df["months_to_recover"] = [(r - p).days / 30.44 if r is not None else np.nan for p, r in zip(df.peak, df.recovered)]
    early = df.peak < pd.Timestamp("2016-01-01")
    for era, m in (("1995_2015", early), ("2016_on", ~early)):
        R.fact(f"q21_{era}_falls", int(m.sum()), "count")
        R.fact(f"q21_{era}_median_depth", float(df.depth[m].median()), "fraction")
        R.fact(f"q21_{era}_worst_depth", float(df.depth[m].min()), "fraction")
        R.fact(f"q21_{era}_median_recovery", float(df.months_to_recover[m].median()), "months")
    R.chart("q21_episodes", [{"peak": str(r.peak.date()), "trough": str(r.trough.date()), "depth": float(r.depth),
                              "recover_months": None if np.isnan(r.months_to_recover) else float(r.months_to_recover)} for r in df.itertuples()])
    R.chart("q21_drawdown", [{"date": str(d.date()), "dd": float(v)} for d, v in dd.resample("ME").min().items()])


def q22():
    a = I.amfi.dropna(subset=["new", "closed", "outstanding"]).copy()
    clean = (a.index >= pd.Period("2025-01", "M")) & (a.index <= pd.Period("2025-04", "M"))
    roll_closed = a["closed"].rolling(12).sum()
    life = a["outstanding"] / roll_closed
    touches = pd.Series(clean, index=a.index).rolling(12).max().astype(bool)
    life_ok = life[~touches].dropna()
    R.fact("q22_life_latest", float(life.iloc[-1]), "years", "outstanding accounts / closures in the last 12 months")
    R.fact("q22_outstanding_latest", float(a["outstanding"].iloc[-1]), "count", "SIP accounts open")
    R.fact("q22_outstanding_latest_crore", float(a["outstanding"].iloc[-1]) / 1e7, "crore", "SIP accounts open, in crore (a count, not rupees)")
    R.label("q22_latest_month", a.index[-1].strftime("%B %Y"))
    R.fact("q22_life_max_outside_cleanup", float(life_ok.max()), "years")
    R.fact("q22_life_min_outside_cleanup", float(life_ok.min()), "years")
    R.fact("q22_life_min_with_cleanup", float(life.dropna().min()), "years")
    R.fact("q22_P22_holds", bool((life_ok < 5).all()), "text")
    life_new = a["outstanding"] / a["new"].rolling(12).sum()
    R.fact("q22_life_new_flow_latest", float(life_new.iloc[-1]), "years", "using new accounts as the flow")
    stop = a["closed"] / a["new"]
    R.fact("q22_stoppage_latest", float(stop.iloc[-1]), "ratio")
    R.fact("q22_stoppage_max", float(stop.max()), "ratio")
    R.label("q22_stoppage_max_month", stop.idxmax().strftime("%B %Y"))
    per_acct = (I.amfi["inflow"] / I.amfi["outstanding"]).dropna()
    R.fact("q22_inflow_per_account_latest", float(per_acct.iloc[-1]), "rupees")
    lv = I.levels["Nifty 500"].dropna()
    me = lv.resample("ME").last()
    trail = (me / me.shift(12) - 1)
    trail.index = trail.index.to_period("M")
    j = pd.concat([a["closed"], trail.rename("trail")], axis=1).dropna()
    j = j[~((j.index >= pd.Period("2025-01", "M")) & (j.index <= pd.Period("2025-04", "M")))]
    R.fact("q22_corr_closures_trailing", float(spearmanr(j["closed"], j["trail"]).statistic), "ratio", "descriptive; clean-up months left out")
    R.chart("q22_life", [{"month": str(m), "life": None if np.isnan(v) else float(v), "cleanup_window": bool(t)} for m, v, t in zip(life.index, life, touches)])
    R.chart("q22_accounts", [{"month": str(m), "new": float(n), "closed": float(c), "stoppage": float(c / n)} for m, n, c in zip(a.index, a["new"], a["closed"])])
    R.check("robustness", True, "with the clean-up months and with new accounts as the flow recorded", "q22")


def naive():
    p = I.panels["Nifty 500"]
    i = int(np.where(p.months == pd.Period("2025-04", "M"))[0][0])
    v = p.value(i, 11) / 12 - 1
    k = p.starts(12)
    allv = p.value(k, 11) / 12 - 1
    R.fact("x0_fy26_cohort_12m", float(v), "fraction", "Nifty 500 SIP April 2025 to March 2026, value against money put in")
    R.fact("x0_fy26_cohort_pctile", float((allv < v).mean()), "fraction", "share of 12-month results since 1995 that were worse")
    R.fact("x0_fy26_cohort_xirr", float(p.xirr(np.array([i]), 12)[0]), "fraction")


def constants():
    """Plan parameters and counts the article quotes, recorded so the numeric gate can trace them."""
    for key, val, note in (("expense_equity", 0.002, "yearly cost of an equity index fund"), ("expense_gold", 0.005, ""),
                           ("expense_gsec", 0.003, ""), ("tax_fd", 0.30, "FD interest tax slab, plus 4% cess"), ("tax_cess", 0.04, ""),
                           ("tax_lt", 0.125, "long-term capital gains"), ("tax_st", 0.20, "short-term capital gains"),
                           ("exit_load", 0.01, ""), ("extra_cost", 0.01, ""), ("calculator", 0.12, ""), ("fall", 0.20, "the fall that pauses or deploys"),
                           ("band_10", 0.10, "depth band and lab resume level"), ("near_high", 0.02, ""), ("stepup", 0.10, ""),
                           ("mix_equity", 0.60, ""), ("choppy", 0.30, "illustration swing")):
        R.fact(f"const_{key}", val, "fraction", note or "plan parameter")
    R.fact("const_lt_exempt", 125_000, "rupees", "long-term gains exempt each year")
    p = I.panels["Nifty 500"]
    i = int(np.where(p.months == pd.Period("2025-04", "M"))[0][0])
    R.fact("x0_invested", 12 * AMT, "rupees")
    R.fact("x0_value", float(AMT * p.value(i, 11)), "rupees")
    years = (I.levels.index[-1] - I.levels["Nifty 500"].dropna().index[0]).days / 365.25
    R.fact("data_years", round(years, 1), "years")
    holds = {k: v["value"] for k, v in R.facts.items() if k.endswith("_holds") and not k.startswith(("q16_P16a", "q16_P16b", "q16_P16c"))}
    R.fact("predictions_total", len(holds), "count")
    R.fact("predictions_held", sum(bool(v) for v in holds.values()), "count")
    R.fact("predictions_failed", sum(not v for v in holds.values()), "count")
    R.fact("q3_n500_10y_inflation_gap", R.facts["q2_n500_10y_p50"]["value"] - R.facts["q3_n500_10y_real_p50"]["value"], "fraction")
    pe = I.pe["NIFTY_50"].dropna()
    R.fact("q16_case2008_value_now_lakh", R.facts["q16_case2008_value_now"]["value"], "rupees")
    for k, val in (("questions", 22), ("chapters", 6), ("horizon_steps_36", 36), ("months_12", 12), ("months_24", 24),
                   ("instalments_120", 120), ("lakh_12", 12), ("lakh_24", 24), ("lakh_1_2", 1.2), ("illus_from", 100), ("illus_to", 200),
                   ("thirty_years", 30), ("day_31", 31), ("data_end_day", 14), ("deposit_terms_1", 1), ("deposit_terms_3", 3),
                   ("two", 2), ("three", 3), ("four", 4), ("five", 5), ("nine", 9), ("ten", 10), ("fifteen", 15), ("nineteen", 19),
                   ("twenty", 20), ("one_in_n", 1), ("half_point", 0.5), ("corr_half", 0.5), ("months_60", 60), ("months_84", 84)):
        R.context(k, val)
    for y in (1995, 1997, 1999, 2000, 2004, 2005, 2007, 2008, 2009, 2010, 2012, 2014, 2015, 2016, 2019, 2020, 2021, 2024, 2025, 2026):
        R.context(f"y{y}", y)


# ================================================================= recompute inputs and main

def recompute_inputs(out_dir: Path) -> None:
    global I
    I = SD.load()
    for a in ("Nifty 500", "Nifty Midcap 150", "Nifty Smallcap 250"):
        lv = I.levels[a].dropna()
        pd.DataFrame({"d": lv.index, "level": lv.to_numpy()}).to_parquet(out_dir / f"tri_{a.split()[-1].lower()}.parquet", index=False)
    dr = I.deposit_rate
    pd.DataFrame({"d": dr.index, "rate_pct": dr.to_numpy()}).to_parquet(out_dir / "deposit_rate_daily.parquet", index=False)
    a = I.amfi.reset_index()
    a["month"] = a["observation_date"].astype(str)
    a.drop(columns=["observation_date"]).to_parquet(out_dir / "amfi_sip.parquet", index=False)


def main() -> None:
    global R, I, FDT, GRID
    R = Results(__file__)
    I = SD.load(R)
    I.deposit_rate_low = SD._deposit_rate(None, "dep_1_3y_low")
    FDT = SD.FD(I.deposit_rate)
    GRID = E.aligned(I.panels, ["Nifty 500", "G-sec 5-year", "Gold"], SD.MENU_START)
    R.label("data_end", I.levels.index[-1].strftime("%-d %B %Y"))
    R.label("menu_from", "April 2005")
    R.context("sip_amount", AMT)
    R.allow("Nifty 500", "Nifty 50", "Midcap 150", "Smallcap 250", "60/40", "60/20/20", "G-sec 5-year", "₹1 crore")
    import time
    only = sys.argv[1:]          # for debugging: run named questions only, and don't write results
    for fn in (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, naive):
        if only and fn.__name__ not in only:
            continue
        t = time.time()
        fn()
        print(f"  {fn.__name__} {time.time() - t:.0f}s", flush=True)
    if not only:
        constants()
        R.write()
    else:
        for k, v in R.facts.items():
            print(f"    {k} = {v['value']}")


if __name__ == "__main__":
    main()
