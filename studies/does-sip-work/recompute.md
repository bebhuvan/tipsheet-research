# Independent recompute: does-sip-work

Written from plan.md, not from compute.py. Compute each fact below from the inputs and these definitions only.

## Inputs (Parquet files in INPUT_DIR)

- `tri_500.parquet`: columns `d` (date), `level` (float). NSE Nifty 500 total-return index, one row per NSE trading session, sorted, from 2 January 1995.
- `tri_150.parquet`, `tri_250.parquet`: the same for the Nifty Midcap 150 and Nifty Smallcap 250, from April 2005. (Not needed for the facts below; provided for checking.)
- `deposit_rate_daily.parquet`: columns `d` (every calendar day), `rate_pct` (float). Bank fixed-deposit rate, per cent a year, for each calendar day.
- `amfi_sip.parquet`: columns `month` ("YYYY-MM"), `inflow` (rupees of gross SIP inflow in the month), `new`, `closed`, `outstanding` (numbers of SIP accounts; `new`, `closed`, `outstanding` start in 2019, `inflow` in April 2016).

## Definitions

**NAV.** For the Nifty 500, NAV on session date t = level(t) × (1 − 0.002) ^ (days(t) / 365), where days(t) is the number of calendar days from the first row's date to t. (A 0.20% yearly expense ratio charged daily.)

**Months.** Group sessions by calendar month. For each month: its *first session* (smallest date) and *last session* (largest date). Use every month from January 1995 to **September 2026** inclusive (October 2026 is incomplete and is dropped). Number the months 0, 1, 2, … in order.

**A SIP.** ₹10,000 is invested on the first session of each month at that session's NAV (units = 10,000 / NAV). A SIP *started in month k* buys in months k, k+1, …. Its *statement value at age j* (j = 1, 2, …) is (units bought in months k … k+j−1) × NAV on the last session of month k+j−1. *Money put in at age j* = 10,000 × j. A SIP is *in the red at age j* if its statement value at age j is below the money put in at age j.

**The 10-year result.** 120 instalments (months k … k+119), valued at the last session of month k+119. *XIRR*: the annual rate r solving Σ amount_i × (1 + r)^(−t_i) = 0, with each instalment as −10,000 at its buy date and the final value as + at the valuation date, t_i in years = (date_i − first buy date) in days / 365.

**Eligible start months for a horizon of H months:** every k with k + H − 1 ≤ the index of September 2026.

**The FD.** Money in the FD grows each calendar day d by the factor exp(ln(1 + rate_pct(d)/100) / 365): money deposited on date a and held to date b grows by the product of the daily factors for days a, a+1, …, b−1. Interest is taxed at 31.2%: at every 31 March, the interest earned since the previous tax event is taxed (the tax is deducted from the balance), and the same is done on the final date. A deposit made on day a starts earning on day a.

**Lost money at H months:** final value (at age H) below 10,000 × H.

**Below the FD at H months:** final value below the value, on the same final date, of the same ₹10,000 instalments placed in the FD on the same buy dates (FD after tax as defined).

