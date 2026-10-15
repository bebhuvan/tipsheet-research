# Does a SIP work? Study plan (canonical)

Status: **draft for approval** (2026-10-15). Frozen at the commit recorded in `freeze.json`. Changes after the freeze go under Amendments.

## The big question

> "Does a SIP actually work? On what, over how long, and does how I run it matter?"

**Who asks it.** Anyone saving monthly through a mutual fund, or about to start. AMFI counts crores of SIP accounts; the exact count, from the data, goes in the article. In 2026 they are getting two opposite messages. "SIPs always win over the long run." And "SIP is broken: FY2025-26 showed losses across most equity SIPs, closures outnumbered new SIPs in some months, and the old success stories came from cheap markets and 12% deposits."

**What they are deciding.** Whether to start, continue, stop or change a SIP; what to put it in; how long to commit; and whether the many SIP "hacks" (dates, step-ups, buying dips) are worth bothering with.

**The argument this study tests.** A SIP is a way of saving, not an investment. Its results are decided almost entirely by *what* it buys, *how long* it runs and *what the market did*. The method's details barely matter, and the investor's own behaviour (stopping when it hurts) matters more than any hack. If the data says otherwise, the article says so.

## Chapters and their claims

Each chapter makes one claim the reader can repeat. The claims are hypotheses; the article states whatever the data shows.

1. **Does it work?** Over 10 years or more, almost always; over 1 to 5 years, often not; after inflation, by a thinner margin than the pitch.
2. **What it works on.** The asset decides more than anything else. Diversifying costs return in the middle of the range and buys protection at the bottom.
3. **Time.** Longer SIPs give steadier returns a year but a wider range of rupees, the early instalments do most of the work, and reaching a goal reliably takes more than the calculator says.
4. **The method.** SIP against lump sum depends on whether you have the lump sum. Dates, frequency and timing tricks move results by fractions of a point; tax and volatility work differently from what the pitch says.
5. **The pain.** Every SIP goes under water at some point. What you do then is the biggest decision you control.
6. **The critique and the crowd.** Testing the serious case against SIPs, whether investors as a group used them well, and how long real SIPs last.

## Headline findings

