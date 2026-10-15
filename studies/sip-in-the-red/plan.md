# Your SIP is in the red: study plan

Status: **draft for approval** (2026-10-15). Frozen at the commit recorded in `freeze.json`. Changes after the freeze go under Amendments.

## The big question

> "My SIP has been losing money for a year. Is something wrong, should I stop, and what actually decides how it ends?"

**Who asks it.** Anyone running an equity SIP in 2026. FY2025-26 was the first year in a long while that most equity SIPs showed a loss. SIP closures outnumbered new registrations in some months of 2026, while monthly SIP inflows set records. The reader is deciding whether to keep going, pause, stop or switch.

**What they believe now.** Two opposite stories are going around. "SIPs never lose over the long run, so ignore it." And "SIP is broken: the old success stories came from cheap markets and high interest rates, and they won't repeat." Underneath both is a belief that a SIP's early losses are a signal, good or bad.

**Why intuition gets it wrong.** A SIP's running return describes recent money, not the whole SIP. Early losses buy cheap units, which can help the ending. But that only pays off if prices recover, which is exactly what the critique doubts. The study separates what history shows from what it can't promise.

## What I already know (honest disclosure)

This study redoes the October 2026 study "Is SIP bad?" (portal repository, `research/studies/is-sip-bad/`), whose article was judged too thin. I have seen its results and the portfolio lab's SIP results (S1 to S16). Anything already computed there is **known**. Below it is labelled `(known)`, recomputed here as a replication, and not presented as a fresh test. The parts relevant here:

- Nifty 500 SIPs started from 1995: 29.7% of start months were below the money put in after 12 months. Their median 10-year return (after tax, lab engine) was 16.7% a year, against 13.8% for all start months. After 24 months: 21.2% below, median 16.4%.
- Losses by horizon: 29.5% of 1-year Nifty 500 SIPs lost money, 7.5% of 5-year ones, none of the 10-year ones. No start month lost money at 9 years or longer.
- For 15-year SIPs, the first five years' instalments made up 55% of the final value. The correlation of the 15-year return with the index's return in the first three years was −0.29; with the last three years, 0.09.
- Pausing during a 20% fall cost 1.5 points a year at the median (lab S4), unconditionally.
- Starting valuation and the 10-year result: computed in October (its prediction failed). I have not re-read the details for this plan and treat the topic as known.

The **new** parts below are things I have not computed or seen: the full distribution behind the medians, depth of loss, the unit mechanism, stopping strategies *conditional on being in the red*, how early returns predict the ending, and valuation conditioning within red SIPs.

## What is already known elsewhere

- **Lump sum against cost averaging.** For someone who already has the money, investing at once beat spreading it out about two-thirds of the time in US, UK and Australian history (Vanguard, Shtekhman, Tasopoulos and Wimmer, "Dollar-cost averaging just means taking risk later", 2012; opened via a hosted copy; Vanguard, Finlay and Zorn, "Cost averaging: Invest now or temporarily hold your cash?", February 2023, opened). Constantinides (1979, *Journal of Financial and Quantitative Analysis* 14(2): 443–450, opened on RePEc) showed dollar-cost averaging is suboptimal as a policy for someone choosing how to deploy a sum. **None of this applies to a salaried saver**, who has no lump sum, and that is the reader here. The site's lab already shows the Indian version (S5).
- **Investors' returns against their funds'.** Dollar-weighted (money-weighted) returns fall below buy-and-hold returns because of when money arrives (Dichev, 2007, *American Economic Review* 97(1): 386–401, doi:10.1257/aer.97.1.386, opened). The gap is disputed: Keswani and Stolin (2008, *Finance Research Letters* 5(4): 228–235, opened) find it is not robust. Morningstar's annual "Mind the Gap" puts the US gap near 1.2 points a year and notes that regular investing itself creates a gap (unverified: page did not load). An Axis Mutual Fund study reports a large gap for Indian equity funds (unverified: the PDF could not be opened).
- **Why people like averaging despite the theory.** Regret and loss aversion (Statman, 1995, *Journal of Portfolio Management* 22(1): 70; unverified, known only through citations).
- **The critique, in its strongest form.** India's SIP success stories date from years when few people ran SIPs, valuations were low and deposits paid 10% or more. Today valuations are high, especially in mid and small caps; deposit rates are lower; and the flood of SIP money may itself have removed the deep falls that make averaging pay. So the past is a poor guide. (Stated without naming its proponents.)
- **What the site already shows.** `/lab/sip/` covers SIP dates, frequency, step-ups, pausing, dip-buying, valuation-aware SIPs and time under water. The article links to those pages and doesn't repeat them.

