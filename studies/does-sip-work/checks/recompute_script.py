import os
import json
import numpy as np
import pandas as pd
from datetime import date

INPUT_DIR = os.environ['INPUT_DIR']
OUTPUT_DIR = os.environ['OUTPUT_DIR']

# ---------------------------------------------------------------------------
# Load and prepare Nifty 500 total-return index
# ---------------------------------------------------------------------------
tri = pd.read_parquet(os.path.join(INPUT_DIR, 'tri_500.parquet'))
tri = tri.sort_values('d').reset_index(drop=True)
tri['d'] = pd.to_datetime(tri['d'])
first_date = tri['d'].iloc[0]
tri['days'] = (tri['d'] - first_date).dt.days
tri['nav'] = tri['level'] * (0.998) ** (tri['days'] / 365.0)

# ---------------------------------------------------------------------------
# Build monthly grid Jan 1995 .. Sep 2026
# ---------------------------------------------------------------------------
tri['month'] = tri['d'].dt.to_period('M')
month_range = pd.period_range(start='1995-01', end='2026-09', freq='M')
gb = tri.groupby('month')

first_dates = gb['d'].first().reindex(month_range)
last_dates = gb['d'].last().reindex(month_range)
first_navs = gb['nav'].first().reindex(month_range)
last_navs = gb['nav'].last().reindex(month_range)
first_levels = gb['level'].first().reindex(month_range)
last_levels = gb['level'].last().reindex(month_range)

if first_dates.isna().any():
    raise ValueError("Missing month in tri_500")

first_dates_ts = pd.to_datetime(first_dates.values).tolist()
last_dates_ts = pd.to_datetime(last_dates.values).tolist()
first_navs = first_navs.values
last_navs = last_navs.values
first_levels = first_levels.values
last_levels = last_levels.values
N = len(month_range)
sep_2026_idx = month_range.get_loc(pd.Period('2026-09', freq='M'))

units = 10000.0 / first_navs
cum_units = np.concatenate(([0.0], np.cumsum(units)))

# ---------------------------------------------------------------------------
# Deposit rate daily factors and FD simulation
# ---------------------------------------------------------------------------
rate_df = pd.read_parquet(os.path.join(INPUT_DIR, 'deposit_rate_daily.parquet'))
rate_df = rate_df.sort_values('d').reset_index(drop=True)
rate_df['d'] = pd.to_datetime(rate_df['d'])
rate_df['factor'] = np.exp(np.log1p(rate_df['rate_pct'] / 100.0) / 365.0)
cum_fact = np.concatenate(([1.0], np.cumprod(rate_df['factor'].values)))
rate_dates = rate_df['d'].values

def prod_factor(a, b):
    if a >= b:
        return 1.0
    ia = np.searchsorted(rate_dates, a.to_datetime64())
    ib = np.searchsorted(rate_dates, b.to_datetime64())
    return cum_fact[ib] / cum_fact[ia]

def fd_single(a, b, principal=10000.0):
    if a >= b:
        return principal
    year_a = a.year
    year_b = b.year
    events = []
    for y in range(year_a, year_b + 1):
        d = pd.Timestamp(date(y, 3, 31))
        if a < d <= b:
            events.append(d)
    if b not in events:
        events.append(b)
    events = sorted(set(events))
    bal = principal
    prev = a
    for d in events:
        G = prod_factor(prev, d)
        bal = bal * (0.688 * G + 0.312)
        prev = d
    return bal

def fd_value(deposits, final_date):
    total = 0.0
    for a, amt in deposits:
        total += fd_single(a, final_date, amt)
    return total

