import os
import json
import math
import numpy as np
import pandas as pd


IN = os.environ["INPUT_DIR"]
OUT = os.environ["OUTPUT_DIR"]
os.makedirs(OUT, exist_ok=True)

ambiguities = []


def ip(name):
    return os.path.join(IN, name)


# ---------------------------------------------------------------- price index
tri = pd.read_parquet(ip("tri_500.parquet"))
tri["d"] = pd.to_datetime(tri["d"])
tri = tri.sort_values("d").reset_index(drop=True)

first_date = tri["d"].iloc[0]
days_from_start = (tri["d"] - first_date).dt.days.values
tri["nav"] = tri["level"].values * (1.0 - 0.002) ** (days_from_start / 365.0)

# ---------------------------------------------------------------- months
last_period = pd.Period("2026-09", freq="M")
tri["ym"] = tri["d"].dt.to_period("M")

sub = tri[tri["ym"] <= last_period].reset_index(drop=True)
gb = sub.groupby("ym", sort=True)
months = list(gb.groups.keys())

nav_first = np.array([sub["nav"].values[gb.indices[m][0]] for m in months], dtype=float)
nav_last = np.array([sub["nav"].values[gb.indices[m][-1]] for m in months], dtype=float)
fdte = [sub["d"].values[gb.indices[m][0]] for m in months]
ldte = [sub["d"].values[gb.indices[m][-1]] for m in months]
fdte = [pd.Timestamp(x) for x in fdte]
ldte = [pd.Timestamp(x) for x in ldte]

N = len(months)
ambiguities.append(
    "Months: used every calendar month with at least one session from Jan-1995 "
    "through Sep-2026 (ordering assumed contiguous); Oct-2026 dropped."
)

u = 10000.0 / nav_first
CU = np.concatenate([[0.0], np.cumsum(u)])


def val(k, j):
    """Statement value at age j (months k .. k+j-1) for a SIP started in month k."""
    return float((CU[k + j] - CU[k]) * nav_last[k + j - 1])


# ---------------------------------------------------------------- deposit rate
dep = pd.read_parquet(ip("deposit_rate_daily.parquet"))
dep["d"] = pd.to_datetime(dep["d"])
dep = dep.sort_values("d").reset_index(drop=True)

rate = dep["rate_pct"].values.astype(float)
f = np.exp(np.log1p(rate / 100.0) / 365.0)
cum = np.concatenate([[1.0], np.cumprod(f)])
dep_idx = {d: i for i, d in enumerate(dep["d"])}


def _ci(d):
    return dep_idx[pd.Timestamp(d)]


def fd_value(deposits, final_date):
    """Value at final_date of a set of (date, amount) deposits, after 31.2% tax
    on accrued interest at each 31 March and at final_date."""
    final_date = pd.Timestamp(final_date)
    deps = [(pd.Timestamp(d), float(a)) for d, a in deposits]
    deps = [x for x in deps if x[1] != 0.0]
    if not deps:
        return 0.0
    start = min(d for d, a in deps)
    if final_date <= start:
        return float(sum(a for d, a in deps))

    tds = [pd.Timestamp(y, 3, 31) for y in range(start.year, final_date.year + 1)]
    tds = [t for t in tds if start < t <= final_date]
    tdset = set(tds)

    evset = sorted(set(tds) | set(d for d, a in deps) | {final_date})

    bal = 0.0
    anchor = 0.0
    dep_since = 0.0
    prev = None
    for ev in evset:
        if prev is not None:
            bal *= cum[_ci(ev)] / cum[_ci(prev)]
        amt = 0.0
        for d, a in deps:
            if d == ev:
                amt += a
        if amt:
            bal += amt
            dep_since += amt
        if ev in tdset or ev == final_date:
            interest = bal - anchor - dep_since
            if interest > 0:
                bal -= 0.312 * interest
            anchor = bal
            dep_since = 0.0
        prev = ev
    return float(bal)