## Data

| Input | What | Traps |
|---|---|---|
| `portal:asset_tri_daily` | NSE total-return indices: Nifty 500 from January 1995, Nifty 50 from June 1999, Midcap 150 and Smallcap 250 from April 2005 | Nifty 500 1995–1998 is probably back-calculated by NSE, with some hindsight in constituents. Midcap 150 and Smallcap 250 before their 2016 launch are back-calculated. Both are flagged in every chart (dashed or marked) and split out in the era check |
| `reference/rbi_hbs74_deposit_rates.csv` | RBI Handbook 2009-10, Table 74: 1–3 year deposit rates, FY1975-76 to July 2010 (public; copied with its source line and hash) | Point-in-time rates of five public-sector banks from 1996-97, top of range |
| `databank:rbi_lending_deposit_rates` (table `wadtdr_outstanding`, all scheduled commercial banks) | RBI's weighted average interest rate on outstanding term deposits, monthly, from March 2013 | A different measure from the 1–3 year card rate: an average over all outstanding deposits, so it moves slowly and sits below the best fresh rate. July 2010 to March 2013 is joined by a straight line. (The weekly maximum-rate series the portal's long-history note uses is in the warehouse only from April 2024, so it can't fill the gap.) |
| `databank:nifty_index_valuations` | Nifty 50 trailing P/E, daily, from 1999 | NSE switched to consolidated earnings in 2021: every P/E used in Q4 comes from a 12-month mark no later than 2017 (10-year endings stop in 2026), so all are on the old standalone basis |
| `portal:macro_cpi_monthly` | All-India CPI, linked | Used only for the rupee examples in today's money |

Coverage confirmed on 2026-10-15 before writing this table: Nifty 50 P/E daily from January 1999; deposit rates as stated.

## Common conventions

- **The SIP:** ₹10,000 on the first NSE session of each month into the index's total-return series, less an index-fund expense ratio of 0.20% a year charged daily. Before tax (tax cost 0.4–0.6 points a year at 10 years, known; noted, not modelled).
- **Statement value** at the last session of month *m* of the SIP's life: units held × that session's level.
- **In the red at age *m*:** statement value below the money put in so far. **Depth:** value ÷ money put in − 1.
- **10-year result:** 120 instalments, valued at the last session of month 120; XIRR on the dated instalments and that value.
- **Start months:** every month with a full 10 years of data after it. Nifty 500: January 1995 to the latest eligible month (about 2016), roughly 260 start months, which is about **2.6 non-overlapping 10-year windows**. Mid and small caps: April 2005 on, about 1.3 windows. Every cross-start-month statistic is a description of this history, not a sample from a stable process, and is reported with its independent count. **No p-values across overlapping start months.**
- **Episodes:** consecutive start months that are all in the red at age *m* form one episode. The number of episodes is reported next to every share.
- **FD:** money accrues daily at the deposit rate known the day before, interest taxed yearly at 30% plus 4% cess (the realistic alternative for a salaried saver in a high bracket). The spliced rate probably runs low after 2010, which flatters "keep going" in Q2, so two sensitivities are fixed now: untaxed, and the rate plus 1 point from August 2010.

## Sub-questions

### Q1. When a SIP was in the red after a year or two, how did it end, and why?

