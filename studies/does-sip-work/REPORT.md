# Study report: does-sip-work

How this study was actually done, written by the lead researcher (an AI model, edited by the people on the study) when it finished. The reader-facing article is `article.mdx`; the frozen plan is `plan.md`.

## What I set out to ask

The owner asked for the site's canonical piece on SIPs: does a SIP work, on what, over how long, and does the way it is run matter. This was the third attempt. The October 2026 study "Is SIP bad?" asked 17 questions at equal depth and read as a results log. A first draft of this redo asked four narrow questions about SIPs in the red, which the owner judged too thin. The final plan has six chapters, each making one claim, with 22 sub-questions. Five of them are headline findings, told in depth.

Sub-questions were kept if they answered a decision a saver actually makes. After a gap review, four were added: how much a goal needs, the tax clock on each instalment, whether volatility helps, and how long real SIPs last. Left out, each with a reason in the plan: real mutual funds (the NAV history is being rebuilt), international SIPs (licences), the withdrawal phase, PPF (no rate history yet), and real estate.

Eleven questions were already answered by the October study or the portfolio lab, and I had seen those results. They are labelled "known" and recomputed with fresh code as replications, with no predictions. Eleven are new, each with a prediction frozen before any result.

## What I found

- Q1 (known): no Nifty 500 SIP lost money over ten years since 1995; 29% lost over one year. A direct answer.
- Q2–Q4, Q7, Q8 (known): replicated within the expected convention gap (this study is before tax with a 0.2% cost; the lab was after tax).
- Q5 (new, P5 held): a 60/20/20 mix cost more in the typical case than it gained in a bad one at ten years, and the reverse at five and fifteen.
- Q6 (new, P6 failed): rebalancing each April added 0.8 points a year, not under 0.5.
- Q9 (part new, P9 failed): de-risking into FDs over the last three years lowered even the bad case.
- Q10 (new, P10 failed): the 12% calculator was conservative; its amount reached ₹1 crore in 90% of 15-year windows.
- Q13 (new, P13 held): a SIP is never fully long-term while it runs; short-term units hold a smaller share of the gains.
- Q14 (new, P14 failed): volatility barely helped, and the total return mattered no more than volatility.
- Q16 (part new, P16 failed in parts a and b; c held): Nifty 500 SIPs in the red at a year ended better (17.9% against 14.1%), and the unit mechanism holds. But the bonus did not grow with depth, and it was absent for mid caps.
- Q17 (new, P17 failed on depth only): keeping going beat every alternative in 100% of Nifty 500 red start months. Stopping's cost did not grow with depth.
- Q18 (new, P18 held): early returns pointed the wrong way, and the correlation with the ending passed 0.5 only at 99 months.
- Q19 (new, P19 failed): cheap and dear markets gave red SIPs about the same ending.
- Q20, Q21 (known): investors' timing cost 0.1 points against a fair benchmark; falls were shallower since 2016, cause unknown.
- Q22 (new, P22 held): the implied average SIP account life is about 1.8 years, never above 4.9 outside the clean-up.

Four of eleven predictions held. The failures are reported in the article as plainly as the successes.

## What changed from the plan

All changes are logged under the plan's Amendments (2026-10-15). They came after the first full run, so after seeing results:
- A bug fix in Q11b (see below).
- `pause_lab`, the October lab's pause rule, added to Q12 as a replication variant beside the plan's own rule. It is labelled in the article.
- `…_all_starts` added to Q16, so the red-at-a-year share can be compared with October's denominator.
- Constants and counts the article quotes (tax rates, expense ratios, the count of predictions held, the AMFI account count) recorded as facts, so the numeric gate can trace them. No result changed.

No question was dropped and no prediction was regraded.

## Mistakes and how they were caught

