"""does-sip-work: build figures.json from results. Every plotted value and every number in a title comes from results.

Design (2026-10-15 redesign, after the owner found the first set grey and clumsy):
- identity colour follows the portfolio, the same in every chart (COL); benchmarks (the FD, money put in, values
  before inflation, "the rest") are grey; the site's slots, checked with the dataviz palette validator;
- `few` is off everywhere: research pages otherwise draw one- and two-series charts in grey;
- grouped bars instead of dot plots with value columns; outcomes for distributions; no one- or two-bar charts.

Run from the repo root:  uv run python studies/does-sip-work/figures.py
"""

from __future__ import annotations

import math

import numpy as np

from desk import figures

R, F, chart = figures.load(__file__)
SRC = "NSE total-return indices (Nifty 500 from 1995); RBI deposit rates; tipsheet calculations"
SRC_MENU = "NSE total-return indices, NSE 5-year G-sec index, domestic gold price; RBI deposit rates; tipsheet calculations"
SRC_AMFI = "AMFI monthly SIP data (via India Data Hub); NSE; tipsheet calculations"
FULL = "₹10,000 on the first trading day of each month, after a 0.2% a year index-fund cost, before tax"
MIXNOTE = "60/20/20 is 60% Nifty 500, 20% government bonds, 20% gold; equal thirds is a third each; both rebalanced each April"

# one colour per portfolio, everywhere (site slots; validated)
COL = {"Nifty 500": 1, "60/20/20": 3, "Equal thirds": 4, "Gold": 5, "Smallcap 250": 6, "Government bonds": 7,
       "Midcap 150": 8, "Nifty 50": 11, "60/40": 12}
BAD = 2          # terracotta: the bad case, where a second measure needs a colour


def v(k):
    return F[k]["value"]


def p(k, d=0):
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


def ser(col, label, slot=None, grey=False, ink=False):
    s = {"col": col, "label": label}
    if ink:
        s["tone"] = "ink"
    elif grey:
        s["tone"] = "hist"
    elif slot is not None:
        s["slot"] = slot
    return s


def key(label, slot=None, grey=False, shape="box", ink=False):
    colour = {"color": "var(--ink)"} if ink else {"color": "var(--hist)"} if grey else {"slot": slot}
    return {"label": label, **colour, "shape": shape}


H = {1: "1 year", 3: "3 years", 5: "5 years", 7: "7 years", 10: "10 years", 15: "15 years", 20: "20 years"}
FIGS: dict[str, dict] = {}

# ================================================================= Chapter 1

