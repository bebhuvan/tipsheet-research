"""does-sip-work: build figures.json from results. Every plotted value and every number in a title comes from results.

Run from the repo root:  uv run python studies/does-sip-work/figures.py
"""

from __future__ import annotations

import math

from desk import figures

R, F, chart = figures.load(__file__)
SRC = "NSE total-return indices (Nifty 500 from 1995); RBI deposit rates; tipsheet calculations"
SRC_MENU = "NSE total-return indices, NSE 5-year G-sec index, domestic gold price; RBI deposit rates; tipsheet calculations"
SRC_AMFI = "AMFI monthly SIP data (via India Data Hub); NSE; tipsheet calculations"
FULL = "₹10,000 on the first trading day of each month, after a 0.2% a year index-fund cost, before tax"


def v(k):
    return F[k]["value"]


def p(k, d=0):
    """A fraction fact as a percentage string."""
    return f"{v(k) * 100:.{d}f}%".replace("-", "−")


def pts(k, d=1):
    return f"{abs(v(k)) * 100:.{d}f} points"


def lakh(x, d=1):
    return f"₹{x / 1e5:.{d}f} lakh"


def crore(x, d=2):
    return f"₹{x / 1e7:.{d}f} crore"


def rs(x):
    return f"₹{x:,.0f}"


def r100(x, d=1):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(x * 100, d)


def _q(x, q_):
    import numpy as np
    return round(float(np.quantile(np.asarray(x, float), q_)))


def cat(rows, key, cols, scale=100, d=1):
    return {"categories": [r[key] for r in rows], "series": {c: [None if r.get(c) is None else round(r[c] * scale, d) for r in rows] for c in cols}}


H = {1: "1 year", 3: "3 years", 5: "5 years", 7: "7 years", 10: "10 years", 15: "15 years", 20: "20 years"}
FIGS: dict[str, dict] = {}

# ================================================================= Chapter 1

rows = chart("q1_by_horizon")
FIGS["q1"] = {
    "title": f"A Nifty 500 SIP lost money in {p('q1_n500_1y_lost')} of one-year windows, {p('q1_n500_5y_lost')} of five-year ones and none of the ten-year ones",
    "sub": f"Share of SIPs started each month since January 1995 that ended below the money put in, below the same money in fixed deposits, or below inflation. {FULL}.",
    "read": "Each dot is a share of start months. Read across a row: the longer the SIP ran, the rarer each kind of failure. The beat-the-FD line falls slowest, because a deposit is a tougher bar than zero.",
    "source": SRC, "job": "answer", "evidence": "measured",
    "spec": {"kind": "dots", "room": "tall", "fmt": "pct", "digits": 0,
             "series": [{"col": "lost", "label": "Lost money", "slot": 2}, {"col": "below_fd", "label": "Behind an FD (after tax)", "slot": 4},
                        {"col": "below_inflation", "label": "Behind inflation", "slot": 6}]},
    "data": {"categories": [H[r["horizon"]] for r in rows], "series": {c: [r100(r[c]) for r in rows] for c in ("lost", "below_fd", "below_inflation")}},
    "legend": [{"label": "Lost money", "slot": 2}, {"label": "Behind an FD", "slot": 4}, {"label": "Behind inflation", "slot": 6}],
}
FIGS["q1_tax"] = {
    "title": f"After today's tax on redemption, {p('q1_n500_5y_below_fd_after_tax')} of five-year SIPs ended behind an FD, against {p('q1_n500_5y_below_fd')} before tax",
    "sub": "The same windows, with long-term gains above ₹1.25 lakh taxed at 12.5% and short-term gains at 20% when the SIP is cashed in. The FD is taxed every year at 30% plus cess.",
    "read": "The grey bar is before tax, the coloured bar after. Tax matters most at short horizons, where more of the SIP is short-term.",
    "source": SRC, "job": "robustness", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0,
             "series": [{"col": "before", "label": "Before tax", "tone": "hist"}, {"col": "after", "label": "After tax", "slot": 4}]},
    "data": {"categories": [H[r["horizon"]] for r in rows], "series": {"before": [r100(r["below_fd"]) for r in rows], "after": [r100(r["below_fd_after_tax"]) for r in rows]}},
    "legend": [{"label": "Before tax", "color": "var(--hist)", "shape": "box"}, {"label": "After tax", "slot": 4, "shape": "box"}],
}
menu = chart("q1_menu")
m5 = [r for r in menu if r["horizon"] == 5]
FIGS["q1_menu"] = {
    "title": "Over five years, the risk of ending behind an FD depended on what the SIP bought",
    "sub": "Share of five-year SIPs started each month from April 2005 that ended behind the same money in FDs, by what they bought.",
    "read": "One bar per asset. Longer bars mean more five-year windows in which the SIP did worse than a fixed deposit.",
    "source": SRC_MENU, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "sort": "desc",
             "series": [{"col": "below_fd", "label": "Behind an FD at five years", "slot": 4}]},
    "data": {"categories": [r["asset"].replace("Nifty ", "") for r in m5], "series": {"below_fd": [r100(r["below_fd"]) for r in m5]}},
}