**Percentiles and medians:** linear interpolation (numpy's default `quantile`).

**Stopping paths (for SIPs in the red at age 12, horizon 120 months):**
- **A, keep going:** the plain 10-year SIP's final value.
- **B, stop and hold:** the units from months k … k+11 are kept to the end (valued at the last session of month k+119); each of the instalments for months k+12 … k+119 goes into the FD on that month's first session instead. Final value = units' value + FD value after tax at the last session of month k+119.
- **C, stop and switch:** at the last session of month k+11, the units are sold at that session's NAV and the proceeds go into the FD; every instalment for months k+12 … k+119 also goes into the FD on its first session. Final value = the FD's value after tax at the last session of month k+119.
- **D, pause until back in the black:** from month k+12 on, at each month's first session, check whether the value of the units held, at the previous month's last-session NAV, is at least the money put into units so far (10,000 per instalment that bought units). While it is not, that month's ₹10,000 goes into the FD; once it is, the SIP resumes and every later instalment buys units (it never pauses again). Final value = units' value + FD value after tax.
- **"A beat X"**: A's final value is greater than X's.

**Units bought while in the red (for SIPs in the red at age 12, 10-year horizon):** instalment number i (i = 2 … 120, buying in month k+i−1) counts as *bought while red* if the SIP was in the red at age i − 1. Units share = units from those instalments ÷ all units; money share = number of those instalments ÷ 120. The fact is the median, over SIPs in the red at age 12, of (units share ÷ money share).

**Running XIRR at age a:** the XIRR of the first a instalments, valued at the last session of month k+a−1.

**Goal amounts:** for 15-year SIPs (180 instalments), let V be each eligible start month's final value per ₹1 a month (final value of the ₹10,000 SIP ÷ 10,000). The amount needed for ₹1 crore (10,000,000) with confidence c is 10,000,000 ÷ (the (1 − c) quantile of V).

**AMFI.** Industry XIRR: each month's `inflow` from April 2016 to the latest month is invested in the Nifty 500 *total-return level* (no expense ratio) on that month's first session, all valued at the level on the last session in `tri_500.parquet`; XIRR of those flows. Trend SIP: fit ln(inflow) = a + b × n by least squares (n = 0, 1, 2, … months from April 2016); invest exp(a + b × n) each month instead; XIRR. Implied SIP life (years) for the latest month = outstanding accounts in the latest month ÷ the sum of `closed` over the latest 12 months.

## Facts to compute

Fractions as 0 to 1. XIRRs and medians as fractions (0.12 = 12% a year). Rupees as rupees.

1. `q1_n500_3y_lost`, `q1_n500_5y_lost`, `q1_n500_10y_lost`: share of eligible start months that lost money at 36, 60 and 120 months.
2. `q1_n500_5y_below_fd`, `q1_n500_10y_below_fd`: share below the FD at 60 and 120 months.
3. `q16_n500_red12`: among start months eligible for the 10-year horizon, the share in the red at age 12.
4. `q16_n500_red_p50`, `q16_n500_rest_p50`: median 10-year XIRR of those in the red at age 12, and of the rest.
5. `q16_n500_b20_p50`: median 10-year XIRR of those whose value at age 12 was more than 20% below the money put in (value ÷ money put in − 1 < −0.20).
6. `q16_n500_units_to_money_ratio_p50`: as defined above.
7. `q17_n500_m12_A_beat_B`, `q17_n500_m12_A_beat_C`, `q17_n500_m12_A_beat_D`: share of SIPs in the red at age 12 in which A beat B, C and D.
8. `q17_n500_m12_gap_C_p50`: median of (A's final value − C's final value), in rupees.
9. `q18_n500_10y_corr_12m`, `q18_n500_10y_corr_36m`, `q18_n500_10y_corr_60m`: Spearman rank correlation, across start months eligible for the 10-year horizon, between the running XIRR at age 12 (36, 60) and the 10-year XIRR.
10. `q10_n500_15y_need_50`, `q10_n500_15y_need_80`, `q10_n500_15y_need_95`: monthly rupees needed for ₹1 crore in 15 years with confidence 0.5, 0.8, 0.95.
11. `q20_n500_industry`, `q20_n500_trend`: industry and trend-SIP XIRRs.
12. `q22_life_latest`: implied SIP life in years.

```keys
q1_n500_3y_lost 0.005
q1_n500_5y_lost 0.005
q1_n500_10y_lost 0.005
q1_n500_5y_below_fd 0.01
q1_n500_10y_below_fd 0.01
q16_n500_red12 0.005
q16_n500_red_p50 0.0005
q16_n500_rest_p50 0.0005
q16_n500_b20_p50 0.0005
q16_n500_units_to_money_ratio_p50 0.02
q17_n500_m12_A_beat_B 0.01
q17_n500_m12_A_beat_C 0.01
q17_n500_m12_A_beat_D 0.01
q17_n500_m12_gap_C_p50 2000
q18_n500_10y_corr_12m 0.01
q18_n500_10y_corr_36m 0.01
q18_n500_10y_corr_60m 0.01
q10_n500_15y_need_50 50
q10_n500_15y_need_80 50
q10_n500_15y_need_95 50
q20_n500_industry 0.0005
q20_n500_trend 0.0005
q22_life_latest 0.05
```