- **Q11b bug, caught by the replication check.** In the "save in an FD and invest each April" path, each April's own instalment stayed in the FD for another year. The first run showed the SIP ahead in 78.6% of windows, against 50.4% in October. The plan's rule (investigate any gap over 1 point) forced a look. After the fix: 50.7% from 2005, matching October.
- **8.4% where the data said 8.35%, caught by the review.** I typed 8.4% for the ten-year real median, and the figure title said 8.3%. The numeric gate passed my 8.4% because it matched a *different* fact. The review flagged the mismatch; the text now says 8.3%.
- **Overclaiming, caught by the review.** The dek said keeping a losing SIP going beat stopping "every time". That is true only for Nifty 500 SIPs at 12 months: small caps and the 24-month cases had exceptions. Fixed in the dek and the closing box.
- **Plan promises missed, caught by the review.** Japan as the critique's strongest example, the AMFI account count, the depth result in Q17 and the total-return correlation in Q14 were all in the plan but missing from the draft. All added.
- **Desk bugs found by this study:** `desk check` crashed on a study's own reference file (added a `file:` input type, with a test); the review reply was cut off because Gemini's hidden reasoning counts against the output limit (limit raised to 65k, plus one retry on a bad reply).
- **A suspected bug that wasn't.** The P/E "double up when cheap" rule showed exactly zero effect. A check showed it fired in 23 months overall and only a handful after 2005, so zero is real.

The independent recompute matched all 23 headline numbers both times, most to eight decimal places. It caught nothing, but it confirms the stopping paths, the taxed FD and the goal amounts were computed as defined.

## Dead ends

- **The four-question draft (`sip-in-the-red`).** Replaced at the owner's request by this canonical plan. Its questions became Q16–Q19.
- **The G-sec index as the FD stand-in.** The owner suggested it for simplicity. I kept the FD, because a saver's real alternative is a deposit, with no price swings and taxed every year, and because the G-sec index starts only in 2001. The G-sec index is the bond leg of the mixes instead.
- **Two partial deposit-rate sources.** A splice of the 2009-10 Handbook with RBI's weighted-average deposit rate, and the rbihub mirror of the Handbook table (its pre-2000 columns are shifted). Both were dropped for DBIE report 282 from the Data bank's raw mirror.
- **Figures not in the article:** a single-bar chart of the FY2026 SIP's first year was dropped; the opening gives the number in words. All 44 remaining figures are used. Several were drawn as category bars where a time axis would be better (Q12 days, Q18 ages), because the kit's time forms need dates.

## What a sceptical reader should check first

1. **Q17's 100%.** It rests on 83 start months but only about 16 separate episodes, and on a taxed FD at the top of RBI's range. With untaxed FDs, keeping going won 98.8% of the time against stopping and holding. Rerun `q17` with other deposit assumptions (`SD.FD(…, bump=…)`) to see where it breaks.
2. **The early Nifty 500 years (1995–98) are probably back-calculated by NSE.** Results split by era (`…_1995_2004` against `…_2005_on`) differ a lot: the SIP against FD-then-April won every pre-2005 window and only half after. Treat pre-2005 findings as weaker.
3. **Mid and small caps before 2016 are back-calculated.** Q4's mid-cap lead and Q16's mid-cap result lean on that history.
4. **Q22's implied life is a stock-flow approximation from industry totals.** Accounts are not investors, and closures include SIPs that reached their end date. The direction is robust; the 1.8 years is not precise.
5. **The numeric gate proves a number exists in the results, not that the sentence uses the right one** (see the 8.4% mistake). Spot-check sentences against `results/results.json`.

## What the desk should change

- **The numeric gate should be able to pin a number to its fact.** An optional inline marker in drafts, stripped on publish, would catch the 8.4% kind of error. Adopt when a second study hits it.
- **Plan constants belong in the plan, not in compute.** About 40 context numbers and constants were added so the gate could trace them. A `## Constants` block in plan.md, read by `desk check`, would be cleaner. Proposed, not built.
- **A slow compute (about five minutes) made each fix cost a full rerun.** `compute.py <question>` debug mode helped; caching inputs between runs would help more.
- **The review's "plan promised X" catches were the most valuable.** Keep that checklist item prominent.
- **Adopted now:** `file:` inputs; the review's 65k limit and retry; canonical studies in chapters (`guides/questions.md`); as many charts as a question needs (`guides/charts.md`).