# ---------------------------------------------------------------- xirr
def xirr(dates, amounts):
    t0 = pd.Timestamp(dates[0])
    t = np.array([(pd.Timestamp(d) - t0).days / 365.0 for d in dates], dtype=float)
    a = np.array(amounts, dtype=float)

    def fv(r):
        return float(np.sum(a * (1.0 + r) ** (-t)))

    lo, hi = -0.9999999, 1.0
    flo = fv(lo)
    fhi = fv(hi)
    while flo * fhi > 0 and hi < 1e8:
        hi *= 2.0
        fhi = fv(hi)
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        fm = fv(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def spearman(x, y):
    x = pd.Series(np.asarray(x, dtype=float))
    y = pd.Series(np.asarray(y, dtype=float))
    rx = x.rank().values
    ry = y.rank().values
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = math.sqrt(float(np.sum(rx * rx)) * float(np.sum(ry * ry)))
    if den == 0:
        return 0.0
    return float(np.sum(rx * ry) / den)


facts = {}

H10 = 120
ks10 = list(range(0, N - H10 + 1))


def xirr10(k):
    dates = [fdte[k + i] for i in range(120)] + [ldte[k + 119]]
    amts = [-10000.0] * 120 + [val(k, 120)]
    return xirr(dates, amts)


def xirr_at(k, a):
    dates = [fdte[k + i] for i in range(a)] + [ldte[k + a - 1]]
    amts = [-10000.0] * a + [val(k, a)]
    return xirr(dates, amts)


# ---------------------------------------------------------------- q1
for H, key in ((36, "q1_n500_3y_lost"), (60, "q1_n500_5y_lost"), (120, "q1_n500_10y_lost")):
    ks = list(range(0, N - H + 1))
    vals = np.array([val(k, H) for k in ks])
    facts[key] = float(np.mean(vals < 10000.0 * H))


# ---------------------------------------------------------------- q2
for H, key in ((60, "q1_n500_5y_below_fd"), (120, "q1_n500_10y_below_fd")):
    ks = list(range(0, N - H + 1))
    cnt = 0
    for k in ks:
        deps = [(fdte[k + i], 10000.0) for i in range(H)]
        fdv = fd_value(deps, ldte[k + H - 1])
        if val(k, H) < fdv:
            cnt += 1
    facts[key] = cnt / float(len(ks))


# ---------------------------------------------------------------- q3 / q4 / q5
red12 = []
rest12 = []
for k in ks10:
    if val(k, 12) < 120000.0:
        red12.append(k)
    else:
        rest12.append(k)

facts["q16_n500_red12"] = len(red12) / float(len(ks10))

red_x = [xirr10(k) for k in red12]
rest_x = [xirr10(k) for k in rest12]
facts["q16_n500_red_p50"] = float(np.median(red_x)) if red_x else 0.0
facts["q16_n500_rest_p50"] = float(np.median(rest_x)) if rest_x else 0.0

b20 = [k for k in ks10 if val(k, 12) / 120000.0 - 1.0 < -0.20]
b20_x = [xirr10(k) for k in b20]
facts["q16_n500_b20_p50"] = float(np.median(b20_x)) if b20_x else 0.0

# ---------------------------------------------------------------- q6
ratios = []
for k in red12:
    red_units = 0.0
    cnt = 0
    for i in range(2, 121):
        if val(k, i - 1) < 10000.0 * (i - 1):
            red_units += u[k + i - 1]
            cnt += 1
    all_units = float(CU[k + 120] - CU[k])
    units_share = red_units / all_units if all_units > 0 else 0.0
    money_share = cnt / 120.0
    if money_share > 0:
        ratios.append(units_share / money_share)
facts["q16_n500_units_to_money_ratio_p50"] = float(np.median(ratios)) if ratios else 0.0


# ---------------------------------------------------------------- q7 / q8
def path_A(k):
    return val(k, 120)


def path_B(k):
    units_val = float((CU[k + 12] - CU[k]) * nav_last[k + 119])
    deps = [(fdte[k + i], 10000.0) for i in range(12, 120)]
    fdv = fd_value(deps, ldte[k + 119])
    return units_val + fdv


def path_C(k):
    proceeds = float((CU[k + 12] - CU[k]) * nav_last[k + 11])
    deps = [(ldte[k + 11], proceeds)]
    deps += [(fdte[k + i], 10000.0) for i in range(12, 120)]
    return fd_value(deps, ldte[k + 119])


def path_D(k):
    U = float(CU[k + 12] - CU[k])
    n_units = 12
    fd_deps = []
    paused = True
    for j in range(12, 120):
        if paused:
            if U * nav_last[k + j - 1] >= 10000.0 * n_units:
                paused = False
        if paused:
            fd_deps.append((fdte[k + j], 10000.0))
        else:
            U += 10000.0 / nav_first[k + j]
            n_units += 1
    final_units = U * nav_last[k + 119]
    fdv = fd_value(fd_deps, ldte[k + 119]) if fd_deps else 0.0
    return float(final_units + fdv)


A = []; B = []; C = []; D = []
for k in red12:
    A.append(path_A(k))
    B.append(path_B(k))
    C.append(path_C(k))
    D.append(path_D(k))

n_red = len(red12)
if n_red:
    facts["q17_n500_m12_A_beat_B"] = float(np.mean([A[i] > B[i] for i in range(n_red)]))
    facts["q17_n500_m12_A_beat_C"] = float(np.mean([A[i] > C[i] for i in range(n_red)]))
    facts["q17_n500_m12_A_beat_D"] = float(np.mean([A[i] > D[i] for i in range(n_red)]))
    facts["q17_n500_m12_gap_C_p50"] = float(np.median([A[i] - C[i] for i in range(n_red)]))
else:
    facts["q17_n500_m12_A_beat_B"] = 0.0
    facts["q17_n500_m12_A_beat_C"] = 0.0
    facts["q17_n500_m12_A_beat_D"] = 0.0
    facts["q17_n500_m12_gap_C_p50"] = 0.0

# ---------------------------------------------------------------- q9
x10_all = [xirr10(k) for k in ks10]
for a, key in ((12, "q18_n500_10y_corr_12m"),
               (36, "q18_n500_10y_corr_36m"),
               (60, "q18_n500_10y_corr_60m")):
    xa = [xirr_at(k, a) for k in ks10]
    facts[key] = spearman(xa, x10_all)

# ---------------------------------------------------------------- q10
H15 = 180
ks15 = list(range(0, N - H15 + 1))
V15 = np.array([val(k, H15) / 10000.0 for k in ks15])
for c, key in ((0.50, "q10_n500_15y_need_50"),
               (0.80, "q10_n500_15y_need_80"),
               (0.95, "q10_n500_15y_need_95")):
    q = float(np.quantile(V15, 1.0 - c))
    facts[key] = 10000000.0 / q

# ---------------------------------------------------------------- q11 (AMFI)
amfi = pd.read_parquet(ip("amfi_sip.parquet"))
amfi["month"] = amfi["month"].astype(str)
amfi = amfi.sort_values("month").reset_index(drop=True)

gb_all = tri.groupby("ym", sort=True)
first_pos_all = {m: gb_all.indices[m][0] for m in gb_all.indices}

level_last_all = float(tri["level"].iloc[-1])
date_last_all = tri["d"].iloc[-1]

rows = amfi[amfi["month"] >= "2016-04"].reset_index(drop=True)

mpos = []
for m in rows["month"]:
    per = pd.Period(m, freq="M")
    pos = first_pos_all[per]
    mpos.append(pos)

# industry XIRR
dates = []
amounts = []
tot_units = 0.0
for i in range(len(rows)):
    pos = mpos[i]
    d0 = tri["d"].iloc[pos]
    lv0 = float(tri["level"].iloc[pos])
    inflow = float(rows["inflow"].iloc[i])
    dates.append(d0)
    amounts.append(-inflow)
    tot_units += inflow / lv0
dates.append(date_last_all)
amounts.append(tot_units * level_last_all)
facts["q20_n500_industry"] = xirr(dates, amounts)

# trend SIP
nvec = np.arange(len(rows), dtype=float)
yvec = np.log(rows["inflow"].values.astype(float))
bcoef, acoef = np.polyfit(nvec, yvec, 1)
amts_trend = np.exp(acoef + bcoef * nvec)

dates = []
amounts = []
tot_units = 0.0
for i in range(len(rows)):
    pos = mpos[i]
    d0 = tri["d"].iloc[pos]
    lv0 = float(tri["level"].iloc[pos])
    amt = float(amts_trend[i])
    dates.append(d0)
    amounts.append(-amt)
    tot_units += amt / lv0
dates.append(date_last_all)
amounts.append(tot_units * level_last_all)
facts["q20_n500_trend"] = xirr(dates, amounts)

# ---------------------------------------------------------------- q22
outstanding_latest = float(amfi["outstanding"].iloc[-1])
closed_sum = float(amfi["closed"].iloc[-12:].sum())
facts["q22_life_latest"] = outstanding_latest / closed_sum

# ---------------------------------------------------------------- write
ambiguities.append(
    "'In the red' and 'lost money' use strict '<' (value below money put in)."
)
ambiguities.append(
    "FD tax at the final valuation date is applied even when that date is not 31 March, "
    "as the specification states."
)
ambiguities.append(
    "Path D keeps a single 'paused' flag that, once cleared, is never re-armed; "
    "the resumed SIP buys units for every later month."
)
ambiguities.append(
    "AMFI industry/trend SIPs value all units at the level of the very last row of tri_500.parquet."
)

with open(os.path.join(OUT, "facts.json"), "w") as fh:
    json.dump({k: float(v) for k, v in facts.items()}, fh, indent=2)

with open(os.path.join(OUT, "ambiguities.json"), "w") as fh:
    json.dump(ambiguities, fh, indent=2)