- **Why a reader cares:** this is the reader's situation. If red SIPs usually ended badly, stopping makes sense; if they usually ended well, the red is noise.
- **Rival answers:** (a) red early means a bad market and a bad decade, so the ending is worse; (b) red early means cheap units, so the ending is better, as long as prices recover.
- **Estimand:**
  1. *(known, replicated)* Share of start months in the red at 12 and 24 months; the median 10-year XIRR of red against not-red start months. Nifty 500 from 1995.
  2. *(new)* The whole distribution for red against not-red: 5th, 25th, 50th and 75th percentiles and the worst 10-year XIRR, and the share that ended below the FD over the same instalments. All four indices.
  3. *(new)* By depth at 12 months: less than 10% below, 10–20% below, more than 20% below, and not in the red. Median 10-year XIRR and count per band (Nifty 500; mid and small caps where bands have at least 10 start months).
  4. *(new, the mechanism)* For each red-at-12-months SIP: the share of units held at month 120 that were bought while the SIP was in the red, against the share of money put in while it was in the red. The same for the share of final value.
- **Method:** descriptive comparison with episodes counted. Block-bootstrap 90% interval (block of 120 start months) on the red-minus-rest median gap, reported as indicative only.
- **Prediction P1:** (a) for all four indices, the median 10-year XIRR of SIPs red at 12 months is higher than that of the rest; (b) for the Nifty 500, the median rises with depth across the three red bands; (c) the share of units bought while in the red is at least 1.5 times the share of money put in while in the red.
- **Checks:** era_split (Nifty 500 starts 1995–2004 against 2005 onward), robustness (red at 24 months instead of 12; expense ratio 1% instead of 0.20%; value at 15 years where data allows)
- **Headline figure:** *outcomes* chart, the 10-year XIRR range (5th–95th, middle half, median) for "red at 12 months, by depth" and "not red", with episode counts. Job: answer. Second: units bought while red against money put in while red (job: mechanism). Third: one real SIP followed month by month, Nifty 500 started January 2008 (job: case).

### Q2. Did stopping a SIP that was in the red protect the investor?

- **Why a reader cares:** stopping is the decision on the table. Lab S4 measured pausing for every SIP; nobody has measured it for the people who actually feel like stopping.
- **Rival answers:** (a) stopping caps the damage when a fall keeps going, so it helps in long bear markets; (b) stopping gives up the cheapest instalments, so it costs, most of all for the deepest-red SIPs.
- **Estimand:** for every start month red at age *m* (12 and 24), four paths over the same 10 years and the same ₹12 lakh of savings:
  - **A, keep going:** the plain SIP.
  - **B, stop and hold:** no more instalments into equity after month *m*; units held; each later ₹10,000 goes into the FD.
  - **C, stop and switch:** units sold at month *m* (before tax), the proceeds and every later ₹10,000 into the FD.
  - **D, pause until back in the black:** instalments go into the FD until the held units' value is at or above the money put in, then the SIP resumes (the FD balance stays in the FD).
  - For each: the final value at month 120 and the paired gap with A in rupees. The share of start months where A ended ahead of each, and the median and worst gap.
- **Method:** paired comparison by start month, episodes counted; Nifty 500 headline, the other three indices as robustness.
- **Prediction P2:** A ends ahead of B and of C in more than 80% of red start months, and ahead of D in more than 65%. The median gap against C is larger for start months more than 20% in the red than for those less than 10% in the red.
- **Checks:** era_split, robustness (FD untaxed; FD rate +1 point from August 2010; *m* = 24; mid and small caps)
- **Headline figure:** paired gaps (A minus each strategy) in rupees, one row per strategy, with the share where A won in the title. Job: answer. Second: the gap by depth band (job: conditioning).

### Q3. When does a SIP's running return start to tell you how it will end?

- **Why a reader cares:** apps show the XIRR from the first month. Readers judge SIPs, and funds, on one or two years' numbers.
- **Rival answers:** (a) early returns are informative: a poor start means a poor fund or market and predicts a poor ending; (b) early returns are noise or even contrarian, because a poor start buys cheap units, and they only become informative late.
- **Estimand:** for Nifty 500 SIPs, at ages 6, 12, 24, 36, 60 and 84 months: the Spearman rank correlation between the running XIRR at that age and the final 10-year XIRR; and the share of SIPs in the bottom third at that age that ended in the bottom third at 10 years (33% if unrelated). Also the first age at which the correlation exceeds 0.5.
- **Method:** descriptive; independent count reported (about 2.6 windows). Midcap 150 and Smallcap 250 from 2005 as robustness.
- **Prediction P3:** the correlation is below zero at 12 and 24 months and does not exceed 0.5 before 60 months.
- **Checks:** era_split, robustness (15-year ending instead of 10, where data allows; mid and small caps)
- **Headline figure:** the correlation by age, with the 0 and 0.5 lines and the independent count. Job: answer. Second: the bottom-third persistence by age against the 33% line (job: spread).