fan = chart("q2_fan")
FIGS["q2"] = {
    "title": f"The typical ten-year Nifty 500 SIP returned {p('q2_n500_10y_p50', 1)} a year, but one in twenty returned under {p('q2_n500_10y_p5', 1)}",
    "sub": f"Spread of SIP returns (XIRR) across start months since 1995, by how long the SIP ran. The dashed line is the 12% most SIP calculators assume. {FULL}.",
    "read": "For each horizon, the dot is the middle result, the thick bar the middle half and the thin line the 5th to 95th percentile. The spread narrows sharply with time, but never closes.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "outcomes", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "p50", "label": "Median"}],
             "outcome": {"mid": "p50", "lo": "p5", "hi": "p95"}, "refs": [{"y": 12, "label": "Calculator's 12%"}]},
    "data": {"categories": [H[r["horizon"]] for r in fan], "series": {c: [r100(r[c]) for r in fan] for c in ("p5", "p25", "p50", "p75", "p95")}},
}
vals = chart("q2_values")
FIGS["q2_rupees"] = {
    "title": f"₹10,000 a month for 20 years (₹24 lakh in all) became {crore(v('q2_n500_20y_value_p50'))} in the typical Nifty 500 SIP",
    "sub": "What the SIP was worth at the end, for a bad start (5th percentile), the typical start and a lucky start, beside the money put in. Rupees of the day.",
    "read": "Grey is what you put in. The three coloured dots show how much the ending depended on when you happened to start.",
    "source": SRC, "job": "case", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [{"col": "invested", "label": "Money put in", "tone": "hist"}, {"col": "p5", "label": "Bad start", "slot": 3},
                        {"col": "p50", "label": "Typical", "slot": 2}, {"col": "p95", "label": "Lucky start", "slot": 5}]},
    "data": {"categories": [H[r["horizon"]] for r in vals], "series": {c: [round(r[c]) for r in vals] for c in ("invested", "p5", "p50", "p95")}},
    "legend": [{"label": "Money put in", "color": "var(--hist)"}, {"label": "Bad start", "slot": 3}, {"label": "Typical", "slot": 2}, {"label": "Lucky start", "slot": 5}],
}

rr = chart("q3_real_nominal")
FIGS["q3"] = {
    "title": f"After inflation, the typical ten-year Nifty 500 SIP returned {p('q3_n500_10y_real_p50', 1)} a year, not {p('q2_n500_10y_p50', 1)}",
    "sub": "Median SIP return by horizon, before and after inflation (each instalment and the final value deflated by all-India CPI to the start month).",
    "read": "Grey is the return you see on a statement; colour is what it bought. The gap is roughly the inflation rate.",
    "source": SRC + "; CPI (MoSPI)", "job": "comparison", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [{"col": "nominal_p50", "label": "Before inflation", "tone": "hist"}, {"col": "real_p50", "label": "After inflation", "slot": 2}]},
    "data": {"categories": [H[r["horizon"]] for r in rr], "series": {c: [r100(r[c]) for r in rr] for c in ("nominal_p50", "real_p50")}},
    "legend": [{"label": "Before inflation", "color": "var(--hist)"}, {"label": "After inflation", "slot": 2}],
}
FIGS["q3_fd"] = {
    "title": f"Since {R['labels']['q3_n500_from']}, an FD after tax lost {pts('q3_n500_fd_real')} a year to inflation; the Nifty 500 beat it by {p('q3_n500_index_real', 1)} a year",
    "sub": "Annual return over the whole period, before and after inflation: the Nifty 500 total-return index and a fixed deposit rolled at banks' 1-3 year rate, interest taxed at 30% plus cess.",
    "read": "Each pair of bars is one investment. The coloured bar is what it earned after inflation; the FD's is below zero.",
    "source": SRC + "; CPI (MoSPI)", "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 1,
             "series": [{"col": "nominal", "label": "Before inflation", "tone": "hist"}, {"col": "real", "label": "After inflation", "slot": 2}]},
    "data": {"categories": ["Nifty 500 (with dividends)", "Fixed deposit (after tax)"],
             "series": {"nominal": [r100(v("q3_n500_index_nominal")), r100(v("q3_n500_fd_nominal"))], "real": [r100(v("q3_n500_index_real")), r100(v("q3_n500_fd_real"))]}},
    "legend": [{"label": "Before inflation", "color": "var(--hist)", "shape": "box"}, {"label": "After inflation", "slot": 2, "shape": "box"}],
}

# ================================================================= Chapter 2

a4 = [r for r in chart("q4_assets") if r["horizon"] == 10]
NAMES = {"Nifty 500": "Nifty 500", "Nifty 50": "Nifty 50", "Nifty Midcap 150": "Midcap 150", "Nifty Smallcap 250": "Smallcap 250", "Gold": "Gold", "G-sec 5-year": "Government bonds"}
FIGS["q4"] = {
    "title": "What a SIP bought set both its typical return and its bad case",
    "sub": "Ten-year SIPs started each month from April 2005: the median return (up) against the 5th-percentile return (across), one point per asset. Mid- and small-cap history before 2016 is back-calculated by NSE.",
    "read": "Up is better on average; right is better in a bad decade. No asset is top-right on its own, which is the case for mixing them.",
    "source": SRC_MENU, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1, "x": {"col": "p5", "label": "Bad case (5th percentile), % a year", "fmt": "pct", "digits": 1},
             "y": {"label": "Median, % a year"}, "series": [{"col": "median", "label": "Median", "slot": 2}], "pin": [NAMES[r["asset"]] for r in a4]},
    "data": {"categories": [NAMES[r["asset"]] for r in a4], "series": {"median": [r100(r["median"]) for r in a4], "p5": [r100(r["p5"]) for r in a4]}},
}
FIGS["q4_pain"] = {
    "title": "Small caps fell deepest below the money put in; government bonds barely dipped",
    "sub": "Ten-year SIPs from April 2005: the deepest the month-end value fell below the money put in, in the worst start month, by asset.",
    "read": "Each bar is the worst moment a SIP in that asset went through, as a share of the money put in so far.",
    "source": SRC_MENU, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "sign": True, "sort": "asc",
             "series": [{"col": "deep", "label": "Deepest fall below money put in", "slot": 3}]},
    "data": {"categories": [NAMES[r["asset"]] for r in a4], "series": {"deep": [r100(r["deepest_worst"]) for r in a4]}},
}