The questions the article tells in depth (mechanism, a real rupee story, one big annotated chart): **Q1** (the verdict), **Q5** (diversification's price), **Q12** (the levers, ranked), **Q16** (the bad start) and **Q17** (stopping). Every other question gets one chart, a short answer and its number.

## What I already know (honest disclosure)

This redoes the October 2026 study "Is SIP bad?" (portal repository, `research/studies/is-sip-bad/`). I have seen its results and the portfolio lab's SIP results (S1 to S16, `docs/research/sip_studies_spec.md`). A question marked **known** below was computed there. It is recomputed here with this repository's own fresh code as a **replication**, its earlier value given as the target, with no prediction. Earlier values used the lab's engine (fund costs and tax), so differences of a few tenths of a point are expected from convention alone. Differences larger than 1 point are investigated and reported. A question marked **new** has not been computed by anyone on this project. Its prediction is written here before any result.

## What is already known elsewhere

- **Lump sum against cost averaging.** For someone who already holds the money, investing at once beat spreading it out about two-thirds of the time in US, UK and Australian history (Vanguard, Shtekhman, Tasopoulos and Wimmer, "Dollar-cost averaging just means taking risk later", 2012, opened via a hosted copy; Vanguard, Finlay and Zorn, "Cost averaging: Invest now or temporarily hold your cash?", February 2023, opened). Constantinides (1979, *Journal of Financial and Quantitative Analysis* 14(2): 443–450, opened on RePEc) showed dollar-cost averaging is a suboptimal policy for deploying a sum. None of this applies to a salaried saver without a lump sum; a SIP is how such a person invests at all.
- **Investors' returns against their funds'.** Money-weighted returns fall below buy-and-hold returns because of when money arrives (Dichev, 2007, *American Economic Review* 97(1): 386–401, doi:10.1257/aer.97.1.386, opened). The gap is disputed: Keswani and Stolin (2008, *Finance Research Letters* 5(4): 228–235, opened) find it is not robust. Morningstar's "Mind the Gap" and an Axis Mutual Fund study report gaps for US and Indian funds (both unverified: could not be opened).
- **Why averaging is popular despite the theory:** regret and loss aversion (Statman, 1995, *Journal of Portfolio Management* 22(1); unverified, known only through citations).
- **The critique, in its strongest form.** India's SIP success stories date from years when few people ran SIPs, valuations were low and deposits paid 10% or more. Today valuations are high, especially in mid and small caps; deposit rates are lower; and the flood of SIP money may have removed the deep falls averaging needs. So the past is a poor guide. (Stated without naming its proponents.)
- **The site's lab** (`/lab/sip/`) has interactive versions of several known results. The article links to it rather than repeating its tools.

## Data

| Input | What | Traps |
|---|---|---|
| `portal:asset_tri_daily` | Total-return levels: Nifty 500 from January 1995, Nifty 50 from June 1999, Midcap 150 and Smallcap 250 from April 2005, gold (domestic rupee price) from August 2000, NSE 5-year G-sec index from September 2001 | Nifty 500 1995–1998 is probably back-calculated by NSE, with some hindsight in its constituents. Midcap 150 and Smallcap 250 before their 2016 launch are back-calculated. Gold before 2005 is the world price × USD/INR (misses import-duty changes). All flagged on charts and tested by the era split |
| `reference/rbi_deposit_rates_1_3y.csv` | RBI Handbook, "Structure of Interest Rates" (DBIE report 282): five major banks' 1–3 year deposit rates as at each end-March, 1971 to 2026, one consistent measure | Fetched from RBI's DBIE by the Data bank; checked against the 2009-10 Handbook table (`rbi_hbs74_deposit_rates.csv`): equal in 31 of 36 overlapping years. Top and bottom of each range both kept; the top is used, and the bottom is a sensitivity. The last row is provisional |
| `portal:macro_cpi_monthly` | All-India CPI, linked across base years, monthly | CPI is published about two weeks after the month; it is used only to deflate realised values, never to make a decision, so the lag doesn't matter |
| `databank:nifty_index_valuations` | Nifty 50 and Nifty 500 trailing P/E, daily, from January 1999 | NSE switched to consolidated earnings in 2021. Q19 uses P/E only at dates up to 2017 (10-year endings stop in 2026), so all on the old basis; today's P/E is shown separately and flagged as a different basis |
| `databank:india_data_hub_series` (`CMMFSIPFLO11M`, `CMMFSIPNEW11M`, `CMMFSIPCLO11M`, `CMMFSIPACC11M`) | AMFI gross monthly SIP inflows (April 2016 on); new, closed and outstanding SIP accounts (April 2019 on) | Derived figures only (no raw series published). AMFI's January–April 2025 clean-up of dormant accounts inflates closures in those months |

## Common conventions

- **The SIP:** ₹10,000 on the first NSE session of each month, into the asset's total-return series, less a yearly expense ratio charged daily: 0.20% for equity index funds, 0.50% for gold, 0.30% for G-secs (typical direct-plan costs of index funds, gold ETFs and gilt funds). Headline results are before tax. Chapter 1's verdict also shows an after-tax version: equity gains above ₹1.25 lakh taxed at 12.5% on final redemption (today's rules applied throughout, stated as such).
- **Statement value** at the last session of a month: units held × that session's level. **In the red:** statement value below the money put in so far.
- **XIRR:** the annualised return on the dated instalments and the final value (`desk.calc.xirr`).
- **Horizons:** 1, 3, 5, 7, 10, 15 and 20 years.
- **Samples:** "long history" means the Nifty 500 from January 1995. "The menu" means every asset and mix over their common history, starts from April 2005. Every start month with a full horizon of data after it is used.
- **Independent periods.** Start months overlap. A 10-year SIP started each month from 1995 gives about 260 start months but only about 2.6 non-overlapping decades; the menu's 10-year results rest on about 1.1. Every statistic across start months is a description of this history, reported with its independent count. **No p-values across overlapping start months.** Where an interval helps, a block bootstrap with a block as long as the horizon is shown and labelled "indicative".
- **Mixes:** 60/40 (Nifty 500 / G-sec), 60/20/20 (Nifty 500 / G-sec / gold) and equal thirds. Each instalment is split at the target weights; rebalanced each April unless Q6 says otherwise.
- **FD:** money accrues daily at the deposit rate (top of range) known on that day. End-March rates are joined by straight lines, since they are point-in-time rates. Interest is taxed yearly at 30% plus 4% cess.
- **Real returns:** every instalment and the final value deflated by CPI to the start month.
- **Data end:** the last session in the input when compute runs, recorded in the results.

## Chapter 1. Does it work?

### Q1. How often did an equity SIP lose money, trail an FD, or trail inflation?

- **Status:** known (replication with a new FD series). Earlier targets, Nifty 500 from 1995, after tax: lost money at 1/3/5/7/10 years 29.5/16.5/7.5/2.4/0.0%; below FD at 1/3/5/10 years 38.8/25.5/15.3/0.4%; below inflation at 3/5/10 years 29.6/23.1/1.5%; no loss at 9 years or longer.
- **Why a reader cares:** the most basic question, and the one the FY2026 losses raised.
- **Estimand:** for the Nifty 500 (long history) at each horizon: the share of start months that lost money, ended below the FD on the same instalments, and ended below inflation; before and after tax. The same for the menu at 5 and 10 years. Episodes (runs of consecutive losing start months) counted. The shortest horizon after which no start month lost money.
- **Checks:** era_split (1995–2004 starts against 2005 on), robustness (FD at the bottom of RBI's range; before against after tax)
- **Headline figure:** three lines by horizon (lost money, below FD, below inflation) with the independent count beneath. Job: answer.

### Q2. What range of returns should a SIP investor expect?

- **Status:** known (replication). Targets: Nifty 500 10-year median 12.8% after tax from 2005, 5th percentile 9.1%, worst 3.4%; 10-year Nifty 50 SIPs ranged from 3.8% to 21.5% a year by end date.
- **Why a reader cares:** calculators assume 12% a year, every year. The record gives a range.
- **Estimand:** the distribution (5th, 25th, 50th, 75th, 95th percentiles, worst, best) of XIRR by horizon for the Nifty 500 (long history), and the final value of ₹10,000 a month in rupees of the day and in today's rupees, at 10, 15 and 20 years. The calculator's 12% drawn as a reference.
- **Checks:** era_split, robustness (Nifty 50 from 1999)
- **Headline figure:** a fan of XIRR percentiles by horizon with the 12% line. Job: spread. Second: final values in rupees (job: case).

### Q3. What did SIPs earn after inflation?

- **Status:** known (replication). The October study computed real XIRR distributions and real index returns since 1995.
- **Why a reader cares:** ₹10,000 in 1995 was a much larger sum than today. Nominal returns flatter.
- **Estimand:** real against nominal XIRR percentiles at 5, 10, 15 and 20 years (Nifty 500, long history). The real total return of the Nifty 500 and Nifty 50 since their starts, against the real FD return over the same period.
- **Checks:** era_split
- **Headline figure:** paired nominal and real distributions by horizon, with zero marked. Job: comparison.

## Chapter 2. What it works on

### Q4. Large, mid or small caps, gold or government bonds?

- **Status:** known (replication). Targets: 10-year medians from 2005, Nifty 500 12.8%, Smallcap 250 14.5% (below the FD in 23.2% of 5-year windows); gold won 17% of 10-year windows against equity.
- **Why a reader cares:** "what should my SIP be in" is the decision with the largest effect, by the October study's own variance split (portfolio 45%, start month 31%).
- **Estimand:** for each single asset on the menu at 5 and 10 years: median XIRR, 5th percentile, worst, share below FD, deepest fall below the money put in, and longest stretch in the red.
- **Checks:** era_split (not possible within the menu's 2005 window; recorded as such, with mid- and small-cap back-calculation flagged instead), robustness (Nifty 50 for the large-cap line)
- **Headline figure:** median against bad case (5th percentile) at 10 years, one named point per asset. Job: comparison.

### Q5. What does diversifying a SIP cost, and what does it buy?

- **Status:** part known, part new. Known targets: at 10 years from 2005, Nifty 500 median 12.8% / 5th percentile 9.1% / worst 3.4% / deepest fall −50.2%; 60/20/20 11.1 / 9.0 / 5.6 / −30.8%; equal thirds 9.8 / 8.1 / 6.5 / −16.7%.
- **New:** the *price* of protection in rupees: for each mix against the Nifty 500, the median final value given up, against the final value gained at the 5th percentile and in the worst start month, and against the reduction in the deepest fall in rupees, at 5, 10 and 15 years.
- **Why a reader cares:** the choice between all-equity and a mix is usually argued in slogans. This puts both sides of the trade in rupees.
- **Rival answers:** (a) diversification is cheap insurance: it gives up a little in the middle and saves a lot in bad cases; (b) over 10 years or more it mostly costs, because equity's bad cases recover.
- **Prediction P5:** at 10 years, for 60/20/20 against the Nifty 500, the median rupees given up exceed the rupees gained at the 5th percentile. At 5 years, the reverse.
- **Checks:** robustness (60/40 and equal thirds; rebalancing off)
- **Headline figure:** for each mix, a bar of median rupees given up beside the 5th-percentile rupees gained, by horizon. Job: answer. Second: the deepest fall below the money put in for each mix (job: spread).

### Q6. Does rebalancing a diversified SIP each year help?

- **Status:** new.
- **Why a reader cares:** advisers say rebalance; most people never do. For a SIP, new instalments already rebalance partly.
- **Rival answers:** (a) rebalancing sells high and buys low, so it lifts returns; (b) for a SIP, instalments do most of that job, and rebalancing mainly changes the risk, not the return.
- **Estimand:** 60/20/20 and 60/40 at 10 years: rebalanced each April against never (instalments at target weights only). Paired difference in XIRR by start month: median and range. The deepest fall below the money put in for each.
- **Prediction P6:** the median paired difference in 10-year XIRR is within ±0.5 points, and rebalancing lowers the median deepest fall.
- **Checks:** robustness (rebalancing every six months; 15 years where data allows)
- **Headline figure:** paired differences by start month with the zero line. Job: answer.

## Chapter 3. Time

### Q7. How much steadier are longer SIPs?

- **Status:** known (replication). Targets: XIRR range (95th − 5th percentile) 41.3 / 15.6 / 6.9 / 3.4 points at 5 / 10 / 15 / 20 years; final-multiple range 1.7 / 2.1 / 1.9 / 2.0×.
- **Why a reader cares:** "stay long and the risk goes away" is half true. The return a year steadies; the rupees don't.
- **Estimand:** for the Nifty 500 (long history) at each horizon: the 5th–95th percentile range of XIRR, and of the final value as a multiple of the money put in.
- **Checks:** era_split
- **Headline figure:** two small panels on one horizon axis (XIRR range, final-multiple range). Job: mechanism.

### Q8. How much did the start date matter?

- **Status:** known (replication). Targets: medians by start year ranged from 25.3% (1997) to 9.3% (2010) for Nifty 50 10-year SIPs; starting within 2% of a market high against 10% or more below it: 12.3% against 12.6% (lab S8).
- **Why a reader cares:** "wait for a fall before starting" is common advice.
- **Estimand:** the median 10-year XIRR by start year (Nifty 500, long history); and the 10-year results by how far the market was below its previous high in the start month (bands: within 2%, 2–10%, more than 10% below).
- **Checks:** era_split
- **Headline figure:** 10-year XIRR by start year, with the bands as a second view. Job: spread.

### Q9. Which years of a SIP matter most, and should you get out near the goal?

- **Status:** part known, part new. Known targets (15-year Nifty 500 SIPs): the first five years' instalments made 55.0% of final value, the last five 14.2%; the correlation of the 15-year XIRR with the first three years' index return −0.29, with the last three years' 0.09.
- **New:** moving out near the goal. For 15-year Nifty 500 SIPs: switching the whole corpus to the FD in equal monthly steps over the last 36 months (and continuing instalments into the FD), against staying in. Median, 5th percentile and worst final value; share of start months where the switch ended ahead.
- **Why a reader cares:** most SIPs have a goal date (a child's college, a house). The fear is a crash in the final year.
- **Rival answers:** (a) de-risking protects the goal at little cost; (b) it gives up the years when the corpus is largest and growing fastest, so it costs more than it protects.
- **Prediction P9:** the switch lowers the median final value and raises the 5th percentile, and ends ahead in fewer than 40% of start months.
- **Checks:** era_split, robustness (switch over 12 months instead of 36; FD at the bottom of range)
- **Headline figure:** the distribution of final values with and without the switch. Job: answer. Second: share of final value by instalment year (job: mechanism).

### Q10. How much do you need to put in each month to reach a goal, and what does starting late cost?

- **Status:** new. (The lab's delay study, the median corpus at 10, 15 and 20 years and the catch-up amount, is known; this asks the goal question across the whole range of outcomes.)
- **Why a reader cares:** calculators give one number at an assumed 12%. A reader planning for a child's college needs to know how likely that number is to be enough.
- **Rival answers:** (a) the 12% calculator is about right; (b) to be fairly sure of reaching a goal you need much more than the calculator says.
- **Estimand:** for the Nifty 500 (long history) and 60/20/20 (the menu), the monthly amount needed to reach ₹1 crore in 10, 15 and 20 years in 50%, 80% and 95% of start months; flat, and with a 10% yearly step-up (the first year's amount). Also the amount a 12%-a-year calculator gives, and the share of start months in which that amount reached the goal. The cost of starting five years late: the monthly amount a 15-year SIP needs to match the 20-year SIP's 80% outcome.
- **Prediction P10:** for ₹1 crore in 15 years on the Nifty 500, the 95% amount is at least 1.5 times the 50% amount, and the 12% calculator's amount reaches the goal in fewer than 60% of start months.
- **Checks:** era_split, robustness (₹1 crore in today's rupees, CPI-adjusted; 60/20/20)
- **Headline figure:** the monthly amount needed by confidence and horizon, with the calculator's amount marked. Job: answer. Second: starting five years late (job: case).

## Chapter 4. The method

### Q11. SIP or lump sum?

- **Status:** known (replication). Targets: for someone holding the money, a lump sum beat a 12-month STP in 59% to 70% of start months (lab S5). For a salaried saver, the monthly SIP against saving in an FD and investing each April: the SIP ended ahead in 50.4% of 10-year windows.
- **Why a reader cares:** "lump sum always beats SIP" is true for someone who has the lump sum, and meaningless for someone who doesn't.
- **Estimand:** (a) investor with ₹12 lakh today: all at once into the Nifty 500, against a 12-month and a 36-month STP from the FD, valued at 10 years; share of start months each won, and the median gap. (b) Investor earning monthly: the SIP against FD-then-invest-each-April, paired by start month at 10 years. (c) Explainer: one window's SIP XIRR against the lump sum's CAGR, and why they differ.
- **Checks:** era_split
- **Headline figure:** two panels, "you have the money" and "you earn it monthly", each the share of start months won and the median rupee gap. Job: comparison.

### Q12. Do dates, frequency or timing tricks matter?

- **Status:** known (replication). Targets, effects on the median 10-year XIRR: best SIP date instead of the 1st +0.1; weekly +0.1; 15% step-up +0.2; waiting for a 20% fall +0.7 (two episodes); waiting for a 2% daily fall −0.3; investing more when P/E is low (earlier: CAPE −0.3, yield gap −1.6); pausing in a 20% fall −1.5; 1% a year more in costs −1.1.
- **Why a reader cares:** a lot of SIP advice is about these levers. Ranked against each other and against the choice of asset, they look small.
- **Estimand:** for Nifty 500 10-year SIPs from 2005, each lever's paired effect on XIRR and on the final value in rupees (median, 10th and 90th percentile across start months): SIP date (each of the 1st to the 28th), weekly against monthly, a 10% yearly step-up (in rupees of extra corpus per rupee of extra savings), waiting for a 20% fall from the peak, investing double when the Nifty 50 P/E is in its cheapest fifth (using only P/E history to date), pausing during a 20% fall, and 1% a year more in costs. On the same chart, the gap between assets from Q4 and between start years from Q8.
- **Checks:** truncation_stable (the P/E rule uses only P/E known on each date), robustness (Nifty 50; 15 years)
- **Headline figure:** a forest chart of every lever's median effect with its 10th–90th range, against the asset and start-year gaps, in points of XIRR and in rupees. Job: answer.

### Q13. Is a SIP "long-term" after a year? The tax clock on every instalment

- **Status:** new.
- **Why a reader cares:** many think a SIP becomes long-term, and lightly taxed, a year after it starts. Each instalment has its own clock, so a SIP is never fully long-term while it runs.
- **Rival answers:** (a) after a year or two it is mostly long-term; (b) a large part of the gains stays short-term for years, because the newest instalments are always young.
- **Estimand:** for Nifty 500 SIPs redeemed in full at ages 12, 18, 24, 36 and 60 months: the share of units held under a year (first in, first out) and the share of gains on them, median and range across start months; the tax under today's rules (20% on short-term gains, 12.5% on long-term gains above ₹1.25 lakh a year), with and without a 1% exit load on units held under a year; the total as a share of the value, against a lump sum of the same money held as long.
- **Prediction P13:** at 24 and 36 months, the median short-term share of gains is below the short-term share of units.
- **Checks:** robustness (no exit load, as most index funds charge none; ₹50,000 a month so the long-term exemption binds)
- **Headline figure:** share of units and of gains that are short-term, by age at redemption. Job: mechanism.

### Q14. Does volatility help a SIP?

- **Status:** new. (The October study's path explainer showed one worked example; this measures it across history.)
- **Why a reader cares:** the pitch for rupee cost averaging says choppy markets help a SIP. More volatility buys more units on the dips, but it also drags down compounding.
- **Rival answers:** (a) more volatile windows gave SIPs an edge over the index's own return; (b) the edge comes from the shape of the path (when the falls came) and the window's overall return, not from volatility as such.
- **Estimand:** for every 10-year window (Nifty 500 long history; each menu asset): the "SIP edge", the SIP's XIRR minus the index's own annualised return over the same dates; its Spearman correlation with the window's realised volatility and with the index's total return over the window. An illustration: two made-up paths with the same start and end level, one smooth and one choppy, and the SIP result on each (tagged illustration).
- **Prediction P14:** across Nifty 500 windows, the SIP edge correlates more strongly (in absolute size) with the window's total return than with its volatility.
- **Checks:** era_split, robustness (Smallcap 250; gold)
- **Headline figure:** SIP edge against volatility, each window coloured by its total return. Job: mechanism. Second: the two-path illustration (job: case).

## Chapter 5. The pain

### Q15. How deep and how long do SIPs go under water?

- **Status:** known (replication). Targets: 96% of Nifty 500 SIPs from 2005 were in the red at some month-end (S10); the longest stretch was 38 months (August 1999 start, S15); worst values against money put in at 1/2/3 years −44.5/−43.5/−37.0%.
- **Why a reader cares:** knowing the pain in advance is what lets people sit through it.
- **Estimand:** for the Nifty 500 (long history): the share of SIPs ever in the red, the deepest fall below the money put in, and the longest stretch in the red, by start year; the same for each asset on the menu.
- **Checks:** era_split
- **Headline figure:** an "underwater" chart for every start month (statement value against money put in), with the deepest episodes labelled. Job: spread.

### Q16. When a SIP was in the red after a year or two, how did it end, and why?

- **Status:** part known, part new. Known targets: 29.7% of Nifty 500 start months from 1995 were in the red at 12 months, with a median 10-year XIRR of 16.7% against 13.8% for all start months; 21.2% at 24 months, median 16.4%.
- **New:** (1) the whole distribution (5th, 25th, 75th percentiles, worst, share below FD) for red against not red, for the Nifty 500, Nifty 50, Midcap 150 and Smallcap 250; (2) by depth at 12 months (less than 10%, 10–20%, more than 20% below); (3) the mechanism: for red SIPs, the share of units held at month 120 that were bought while in the red, against the share of money put in while in the red.
- **Why a reader cares:** this is the reader's situation in 2026.
- **Rival answers:** (a) a bad start means a bad decade and a worse ending; (b) a bad start buys cheap units and a better ending, as long as prices recover.
- **Prediction P16:** (a) for all four indices, the median 10-year XIRR of SIPs in the red at 12 months is higher than the rest's; (b) for the Nifty 500, the median rises with depth across the three red bands; (c) the share of units bought while red is at least 1.5 times the share of money put in while red.
- **Checks:** era_split, robustness (24 months; expense ratio 1%; 15-year ending where data allows)
- **Headline figure:** outcomes by depth at 12 months against "not red", with episode counts. Job: answer. Second: units bought while red against money put in while red (job: mechanism). Third: the January 2008 Nifty 500 SIP followed month by month (job: case).

### Q17. Did stopping a SIP that was in the red protect the investor?

- **Status:** new. (Lab S4 measured pausing for every SIP; this conditions on being in the red.)
- **Why a reader cares:** stopping is the decision on the table, and people make it when they're down.
- **Rival answers:** (a) stopping caps the damage when a fall continues; (b) stopping gives up the cheapest instalments, so it costs, most of all in the deepest falls.
- **Estimand:** for every Nifty 500 start month in the red at month *m* (12, 24), four paths over the same 10 years and ₹12 lakh of savings: **A** keep going; **B** stop and hold, with later instalments into the FD; **C** sell at month *m*, with proceeds and later instalments into the FD; **D** pause into the FD until the held units are back above the money put in, then resume (the FD balance stays). For each, the paired final-value gap with A in rupees: median, worst, best, the share where A ended ahead, and the gap by depth band.
- **Prediction P17:** A ends ahead of B and of C in more than 80% of red start months, and ahead of D in more than 65%. The median gap against C is larger for start months more than 20% in the red than for those less than 10% in the red.
- **Checks:** era_split, robustness (FD untaxed; FD at the bottom of range; *m* = 24; the other three indices)
- **Headline figure:** paired gaps (A minus each path) in rupees, one row per path, with the share A won in the title. Job: answer. Second: the gap by depth band (job: conditioning).

### Q18. When does a SIP's running return start to tell you how it will end?

- **Status:** new.
- **Why a reader cares:** apps show the XIRR from the first month, and people judge SIPs and funds on one or two years of it.
- **Rival answers:** (a) early returns predict the ending: a poor start means a poor ending; (b) early returns are noise or even point the other way, and only become informative late.
- **Estimand:** for Nifty 500 SIPs, at ages 6, 12, 24, 36, 60 and 84 months: the Spearman rank correlation between the running XIRR and the final 10-year XIRR; the share of SIPs in the bottom third at that age that ended in the bottom third (33% if unrelated); the first age at which the correlation exceeds 0.5.
- **Prediction P18:** the correlation is below zero at 12 and 24 months and does not exceed 0.5 before 60 months.
- **Checks:** era_split, robustness (mid and small caps from 2005; 15-year ending)
- **Headline figure:** the correlation by age, with 0 and 0.5 marked and the independent count. Job: answer.

## Chapter 6. The critique and the crowd

### Q19. Was the bonus for a bad start really about cheap prices, and where are prices now?

- **Status:** new. (The October study correlated starting P/E with 10-year results; that is known and not repeated here. This conditions on being in the red.)
- **Why a reader cares:** if a bad start paid off only because the fall made the market cheap, a fall that leaves it expensive might not pay. This is the honest limit on Q16.
- **Rival answers:** (a) the bonus is a valuation effect: red SIPs did better only when the Nifty was cheap at month 12; (b) averaging into any fall that recovers pays, whatever the valuation.
- **Estimand:** Nifty 50 SIPs in the red at 12 months: median 10-year XIRR when the month-12 trailing P/E was below the median of all month-12 P/Es, against above it; the Spearman correlation of month-12 P/E with the 10-year XIRR, within red SIPs and within all SIPs. Then, as context and not a forecast: today's Nifty 50 P/E percentile (different earnings basis, flagged) and today's deposit rate against their histories.
- **Prediction P19:** red SIPs with month-12 P/E below the median have a median 10-year XIRR at least 2 points higher than red SIPs with P/E above it.
- **Checks:** era_split (not possible: about 1.7 independent windows; recorded as such), robustness (P/E at the start month instead of month 12)
- **Headline figure:** month-12 P/E against 10-year XIRR, red SIPs in colour, episodes labelled. Job: mechanism. Second: today's percentiles (job: caveat).

### Q20. Did investors' SIP money arrive at bad times?

- **Status:** known (replication). Targets (Nifty 500, before tax, April 2016 on): industry 11.4%, constant SIP 12.6%, index 13.7% a year; against a SIP growing at the contributions' own trend (23.3% a year), the gap was −0.1 points.
- **Why a reader cares:** the critique says SIP money pours in near peaks. The answer depends on the benchmark, and the trend benchmark is the fair one.
- **Estimand:** AMFI's monthly SIP inflows treated as instalments into the Nifty 500 total-return index: XIRR to the data end against a constant SIP and a trend-growth SIP over the same months; the same without the last 12 months.
- **Checks:** robustness (Midcap 150 and Smallcap 250 in place of the Nifty 500)
- **Headline figure:** the three returns as bars, with the benchmark explained. Job: comparison.

### Q21. Have market falls become shallower since SIP money grew?

- **Status:** known (replication, descriptive).
- **Why a reader cares:** the critique says SIP flows killed the deep falls that make averaging pay.
- **Estimand:** each fall of 10% or more in the Nifty 500 total-return index, its depth and recovery time, 1995–2015 against 2016 to the data end.
- **Checks:** none (descriptive: about ten years of large SIP flows cannot separate cause from coincidence, and the article says so)
- **Headline figure:** the index's drawdown chart with episodes labelled and 2016 marked. Job: caveat.

### Q22. How long do real SIPs last, and what does the stoppage ratio count?

- **Status:** new. (The October study's registrations-against-returns correlation is known: registrations did not follow the trailing 12-month return as strongly as predicted.)
- **Why a reader cares:** every 10-year statistic in this study assumes the SIP survives 10 years. If the typical SIP is stopped after two or three, most investors never see the outcomes the pitch promises. The "stoppage ratio above 100%" headlines also need explaining.
- **Rival answers:** (a) most SIPs run for many years, as advised; (b) the typical SIP account lasts only a few years.
- **Estimand:** monthly from April 2019, from AMFI's counts of new, closed and outstanding SIP accounts: the implied average life of an account (outstanding accounts divided by monthly closures, a steady-state approximation, as a 12-month rolling value), with and without AMFI's dormant-account clean-up of January to April 2025; the stoppage ratio (closed over new); the average monthly inflow per outstanding account. Closures against the Nifty 500's trailing 12-month return, descriptive.
- **Caveats set now:** an account is not an investor (one person can hold many SIPs); closures include SIPs that reached the end date they were set up with, failed bank mandates and the clean-up. The implied life is a rough measure, and the article says so.
- **Prediction P22:** the implied average life of a SIP account, outside the clean-up months, is under 5 years throughout 2019 to 2026.
- **Checks:** robustness (including the clean-up months; new accounts instead of closures as the flow)
- **Headline figure:** implied average life over time, with the clean-up marked. Job: answer. Second: new and closed accounts with the stoppage ratio explained (job: caveat).

**The critique scorecard.** The chapter ends with a table: each argument of the critique in its strongest form, what the data shows with its number, and a verdict of **agrees**, **disagrees** or **can't tell yet**.

## SIP myths, checked

The article ends with a table: each popular claim, the question that answers it, and a one-line verdict with its number.

| Claim | Answered by |
|---|---|
| "SIPs never lose money in the long run" | Q1, Q2 |
| "SIPs beat FDs" / "SIPs don't beat FDs" | Q1 |
| "SIP returns beat inflation comfortably" | Q3 |
| "Small-cap SIPs are best for the long run" | Q4 |
| "Debt and gold are for the timid" | Q5 |
| "The longer you stay, the less risk" | Q7 |
| "Wait for a fall before starting" | Q8, Q12 |
| "Stay invested till the goal" | Q9 |
| "₹10,000 a month for 20 years makes you a crorepati" | Q10 |
| "Lump sum always beats SIP" | Q11 |
| "The 25th is a better SIP date" / "weekly is better" / "step-ups give higher returns" | Q12 |
| "After a year my SIP is long-term" | Q13 |
| "Volatility is good for SIPs" | Q14 |
| "Rupee cost averaging means you always buy cheap" | Q14, explainer |
| "My SIP is negative, so SIPs don't work" | Q15, Q16 |
| "Stop the SIP when the market falls" | Q17 |
| "My SIP's return after a year tells me if it's working" | Q18 |
| "The old SIP success stories won't repeat" | Q19 |
| "SIP investors pour in at the top" | Q20 |
| "SIP flows have killed deep falls" | Q21 |
| "Investors are fleeing SIPs (stoppage ratio above 100%)" | Q22 |

## Naive questions answered as context

- *Why does my app show −30% XIRR when I've lost only 8%?* Annualising a few months' money (worked example).
- *How can my SIP be in the red when the market is up since I started?* The arithmetic of averaging (worked example).
- *Is FY2026 unusual?* The Nifty 500 SIP started April 2025 and valued at end-March 2026, placed on the historical distribution of 12-month results.
- *Why does the same fund show different returns for a SIP and a lump sum?* (Q10c.)

## Questions I won't ask

- **Individual funds, active against index, direct against regular plans:** the fund NAV history is being rebuilt and isn't ready. A later canonical study.
- **What SIPs will return from here:** no forecasts. Q19's percentiles are context only.
- **PPF, real estate, NPS:** no clean return series in our data yet (PPF rates are public and could be added in a later amendment; real estate has no clean long series).
- **Whether SIP flows *caused* any market change:** too little history to separate cause from coincidence (Q21 describes only).
- **Other countries' lost decades (Japan):** index licences not cleared. Mentioned in words only, as the critique's strongest example.
- **Tax optimisation and harvesting:** a separate topic (Q13 covers only the tax clock).
- **Individual investors' outcomes:** AMFI publishes industry totals only; account-level SIP histories sit with the registrars (CAMS, KFintech) and aren't public. Q20 and Q22 use the totals.
- **International SIPs (S&P 500, Nasdaq feeder funds):** index licences not cleared.
- **The withdrawal phase (SWPs, retirement):** a separate study.
- **Hybrid and balanced-advantage funds, ELSS, NPS:** fund-level data, waiting for the NAV cleanup, or a different topic.
- **SIP against PPF:** worth adding once PPF's notified rate history is fetched (public); a later amendment, not part of this freeze.

## What would change my mind

- If the method levers in Q12 move results by as much as the choice of asset in Q4, the study's central argument is wrong, and the article leads with that.
- If SIPs in the red at 12 months ended *worse* for any index with two or more episodes, the reassuring story fails for that index.
- If stopping and holding (Q17 B) beat keeping going in a third or more of red start months, "don't stop" isn't the lesson, and the article says what it depends on.
- If red SIPs did no better when the market was still dear (Q19), the critique has a real point about today.

## Headline numbers for the independent recompute

Q1: shares lost money and below FD at 3, 5 and 10 years (Nifty 500). Q5: median and 5th-percentile final values for the Nifty 500 and 60/20/20 at 10 years. Q12: the date, weekly and pause effects. Q16: share red at 12 months, the two medians, the three depth-band medians, the unit share. Q17: share where A beat B, C and D, and the median gap against C. Q18: correlations at 12, 36 and 60 months. Q10: the 50%, 80% and 95% monthly amounts for ₹1 crore in 15 years (Nifty 500). Q22: the implied average life in the latest 12 months.

## Amendments

None yet.