<!-- auto:start -->

## The record

_Generated by `desk report` from the study's files and git history. Do not edit by hand._

### Timeline

- Plan frozen at `b974bf7` on 2026-10-15.
- Tag `does-sip-work/plan-frozen`
- `33a3e8b 2026-10-15 Desk: canonical studies in chapters, with headline findings and known/new status`
- `122082e 2026-10-15 does-sip-work: canonical SIP plan for approval (not frozen)`
- `45b3432 2026-10-15 does-sip-work: four new questions and a myths table`
- `b974bf7 2026-10-15 does-sip-work: plan approved (freeze commit)`
- `083455e 2026-10-15 does-sip-work: record the freeze`
- `bd26933 2026-10-15 does-sip-work: first run, replication gaps investigated, one bug fixed`
- `8bbf6b7 2026-10-15 does-sip-work: results, 45 figures and the article draft; free checks pass`
- `029462a 2026-10-15 does-sip-work: review answered, recompute 23/23, report written; awaiting sign-off`

### Sub-questions

- **Q1.** How often did an equity SIP lose money, trail an FD, or trail inflation? (declared checks: era_split, robustness)
- **Q2.** What range of returns should a SIP investor expect? (declared checks: era_split, robustness)
- **Q3.** What did SIPs earn after inflation? (declared checks: era_split)
- **Q4.** Large, mid or small caps, gold or government bonds? (declared checks: era_split, robustness)
- **Q5.** What does diversifying a SIP cost, and what does it buy? (declared checks: robustness)
- **Q6.** Does rebalancing a diversified SIP each year help? (declared checks: robustness)
- **Q7.** How much steadier are longer SIPs? (declared checks: era_split)
- **Q8.** How much did the start date matter? (declared checks: era_split)
- **Q9.** Which years of a SIP matter most, and should you get out near the goal? (declared checks: era_split, robustness)
- **Q10.** How much do you need to put in each month to reach a goal, and what does starting late cost? (declared checks: era_split, robustness)
- **Q11.** SIP or lump sum? (declared checks: era_split)
- **Q12.** Do dates, frequency or timing tricks matter? (declared checks: truncation_stable, robustness)
- **Q13.** Is a SIP "long-term" after a year? The tax clock on every instalment (declared checks: robustness)
- **Q14.** Does volatility help a SIP? (declared checks: era_split, robustness)
- **Q15.** How deep and how long do SIPs go under water? (declared checks: era_split)
- **Q16.** When a SIP was in the red after a year or two, how did it end, and why? (declared checks: era_split, robustness)
- **Q17.** Did stopping a SIP that was in the red protect the investor? (declared checks: era_split, robustness)
- **Q18.** When does a SIP's running return start to tell you how it will end? (declared checks: era_split, robustness)
- **Q19.** Was the bonus for a bad start really about cheap prices, and where are prices now? (declared checks: era_split, robustness)
- **Q20.** Did investors' SIP money arrive at bad times? (declared checks: robustness)
- **Q21.** Have market falls become shallower since SIP money grew? (declared checks: none)
- **Q22.** How long do real SIPs last, and what does the stoppage ratio count? (declared checks: robustness)

### Amendments to the plan