pp = [r for r in chart("q5_price_of_protection") if r["mix"] == "60/20/20"]
FIGS["q5"] = {
    "title": f"Over ten years, a 60/20/20 SIP gave up {lakh(v('q5_m602020_10y_given_up_median'))} in the typical case to gain {lakh(v('q5_m602020_10y_gained_p5'))} in a bad one",
    "sub": "60% Nifty 500, 20% government bonds, 20% gold, rebalanced each April, against an all-Nifty 500 SIP over the same months (starts from April 2005): the typical final value given up, and the bad-case (5th percentile) final value gained.",
    "read": "For each horizon, compare the two bars. Where 'gained in a bad case' is longer, diversifying paid for itself; where 'given up' is longer, it cost more than it protected.",
    "source": SRC_MENU, "job": "answer", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [{"col": "given", "label": "Given up in the typical case", "tone": "hist"}, {"col": "gained", "label": "Gained in a bad case", "slot": 2}]},
    "data": {"categories": [H[r["horizon"]] for r in pp], "series": {"given": [round(r["given_up_median"]) for r in pp], "gained": [round(r["gained_p5"]) for r in pp]}},
    "legend": [{"label": "Given up, typical case", "color": "var(--hist)", "shape": "box"}, {"label": "Gained, bad case", "slot": 2, "shape": "box"}],
}
p10 = [r for r in chart("q5_price_of_protection") if r["horizon"] == 10]
FIGS["q5_deep"] = {
    "title": f"The deepest fall below the money put in was {p('q5_n500_10y_deepest_worst')} for the Nifty 500, and {p('q5_m602020_10y_deepest_worst')} for 60/20/20",
    "sub": "Ten-year SIPs from April 2005: the deepest month-end fall below the money put in, in the worst start month.",
    "read": "One bar per portfolio. Mixing in bonds and gold roughly halved the worst fall a SIP holder had to sit through.",
    "source": SRC_MENU, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 0, "sign": True,
             "series": [{"col": "deep", "label": "Deepest fall below money put in", "slot": 3}]},
    "data": {"categories": ["Nifty 500"] + [r["mix"] for r in p10],
             "series": {"deep": [r100(v("q5_n500_10y_deepest_worst"))] + [r100(v(k)) for k in ("q5_m6040_10y_deepest_worst", "q5_m602020_10y_deepest_worst", "q5_mthirds_10y_deepest_worst")]}},
}
FIGS["q5_menu"] = {
    "title": "",
    "sub": "Ten-year SIPs from April 2005: median and 5th-percentile return of each portfolio.",
    "read": "Grey dot is the bad case, coloured the typical case. Moving down the list, the two dots draw closer: less upside, less downside.",
    "source": SRC_MENU, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [{"col": "p5", "label": "Bad case (5th percentile)", "tone": "hist"}, {"col": "p50", "label": "Median", "slot": 2}]},
    "data": {"categories": ["Nifty 500", "60/40", "60/20/20", "Equal thirds"],
             "series": {"p5": [r100(v(k)) for k in ("q5_n500_10y_p5", "q5_m6040_10y_p5", "q5_m602020_10y_p5", "q5_mthirds_10y_p5")],
                        "p50": [r100(v(k)) for k in ("q5_n500_10y_p50", "q5_m6040_10y_p50", "q5_m602020_10y_p50", "q5_mthirds_10y_p50")]}},
    "legend": [{"label": "Bad case", "color": "var(--hist)"}, {"label": "Median", "slot": 2}],
}
FIGS["q5_menu"]["title"] = (f"The Nifty 500's median was {p('q5_n500_10y_p50', 1)} against {p('q5_m602020_10y_p50', 1)} for 60/20/20, "
                            f"but its bad case was lower: {p('q5_n500_10y_p5', 1)} against {p('q5_m602020_10y_p5', 1)}")

q6 = [r for r in chart("q6_paired") if r["mix"] == "60/20/20" and r["horizon"] == 10]
FIGS["q6"] = {
    "title": f"Rebalancing a 60/20/20 SIP each April added a median {pts('q6_m602020_10y_diff_p50')} a year, in at least nine in ten start months",
    "sub": "Ten-year SIPs from April 2005: return rebalanced to 60/20/20 each April minus return with instalments split 60/20/20 but never rebalanced, by start month.",
    "read": "Each bar is one start month. Above zero, rebalancing helped. At least nine in ten bars are above zero.",
    "source": SRC_MENU, "job": "answer", "evidence": "tested",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 1, "period": "month", "range": False, "sign": True,
             "series": [{"col": "diff", "label": "Rebalanced minus never", "slot": 2}]},
    "data": {"dates": [r["start"] + "-01" for r in q6], "series": {"diff": [r100(r["diff"], 2) for r in q6]}},
}

# ================================================================= Chapter 3

q7 = chart("q7_ranges")
FIGS["q7"] = {
    "title": f"From 5 to 20 years, the spread of yearly returns shrank from {pts('q7_n500_5y_xirr_range', 0)} to {pts('q7_n500_20y_xirr_range')}",
    "sub": "Nifty 500 SIPs since 1995: the 5th and 95th percentile return a year, by horizon.",
    "read": "The two dots for each horizon bracket nine in ten outcomes. They squeeze together as the SIP runs longer.",
    "source": SRC, "job": "mechanism", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [{"col": "xirr_p5", "label": "5th percentile", "slot": 3}, {"col": "xirr_p95", "label": "95th percentile", "slot": 5}]},
    "data": {"categories": [H[r["horizon"]] for r in q7], "series": {c: [r100(r[c]) for r in q7] for c in ("xirr_p5", "xirr_p95")}},
    "legend": [{"label": "5th percentile", "slot": 3}, {"label": "95th percentile", "slot": 5}],
}
FIGS["q7_mult"] = {
    "title": f"But in rupees the gap did not shrink: at 20 years the final value ran from {v('q7_n500_20y_multiple_p5'):.1f} to {v('q7_n500_20y_multiple_p95'):.1f} times the money put in",
    "sub": "Nifty 500 SIPs since 1995: the 5th and 95th percentile final value, as a multiple of the money put in, by horizon.",
    "read": "A small difference in yearly return, compounded over 20 years, is a large difference in rupees.",
    "source": SRC, "job": "mechanism", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "x", "digits": 1,
             "series": [{"col": "mult_p5", "label": "5th percentile", "slot": 3}, {"col": "mult_p95", "label": "95th percentile", "slot": 5}]},
    "data": {"categories": [H[r["horizon"]] for r in q7], "series": {c: [round(r[c], 2) for r in q7] for c in ("mult_p5", "mult_p95")}},
    "legend": [{"label": "5th percentile", "slot": 3}, {"label": "95th percentile", "slot": 5}],
}