rows = chart("q1_by_horizon")
FIGS["q1"] = {
    "title": f"A Nifty 500 SIP lost money in {p('q1_n500_1y_lost')} of one-year windows, {p('q1_n500_5y_lost')} of five-year ones and none of the ten-year ones",
    "sub": f"Share of SIPs started each month since January 1995 that ended below the money put in, behind the same money in fixed deposits, or behind inflation. {FULL}.",
    "read": "Each group of bars is a horizon. All three bars shrink as the SIP runs longer; the terracotta one, behind an FD, shrinks last because a deposit is a tougher bar than zero.",
    "source": SRC, "job": "answer", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "tall", "fmt": "pct", "digits": 0,
             "series": [ser("lost", "Lost money", ink=True), ser("below_fd", "Behind an FD (after tax)", BAD), ser("below_inflation", "Behind inflation", grey=True)]},
    "data": {"categories": [H[r["horizon"]] for r in rows], "series": {c: [r100(r[c]) for r in rows] for c in ("lost", "below_fd", "below_inflation")}},
    "legend": [key("Lost money", ink=True), key("Behind an FD", BAD), key("Behind inflation", grey=True)],
}
risk = chart("q2_mix_risk")
r5 = [r for r in risk if r["horizon"] == 5]
FIGS["q1_mix"] = {
    "title": f"Over five years, a 60/20/20 SIP ended behind an FD in {p('q2_mix_m602020_5y_below_fd', 1)} of start months; the all-equity SIP in {p('q2_mix_n500_5y_below_fd')}",
    "sub": f"Five-year SIPs started each month from April 2005, by portfolio: share that lost money, ended behind the same money in FDs, or behind inflation. {MIXNOTE}.",
    "read": "One group per portfolio. Mixing in bonds and gold all but removed the five-year risk of losing money or trailing a deposit.",
    "source": SRC_MENU, "job": "comparison", "evidence": "exploratory",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [ser("lost", "Lost money", ink=True), ser("below_fd", "Behind an FD", BAD), ser("below_inflation", "Behind inflation", grey=True)]},
    "data": {"categories": [r["portfolio"] for r in r5], "series": {c: [r100(r[c], 1) for r in r5] for c in ("lost", "below_fd", "below_inflation")}},
    "legend": [key("Lost money", ink=True), key("Behind an FD", BAD), key("Behind inflation", grey=True)],
}
fan = [r for r in chart("q2_fan") if r["horizon"] >= 3]
FIGS["q2"] = {
    "title": f"The typical ten-year Nifty 500 SIP returned {p('q2_n500_10y_p50', 1)} a year, but one in twenty returned under {p('q2_n500_10y_p5', 1)}",
    "sub": f"Spread of SIP returns (XIRR) across start months since 1995, by how long the SIP ran. {FULL}. One-year results are left off: annualising a few months' money stretches them across hundreds of points.",
    "read": "For each horizon, the dot is the middle result, the thick bar the middle half and the thin line the 5th to 95th percentile. The spread narrows sharply with time, but never closes.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "outcomes", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "p50", "label": "Median", "slot": COL["Nifty 500"]}],
             "outcome": {"mid": "p50", "lo": "p5", "hi": "p95"}},
    "data": {"categories": [H[r["horizon"]] for r in fan], "series": {c: [r100(r[c]) for r in fan] for c in ("p5", "p25", "p50", "p75", "p95")}},
}
mrows = [r for r in chart("q2_mix_fan") if r["horizon"] in (5, 10)]
FIGS["q2_mix"] = {
    "title": f"Over ten years, 60/20/20 returned a median {p('q2_mix_m602020_10y_p50', 1)} against {p('q2_mix_n500_10y_p50', 1)} for the Nifty 500, with a firmer floor: {p('q2_mix_m602020_10y_worst', 1)} at worst against {p('q2_mix_n500_10y_worst', 1)}",
    "sub": f"SIP returns (XIRR) for each portfolio over the same start months from April 2005, at five and ten years. {MIXNOTE}.",
    "read": "Each row: dot is the median, thick bar the middle half, thin line the 5th to 95th percentile. The mixes' rows are shorter: less upside, much less downside.",
    "source": SRC_MENU, "job": "comparison", "evidence": "exploratory",
    "spec": {"kind": "outcomes", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "p50", "label": "Median", "tone": "ink"}],
             "outcome": {"mid": "p50", "lo": "p5", "hi": "p95", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": [f"{r['portfolio']}, {H[r['horizon']]}" for r in mrows],
             "series": {**{c: [r100(r[c]) for r in mrows] for c in ("p5", "p25", "p50", "p75", "p95")}, "n": [r["n"] for r in mrows]}},
}
vals = chart("q2_values")
FIGS["q2_rupees"] = {
    "title": f"₹10,000 a month for 20 years (₹24 lakh in all) became {crore(v('q2_n500_20y_value_p50'))} in the typical Nifty 500 SIP",
    "sub": "What the SIP was worth at the end, for a bad start (5th percentile) and the typical start, beside the money put in. Rupees of the day.",
    "read": "Grey is what went in. The gap between the two coloured bars is how much the ending depended on when you happened to start.",
    "source": SRC, "job": "case", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [ser("invested", "Money put in", grey=True), ser("p5", "Bad start", BAD), ser("p50", "Typical", COL["Nifty 500"])]},
    "data": {"categories": [H[r["horizon"]] for r in vals], "series": {c: [round(r[c]) for r in vals] for c in ("invested", "p5", "p50")}},
    "legend": [key("Money put in", grey=True), key("Bad start", BAD), key("Typical", COL["Nifty 500"])],
}
rr = chart("q3_real_nominal")
FIGS["q3"] = {
    "title": f"After inflation, the typical ten-year Nifty 500 SIP returned {p('q3_n500_10y_real_p50', 1)} a year, not {p('q2_n500_10y_p50', 1)}",
    "sub": "Median SIP return by horizon, before and after inflation (each instalment and the final value deflated by all-India CPI to the start month).",
    "read": "Grey is the return on a statement; blue is what it bought. The gap, about six points a year, is roughly the inflation rate.",
    "source": SRC + "; CPI (MoSPI)", "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [ser("nominal_p50", "Before inflation", grey=True), ser("real_p50", "After inflation", COL["Nifty 500"])]},
    "data": {"categories": [H[r["horizon"]] for r in rr], "series": {c: [r100(r[c]) for r in rr] for c in ("nominal_p50", "real_p50")}},
    "legend": [key("Before inflation", grey=True), key("After inflation", COL["Nifty 500"])],
}
FIGS["q3_fd"] = {
    "title": f"Since {R['labels']['q3_n500_from']}, an FD after tax lost {pts('q3_n500_fd_real')} a year to inflation; the Nifty 500 gained {p('q3_n500_index_real', 1)} a year after it",
    "sub": "Annual return over the whole period, before and after inflation: the Nifty 500 total-return index, and a fixed deposit rolled at banks' 1-3 year rate with interest taxed at 30% plus cess.",
    "read": "Each pair is one investment. The FD's after-inflation bar is below zero.",
    "source": SRC + "; CPI (MoSPI)", "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "compact", "fmt": "pct", "digits": 1,
             "series": [ser("nominal", "Before inflation", grey=True), ser("real", "After inflation", COL["Nifty 500"])]},
    "data": {"categories": ["Nifty 500 (with dividends)", "Fixed deposit (after tax)"],
             "series": {"nominal": [r100(v("q3_n500_index_nominal")), r100(v("q3_n500_fd_nominal"))], "real": [r100(v("q3_n500_index_real")), r100(v("q3_n500_fd_real"))]}},
    "legend": [key("Before inflation", grey=True), key("After inflation", COL["Nifty 500"])],
}

# ================================================================= Chapter 2

a4 = [r for r in chart("q4_assets") if r["horizon"] == 10]
NAMES = {"Nifty 500": "Nifty 500", "Nifty 50": "Nifty 50", "Nifty Midcap 150": "Midcap 150", "Nifty Smallcap 250": "Smallcap 250",
         "Gold": "Gold", "G-sec 5-year": "Government bonds"}
pts_ = [(NAMES[r["asset"]], r["median"], r["p5"]) for r in a4] + [("60/20/20", v("q2_mix_m602020_10y_p50"), v("q2_mix_m602020_10y_p5")),
                                                                  ("Equal thirds", v("q2_mix_mthirds_10y_p50"), v("q2_mix_mthirds_10y_p5"))]