# ---------------------------------------------------------------------------
# XIRR solver (bisection)
# ---------------------------------------------------------------------------
def xirr(amounts, dates):
    d0 = dates[0]
    t = np.array([(d - d0).days / 365.0 for d in dates])
    amts = np.array(amounts, dtype=float)
    def npv(r):
        return np.sum(amts * (1.0 + r) ** (-t))
    low = -0.999999999
    high = 10.0
    while npv(low) < 0:
        low = (low - 1.0) / 2.0
    while npv(high) > 0:
        high *= 2
    for _ in range(200):
        mid = (low + high) / 2.0
        if npv(mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

# ---------------------------------------------------------------------------
# Spearman rank correlation
# ---------------------------------------------------------------------------
def spearman_rank_corr(x, y):
    def rankdata(a):
        order = np.argsort(a)
        ranks = np.empty_like(order, dtype=float)
        sorted_a = a[order]
        i = 0
        while i < len(a):
            j = i
            while j + 1 < len(a) and sorted_a[j+1] == sorted_a[i]:
                j += 1
            avg_rank = (i + 1 + j + 1) / 2.0
            ranks[order[i:j+1]] = avg_rank
            i = j + 1
        return ranks
    rx = rankdata(x)
    ry = rankdata(y)
    return np.corrcoef(rx, ry)[0,1]

# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------
facts = {}

def eligible_ks(H):
    return np.arange(0, sep_2026_idx - H + 2)

# q1 lost
for H, key in [(36, 'q1_n500_3y_lost'), (60, 'q1_n500_5y_lost'), (120, 'q1_n500_10y_lost')]:
    ks = eligible_ks(H)
    lost = 0
    for k in ks:
        j = H
        val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
        money = 10000 * j
        if val < money:
            lost += 1
    facts[key] = lost / len(ks)

# q1 below FD
for H, key in [(60, 'q1_n500_5y_below_fd'), (120, 'q1_n500_10y_below_fd')]:
    ks = eligible_ks(H)
    below = 0
    for k in ks:
        j = H
        val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
        final_date = last_dates_ts[k+j-1]
        deposits = [(first_dates_ts[k+i], 10000.0) for i in range(j)]
        fd_val = fd_value(deposits, final_date)
        if val < fd_val:
            below += 1
    facts[key] = below / len(ks)

# q16 red12
ks_10y = eligible_ks(120)
red12 = np.zeros(len(ks_10y), dtype=bool)
value12 = np.zeros(len(ks_10y))
for idx, k in enumerate(ks_10y):
    j = 12
    val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
    value12[idx] = val
    if val < 10000 * j:
        red12[idx] = True
facts['q16_n500_red12'] = red12.mean()

# 10y XIRR
xirr_10y = np.zeros(len(ks_10y))
for idx, k in enumerate(ks_10y):
    j = 120
    final_val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
    buy_dates = [first_dates_ts[k+i] for i in range(j)]
    final_date = last_dates_ts[k+j-1]
    amounts = [-10000.0] * j + [final_val]
    dates = buy_dates + [final_date]
    xirr_10y[idx] = xirr(amounts, dates)

red_xirr = xirr_10y[red12]
rest_xirr = xirr_10y[~red12]
facts['q16_n500_red_p50'] = float(np.median(red_xirr))
facts['q16_n500_rest_p50'] = float(np.median(rest_xirr))

b20_mask = value12 < 96000.0
b20_xirr = xirr_10y[b20_mask]
facts['q16_n500_b20_p50'] = float(np.median(b20_xirr))

# units to money ratio
ratios = []
for idx, k in enumerate(ks_10y):
    if not red12[idx]:
        continue
    all_units = cum_units[k+120] - cum_units[k]
    red_inst = []
    for i in range(2, 121):
        age = i - 1
        j = age
        val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
        money = 10000 * j
        if val < money:
            red_inst.append(i)
    units_red = sum(units[k+i-1] for i in red_inst)
    units_share = units_red / all_units
    money_share = len(red_inst) / 120.0
    if money_share > 0:
        ratios.append(units_share / money_share)
facts['q16_n500_units_to_money_ratio_p50'] = float(np.median(ratios)) if ratios else 0.0

# q17
A_beat_B = []
A_beat_C = []
A_beat_D = []
gaps_C = []
for idx, k in enumerate(ks_10y):
    if not red12[idx]:
        continue
    j = 120
    A = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
    units_first_12 = cum_units[k+12] - cum_units[k]
    units_val_end = units_first_12 * last_navs[k+119]
    deposits_B = [(first_dates_ts[k+i], 10000.0) for i in range(12, 120)]
    fd_B = fd_value(deposits_B, last_dates_ts[k+119])
    B = units_val_end + fd_B
    proceeds = units_first_12 * last_navs[k+11]
    fd_C = fd_single(last_dates_ts[k+11], last_dates_ts[k+119], proceeds)
    deposits_C = [(first_dates_ts[k+i], 10000.0) for i in range(12, 120)]
    fd_C += fd_value(deposits_C, last_dates_ts[k+119])
    C = fd_C
    units_held = units_first_12
    money_in_units = 120000.0
    fd_deposits_D = []
    resumed = False
    for m in range(k+12, k+120):
        if not resumed:
            prev_nav = last_navs[m-1]
            val = units_held * prev_nav
            if val >= money_in_units:
                resumed = True
        if resumed:
            units_held += units[m]
            money_in_units += 10000.0
        else:
            fd_deposits_D.append((first_dates_ts[m], 10000.0))
    D = units_held * last_navs[k+119] + fd_value(fd_deposits_D, last_dates_ts[k+119])
    A_beat_B.append(A > B)
    A_beat_C.append(A > C)
    A_beat_D.append(A > D)
    gaps_C.append(A - C)

facts['q17_n500_m12_A_beat_B'] = float(np.mean(A_beat_B)) if A_beat_B else 0.0
facts['q17_n500_m12_A_beat_C'] = float(np.mean(A_beat_C)) if A_beat_C else 0.0
facts['q17_n500_m12_A_beat_D'] = float(np.mean(A_beat_D)) if A_beat_D else 0.0
facts['q17_n500_m12_gap_C_p50'] = float(np.median(gaps_C)) if gaps_C else 0.0

# q18
def running_xirr(k, a):
    j = a
    final_val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
    buy_dates = [first_dates_ts[k+i] for i in range(a)]
    final_date = last_dates_ts[k+j-1]
    amounts = [-10000.0] * a + [final_val]
    dates = buy_dates + [final_date]
    return xirr(amounts, dates)

for a, key in [(12, 'q18_n500_10y_corr_12m'), (36, 'q18_n500_10y_corr_36m'), (60, 'q18_n500_10y_corr_60m')]:
    xirr_a = np.array([running_xirr(k, a) for k in ks_10y])
    corr = spearman_rank_corr(xirr_a, xirr_10y)
    facts[key] = float(corr)

# q10
ks_15y = eligible_ks(180)
V = []
for k in ks_15y:
    j = 180
    final_val = last_navs[k+j-1] * (cum_units[k+j] - cum_units[k])
    V.append(final_val / 10000.0)
V = np.array(V)
facts['q10_n500_15y_need_50'] = 10000000.0 / np.quantile(V, 0.5)
facts['q10_n500_15y_need_80'] = 10000000.0 / np.quantile(V, 0.2)
facts['q10_n500_15y_need_95'] = 10000000.0 / np.quantile(V, 0.05)

# q20 AMFI
amfi = pd.read_parquet(os.path.join(INPUT_DIR, 'amfi_sip.parquet'))
amfi['period'] = pd.PeriodIndex(amfi['month'], freq='M')
amfi = amfi[amfi['period'] >= pd.Period('2016-04', freq='M')].reset_index(drop=True)
final_level = tri['level'].iloc[-1]
final_date_tri = pd.Timestamp(tri['d'].iloc[-1])

industry_amounts = []
industry_dates = []
total_units_industry = 0.0
for _, row in amfi.iterrows():
    p = row['period']
    idx = month_range.get_loc(p)
    first_session = first_dates_ts[idx]
    level_first = first_levels[idx]
    inflow = row['inflow']
    units_bought = inflow / level_first
    total_units_industry += units_bought
    industry_amounts.append(-inflow)
    industry_dates.append(first_session)
final_value_industry = total_units_industry * final_level
industry_amounts.append(final_value_industry)
industry_dates.append(final_date_tri)
facts['q20_n500_industry'] = xirr(industry_amounts, industry_dates)

# Trend SIP
n = np.arange(len(amfi))
ln_inflow = np.log(amfi['inflow'].values)
coeff = np.polyfit(n, ln_inflow, 1)
b = coeff[0]
a = coeff[1]
fitted_inflow = np.exp(a + b * n)
trend_amounts = []
trend_dates = []
total_units_trend = 0.0
for i, row in amfi.iterrows():
    p = row['period']
    idx = month_range.get_loc(p)
    first_session = first_dates_ts[idx]
    level_first = first_levels[idx]
    fitted = fitted_inflow[i]
    total_units_trend += fitted / level_first
    trend_amounts.append(-fitted)
    trend_dates.append(first_session)
final_value_trend = total_units_trend * final_level
trend_amounts.append(final_value_trend)
trend_dates.append(final_date_tri)
facts['q20_n500_trend'] = xirr(trend_amounts, trend_dates)

# q22
latest = amfi.iloc[-1]
outstanding = latest['outstanding']
closed_sum = amfi['closed'].iloc[-12:].sum()
facts['q22_life_latest'] = outstanding / closed_sum

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
with open(os.path.join(OUTPUT_DIR, 'facts.json'), 'w') as f:
    json.dump(facts, f, indent=2)

ambiguities = [
    "Tax on 31 March is applied to interest accrued up to the start of 31 March (growth through 30 March); growth on 31 March belongs to the next segment. Same for final date, tax applies to growth up to final date (exclusive of final day).",
    "For SIPs in the red at age 12 with no instalments bought while red (money_share = 0), the ratio is undefined and such SIPs are excluded from the median of units-to-money ratio.",
    "For AMFI trend SIP, the same months as industry XIRR (April 2016 to latest month in amfi_sip) are used, with n=0 for April 2016.",
    "For FD, if a deposit is made on 31 March, no tax event is applied on that date for that deposit (interest zero), and the first tax event is the next 31 March.",
    "For running XIRR at age a, the final value is at the last session of month k+a-1, using the first a instalments.",
]
with open(os.path.join(OUTPUT_DIR, 'ambiguities.json'), 'w') as f:
    json.dump(ambiguities, f, indent=2)