q8 = chart("q8_by_start_year")
FIGS["q8"] = {
    "title": f"The start year mattered enormously: the median ten-year return ranged from {p('q8_n500_10y_worst_year_median', 1)} to {p('q8_n500_10y_best_year_median', 1)}",
    "sub": "Median ten-year Nifty 500 SIP return for start months in each calendar year. Years before 1999 rest on a probably back-calculated index.",
    "read": "Each bar is one start year. Nobody could have known in advance which bar they were standing on.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "median", "label": "Median ten-year return", "slot": 2}]},
    "data": {"categories": [str(r["year"]) for r in q8], "series": {"median": [r100(r["median"]) for r in q8]}},
}
b8 = chart("q8_bands")
FIGS["q8_bands"] = {
    "title": f"Starting near a market high made little difference: {p('q8_n500_10y_near_high_p50', 1)} against {p('q8_n500_10y_far_p50', 1)} for starts more than 10% below it",
    "sub": "Ten-year Nifty 500 SIP returns by how far the market was below its previous high in the start month.",
    "read": "Each row shows the median (dot) and the 5th to 95th percentile range. The rows overlap almost completely.",
    "source": SRC, "job": "conditioning", "evidence": "measured",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "pct", "digits": 1, "series": [{"col": "median", "label": "Median"}],
             "outcome": {"mid": "median", "lo": "p5", "hi": "p95", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": [r["band"].replace("-", " to ") for r in b8], "series": {"median": [r100(r["median"]) for r in b8], "p5": [r100(r["p5"]) for r in b8],
                                                                                    "p95": [r100(r["p95"]) for r in b8], "n": [r["n"] for r in b8]}},
}

q9y = chart("q9_value_by_year")
FIGS["q9_years"] = {
    "title": f"In a 15-year SIP, the first five years' instalments made up {p('q9_n500_15y_first5_share_p50')} of the final value; the last five, {p('q9_n500_15y_last5_share_p50')}",
    "sub": "Share of a 15-year Nifty 500 SIP's final value that came from each year's instalments (median across start months since 1995).",
    "read": "Each bar is one year of instalments. Early money had the longest to compound, so it ended up doing most of the work.",
    "source": SRC, "job": "mechanism", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 0, "series": [{"col": "share", "label": "Share of final value", "slot": 2}]},
    "data": {"categories": [f"Year {r['year']}" for r in q9y], "series": {"share": [r100(r["share"]) for r in q9y]}},
}
FIGS["q9_years"]["spec"]["kind"] = "hbars"
FIGS["q9_glide"] = {
    "title": f"Moving to FDs over the last three years ended ahead in only {p('q9_g36_ahead')} of 15-year SIPs, and lowered even the bad case",
    "sub": "15-year Nifty 500 SIPs since 1995: final value if the SIP stayed invested, against switching the corpus to FDs in 36 (or 12) equal monthly steps and paying the last instalments into FDs. Equity before tax; FD interest taxed.",
    "read": "For each choice: the dot is the typical final value, the line runs from the bad case (5th percentile) to the median. Staying put was better in both.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "dots", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [{"col": "p5", "label": "Bad case (5th percentile)", "tone": "hist"}, {"col": "p50", "label": "Median", "slot": 2}]},
    "data": {"categories": ["Stayed invested", "Switched over the last 12 months", "Switched over the last 36 months"],
             "series": {"p5": [round(v(k)) for k in ("q9_stay_p5", "q9_g12_p5", "q9_g36_p5")], "p50": [round(v(k)) for k in ("q9_stay_p50", "q9_g12_p50", "q9_g36_p50")]}},
    "legend": [{"label": "Bad case", "color": "var(--hist)"}, {"label": "Median", "slot": 2}],
}

need = [r for r in chart("q10_need") if r["asset"] == "Nifty 500"]
FIGS["q10"] = {
    "title": f"To reach ₹1 crore in 15 years nineteen times in twenty, the Nifty 500 record says {rs(v('q10_n500_15y_need_95'))} a month; a 12% calculator says {rs(v('q10_calc12_15y_amount'))}",
    "sub": "Monthly amount that would have reached ₹1 crore (rupees of the day) in half, four in five and nineteen in twenty of the start months since 1995, by horizon.",
    "read": "Each group is a horizon. The higher the certainty you want, the more you must put in; the gaps between the dots are the price of certainty.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "dots", "room": "standard", "fmt": "num", "digits": 0, "unit": "₹ a month",
             "series": [{"col": "c50", "label": "50% sure", "slot": 5}, {"col": "c80", "label": "80% sure", "slot": 4}, {"col": "c95", "label": "95% sure", "slot": 2}]},
    "data": {"categories": [H[y] for y in (10, 15, 20)],
             "series": {f"c{c}": [round([r["flat"] for r in need if r["horizon"] == y and round(r["confidence"] * 100) == c][0]) for y in (10, 15, 20)] for c in (50, 80, 95)}},
    "legend": [{"label": "50% sure", "slot": 5}, {"label": "80% sure", "slot": 4}, {"label": "95% sure", "slot": 2}],
}
FIGS["q10_late"] = {
    "title": f"Starting five years late meant {rs(v('q10_late_need_15y'))} a month instead of ₹10,000 to end up in the same place",
    "sub": "The amount a 15-year Nifty 500 SIP needed to match, four times in five, what ₹10,000 a month for 20 years produced four times in five.",
    "read": "The grey bar is the 20-year saver; the coloured bar is what the late starter had to put in each month.",
    "source": SRC, "job": "case", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "num", "digits": 0, "unit": "₹ a month",
             "series": [{"col": "amt", "label": "Monthly amount", "slot": 2}]},
    "data": {"categories": ["20 years from the start", "15 years, starting 5 years late"], "series": {"amt": [10000, round(v("q10_late_need_15y"))]}},
}

# ================================================================= Chapter 4