FIGS["q4"] = {
    "title": "What a SIP bought set both its typical return and its bad case; the mixes sat in between",
    "sub": "Ten-year SIPs started each month from April 2005: median return (up) against 5th-percentile return (across). Mid- and small-cap history before 2016 is back-calculated by NSE.",
    "read": "Up is better on average; right is better in a bad decade. The two mixes sit between equities and the safe assets, nearer the equities on return and well to the right of small caps.",
    "source": SRC_MENU, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1, "x": {"col": "p5", "label": "Bad case (5th percentile), % a year", "fmt": "pct", "digits": 1},
             "y": {"label": "Median, % a year"}, "series": [{"col": "median", "label": "Median", "tone": "ink"}], "pin": [n for n, _, _ in pts_]},
    "data": {"categories": [n for n, _, _ in pts_], "series": {"median": [r100(m) for _, m, _ in pts_], "p5": [r100(b) for _, _, b in pts_]}},
}
pain = [(NAMES[r["asset"]], r["deepest_worst"], r["longest_max"]) for r in a4] + \
       [("60/20/20", v("q2_mix_m602020_10y_deepest_worst"), v("q2_mix_m602020_10y_longest_red_max")),
        ("Equal thirds", v("q2_mix_mthirds_10y_deepest_worst"), v("q2_mix_mthirds_10y_longest_red_max"))]
deep_sorted = sorted(pain, key=lambda t: t[1])
FIGS["q4_pain"] = {
    "title": f"Small caps fell deepest below the money put in ({p('q4_smallcap250_10y_deepest_worst')}); a 60/20/20 mix fell {p('q2_mix_m602020_10y_deepest_worst')}, equal thirds {p('q2_mix_mthirds_10y_deepest_worst')}",
    "sub": "Ten-year SIPs from April 2005: the deepest the month-end value fell below the money put in, in the worst start month, by what the SIP bought.",
    "read": "Each bar is the worst moment a SIP holder had to sit through, as a share of the money put in so far. The mixes cut it to between a half and a quarter of the all-equity fall.",
    "source": SRC_MENU, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "series": [ser("deep", "Deepest fall below money put in", BAD)]},
    "data": {"categories": [n for n, _, _ in deep_sorted], "series": {"deep": [r100(d) for _, d, _ in deep_sorted]}},
}
long_sorted = sorted(pain, key=lambda t: -t[2])
FIGS["q4_long"] = {
    "title": f"The mixes also recovered sooner: the longest stretch below the money put in was {v('q2_mix_n500_10y_longest_red_max')} months for the Nifty 500 and {v('q2_mix_mthirds_10y_longest_red_max')} for equal thirds",
    "sub": "Ten-year SIPs from April 2005: the longest unbroken run of month-ends below the money put in, in the worst start month.",
    "read": "Each bar is the longest wait, in months, before a SIP in that asset was back above what had gone in.",
    "source": SRC_MENU, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "int", "digits": 0, "unit": "months", "series": [ser("long", "Longest stretch below money put in", ink=True)]},
    "data": {"categories": [n for n, _, _ in long_sorted], "series": {"long": [int(l) for _, _, l in long_sorted]}},
}
pp = [r for r in chart("q5_price_of_protection") if r["mix"] == "60/20/20"]
FIGS["q5"] = {
    "title": f"Over ten years, a 60/20/20 SIP gave up {lakh(v('q5_m602020_10y_given_up_median'))} in the typical case to gain {lakh(v('q5_m602020_10y_gained_p5'))} in a bad one",
    "sub": "60/20/20 against an all-Nifty 500 SIP over the same months (starts from April 2005): the typical final value given up, and the bad-case (5th percentile) final value gained.",
    "read": "For each horizon, compare the bars. Where the green bar (gained in a bad case) is longer, diversifying paid for itself; where the grey bar is longer, it cost more than it protected.",
    "source": SRC_MENU, "job": "answer", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [ser("given", "Given up in the typical case", grey=True), ser("gained", "Gained in a bad case", COL["60/20/20"])]},
    "data": {"categories": [H[r["horizon"]] for r in pp], "series": {"given": [round(r["given_up_median"]) for r in pp], "gained": [round(r["gained_p5"]) for r in pp]}},
    "legend": [key("Given up, typical case", grey=True), key("Gained, bad case", COL["60/20/20"])],
}
q6 = [r for r in chart("q6_paired") if r["mix"] == "60/20/20" and r["horizon"] == 10]
FIGS["q6"] = {
    "title": f"Rebalancing a 60/20/20 SIP each April added a median {pts('q6_m602020_10y_diff_p50')} a year, in at least nine in ten start months",
    "sub": "Ten-year SIPs from April 2005: return rebalanced to 60/20/20 each April minus return with instalments split 60/20/20 but never rebalanced, by start month.",
    "read": "Each bar is one start month. Above zero, rebalancing helped.",
    "source": SRC_MENU, "job": "answer", "evidence": "tested",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 1, "period": "month", "range": False,
             "series": [ser("diff", "Rebalanced minus never", COL["60/20/20"])]},
    "data": {"dates": [r["start"] + "-01" for r in q6], "series": {"diff": [r100(r["diff"], 2) for r in q6]}},
}

# ================================================================= Chapter 3