**2026-10-15, after the first full run (code and replication, no prediction regraded).** The plan allows differences from the October targets of up to 1 point from conventions alone, and asks for anything larger to be investigated. Four were:
- *Q11b, SIP against FD-then-April:* a bug in my code. Each April's own instalment stayed in the FD for another year instead of moving with the balance, as the plan's estimand requires. Fixed. The pre-fix result (SIP ahead in 78.6% of windows) is kept in the report.
- *Q12, pausing:* a definition difference. The plan says only "pausing during a 20% fall". My rule pauses from the first session 20% or more below the peak until the index is back at its previous peak, with the paused money kept in the FD (as Q17's path D). The October lab paused from a month-end more than 20% below the peak until a month-end back above −10%. Both are reported, labelled; the lab's rule is added as `pause_lab`.
- *Q5 and Q15, the deepest fall below the money put in:* the lab used daily statement values; this plan specifies month-end values, so its falls are shallower. No change.
- *Q5, the mixes' medians (about 1.3 points higher):* the lab taxed debt and gold at slab rates and used NSE's 10-year G-sec index; this plan is before tax and uses the 5-year index. No change.
- *Q16, the share in the red at 12 and 24 months:* the October figure counted every start month to the data end; this plan counts start months with a full 10 years. Both are now recorded (`…_all_starts`).

### Results

- Computed 2026-10-15T08:02:53+00:00 from `compute.py` (sha256 `f89f078e9d22`).
- 868 facts, 0 of them exploratory; 0 exploratory variants tried.
- Inputs:
  - `portal:asset_tri_daily`: asset_tri_daily.parquet, sha256 `c3cf5febecc3`
  - `portal:macro_cpi_monthly`: macro_cpi_monthly.parquet, sha256 `40cbfa3aca7e`
  - `databank:nifty_index_valuations`: niftyindices_nifty_index_valuations_warehouse_20261015t055811986094z.parquet, sha256 `03dd032cf5f2`
  - `databank:india_data_hub_series`: india_data_hub_india_data_hub_series_warehouse_20261015t050209340117z.parquet, sha256 `a00cfc6a9431`
  - `file:studies/does-sip-work/reference/rbi_deposit_rates_1_3y.csv`: rbi_deposit_rates_1_3y.csv, sha256 `0bf470c69f86`

| Check | Passed | Detail |
|---|---|---|
| input_no_duplicates[d] | yes | 0 duplicate rows on ['d'] |
| input_daily_move[Nifty 500] | yes | 0 of 7876 values outside [-0.25, 0.25] |
| input_daily_move[Nifty 50] | yes | 0 of 6788 values outside [-0.25, 0.25] |
| input_daily_move[Nifty Midcap 150] | yes | 0 of 5341 values outside [-0.25, 0.25] |
| input_daily_move[Nifty Smallcap 250] | yes | 0 of 5341 values outside [-0.25, 0.25] |
| input_daily_move[Gold] | yes | 0 of 6509 values outside [-0.25, 0.25] |
| input_daily_move[G-sec 5-year] | yes | 0 of 6241 values outside [-0.25, 0.25] |
| input_cpi_monthly_change | yes | 0 of 455 values outside [-0.05, 0.08] |
| q1:era_split | yes | below-FD and loss shares split at 2005 starts recorded for 5 and 10 years |
| q1:robustness | yes | FD at the bottom of RBI's range and after-tax versions recorded |
| q2:era_split | yes | 10-year medians by era recorded |
| q2:robustness | yes | Nifty 50 from 1999 recorded |
| q3:era_split | yes | real 10-year medians by era recorded |
| q4:era_split | yes | not possible within the menu's 2005 window; back-calculated mid/small-cap history flagged instead |
| q4:robustness | yes | Nifty 50 recorded as the large-cap line beside the Nifty 500 |
| q5:robustness | yes | 60/40 and equal thirds recorded beside 60/20/20; 60/20/20 without rebalancing recorded |
| q6:robustness | yes | six-monthly rebalancing and 15-year windows recorded |
| q7:era_split | yes | 10-year ranges by era recorded |
| q8:era_split | yes | band medians by era recorded |
| q9:era_split | yes | glide outcome by era recorded |
| q9:robustness | yes | 12-month switch and FD at the bottom of the range recorded |
| q10:era_split | yes | 15-year 80% amounts by era recorded |
| q10:robustness | yes | real ₹1 crore and 60/20/20 recorded |
| q11:era_split | yes | lump sum and FD-then-April by era recorded |
| q12:truncation_stable | yes | P/E 'cheap' flags for 168 months to 2015-12-31 identical when later data is removed |
| q12:robustness | yes | Nifty 50 cost effect recorded; 15-year date effect not computed (see notes) |
| q13:robustness | yes | no exit load and ₹50,000 a month recorded |
| q14:era_split | yes | correlations by era recorded |
| q14:robustness | yes | Smallcap 250 and gold recorded |
| q15:era_split | yes | longest stretch by era recorded |
| q16:era_split | yes | red and rest medians by era recorded |
| q16:robustness | yes | 24 months, 1% expense ratio and 15-year ending recorded |
| q17:era_split | yes | A-beat shares by era recorded |
| q17:robustness | yes | untaxed FD, FD at the bottom of range, 24 months and the other three indices recorded |
| q18:era_split | yes | 12-month correlation by era recorded |
| q18:robustness | yes | Midcap 150, Smallcap 250 and 15-year ending recorded |
| q19:era_split | yes | not possible: about 1.7 independent windows; recorded as such |
| q19:robustness | yes | P/E at the start month recorded |
| q20:robustness | yes | Midcap 150 and Smallcap 250 recorded |
| q22:robustness | yes | with the clean-up months and with new accounts as the flow recorded |

### Independent recompute

Model: deepseek-flash; 2 attempt(s). Its script is `checks/recompute_script.py`.

| Fact | Ours | Theirs | Tolerance | Match |
|---|---|---|---|---|
| q1_n500_3y_lost | 0.15606936 | 0.15606936416184972 | 0.005 | yes |
| q1_n500_5y_lost | 0.06521739 | 0.06521739130434782 | 0.005 | yes |
| q1_n500_10y_lost | 0.0 | 0.0 | 0.005 | yes |
| q1_n500_5y_below_fd | 0.1552795 | 0.15527950310559005 | 0.01 | yes |
| q1_n500_10y_below_fd | 0.00381679 | 0.003816793893129771 | 0.01 | yes |
| q16_n500_red12 | 0.31679389 | 0.31679389312977096 | 0.005 | yes |
| q16_n500_red_p50 | 0.17869818 | 0.1786981799901547 | 0.0005 | yes |
| q16_n500_rest_p50 | 0.1407578 | 0.14075779987678205 | 0.0005 | yes |
| q16_n500_b20_p50 | 0.14500358 | 0.14500357590267232 | 0.0005 | yes |
| q16_n500_units_to_money_ratio_p50 | 1.61773577 | 1.6177357678658295 | 0.02 | yes |
| q17_n500_m12_A_beat_B | 1.0 | 1.0 | 0.01 | yes |
| q17_n500_m12_A_beat_C | 1.0 | 1.0 | 0.01 | yes |
| q17_n500_m12_A_beat_D | 1.0 | 1.0 | 0.01 | yes |
| q17_n500_m12_gap_C_p50 | 1482046.15292757 | 1482046.1529275388 | 2000.0 | yes |
| q18_n500_10y_corr_12m | -0.3465821 | -0.3465821003526043 | 0.01 | yes |
| q18_n500_10y_corr_36m | 0.09599318 | 0.09599317544374128 | 0.01 | yes |
| q18_n500_10y_corr_60m | -0.0203112 | -0.02031119522814856 | 0.01 | yes |
| q10_n500_15y_need_50 | 16454.55316227 | 16454.553162268974 | 50.0 | yes |
| q10_n500_15y_need_80 | 19458.95771258 | 19458.95771258352 | 50.0 | yes |
| q10_n500_15y_need_95 | 22809.92280693 | 22809.922806930543 | 50.0 | yes |
| q20_n500_industry | 0.11171912 | 0.11171911613684193 | 0.0005 | yes |
| q20_n500_trend | 0.1130728 | 0.11307280098552186 | 0.0005 | yes |
| q22_life_latest | 1.79739857 | 1.7973985672311907 | 0.05 | yes |

Ambiguities the recomputing model resolved:
- Months: used every calendar month with at least one session from Jan-1995 through Sep-2026 (ordering assumed contiguous); Oct-2026 dropped.
- 'In the red' and 'lost money' use strict '<' (value below money put in).
- FD tax at the final valuation date is applied even when that date is not 31 March, as the specification states.
- Path D keeps a single 'paused' flag that, once cleared, is never re-armed; the resumed SIP buys units for every later month.
- AMFI industry/trend SIPs value all units at the level of the very last row of tri_500.parquet.

### Review and cold read

Model: gemini-3.8-flash. Overall: The article's biggest weakness is that it occasionally overstates findings into absolute claims—such as asserting that continuing a losing SIP beat stopping 'every time' and phrasing takeaways as prescriptive financial advice—while omitting mandated nuances like drawdown depth breakdowns and the critique comparison to Japan. Its biggest strength is its rigorous, rupee-denominated empirical framework that transparently tests popular investing heuristics and exposes the severe historical penalty of pausing or stopping instalments during market drawdowns.

| Id | Severity | Problem | Response |
|---|---|---|---|
| r1 | must_fix | Claiming that keeping a losing SIP going beat stopping 'every time' overstates the findings, as small-cap SIPs that stopped beat continuing in 11% of start months and 24-month red Nifty 500 SIPs beat continuing in 1.6% of cases. | fixed: the dek now says 'for SIPs in the red after a year, keeping going beat stopping in 100% of cases'; the body already names the small-cap and 24-month exceptions. |
| r2 | must_fix | The summary takeaway read alone overclaims by stating stopping left people worse off 'in every case in this record', contradicting the study's own small-cap and 24-month findings. | fixed: the closing box now limits the claim to broad-market SIPs in the red after a year. |
| r3 | must_fix | Phrasing research findings as imperative directives ('Don't spend energy...', 'Spend it on choosing...') constitutes direct financial advice rather than empirical reporting. | fixed: the closing box now describes what mattered in the record instead of telling the reader what to do. |
| r4 | must_fix | The draft omits international lost decades (specifically Japan), which the plan explicitly required as the critique in its strongest form. | fixed: Chapter 6 now names Japan as the critique's strongest example, in words only, as the plan said (index licences not cleared, so no data). |
| r5 | should_fix | The draft fails to report the planned estimand and second figure examining the rupee cost of stopping broken down by drawdown depth bands, omitting the reason why prediction P17 failed. | fixed: Q17 now reports the depth-band result and why P17 failed. |
| r6 | should_fix | The draft omits the planned estimand comparing the SIP edge's correlation with the window's total return (-0.18), obscuring the testing of Prediction P14. | fixed: Q14 now reports the total-return correlation (−0.18) and says P14 failed. |
| r7 | should_fix | The abbreviation 'STP' is used in the chart caption without ever being spelled out or explained in the text. | fixed: STP is defined at first use in the text. |
| r8 | should_fix | The financial ratio 'P/E' is introduced without explaining what a price-to-earnings ratio measures. | fixed: P/E is defined at first use. |
| r9 | should_fix | The acronym 'XIRR' is used without defining what it stands for or clarifying how it measures money-weighted returns across periodic instalments. | fixed: the first XIRR now says it is the annualised return across dated instalments; I kept it short rather than spelling out the acronym. |
| r10 | should_fix | Figure F.q12_days (showing returns across days 1 to 28 of the month) is placed directly after text discussing waiting for 20% falls rather than near the paragraph discussing SIP dates. | fixed: the date-of-month figure now sits after the sentence about SIP dates. |
| r11 | should_fix | Juxtaposing 'at current prices, after inflation' with 'in rupees of the day' creates a confusing phrasing that requires re-reading to understand purchasing power deflations. | fixed: rewritten as 'Aiming for ₹1 crore of current purchasing power, with the goal adjusted for inflation…'. |
| r12 | minor | The draft omits the exact AMFI count of outstanding SIP accounts, which the approved plan required to be included from the data. | fixed: the opening now gives AMFI's count of open SIP accounts (new fact q22_outstanding_latest). |
| r13 | minor | The text reports an 8.4% real return, whereas the exact result is 8.35% (rounding down to 8.3%, as correctly shown in Figure F.q3 caption). | fixed: 8.3% in the text and the scorecard, matching the exact 8.35% (8.347%). The numeric gate had passed 8.4% by matching a different fact, a known limit of the gate. |

The cold reader's answers to each sub-question, from the article alone:
- **q1**: A Nifty 500 SIP lost money in 29% of one-year windows, 16% of three-year windows, 7% of five-year windows, and 0% of ten-year windows (with no start month losing from eight years on), while trailing a taxed fixed deposit in 38%, 25%, 16%, and 0.4% of windows respectively, and trailing inflation in 0.8% of ten-year windows.
- **q2**: Ten-year Nifty 500 SIPs returned a median of 14.6% a year across a wide range (5th percentile 9.8%, worst 4.3%, best 32.7%), with ₹10,000 monthly over 20 years typically yielding ₹1.30 crore (ranging from ₹1.00 crore to ₹1.54 crore).
- **q3**: After inflation, the typical ten-year Nifty 500 SIP earned 8.4% a year (with 5% of periods earning under 2.0% and 0.8% losing purchasing power), whereas a taxed fixed deposit lost 0.7 percentage points a year to inflation.
- **q4**: Over ten years from 2005, mid caps had the highest median (17.9%) and bad-case (12.0%) returns, small caps had high medians (15.3%) but lost money in their worst start (-0.5%) with a 54% maximum fall, the Nifty 500 returned 13.5% (bad case 9.3%), and government bonds returned 8.0% with only a 4% maximum fall.
- **q5**: Over ten years, a 60/20/20 mix gave up ₹1.4 lakh of median final value to gain ₹0.2 lakh at the 5th percentile while reducing the worst drawdown from 44% to 25%, whereas over 5 and 15 years the bad-case rupee gain exceeded the median rupee sacrificed.
- **q6**: Rebalancing a 60/20/20 SIP each April added a median 0.8 percentage points a year over ten years and improved returns in at least nine in ten start months.
- **q7**: Longer SIP horizons compressed the 5th-to-95th percentile spread of annualised returns from 41 percentage points at five years to 3.5 points at twenty years, yet the 20-year rupee multiple still ranged widely between 4.2 and 6.4 times total contributions.
- **q8**: The starting year caused ten-year median returns to range widely from 9.3% in 2010 to 26.5% in 1997, whereas starting near a market peak versus 10% below it made almost no difference (13.6% versus 14.9%).
- **q9**: The first five years of instalments accounted for 55% of a 15-year SIP's final value, and switching the portfolio to fixed deposits over the final 36 months ended ahead in only 19% of start months while lowering the 5th-percentile corpus from ₹43.8 lakh to ₹39.5 lakh.
- **q10**: Reaching ₹1 crore in 15 years required monthly contributions of ₹16,455 for 50% confidence, ₹19,459 for 80% confidence, and ₹22,810 for 95% confidence (versus ₹21,011 from a 12% calculator), while delaying by five years forced contributions to jump to ₹21,612 a month.
- **q11**: For an investor with an existing lump sum, investing immediately beat a 12-month STP in 57% of start months; for a salaried saver, monthly SIPs beat saving in an FD and investing annually in 73% of start months.
- **q12**: Execution dates, weekly frequency, and valuation rules altered 10-year returns by 0.2 percentage points or less, whereas pausing during a 20% crash or incurring a 1% higher expense ratio reduced annual returns by 1.1 to 3.8 percentage points.
- **q13**: A SIP is never fully long-term while active because each monthly instalment resets its own one-year clock; at two years, 50% of units remain short-term (holding 27% of gains), and redemption costs fluctuate as exit loads lapse and gains exceed the ₹1.25 lakh annual exemption.
- **q14**: Volatility did not reliably enhance SIP results, showing only a 0.23 rank correlation with the SIP's return edge over the buy-and-hold index (and −0.05 after 2005) because extra units bought during dips were counterbalanced by expensive units bought at peaks.
- **q15**: Nearly all Nifty 500 SIPs (97%) experienced underwater periods, enduring a maximum drawdown of 44% below invested capital and a longest continuous underwater stretch of 38 months.
- **q16**: Nifty 500 SIPs in the red after 12 months achieved higher median 10-year returns than those in the black (17.9% versus 14.1%) because the 18% of money deployed while underwater acquired 30% of total units, though this bonus did not materialize in mid caps.
- **q17**: For Nifty 500 SIPs in the red at 12 months, continuing instalments beat stopping, switching to FDs, or pausing in 100% of historical start months (saving a median ₹1.4 lakh to ₹14.8 lakh), although in small caps stopping beat continuing in 11% of cases.
- **q18**: A SIP's running return is uninformative or slightly misleading early in its life (showing a −0.35 correlation with final 10-year returns at 12 months) and does not surpass a 0.5 correlation until 99 months.
- **q19**: Historical Nifty 50 SIPs in the red at 12 months finished similarly whether trailing P/E was low or high (14.8% versus 14.3%), while currently Nifty 50 P/E stands at its 35th percentile and deposit rates at their 25th percentile.
- **q20**: Aggregate SIP inflows did not exhibit adverse timing; when compared against a benchmark growing at the inflows' 23% annual trend, actual investor cash flows trailed by only 0.1 percentage points (11.2% versus 11.3%).
- **q21**: Market drawdowns were somewhat shallower after 2016 (median fall of 16% versus 20% prior to 2016), but ten years of data is insufficient to prove that SIP inflows caused this moderation.
- **q22**: Based on AMFI closure data, the implied average lifespan of a SIP account is roughly 1.8 years (and has never exceeded 4.9 years outside cleanups), while the April 2025 closure spike to 3.5 times registrations was a dormant account cleanup artifact.

### Model calls and cost

| When | Role | Model | Tokens in / out | ₹ |
|---|---|---|---|---|
| 2026-10-15T07:46:25+00:00 | recompute | deepseek-flash | 2,738 / 32,000 | 3.45 |
| 2026-10-15T07:49:01+00:00 | recompute | deepseek-flash | 2,754 / 31,459 | 3.39 |
| 2026-10-15T07:52:32+00:00 | review | gemini-3.8-flash | 55,313 / 1,274 | 4.07 |
| 2026-10-15T07:58:10+00:00 | review | gemini-3.8-flash | 55,313 / 4,188 | 5.03 |
| 2026-10-15T08:05:55+00:00 | recompute | deepseek-flash | 2,738 / 32,000 | 3.45 |
| 2026-10-15T08:07:22+00:00 | recompute | deepseek-flash | 2,754 / 17,349 | 1.90 |

Total: ₹21.29. Every request and reply is in `checks/transcripts/`. The lead model's work (plan, code, article, this report) ran in an interactive session and is not metered here.

### Last `desk check`

2026-10-15T08:15:25+00:00: plan_shape ok, plan_frozen ok, results_fresh ok, checks_passed ok, declared_checks ok, questions_answered ok, figures_fresh ok, figures_complete ok, numbers_traced ok, headline_confirmatory ok, style ok, sections ok, reader_copy_clean ok, front_matter ok, recompute ok, review_answered ok, report ok, budget ok, human_read pending

<!-- auto:end -->