FIGS["q11"] = {
    "title": f"With a lump sum in hand, investing it at once beat a 12-month STP in {p('q11_lump_beat_stp12')} of start months",
    "sub": "₹12 lakh into the Nifty 500 at once, against moving it in from an FD over 12 or 36 months, valued after 10 years; and, for someone earning monthly, a monthly SIP against saving in an FD and investing the pot each April.",
    "read": "Each bar is the share of start months since 1995 in which the first choice ended ahead. Half would mean a coin toss.",
    "source": SRC, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "refs": [{"y": 50, "label": "Coin toss"}],
             "series": [{"col": "won", "label": "First choice ended ahead", "slot": 2}]},
    "data": {"categories": ["Lump sum vs 12-month STP", "Lump sum vs 36-month STP", "Monthly SIP vs FD, invested each April"],
             "series": {"won": [r100(v("q11_lump_beat_stp12")), r100(v("q11_lump_beat_stp36")), r100(v("q11_sip_beat_fd_april"))]}},
}
lev = {r["lever"]: r for r in chart("q12_levers")}
LEV = [("best_date", "Best SIP date instead of the 1st"), ("weekly", "Weekly instead of monthly"), ("stepup", "10% yearly step-up"),
       ("wait_fall", "Save in FD, invest after 20% falls"), ("pe_double", "Double up when P/E is cheap"),
       ("pause_lab", "Pause in a 20% fall (resume near the top)"), ("pause_fall", "Pause in a 20% fall (resume at the top)"),
       ("cost_1pct", "1% a year more in costs")]
FIGS["q12"] = {
    "title": f"Every SIP trick moved the ten-year return by less than the choice of asset ({pts('q12_asset_gap')}) or start year",
    "sub": "Median change in ten-year Nifty 500 SIP return from each change to a plain monthly SIP, with the 10th to 90th percentile across start months (April 2005 on). Paused or waiting money sits in a taxed FD.",
    "read": "Each row is one change; right of zero helped, left hurt. Compare the size of every row with the two grey bars at the bottom: the spread between assets and between start years.",
    "source": SRC, "job": "answer", "evidence": "measured",
    "spec": {"kind": "forest", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "m", "label": "Median effect"}],
             "ci": {"mid": "m", "lo": "l", "hi": "h", "ref": 0, "label": "10th to 90th percentile"}},
    "data": {"categories": [n for _, n in LEV] + ["Spread between assets (medians)", "Spread between start years (medians)"],
             "series": {"m": [r100(lev[k]["p50"], 2) for k, _ in LEV] + [r100(v("q12_asset_gap")), r100(v("q12_start_year_gap"))],
                        "l": [r100(lev[k]["p10"], 2) for k, _ in LEV] + [None, None],
                        "h": [r100(lev[k]["p90"], 2) for k, _ in LEV] + [None, None]}},
}
days = chart("q12_by_day")
FIGS["q12_days"] = {
    "title": f"The SIP date barely mattered: the best day of the month added {pts('q12_best_date_p50', 2)} a year over ten years",
    "sub": "Median change in ten-year Nifty 500 SIP return from buying on each day of the month (the first trading day on or after it) instead of the 1st.",
    "read": "Each bar is one day of the month. The whole chart spans a fraction of a point.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 2, "sign": True, "series": [{"col": "e", "label": "Change against the 1st", "slot": 2}]},
    "data": {"categories": [str(r["day"]) for r in days], "series": {"e": [r100(r["effect_p50"], 3) for r in days]}},
}
FIGS["q12_days"]["spec"]["kind"] = "hbars"

t13 = chart("q13_tax_clock")
AGE = {12: "1 year", 18: "18 months", 24: "2 years", 36: "3 years", 60: "5 years"}
FIGS["q13"] = {
    "title": f"Cash in a SIP after two years and {p('q13_24m_st_units')} of its units are still short-term, though they hold only {p('q13_24m_st_gain_share_p50')} of the gains",
    "sub": "Nifty 500 SIPs cashed in fully at each age: share of units held under a year (taxed as short-term) and their share of the gain (median, SIPs with a gain).",
    "read": "Each instalment has its own clock. The grey dot is the share of units still under a year old; the coloured dot is their share of the gain, smaller because new units have had little time to gain.",
    "source": SRC, "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 0,
             "series": [{"col": "units", "label": "Short-term units", "tone": "hist"}, {"col": "gains", "label": "Short-term share of gains", "slot": 2}]},
    "data": {"categories": [AGE[r["age"]] for r in t13], "series": {"units": [r100(r["st_units"]) for r in t13], "gains": [r100(r["st_gain_share"]) for r in t13]}},
    "legend": [{"label": "Short-term units", "color": "var(--hist)"}, {"label": "Short-term share of gains", "slot": 2}],
}
FIGS["q13_cost"] = {
    "title": f"Tax and a 1% exit load took {p('q13_12m_cost_p50', 1)} of a one-year SIP's value, and {p('q13_36m_cost_p50', 1)} at three years",
    "sub": "Median tax plus exit load on cashing in a ₹10,000-a-month Nifty 500 SIP, as a share of its value, against the tax on the same money invested as a lump sum at the start and held as long.",
    "read": "Grey is the lump sum, colour the SIP. The SIP's cost falls as more units cross the one-year mark, then rises again as long-term gains outgrow the ₹1.25 lakh exemption.",
    "source": SRC, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [{"col": "lump", "label": "Lump sum", "tone": "hist"}, {"col": "sip", "label": "SIP (tax + 1% load)", "slot": 2}]},
    "data": {"categories": [AGE[r["age"]] for r in t13], "series": {"lump": [r100(r["lump_cost"], 2) for r in t13], "sip": [r100(r["cost"], 2) for r in t13]}},
    "legend": [{"label": "Lump sum", "color": "var(--hist)"}, {"label": "SIP", "slot": 2}],
}