q7 = chart("q7_ranges")
FIGS["q7"] = {
    "title": f"In rupees, longer SIPs did not converge: at 20 years the final value ran from {v('q7_n500_20y_multiple_p5'):.1f} to {v('q7_n500_20y_multiple_p95'):.1f} times the money put in",
    "sub": "Nifty 500 SIPs since 1995: final value as a multiple of the money put in, by horizon (median, and the 5th to 95th percentile).",
    "read": "The yearly return steadies with time, but compounding turns a small difference in yearly return into a large one in rupees, so the lines stay long.",
    "source": SRC, "job": "mechanism", "evidence": "measured",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "x", "digits": 1, "series": [{"col": "m", "label": "Median multiple", "slot": COL["Nifty 500"]}],
             "outcome": {"mid": "m", "lo": "l", "hi": "h"}},
    "data": {"categories": [H[r["horizon"]] for r in q7], "series": {"m": [round(r["mult_p50"], 2) for r in q7], "l": [round(r["mult_p5"], 2) for r in q7],
                                                                    "h": [round(r["mult_p95"], 2) for r in q7]}},
}
q8 = chart("q8_by_start_year")
FIGS["q8"] = {
    "title": f"The start year mattered enormously: the median ten-year return ranged from {p('q8_n500_10y_worst_year_median', 1)} to {p('q8_n500_10y_best_year_median', 1)}",
    "sub": "Median ten-year Nifty 500 SIP return for start months in each calendar year. Years before 1999 rest on a probably back-calculated index.",
    "read": "Each bar is one start year. Nobody could have known in advance which bar they were standing on.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "tall", "fmt": "pct", "digits": 1, "series": [ser("median", "Median ten-year return", COL["Nifty 500"])]},
    "data": {"categories": [str(r["year"]) for r in q8], "series": {"median": [r100(r["median"]) for r in q8]}},
}
b8 = chart("q8_bands")
FIGS["q8_bands"] = {
    "title": f"Starting near a market high made little difference: {p('q8_n500_10y_near_high_p50', 1)} against {p('q8_n500_10y_far_p50', 1)} for starts more than 10% below it",
    "sub": "Ten-year Nifty 500 SIP returns by how far the market was below its previous high in the start month.",
    "read": "Each row: median (dot), 5th to 95th percentile (line). The rows overlap almost completely.",
    "source": SRC, "job": "conditioning", "evidence": "measured",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "pct", "digits": 1, "series": [{"col": "median", "label": "Median", "slot": COL["Nifty 500"]}],
             "outcome": {"mid": "median", "lo": "p5", "hi": "p95", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": [r["band"].replace("-", " to ") for r in b8], "series": {"median": [r100(r["median"]) for r in b8], "p5": [r100(r["p5"]) for r in b8],
                                                                                    "p95": [r100(r["p95"]) for r in b8], "n": [r["n"] for r in b8]}},
}
q9y = chart("q9_value_by_year")
FIGS["q9_years"] = {
    "title": f"In a 15-year SIP, the first five years' instalments made up {p('q9_n500_15y_first5_share_p50')} of the final value; the last five, {p('q9_n500_15y_last5_share_p50')}",
    "sub": "Share of a 15-year Nifty 500 SIP's final value that came from each year's instalments (median across start months since 1995).",
    "read": "Each bar is one year of instalments. Early money had the longest to compound, so it did most of the work.",
    "source": SRC, "job": "mechanism", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "series": [ser("share", "Share of final value", COL["Nifty 500"])]},
    "data": {"categories": [f"Year {r['year']}" for r in q9y], "series": {"share": [r100(r["share"]) for r in q9y]}},
}
FIGS["q9_glide"] = {
    "title": f"Moving to FDs over the last three years ended ahead in only {p('q9_g36_ahead')} of 15-year SIPs, and lowered even the bad case",
    "sub": "15-year Nifty 500 SIPs since 1995: final value if the SIP stayed invested, against switching the corpus to FDs in 36 (or 12) equal monthly steps and paying the last instalments into FDs. Equity before tax; FD interest taxed.",
    "read": "For each choice, the terracotta bar is the bad case (5th percentile) and the blue bar the typical one. Staying put was higher on both.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "div": 100000,
             "series": [ser("p5", "Bad case (5th percentile)", BAD), ser("p50", "Typical", COL["Nifty 500"])]},
    "data": {"categories": ["Stayed invested", "Switched over the last 12 months", "Switched over the last 36 months"],
             "series": {"p5": [round(v(k)) for k in ("q9_stay_p5", "q9_g12_p5", "q9_g36_p5")], "p50": [round(v(k)) for k in ("q9_stay_p50", "q9_g12_p50", "q9_g36_p50")]}},
    "legend": [key("Bad case", BAD), key("Typical", COL["Nifty 500"])],
}
need = [r for r in chart("q10_need") if r["asset"] == "Nifty 500"]
FIGS["q10"] = {
    "title": f"To reach ₹1 crore in 15 years nineteen times in twenty, the Nifty 500 record says {rs(v('q10_n500_15y_need_95'))} a month; a 12% calculator says {rs(v('q10_calc12_15y_amount'))}",
    "sub": "Monthly amount that would have reached ₹1 crore (rupees of the day) in half, four in five and nineteen in twenty of the start months since 1995, by horizon.",
    "read": "Each group is a horizon. The more certain you want to be, the longer the bar; the gaps between the bars are the price of certainty.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "num", "digits": 0, "unit": "₹ a month",
             "series": [ser("c50", "Half the time", grey=True), ser("c80", "Four times in five", BAD), ser("c95", "Nineteen in twenty", COL["Nifty 500"])]},
    "data": {"categories": [H[y] for y in (10, 15, 20)],
             "series": {f"c{c}": [round([r["flat"] for r in need if r["horizon"] == y and round(r["confidence"] * 100) == c][0]) for y in (10, 15, 20)] for c in (50, 80, 95)}},
    "legend": [key("Half the time", grey=True), key("Four times in five", BAD), key("Nineteen in twenty", COL["Nifty 500"])],
}

# ================================================================= Chapter 4

FIGS["q11"] = {
    "title": f"With a lump sum in hand, investing it at once beat a 12-month STP in {p('q11_lump_beat_stp12')} of start months",
    "sub": "₹12 lakh into the Nifty 500 at once, against moving it in from an FD over 12 or 36 months, valued after 10 years; and, for someone earning monthly, a monthly SIP against saving in an FD and investing the pot each April.",
    "read": "Each bar is the share of start months since 1995 in which the first choice ended ahead. Half would be a coin toss.",
    "source": SRC, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "domain": [0, 100], "series": [ser("won", "First choice ended ahead", COL["Nifty 500"])]},
    "data": {"categories": ["Lump sum vs 12-month STP", "Lump sum vs 36-month STP", "Monthly SIP vs FD, invested each April"],
             "series": {"won": [r100(v("q11_lump_beat_stp12")), r100(v("q11_lump_beat_stp36")), r100(v("q11_sip_beat_fd_april"))]}},
}
lev = {r["lever"]: r for r in chart("q12_levers")}
LEV = [("best_date", "Best SIP date instead of the 1st"), ("weekly", "Weekly instead of monthly"), ("stepup", "10% yearly step-up"),
       ("pe_double", "Double up when P/E is cheap"), ("wait_fall", "Save in FD, invest after 20% falls"),
       ("cost_1pct", "1% a year more in costs"), ("pause_lab", "Pause in a 20% fall (resume near the top)"), ("pause_fall", "Pause in a 20% fall (resume at the top)")]