### Q4. Was the bonus for a bad start really about cheap prices, and could it fail?

- **Why a reader cares:** if red SIPs did better only because the fall made the market cheap, then a fall that leaves the market expensive (the critique's fear for today) might not pay. This is the honest limit on Q1's comfort.
- **Rival answers:** (a) the bonus came from valuation: falls left the market cheap, and the cheap units re-rated; where the market was still dear after the fall, red SIPs did no better; (b) averaging into any fall that later recovers pays, whatever the valuation level.
- **Estimand:** for Nifty 50 SIPs (P/E from 1999) red at 12 months: the median 10-year XIRR for those whose Nifty 50 trailing P/E at month 12 was below the median of all month-12 P/Es, against those above it. The Spearman correlation between P/E at month 12 and the 10-year XIRR, within red SIPs and within all SIPs. Plus, *descriptive*: where today's Nifty 50 P/E and deposit rate sit in their own histories (percentiles), dated, clearly marked as context for the reader and not a forecast.
- **Method:** descriptive; with P/E only from 1999 and 10-year endings to about 2016, this rests on roughly 1.7 independent windows and two or three episodes of red. It cannot settle the question. It shows which story the Indian record leans towards, and the article says so.
- **Prediction P4:** red SIPs with month-12 P/E below the median have a median 10-year XIRR at least 2 points higher than red SIPs with P/E above it.
- **Checks:** era_split (not possible with this sample: recorded as "not possible" with the reason), robustness (P/E at the start month instead of month 12)
- **Headline figure:** scatter of month-12 P/E against 10-year XIRR, red SIPs in colour and the rest grey, episodes labelled. Job: mechanism. Second: today's P/E and deposit rate percentiles (job: caveat).

## Naive questions answered as context

- *Why can a SIP be in the red when the market is up since I started?* The arithmetic of averaging (a short worked example).
- *Why is my app's XIRR −30% when I've lost only 8%?* Annualising a few months' money (a worked example).
- *Is FY2026 unusual?* The Nifty 500 SIP started April 2025, valued at end-March 2026, placed on the historical distribution of 12-month results.
- *Do SIPs ever lose money over 10 years?* (known) None of the Nifty 500 start months since 1995 did; but a 10-year SIP fell below an FD in a few (known).

## Questions I won't ask

- **Individual funds, active against index, direct against regular:** the fund NAV history is being rebuilt and isn't ready. A later study.
- **What SIPs will return from here:** no forecast. Q4's percentiles are context only.
- **Whether SIP flows caused shallower falls:** about ten years of large SIP flows can't separate cause from coincidence.
- **Tax planning, step-ups, SIP dates, weekly SIPs:** covered by the lab; linked.
- **Other countries' lost decades (Japan):** index licences not cleared. Mentioned in words only, as the critique's strongest example.

## What would change my mind

- If red SIPs ended *worse* than the rest for any index with two or more episodes, the comforting story is wrong for that index, and the article leads with it.
- If stopping and holding (B) beat keeping going (A) in a third or more of red start months, "don't stop" isn't the lesson. The lesson becomes "it depends", and the article says on what.
- If Q4 shows red SIPs did no better when the market was still dear, the bonus is a valuation story, and the critique has a real point about today.

## Headline numbers for the independent recompute

Q1: share red at 12 months, median 10-year XIRR red and not red (Nifty 500), median by depth band, share of units bought while red. Q2: share of red start months where A beat B, C and D, and median gap A−C (Nifty 500, *m* = 12). Q3: correlations at 12, 36 and 60 months. Q4: the two medians and the within-red correlation.

## Amendments

None yet.