e14 = chart("q14_edge")
FIGS["q14"] = {
    "title": f"Volatility did not reliably help: the SIP's edge over the index tracked volatility only weakly (rank correlation {v('q14_n500_corr_vol'):.2f})",
    "sub": "Every ten-year Nifty 500 window since 1995: the SIP's return minus the index's own return over the same dates, against how volatile the window was.",
    "read": "Each dot is a start month. If choppy markets helped SIPs, the dots would climb steeply to the right. They drift up only slightly, and even that vanished for SIPs started after 2005.",
    "source": SRC, "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1, "labels": "none",
             "x": {"col": "vol", "label": "Volatility of the window, % a year", "fmt": "pct", "digits": 0},
             "y": {"label": "SIP minus index, points a year"}, "series": [{"col": "edge", "label": "SIP edge", "slot": 2}]},
    "data": {"categories": [r["start"] for r in e14], "series": {"edge": [r100(r["edge"], 2) for r in e14], "vol": [r100(r["vol"], 1) for r in e14]}},
}
sm, ch = chart("q14_illus_smooth"), chart("q14_illus_choppy")
FIGS["q14_illus"] = {
    "title": f"Two made-up markets from 100 to 200 in ten years: the choppy one gave a SIP {p('q14_illus_choppy_xirr', 2)} a year, the smooth one {p('q14_illus_smooth_xirr', 2)}",
    "sub": "An illustration, not data: the same start and end, one path smooth and one swinging 30% either way.",
    "read": "The SIP bought more units in the choppy path's dips, but also more at its peaks. Net, the difference is tiny.",
    "source": "tipsheet illustration", "job": "case", "evidence": "illustration",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "period": "month", "range": False,
             "series": [{"col": "smooth", "label": "Smooth", "tone": "hist"}, {"col": "choppy", "label": "Choppy", "slot": 2}]},
    "data": {"dates": [r["month"] + "-28" for r in sm], "series": {"smooth": [round(r["level"], 1) for r in sm], "choppy": [round(r["level"], 1) for r in ch]}},
}

# ================================================================= Chapter 5

b15 = chart("q15_by_start")
FIGS["q15"] = {
    "title": f"{p('q15_n500_ever_red')} of Nifty 500 SIPs since 1995 were below the money put in at some month-end; the deepest fall was {p('q15_n500_deepest')}",
    "sub": "For SIPs started each month and followed to today: the deepest the month-end value fell below the money put in.",
    "read": "Each bar is one start month. The clusters are the crashes that began in 2000, 2008 and 2020; almost every SIP met at least one.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 0, "period": "month", "range": False, "sign": True,
             "series": [{"col": "deep", "label": "Deepest fall below money put in", "slot": 3}]},
    "data": {"dates": [r["start"] + "-01" for r in b15], "series": {"deep": [r100(r["deepest"]) for r in b15]}},
}
FIGS["q15_long"] = {
    "title": f"The longest stretch below the money put in was {v('q15_n500_longest')} months, for a SIP started in {R['labels']['q15_n500_longest_start']}",
    "sub": "For SIPs started each month and followed to today: the longest unbroken run of month-ends below the money put in.",
    "read": "Each bar is one start month. Most runs were short; the late-1990s starts waited longest.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "int", "digits": 0, "unit": "months", "period": "month", "range": False,
             "series": [{"col": "longest", "label": "Longest run below money put in", "slot": 3}]},
    "data": {"dates": [r["start"] + "-01" for r in b15], "series": {"longest": [r["longest"] for r in b15]}},
}

o16 = chart("q16_outcomes")
n500 = [r for r in o16 if r["asset"] == "Nifty 500" and r["group"] in ("0-10% below", "10-20% below", "over 20% below", "not red")]
FIGS["q16"] = {
    "title": f"Nifty 500 SIPs in the red after a year went on to a median {p('q16_n500_red_p50', 1)} a year over ten years, against {p('q16_n500_rest_p50', 1)} for the rest",
    "sub": "Ten-year Nifty 500 SIP returns since 1995, by how far the SIP was below the money put in at 12 months.",
    "read": "Each row: dot is the median, thick bar the middle half, thin line the 5th to 95th percentile. The counts are start months; the episodes behind them are far fewer.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "pct", "digits": 1, "series": [{"col": "p50", "label": "Median"}],
             "outcome": {"mid": "p50", "lo": "p5", "hi": "p95", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": ["Under 10% below at 12 months", "10 to 20% below", "More than 20% below", "Not in the red"],
             "series": {c: [r100(r[c]) if c != "n" else r[c] for r in n500] for c in ("p5", "p25", "p50", "p75", "p95", "n")}},
}
idx = [r for r in o16 if r["group"] in ("red", "rest")]
FIGS["q16_indices"] = {
    "title": "For mid and small caps the bonus for a bad start was small or absent",
    "sub": "Median ten-year SIP return for SIPs in the red at 12 months against the rest, by index (Nifty 500 from 1995, Nifty 50 from 1999, mid and small caps from 2005).",
    "read": "Coloured is the red-at-a-year group, grey the rest. Where colour is right of grey, a bad start was followed by a better ending.",
    "source": SRC, "job": "conditioning", "evidence": "tested",
    "spec": {"kind": "dots", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [{"col": "rest", "label": "Not in the red at a year", "tone": "hist"}, {"col": "red", "label": "In the red at a year", "slot": 2}]},
    "data": {"categories": ["Nifty 500", "Nifty 50", "Midcap 150", "Smallcap 250"],
             "series": {"rest": [r100(v(f"q16_{k}_rest_p50")) for k in ("n500", "n50", "mid150", "small250")],
                        "red": [r100(v(f"q16_{k}_red_p50")) for k in ("n500", "n50", "mid150", "small250")]}},
    "legend": [{"label": "Not in the red", "color": "var(--hist)"}, {"label": "In the red at a year", "slot": 2}],
}
FIGS["q16_mechanism"] = {
    "title": f"Why a bad start helped: {p('q16_n500_money_while_red_p50')} of the money went in while the SIP was red, but it bought {p('q16_n500_units_while_red_p50')} of the units",
    "sub": "Nifty 500 SIPs in the red at 12 months: median share of all instalments made while the SIP was below the money put in, and median share of the units those instalments bought.",
    "read": "Money put in during the bad months bought units cheaply. Those units are worth the same as any other at the end, so they punch above their weight.",
    "source": SRC, "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 0, "series": [{"col": "s", "label": "Share", "slot": 2}]},
    "data": {"categories": ["Share of money put in while red", "Share of units bought while red"],
             "series": {"s": [r100(v("q16_n500_money_while_red_p50")), r100(v("q16_n500_units_while_red_p50"))]}},
}
c08 = chart("q16_case2008")
FIGS["q16_case"] = {
    "title": f"A Nifty 500 SIP started in January 2008 fell {p('q16_case2008_deepest')} below the money put in, then returned {p('q16_case2008_xirr_10y', 1)} a year over ten years",
    "sub": "₹10,000 a month from January 2008, month by month to today: money put in and what it was worth.",
    "read": "Grey is the money put in, colour the statement value. The colour line spent its first year and more below grey, then never looked back.",
    "source": SRC, "job": "case", "evidence": "illustration",
    "spec": {"kind": "line", "room": "tall", "fmt": "num", "digits": 1, "unit": "₹ lakh, log scale", "div": 100000, "log": True, "period": "month", "range": False,
             "series": [{"col": "value", "label": "What it was worth", "slot": 2}, {"col": "invested", "label": "Money put in", "tone": "hist"}]},
    "data": {"dates": [r["month"] + "-28" for r in c08], "series": {"value": [round(r["value"]) for r in c08], "invested": [round(r["invested"]) for r in c08]}},
}