FIGS["q12"] = {
    "title": f"Every SIP trick moved the ten-year return by less than the choice of asset ({pts('q12_asset_gap')}) or start year",
    "sub": "Median change in ten-year Nifty 500 SIP return from each change to a plain monthly SIP, with the 10th to 90th percentile across start months (April 2005 on). Paused or waiting money sits in a taxed FD.",
    "read": "Each row is one change; right of zero helped, left hurt. The two rows at the bottom are the spread between assets and between start years: every trick is a sliver beside them.",
    "source": SRC, "job": "answer", "evidence": "measured",
    "spec": {"kind": "forest", "room": "tall", "fmt": "pct", "digits": 1, "series": [{"col": "m", "label": "Median effect", "slot": COL["Nifty 500"]}],
             "ci": {"mid": "m", "lo": "l", "hi": "h", "ref": 0, "label": "10th to 90th percentile"}},
    "data": {"categories": [n for _, n in LEV] + ["Spread between assets (medians)", "Spread between start years (medians)"],
             "series": {"m": [r100(lev[k]["p50"], 2) for k, _ in LEV] + [r100(v("q12_asset_gap")), r100(v("q12_start_year_gap"))],
                        "l": [r100(lev[k]["p10"], 2) for k, _ in LEV] + [None, None],
                        "h": [r100(lev[k]["p90"], 2) for k, _ in LEV] + [None, None]}},
}
t13 = chart("q13_tax_clock")
AGE = {12: "1 year", 18: "18 months", 24: "2 years", 36: "3 years", 60: "5 years"}
FIGS["q13"] = {
    "title": f"Cash in a SIP after two years and {p('q13_24m_st_units')} of its units are still short-term, though they hold only {p('q13_24m_st_gain_share_p50')} of the gains",
    "sub": "Nifty 500 SIPs cashed in fully at each age: share of units held under a year (taxed as short-term) and their share of the gain (median, SIPs with a gain).",
    "read": "Each instalment has its own one-year clock. Grey is the share of units still under a year old; blue is their share of the gain, smaller because new units have had little time to grow.",
    "source": SRC, "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0,
             "series": [ser("units", "Short-term units", grey=True), ser("gains", "Short-term share of gains", COL["Nifty 500"])]},
    "data": {"categories": [AGE[r["age"]] for r in t13], "series": {"units": [r100(r["st_units"]) for r in t13], "gains": [r100(r["st_gain_share"]) for r in t13]}},
    "legend": [key("Short-term units", grey=True), key("Short-term share of gains", COL["Nifty 500"])],
}
FIGS["q13_cost"] = {
    "title": f"Tax and a 1% exit load took {p('q13_12m_cost_p50', 1)} of a one-year SIP's value, and {p('q13_36m_cost_p50', 1)} at three years",
    "sub": "Median tax plus exit load on cashing in a ₹10,000-a-month Nifty 500 SIP, as a share of its value, against the tax on the same money invested as a lump sum at the start and held as long.",
    "read": "Grey is the lump sum, blue the SIP. The SIP's cost falls as more units pass the one-year mark, then rises again as long-term gains outgrow the ₹1.25 lakh exemption.",
    "source": SRC, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [ser("lump", "Lump sum", grey=True), ser("sip", "SIP (tax + 1% load)", COL["Nifty 500"])]},
    "data": {"categories": [AGE[r["age"]] for r in t13], "series": {"lump": [r100(r["lump_cost"], 2) for r in t13], "sip": [r100(r["cost"], 2) for r in t13]}},
    "legend": [key("Lump sum", grey=True), key("SIP", COL["Nifty 500"])],
}
e14 = chart("q14_edge")
indep = [r["start"] for r in e14 if r["start"] in ("1995-01", "2005-01")]
FIGS["q14"] = {
    "title": f"Volatility did not reliably help: the SIP's edge over the index tracked volatility only weakly (rank correlation {v('q14_n500_corr_vol'):.2f})",
    "sub": "Every ten-year Nifty 500 window since 1995: the SIP's return minus the index's own return over the same dates, against how volatile the window was. Neighbouring windows overlap; the two non-overlapping ones (January 1995 and January 2005 starts) are named.",
    "read": "Each dot is a start month. If choppy markets helped SIPs, the dots would climb steeply to the right. They drift up only slightly, and even that vanished for SIPs started after 2005.",
    "source": SRC, "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1,
             "x": {"col": "vol", "label": "Volatility of the window, % a year", "fmt": "pct", "digits": 0},
             "y": {"label": "SIP minus index, points a year"}, "series": [{"col": "edge", "label": "SIP edge", "slot": COL["Nifty 500"]}], "pin": indep},
    "data": {"categories": [r["start"] for r in e14], "series": {"edge": [r100(r["edge"], 2) for r in e14], "vol": [r100(r["vol"], 1) for r in e14]}},
}
sm, ch = chart("q14_illus_smooth"), chart("q14_illus_choppy")
FIGS["q14_illus"] = {
    "title": f"Two made-up markets from 100 to 200 in ten years: the choppy one gave a SIP {p('q14_illus_choppy_xirr', 2)} a year, the smooth one {p('q14_illus_smooth_xirr', 2)}",
    "sub": "An illustration, not data: the same start and end, one path smooth and one swinging 30% either way.",
    "read": "The SIP bought more units in the choppy path's dips, but more expensive ones at its peaks. Net, the difference is tiny.",
    "source": "tipsheet illustration", "job": "case", "evidence": "illustration",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "period": "month", "range": False,
             "series": [ser("smooth", "Smooth", grey=True), ser("choppy", "Choppy", COL["Nifty 500"])]},
    "data": {"dates": [r["month"] + "-28" for r in sm], "series": {"smooth": [round(r["level"], 1) for r in sm], "choppy": [round(r["level"], 1) for r in ch]}},
    "legend": [key("Smooth", grey=True, shape="line"), key("Choppy", COL["Nifty 500"], shape="line")],
}