g17 = chart("q17_gaps")
FIGS["q17"] = {
    "title": f"Keeping a red SIP going beat stopping in {p('q17_n500_m12_A_beat_B')} of cases; switching to FDs cost a median {lakh(v('q17_n500_m12_gap_C_p50'))}",
    "sub": "Nifty 500 SIPs in the red at 12 months, over the same ten years and the same ₹12 lakh of savings: keeping going, against stopping and holding (new money to FDs), selling and switching to FDs, or pausing until back in the black. Paired gap in final value.",
    "read": "Each row is one alternative: how many rupees keeping going ended ahead by (median, with the 5th to 95th percentile). Everything is right of zero.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000, "series": [{"col": "m", "label": "Median gap"}],
             "outcome": {"mid": "m", "lo": "l", "hi": "h", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": ["Against stopping and holding", "Against selling and switching to FDs", "Against pausing until back in the black"],
             "series": {}},
}


FIGS["q17"]["data"]["series"] = (lambda rows: {"m": [_q([r["gap"] for r in rows if r["path"] == s], .5) for s in "BCD"],
                                              "l": [_q([r["gap"] for r in rows if r["path"] == s], .05) for s in "BCD"],
                                              "h": [_q([r["gap"] for r in rows if r["path"] == s], .95) for s in "BCD"],
                                              "n": [sum(1 for r in rows if r["path"] == s) for s in "BCD"]})(
    [r for r in g17 if r["asset"] == "Nifty 500" and r["age"] == 12])
FIGS["q17_indices"] = {
    "title": f"Small caps were the one place stopping sometimes paid: keeping going won {p('q17_small250_m12_A_beat_B')} of the time",
    "sub": "SIPs in the red at 12 months, by index: share of start months in which keeping going beat stopping and holding, selling to FDs, and pausing.",
    "read": "Each group is an index; a full bar means keeping going won every time.",
    "source": SRC, "job": "robustness", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "domain": [0, 100],
             "series": [{"col": "B", "label": "vs stop and hold", "slot": 2}, {"col": "C", "label": "vs sell to FDs", "slot": 4}, {"col": "D", "label": "vs pause", "slot": 6}]},
    "data": {"categories": ["Nifty 500", "Nifty 50", "Midcap 150", "Smallcap 250"],
             "series": {s: [r100(v(f"q17_{k}_m12_A_beat_{s}")) for k in ("n500", "n50", "mid150", "small250")] for s in "BCD"}},
    "legend": [{"label": "vs stop and hold", "slot": 2, "shape": "box"}, {"label": "vs sell to FDs", "slot": 4, "shape": "box"}, {"label": "vs pause", "slot": 6, "shape": "box"}],
}

c18 = chart("q18_corr_by_age")
FIGS["q18"] = {
    "title": f"A SIP's return in its first year said little about its ending, and if anything pointed the wrong way (correlation {v('q18_n500_10y_corr_12m'):.2f})",
    "sub": "Nifty 500 SIPs since 1995: rank correlation between the return shown at each age and the final ten-year return.",
    "read": "Above zero, a good early number meant a good ending; below zero, the opposite. The line hovers around zero for years and only climbs late in the SIP's life.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "bars", "room": "standard", "fmt": "num", "digits": 2, "sign": True, "series": [{"col": "c", "label": "Correlation with the ending", "slot": 2}]},
    "data": {"categories": [f"{r['age']}m" for r in c18], "series": {"c": [round(r["corr"], 2) for r in c18]}},
}
FIGS["q18"]["spec"]["kind"] = "hbars"

# ================================================================= Chapter 6

s19 = chart("q19_scatter")
FIGS["q19"] = {
    "title": f"Among Nifty 50 SIPs in the red at a year, cheap and dear markets ended about the same: {p('q19_red_cheap_p50', 1)} against {p('q19_red_dear_p50', 1)}",
    "sub": "Nifty 50 SIPs since 1999: the index's trailing P/E at the SIP's 12-month mark against its ten-year return. SIPs in the red at 12 months are in colour.",
    "read": "Each dot is a start month. If the bad-start bonus came only from cheap prices, the coloured dots on the left would sit well above those on the right.",
    "source": SRC + "; NSE P/E", "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1, "labels": "none",
             "x": {"col": "pe12", "label": "Nifty 50 P/E at 12 months", "fmt": "num", "digits": 0},
             "y": {"label": "Ten-year SIP return, % a year"}, "series": [{"col": "xirr", "label": "Ten-year return", "slot": 2}],
             "pin": [r["start"] for r in s19 if r["red"]]},
    "data": {"categories": [r["start"] for r in s19], "series": {"xirr": [r100(r["xirr"]) for r in s19], "pe12": [round(r["pe12"], 1) for r in s19]}},
}
FIGS["q19_now"] = {
    "title": f"Today's Nifty 50 P/E of {v('q19_pe_now'):.1f} sits at the {p('q19_pe_now_pctile')} mark of its history; the FD rate at the {p('q19_fd_now_pctile')} mark",
    "sub": "Where today's valuation and deposit rate sit against their own history (P/E since 1999, deposit rate since 1995). Context, not a forecast. NSE's earnings basis changed in 2021.",
    "read": "A bar at 50% would be an ordinary reading. Neither is extreme.",
    "source": "NSE; RBI; tipsheet calculations", "job": "caveat", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 0, "domain": [0, 100], "series": [{"col": "pc", "label": "Percentile", "slot": 2}]},
    "data": {"categories": ["Nifty 50 P/E", "FD rate"], "series": {"pc": [r100(v("q19_pe_now_pctile")), r100(v("q19_fd_now_pctile"))]}},
}

FIGS["q20"] = {
    "title": f"Investors' SIP money earned {p('q20_n500_industry', 1)} a year, against {p('q20_n500_trend', 1)} for money growing at the same trend: no sign of bad timing",
    "sub": f"AMFI's monthly SIP inflows, {R['labels']['q20_from']} to {R['labels']['q20_to']}, as if invested in the Nifty 500 total-return index, against a steady SIP, a SIP growing at the inflows' own trend ({p('q20_trend_growth')} a year), and the index itself. Before tax and costs.",
    "read": "A steady SIP is the wrong yardstick: inflows grew every year, so more money naturally went in later, at higher prices. Against the fair yardstick the gap all but disappears.",
    "source": SRC_AMFI, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1, "series": [{"col": "x", "label": "Return a year", "slot": 2}]},
    "data": {"categories": ["Investors' actual SIP money", "Money growing at its trend", "Steady amounts, same months", "The index itself"],
             "series": {"x": [r100(v(k)) for k in ("q20_n500_industry", "q20_n500_trend", "q20_n500_constant", "q20_n500_index")]}},
}
inf = chart("q20_inflows")
FIGS["q20_inflows"] = {
    "title": f"Monthly SIP inflows grew at about {p('q20_trend_growth')} a year",
    "sub": "AMFI's gross monthly SIP inflows and their log-linear trend.",
    "read": "The line is the trend; the bars are each month's inflow.",
    "source": SRC_AMFI, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "unit": "₹ crore", "div": 1e7, "period": "month", "range": False,
             "series": [{"col": "inflow", "label": "Monthly inflow", "slot": 2}, {"col": "trend", "label": "Trend", "tone": "hist"}]},
    "data": {"dates": [r["month"] + "-28" for r in inf], "series": {"inflow": [round(r["inflow"]) for r in inf], "trend": [round(r["trend"]) for r in inf]}},
}

dd = chart("q21_drawdown")
FIGS["q21"] = {
    "title": f"Falls of 10% or more kept coming after SIP money grew: {v('q21_2016_on_falls')} since 2016, the worst {p('q21_2016_on_worst_depth')}",
    "sub": "Nifty 500 total-return index: how far below its previous peak it was at each month's low, 1995 to today.",
    "read": "The shaded area is the distance below the last high. Deep falls became rarer after 2016, but ten years is too short to say why.",
    "source": SRC, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "area", "room": "standard", "fmt": "pct", "digits": 0, "period": "month", "range": False,
             "series": [{"col": "dd", "label": "Below the previous peak", "slot": 3}], "events": [{"date": "2016-04-01", "label": "SIP inflows start to climb"}]},
    "data": {"dates": [r["date"] for r in dd], "series": {"dd": [r100(r["dd"]) for r in dd]}},
}

lf = chart("q22_life")
FIGS["q22"] = {
    "title": f"At today's rate of closures, the average SIP account lasts about {v('q22_life_latest'):.1f} years",
    "sub": "Outstanding SIP accounts divided by accounts closed over the previous 12 months: a rough average life. Shaded windows include AMFI's January–April 2025 clean-up of dormant accounts.",
    "read": "Each point is a rough measure of how long a SIP account lasts, given how fast accounts were closing that year. It has never been above five years.",
    "source": SRC_AMFI, "job": "answer", "evidence": "tested",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 1, "unit": "years", "period": "month", "range": False,
             "series": [{"col": "life", "label": "Implied average life", "slot": 2}],
             "events": [{"date": "2025-01-01", "to": "2025-04-30", "label": "Clean-up"}]},
    "data": {"dates": [r["month"] + "-28" for r in lf], "series": {"life": [None if r["life"] is None else round(r["life"], 2) for r in lf]}},
}
ac = chart("q22_accounts")
FIGS["q22_accounts"] = {
    "title": f"Closures spiked to {v('q22_stoppage_max'):.1f} times new registrations in {R['labels']['q22_stoppage_max_month']}, during AMFI's clean-up",
    "sub": "New and closed SIP accounts each month (AMFI). Closures include SIPs that reached their end date, failed bank mandates and the 2025 clean-up.",
    "read": "When the coloured line is above the grey, more accounts closed than opened that month.",
    "source": SRC_AMFI, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "unit": "lakh accounts", "div": 1e5, "period": "month", "range": False,
             "series": [{"col": "closed", "label": "Closed", "slot": 3}, {"col": "new", "label": "New", "tone": "hist"}]},
    "data": {"dates": [r["month"] + "-28" for r in ac], "series": {"closed": [round(r["closed"]) for r in ac], "new": [round(r["new"]) for r in ac]}},
}

FIGS["x0"] = {
    "title": f"The SIP started in April 2025 ended its first year {p('x0_fy26_cohort_12m')} down; {p('x0_fy26_cohort_pctile')} of first years since 1995 were worse",
    "sub": "Nifty 500 SIP of ₹10,000 a month from April 2025, valued at the end of March 2026, against every 12-month SIP since 1995.",
    "read": "A bad year, but not an unusual one.",
    "source": SRC, "job": "case", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 0, "sign": True, "series": [{"col": "x", "label": "Value against money put in", "slot": 3}]},
    "data": {"categories": ["FY2025-26 SIP after 12 months"], "series": {"x": [r100(v("x0_fy26_cohort_12m"))]}},
}

if __name__ == "__main__":
    figures.write(__file__, FIGS)