# ================================================================= Chapter 5

b15 = chart("q15_by_start")
FIGS["q15"] = {
    "title": f"{p('q15_n500_ever_red')} of Nifty 500 SIPs since 1995 were below the money put in at some month-end; the deepest fall was {p('q15_n500_deepest')}",
    "sub": "For SIPs started each month and followed to today: the deepest the month-end value fell below the money put in.",
    "read": "Each bar is one start month. The clusters are the crashes that began in 2000, 2008 and 2020; almost every SIP met at least one.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "pct", "digits": 0, "period": "month", "range": False,
             "series": [ser("deep", "Deepest fall below money put in", BAD)]},
    "data": {"dates": [r["start"] + "-01" for r in b15], "series": {"deep": [r100(r["deepest"]) for r in b15]}},
}
FIGS["q15_long"] = {
    "title": f"The longest stretch below the money put in was {v('q15_n500_longest')} months, for a SIP started in {R['labels']['q15_n500_longest_start']}",
    "sub": "For Nifty 500 SIPs started each month and followed to today: the longest unbroken run of month-ends below the money put in.",
    "read": "Each bar is one start month. Most runs were short; the starts around 2000 waited longest.",
    "source": SRC, "job": "spread", "evidence": "measured",
    "spec": {"kind": "bars", "room": "standard", "fmt": "int", "digits": 0, "unit": "months", "period": "month", "range": False,
             "series": [ser("longest", "Longest run below money put in", ink=True)]},
    "data": {"dates": [r["start"] + "-01" for r in b15], "series": {"longest": [r["longest"] for r in b15]}},
}
under = [(NAMES[r["asset"]], r["ever_red"]) for r in chart("q15_menu")] + [(r["asset"], r["ever_red"]) for r in chart("q15_mix")]
under.sort(key=lambda t: -t[1])
FIGS["q15_menu"] = {
    "title": f"Nine in ten 60/20/20 SIPs also went under water at some point ({p('q15_mix_m602020_ever_red')}), but never by more than {p('q15_mix_m602020_deepest')}",
    "sub": "SIPs started each month from April 2005 and followed to today: share that were below the money put in at some month-end, by portfolio.",
    "read": "Each bar is a portfolio. Going under water was near-universal for anything holding equity; the difference was how far and for how long (Chapter 2).",
    "source": SRC_MENU, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "domain": [0, 100], "series": [ser("ever", "Ever below the money put in", BAD)]},
    "data": {"categories": [n for n, _ in under], "series": {"ever": [r100(e) for _, e in under]}},
}
o16 = chart("q16_outcomes")
n500 = [r for r in o16 if r["asset"] == "Nifty 500" and r["group"] in ("0-10% below", "10-20% below", "over 20% below", "not red")]
FIGS["q16"] = {
    "title": f"Nifty 500 SIPs in the red after a year went on to a median {p('q16_n500_red_p50', 1)} a year over ten years, against {p('q16_n500_rest_p50', 1)} for the rest",
    "sub": "Ten-year Nifty 500 SIP returns since 1995, by how far the SIP was below the money put in at 12 months.",
    "read": "Each row: dot is the median, thick bar the middle half, thin line the 5th to 95th percentile. The counts are start months; the separate episodes behind them are far fewer.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "pct", "digits": 1, "series": [{"col": "p50", "label": "Median", "slot": COL["Nifty 500"]}],
             "outcome": {"mid": "p50", "lo": "p5", "hi": "p95", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": ["Under 10% below at 12 months", "10 to 20% below", "More than 20% below", "Not in the red"],
             "series": {c: [r100(r[c]) if c != "n" else r[c] for r in n500] for c in ("p5", "p25", "p50", "p75", "p95", "n")}},
}
mx16 = {r["asset"]: r for r in chart("q16_mix")}
cats16 = ["Nifty 500", "Nifty 50", "Midcap 150", "Smallcap 250", "60/20/20", "Equal thirds"]
red16 = [v(f"q16_{k}_red_p50") for k in ("n500", "n50", "mid150", "small250")] + [mx16["60/20/20"]["red"], mx16["Equal thirds"]["red"]]
rest16 = [v(f"q16_{k}_rest_p50") for k in ("n500", "n50", "mid150", "small250")] + [mx16["60/20/20"]["rest"], mx16["Equal thirds"]["rest"]]
FIGS["q16_indices"] = {
    "title": "The bonus for a bad start was an equity effect: absent for mid caps, and reversed for the mixes",
    "sub": "Median ten-year SIP return for SIPs in the red at 12 months against the rest (Nifty 500 from 1995, Nifty 50 from 1999, mid and small caps and the mixes from 2005). The two mixes were added after the results, at the editor's request; the four indices were planned.",
    "read": "For each portfolio, blue is the red-at-a-year group and grey the rest. Where blue is longer, a bad start was followed by a better ending.",
    "source": SRC_MENU, "job": "conditioning", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1,
             "series": [ser("rest", "Not in the red at a year", grey=True), ser("red", "In the red at a year", COL["Nifty 500"])]},
    "data": {"categories": cats16, "series": {"rest": [r100(x) for x in rest16], "red": [r100(x) for x in red16]}},
    "legend": [key("Not in the red", grey=True), key("In the red at a year", COL["Nifty 500"])],
}
c08 = chart("q16_case2008")
FIGS["q16_case"] = {
    "title": f"A Nifty 500 SIP started in January 2008 fell {p('q16_case2008_deepest')} below the money put in, then returned {p('q16_case2008_xirr_10y', 1)} a year over ten years",
    "sub": "₹10,000 a month from January 2008, month by month to today: money put in and what it was worth.",
    "read": "Grey is the money put in, blue the statement value. Blue spent more than a year below grey, then never looked back.",
    "source": SRC, "job": "case", "evidence": "illustration",
    "spec": {"kind": "line", "room": "tall", "fmt": "num", "digits": 1, "unit": "₹ lakh, log scale", "div": 100000, "log": True, "period": "month", "range": False,
             "series": [ser("value", "What it was worth", COL["Nifty 500"]), ser("invested", "Money put in", grey=True)]},
    "data": {"dates": [r["month"] + "-28" for r in c08], "series": {"value": [round(r["value"]) for r in c08], "invested": [round(r["invested"]) for r in c08]}},
    "legend": [key("What it was worth", COL["Nifty 500"], shape="line"), key("Money put in", grey=True, shape="line")],
}


def _q(x, q_):
    """A quantile of rupee amounts, in lakh."""
    return round(float(np.quantile(np.asarray(x, float), q_)) / 1e5, 2)


g17 = [r for r in chart("q17_gaps") if r["asset"] == "Nifty 500" and r["age"] == 12]
FIGS["q17"] = {
    "title": f"For Nifty 500 SIPs in the red at a year, keeping going beat stopping in {p('q17_n500_m12_A_beat_B')} of cases; switching to FDs cost a median {lakh(v('q17_n500_m12_gap_C_p50'))}",
    "sub": "Over the same ten years and the same ₹12 lakh of savings: keeping going, against stopping and holding (new money to FDs), selling and switching to FDs, or pausing until back in the black. Paired gap in final value.",
    "read": "Each row is one alternative: how many rupees keeping going ended ahead by (dot: median; line: 5th to 95th percentile). Every row is right of zero.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "outcomes", "room": "standard", "fmt": "num", "digits": 1, "unit": "₹ lakh", "series": [{"col": "m", "label": "Median gap", "slot": COL["Nifty 500"]}],
             "outcome": {"mid": "m", "lo": "l", "hi": "h", "n": "n", "nLabel": "start months", "minN": 0}},
    "data": {"categories": ["Against stopping and holding", "Against selling and switching to FDs", "Against pausing until back in the black"],
             "series": {"m": [_q([r["gap"] for r in g17 if r["path"] == s], .5) for s in "BCD"],
                        "l": [_q([r["gap"] for r in g17 if r["path"] == s], .05) for s in "BCD"],
                        "h": [_q([r["gap"] for r in g17 if r["path"] == s], .95) for s in "BCD"],
                        "n": [sum(1 for r in g17 if r["path"] == s) for s in "BCD"]}},
}
FIGS["q17_indices"] = {
    "title": f"Small caps were the one place stopping sometimes paid: keeping going won {p('q17_small250_m12_A_beat_B')} of the time",
    "sub": "SIPs in the red at 12 months, by index: share of start months in which keeping going beat stopping and holding, selling to FDs, and pausing.",
    "read": "Each group is an index; a full bar means keeping going won every time.",
    "source": SRC, "job": "robustness", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 0, "domain": [0, 100],
             "series": [ser("B", "vs stop and hold", ink=True), ser("C", "vs sell to FDs", BAD), ser("D", "vs pause", grey=True)]},
    "data": {"categories": ["Nifty 500", "Nifty 50", "Midcap 150", "Smallcap 250"],
             "series": {s: [r100(v(f"q17_{k}_m12_A_beat_{s}")) for k in ("n500", "n50", "mid150", "small250")] for s in "BCD"}},
    "legend": [key("vs stop and hold", ink=True), key("vs sell to FDs", BAD), key("vs pause", grey=True)],
}
c18 = [r for r in chart("q18_corr_by_age") if r["age"] % 6 == 0]
FIGS["q18"] = {
    "title": f"A SIP's return in its first year said little about its ending, and if anything pointed the wrong way (correlation {v('q18_n500_10y_corr_12m'):.2f})",
    "sub": "Nifty 500 SIPs since 1995: rank correlation between the return shown at each age and the final ten-year return, every six months.",
    "read": "Above zero, a good early number meant a good ending; below zero, the opposite. It stays near zero for years and first passes 0.5 at 99 months.",
    "source": SRC, "job": "answer", "evidence": "tested",
    "spec": {"kind": "hbars", "room": "tall", "fmt": "num", "digits": 2, "sign": True, "series": [ser("c", "Correlation with the ending", COL["Nifty 500"])]},
    "data": {"categories": [f"{r['age']} months" for r in c18], "series": {"c": [round(r["corr"], 2) for r in c18]}},
}

# ================================================================= Chapter 6

s19 = chart("q19_scatter")
FIGS["q19"] = {
    "title": f"Among Nifty 50 SIPs in the red at a year, cheap and dear markets ended about the same: {p('q19_red_cheap_p50', 1)} against {p('q19_red_dear_p50', 1)}",
    "sub": "Nifty 50 SIPs since 1999: the index's trailing P/E at the SIP's 12-month mark against its ten-year return. SIPs in the red at 12 months are coloured. Neighbouring start months overlap heavily; this is about two decades of history.",
    "read": "Each dot is a start month. If the bad-start bonus came only from cheap prices, the coloured dots on the left would sit well above those on the right.",
    "source": SRC + "; NSE P/E", "job": "mechanism", "evidence": "tested",
    "spec": {"kind": "scatter", "room": "tall", "fmt": "pct", "digits": 1, "labels": "none",
             "x": {"col": "pe12", "label": "Nifty 50 P/E at 12 months", "fmt": "num", "digits": 0},
             "y": {"label": "Ten-year SIP return, % a year"}, "series": [{"col": "xirr", "label": "Ten-year return", "slot": COL["Nifty 50"]}],
             "pin": [r["start"] for r in s19 if r["red"]]},
    "data": {"categories": [r["start"] for r in s19], "series": {"xirr": [r100(r["xirr"]) for r in s19], "pe12": [round(r["pe12"], 1) for r in s19]}},
}
FIGS["q20"] = {
    "title": f"Investors' SIP money earned {p('q20_n500_industry', 1)} a year, against {p('q20_n500_trend', 1)} for money growing at the same trend: no sign of bad timing",
    "sub": f"AMFI's monthly SIP inflows, {R['labels']['q20_from']} to {R['labels']['q20_to']}, as if invested in the Nifty 500 total-return index, against a steady SIP, a SIP growing at the inflows' own trend ({p('q20_trend_growth')} a year), and the index itself. Before tax and costs.",
    "read": "A steady SIP is the wrong yardstick: inflows grew every year, so more money naturally went in later, at higher prices. Against the fair yardstick (the second bar) the gap all but disappears.",
    "source": SRC_AMFI, "job": "comparison", "evidence": "measured",
    "spec": {"kind": "hbars", "room": "standard", "fmt": "pct", "digits": 1, "series": [ser("x", "Return a year", COL["Nifty 500"])]},
    "data": {"categories": ["Investors' actual SIP money", "Money growing at its trend", "Steady amounts, same months", "The index itself"],
             "series": {"x": [r100(v(k)) for k in ("q20_n500_industry", "q20_n500_trend", "q20_n500_constant", "q20_n500_index")]}},
}
inf = chart("q20_inflows")
FIGS["q20_inflows"] = {
    "title": f"Monthly SIP inflows grew at about {p('q20_trend_growth')} a year",
    "sub": "AMFI's gross monthly SIP inflows and their log-linear trend.",
    "read": "Blue is each month's inflow; grey the trend it is compared with.",
    "source": SRC_AMFI, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "unit": "₹ crore", "div": 1e7, "period": "month", "range": False,
             "series": [ser("inflow", "Monthly inflow", COL["Nifty 500"]), ser("trend", "Trend", grey=True)]},
    "data": {"dates": [r["month"] + "-28" for r in inf], "series": {"inflow": [round(r["inflow"]) for r in inf], "trend": [round(r["trend"]) for r in inf]}},
    "legend": [key("Monthly inflow", COL["Nifty 500"], shape="line"), key("Trend", grey=True, shape="line")],
}
dd = chart("q21_drawdown")
FIGS["q21"] = {
    "title": f"Falls of 10% or more kept coming after SIP money grew: {v('q21_2016_on_falls')} since 2016, the worst {p('q21_2016_on_worst_depth')}",
    "sub": "Nifty 500 total-return index: how far below its previous peak it was at each month's low, 1995 to today.",
    "read": "The shaded area is the distance below the last high. Deep falls became rarer after 2016, but ten years is too short to say why.",
    "source": SRC, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "area", "room": "standard", "fmt": "pct", "digits": 0, "period": "month", "range": False,
             "series": [ser("dd", "Below the previous peak", BAD)], "events": [{"date": "2016-04-01", "label": "SIP inflows start to climb"}]},
    "data": {"dates": [r["date"] for r in dd], "series": {"dd": [r100(r["dd"]) for r in dd]}},
}
lf = chart("q22_life")
FIGS["q22"] = {
    "title": f"At the current rate of closures, the average SIP account lasts about {v('q22_life_latest'):.1f} years",
    "sub": "Open SIP accounts divided by accounts closed over the previous 12 months: a rough average life. The shaded months are AMFI's January–April 2025 clean-up of dormant accounts.",
    "read": "Each point is a rough measure of how long a SIP account lasts, given how fast accounts were closing that year. It has never been above five years.",
    "source": SRC_AMFI, "job": "answer", "evidence": "tested",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 1, "unit": "years", "period": "month", "range": False,
             "series": [ser("life", "Implied average life", COL["Nifty 500"])],
             "events": [{"date": "2025-01-01", "to": "2025-04-30", "label": "Clean-up"}]},
    "data": {"dates": [r["month"] + "-28" for r in lf], "series": {"life": [None if r["life"] is None else round(r["life"], 2) for r in lf]}},
}
ac = chart("q22_accounts")
FIGS["q22_accounts"] = {
    "title": f"Closures spiked to {v('q22_stoppage_max'):.1f} times new registrations in {R['labels']['q22_stoppage_max_month']}, during AMFI's clean-up",
    "sub": "New and closed SIP accounts each month (AMFI). Closures include SIPs that reached their end date, failed bank mandates and the 2025 clean-up.",
    "read": "When the terracotta line is above the grey, more accounts closed than opened that month.",
    "source": SRC_AMFI, "job": "caveat", "evidence": "measured",
    "spec": {"kind": "line", "room": "standard", "fmt": "num", "digits": 0, "unit": "lakh accounts", "div": 1e5, "period": "month", "range": False,
             "series": [ser("closed", "Closed", BAD), ser("new", "New", grey=True)]},
    "data": {"dates": [r["month"] + "-28" for r in ac], "series": {"closed": [round(r["closed"]) for r in ac], "new": [round(r["new"]) for r in ac]}},
    "legend": [key("Closed", BAD, shape="line"), key("New", grey=True, shape="line")],
}

for _f in FIGS.values():
    _f["few"] = False            # research pages draw few-series charts grey otherwise; colour follows the portfolio here

if __name__ == "__main__":
    figures.write(__file__, FIGS)
