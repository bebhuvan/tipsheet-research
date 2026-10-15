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
- **Four slips caught by the sentence audit (`desk audit`).** One wrong attribution: the text said "the industry's money earned 11.3%", but 11.3% was the trend SIP (the industry earned 11.2%). The gate matched a number to the wrong fact: "41 points to 3.5", printed without a unit, matched the stoppage ratio of 3.53 instead of the 3.5-point spread. One number had no fact behind it ("12% deposits", the critique's phrase). One was imprecise ("eight years in", where the result is 99 months). All four were fixed. Eight more flags were false alarms (plan definitions, or a fact whose name misled the auditor), answered in `checks/responses.json`.
- **The second review caught real misses**, after the portfolio comparisons were added. The "SIP myths, checked" table the plan promised had never been written; the 24-month stopping result was overstated (98%, not 100%); and a chart description still talked about dots after the redesign.
- **Charts the owner found grey and clumsy.** Research pages draw one- and two-series charts in grey (the site's `few` mode), so "before" and "after inflation" were the same colour; there were also dot plots with value columns and one- and two-bar charts. The figures were redesigned: colour follows the portfolio, grouped bars, weak charts cut. I had screenshots of the first set and did not question the grey.
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
- **The sentence audit needed two fixes before it was useful.** The first run flagged 62 "issues", almost all false. Number words ("ten-year", "one in twenty") were being audited as claims, and each number's candidate facts were capped at six, which often cut off the right one. After both fixes: 13 flags, four real. The audit is now incremental (unchanged sentences keep their verdicts), so a small edit costs a few rupees, not ₹45.
- **DeepSeek's reasoning can eat the whole output budget.** At 32k tokens, several audit batches and one recompute attempt returned nothing. All DeepSeek roles now have 64k. About ₹15 was wasted on retries.
- **Fact names should explain themselves.** `q8_n500_10y_worst_year_median` misled the auditor ("median of the worst year"). A plain note on every fact would help the audit and readers of the results.
- **Adopted now:** `file:` inputs; the review's 65k limit and retry; `desk audit` (replaced the hand spot-check), incremental; `desk publish --preview`; a check that every figure the article uses exists; canonical studies in chapters (`guides/questions.md`); as many charts as a question needs (`guides/charts.md`).

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
- `eec5097 2026-10-15 does-sip-work: portfolio comparisons and a chart redesign`
- `bcdcdfb 2026-10-15 does-sip-work: second review answered; the myths table the plan promised`

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

**2026-10-15, after results, at the owner's request: Q1 and Q2 for diversified SIPs (exploratory).** The owner noted that leading with an all-equity SIP can mislead, since many savers hold a mix. Added: the distribution of returns (5th, 50th, 95th percentile, worst) and the shares that lost money, trailed an FD and trailed inflation, at 1, 3, 5, 7, 10 and 15 years, for the Nifty 500, 60/20/20 and equal thirds, all over the same start months from April 2005 and rebalanced each April. No prediction; the facts are tagged exploratory and kept out of the title, dek and finding.

### Results

- Computed 2026-10-15T08:46:45+00:00 from `compute.py` (sha256 `c1a90e604c73`).
- 1042 facts, 170 of them exploratory; 20 exploratory variants tried.
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

Exploratory variants tried:
- Q1/Q2 for Nifty 500 at 1 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 1 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 1 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Nifty 500 at 3 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 3 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 3 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Nifty 500 at 5 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 5 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 5 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Nifty 500 at 7 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 7 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 7 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Nifty 500 at 10 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 10 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 10 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Nifty 500 at 15 years, starts from April 2005, rebalanced each April
- Q1/Q2 for 60/20/20 at 15 years, starts from April 2005, rebalanced each April
- Q1/Q2 for Equal thirds at 15 years, starts from April 2005, rebalanced each April
- Q15 to-date paths and Q16 red-at-12-months for 60/20/20, starts from April 2005
- Q15 to-date paths and Q16 red-at-12-months for Equal thirds, starts from April 2005

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
| q17_n500_m12_gap_C_p50 | 1482046.15292757 | 1482046.1529275384 | 2000.0 | yes |
| q18_n500_10y_corr_12m | -0.3465821 | -0.34658210035260434 | 0.01 | yes |
| q18_n500_10y_corr_36m | 0.09599318 | 0.09599317544374128 | 0.01 | yes |
| q18_n500_10y_corr_60m | -0.0203112 | -0.020311195228148563 | 0.01 | yes |
| q10_n500_15y_need_50 | 16454.55316227 | 16454.553162268974 | 50.0 | yes |
| q10_n500_15y_need_80 | 19458.95771258 | 19458.95771258352 | 50.0 | yes |
| q10_n500_15y_need_95 | 22809.92280693 | 22809.922806930543 | 50.0 | yes |
| q20_n500_industry | 0.11171912 | 0.11171911613684193 | 0.0005 | yes |
| q20_n500_trend | 0.1130728 | 0.11307280098552186 | 0.0005 | yes |
| q22_life_latest | 1.79739857 | 1.7973985672311907 | 0.05 | yes |

Ambiguities the recomputing model resolved:
- Tax on 31 March is applied to interest accrued up to the start of 31 March (growth through 30 March); growth on 31 March belongs to the next segment. Same for final date, tax applies to growth up to final date (exclusive of final day).
- For SIPs in the red at age 12 with no instalments bought while red (money_share = 0), the ratio is undefined and such SIPs are excluded from the median of units-to-money ratio.
- For AMFI trend SIP, the same months as industry XIRR (April 2016 to latest month in amfi_sip) are used, with n=0 for April 2016.
- For FD, if a deposit is made on 31 March, no tax event is applied on that date for that deposit (interest zero), and the first tax event is the next 31 March.
- For running XIRR at age a, the final value is at the last session of month k+a-1, using the first a instalments.

### Review and cold read

Model: gemini-3.8-flash. Overall: The article's biggest weakness is its omission of planned deliverables and text facts, specifically leaving out the required closing 'SIP myths, checked' table, dropping inflation failure rates from the body of Q1, and misdescribing Figure F.q1's chart type. Its biggest strength is its relentless empirical discipline and clarity, dismantling common industry myths by translating 30 years of market data into intuitive rupee outcomes that vividly demonstrate why staying invested during market drops beats stopping.

| Id | Severity | Problem | Response |
|---|---|---|---|
| r1 | must_fix | The draft omits the frozen plan's mandatory closing 'SIP myths, checked' table that maps 20 popular claims to their answering questions and verdicts. | fixed: added the 'SIP myths, checked' table the plan promised, 21 claims with the answering question, the record and a verdict. |
| r2 | must_fix | Although the sub-question heading explicitly includes 'or trail inflation?', the body text of Q1 completely fails to report the historical rates at which a Nifty 500 equity SIP trailed inflation across horizons. | fixed: Q1 now gives the shares that trailed inflation at 1, 3, 5, 7 and 10 years. |
| r3 | must_fix | The 'How to read it' explanation tells the reader to look for rows of dots and lines falling downwards, whereas Figure F.q1 actually presents grouped vertical bars. | fixed: Q1's 'how to read it' now describes the grouped bars (the chart was redesigned from dots). |
| r4 | must_fix | The statement asserts that the 100% win rate held at 24 months, but for 24-month red Nifty 500 SIPs, keeping going beat path B and path C in 98.4% of start months (failing in one start month by up to ₹1.06 lakh). | fixed: the 24-month result is now stated as 98%, with the one start month where stopping and holding came out ahead (₹1.1 lakh). |
| r5 | must_fix | The 'Still lost? Read this' summary states that 'how cheaply' you bought mattered, which contradicts the study's central findings (Q8, Q12, Q19) showing market timing and valuation made virtually no difference, erroneously replacing the proven driver: how long the SIP ran. | fixed: 'how cheaply' replaced with 'how long it ran', which is what the findings support. |
| r6 | should_fix | The acronym AMFI is used without being expanded or explained for a lay reader. | fixed: AMFI is spelled out at first use. |
| r7 | should_fix | The abbreviation SIP and the benchmark index Nifty 500 are introduced in the very first sentence without being defined or expanded for a novice investor. | fixed: SIP and the Nifty 500 are explained in the first sentence. |
| r8 | should_fix | The draft reports the failure of the return portion of Prediction P6 but omits the result for the risk portion, which predicted that rebalancing would lower the median deepest fall. | fixed: Q6 now reports the risk half of P6 (median deepest fall 4.9% with rebalancing, 4.7% without). |
| r9 | minor | The compressed sentence packs multiple sensitivity checks into a single clause with an ambiguous trailing parenthetical, forcing the reader to re-read to parse what 99% refers to. | fixed: split into separate sentences for the indices, untaxed FDs and 24 months. |

The cold reader's answers to each sub-question, from the article alone:
- **q1**: Over ten years, an equity SIP never lost money, trailed an FD in only 0.4% of start months, and trailed inflation in 0.8%, though over one to five years it lost money in 7% to 29% of windows and trailed an FD in 16% to 38% (with shorter-horizon inflation failure rates omitted from the text).
- **q2**: An investor should expect a wide range around the median ten-year return of 14.6% a year, with 90% of outcomes falling between 9.8% and 26.0% and extremes ranging from 4.3% to 32.7%.
- **q3**: After inflation, the typical ten-year Nifty 500 SIP earned 8.3% a year (about six percentage points below nominal), with 5% of start months earning under 2.0% and only 0.8% failing to beat inflation outright.
- **q4**: Over ten years, the Midcap 150 delivered the highest median return (17.9%) and Smallcap 250 returned 15.3% but experienced a negative worst case (−0.5%) and a 54% maximum fall, while the Nifty 500 returned 13.5%, gold 8.9%, and government bonds 8.0% with minimal drawdown.
- **q5**: Diversifying into a 60/20/20 mix cost ₹1.4 lakh in median final value over ten years while gaining only ₹0.2 lakh in the 5th-percentile bad case, but over five and fifteen years the bad-case gain exceeded the median cost while roughly halving the worst-case fall from 44% to 25%.
- **q6**: Rebalancing a 60/20/20 SIP annually each April added a median 0.8 percentage points a year over ten years, helping in at least nine in ten start months.
- **q7**: Longer SIPs become dramatically steadier in annualised returns as the 5th-to-95th percentile spread narrows from 41 points at five years to 3.5 points at twenty, but rupee multiples remain wide apart, spanning 4.2 to 6.4 times the invested capital at twenty years.
- **q8**: The start year mattered enormously because ten-year median returns ranged from 9.3% for 2010 starts to 26.5% for 1997 starts, yet starting within 2% of a market peak versus more than 10% below it made almost no difference (13.6% versus 14.9%).
- **q9**: The first five years matter most, contributing 55% of a 15-year SIP's final value compared to 14% from the last five, and de-risking into fixed deposits over the final 36 months proved costly, ending ahead in only 19% of cases and lowering even the 5th-percentile bad case.
- **q10**: To reach ₹1 crore in 15 years on the Nifty 500, an investor needed ₹16,455 a month for a 50% chance, ₹19,459 for an 80% chance, and ₹22,810 for a 95% chance (with a 12% calculator asking for ₹21,011 and succeeding 90% of the time), while starting five years late required ₹21,612 a month over 15 years to match the 20-year outcome.
- **q11**: For an investor holding a lump sum, deploying it immediately beat a 12-month STP in 57% of start months, while for a salaried saver earning monthly, an ongoing monthly SIP beat saving in an FD to invest annually in 73% of start months.
- **q12**: SIP dates, weekly frequency, and valuation-doubling rules barely mattered, shifting ten-year returns by only 0.0 to 0.2 percentage points, whereas pausing during falls cost 2.0 to 3.8 points and a 1% higher expense ratio cost 1.1 points a year.
- **q13**: No, a SIP is not long-term after a year because each instalment has its own one-year clock; after two years, 50% of the units are still short-term (holding 27% of gains) and subject to short-term capital gains tax plus potential exit loads.
- **q14**: Volatility did not reliably help an equity SIP, as the SIP's 0.7 percentage point median return edge over index buy-and-hold correlated only weakly (0.23) with window volatility across the entire history and showed zero correlation after 2005.
- **q15**: Practically all Nifty 500 SIPs went under water at some point (97% of start months), with the deepest fall reaching 44% below invested money and the longest unbroken stretch in the red lasting 38 months.
- **q16**: SIPs in the red at 12 months ended with a higher median ten-year return (17.9% versus 14.1% for the rest) because depressed markets allowed 18% of contributions to purchase 30% of final units, though this bonus did not extend to mid caps or multi-asset mixes.
- **q17**: Stopping a red Nifty 500 SIP never protected the investor, as continuing beat stopping-and-holding, switching to FDs, or pausing in 100% of 12-month red cases, with an FD switch costing a median ₹14.8 lakh.
- **q18**: A SIP's running return does not begin to reliably predict its final outcome until 99 months (over eight years) in, and early returns at 12 months actually correlate negatively (−0.35) with the ten-year ending return.
- **q19**: In the historical record, the bad-start bonus did not depend on cheap valuations, as month-12 red SIPs when P/E was above median finished at 14.3% compared to 14.8% when below median, while currently Nifty 50 P/E stands at the 35th percentile and deposit rates at the 25th percentile.
- **q20**: No, industry SIP money did not arrive at bad times: actual inflows earned 11.2% a year since 2016, trailing a trend-growth benchmark by only 0.1 percentage points.
- **q21**: Market falls of 10% or more have been somewhat shallower and less frequent since 2016 (7 falls with a 16% median depth, down from 11 falls with a 20% median depth), but a single decade is insufficient to prove that SIP inflows caused this moderation.
- **q22**: The implied average life of a SIP account is currently about 1.8 years (never exceeding 4.9 years outside clean-ups), while the stoppage ratio reflects account closures relative to new registrations and spiked to 3.5 during AMFI's 2025 clean-up.

### Model calls and cost

| When | Role | Model | Tokens in / out | ₹ |
|---|---|---|---|---|
| 2026-10-15T07:46:25+00:00 | recompute | deepseek-flash | 2,738 / 32,000 | 3.45 |
| 2026-10-15T07:49:01+00:00 | recompute | deepseek-flash | 2,754 / 31,459 | 3.39 |
| 2026-10-15T07:52:32+00:00 | review | gemini-3.8-flash | 55,313 / 1,274 | 4.07 |
| 2026-10-15T07:58:10+00:00 | review | gemini-3.8-flash | 55,313 / 4,188 | 5.03 |
| 2026-10-15T08:05:55+00:00 | recompute | deepseek-flash | 2,738 / 32,000 | 3.45 |
| 2026-10-15T08:07:22+00:00 | recompute | deepseek-flash | 2,754 / 17,349 | 1.90 |
| 2026-10-15T08:22:18+00:00 | recompute | deepseek-flash | 13,459 / 32,000 | 3.73 |
| 2026-10-15T08:24:43+00:00 | recompute | deepseek-flash | 13,459 / 28,999 | 3.42 |
| 2026-10-15T08:27:20+00:00 | recompute | deepseek-flash | 15,322 / 32,000 | 3.78 |
| 2026-10-15T08:29:55+00:00 | recompute | deepseek-flash | 15,322 / 30,050 | 3.58 |
| 2026-10-15T08:32:25+00:00 | recompute | deepseek-flash | 14,362 / 32,000 | 3.76 |
| 2026-10-15T08:34:51+00:00 | recompute | deepseek-flash | 14,362 / 30,972 | 3.65 |
| 2026-10-15T08:37:27+00:00 | recompute | deepseek-flash | 11,049 / 31,999 | 3.67 |
| 2026-10-15T08:40:01+00:00 | recompute | deepseek-flash | 11,049 / 32,000 | 3.67 |
| 2026-10-15T08:53:43+00:00 | recompute | deepseek-flash | 2,738 / 39,360 | 4.23 |
| 2026-10-15T08:54:02+00:00 | recompute | deepseek-flash | 7,288 / 4,363 | 0.65 |
| 2026-10-15T08:58:55+00:00 | review | gemini-3.8-flash | 61,855 / 3,673 | 5.29 |
| 2026-10-15T09:01:49+00:00 | audit | deepseek-flash | 5,799 / 18,330 | 2.09 |
| 2026-10-15T09:03:50+00:00 | audit | deepseek-flash | 9,268 / 27,036 | 3.10 |
| 2026-10-15T09:06:24+00:00 | audit | deepseek-flash | 8,408 / 30,814 | 3.48 |
| 2026-10-15T09:08:29+00:00 | audit | deepseek-flash | 8,390 / 26,954 | 3.07 |
| 2026-10-15T09:10:36+00:00 | audit | deepseek-flash | 8,625 / 24,055 | 2.77 |
| 2026-10-15T09:13:08+00:00 | audit | deepseek-flash | 8,564 / 29,951 | 3.39 |
| 2026-10-15T09:15:10+00:00 | audit | deepseek-flash | 6,994 / 24,038 | 2.72 |
| 2026-10-15T09:17:18+00:00 | audit | deepseek-flash | 6,041 / 25,055 | 2.81 |
| 2026-10-15T09:19:55+00:00 | audit | deepseek-flash | 7,906 / 31,325 | 3.52 |
| 2026-10-15T09:25:13+00:00 | audit | deepseek-flash | 5,137 / 64,000 | 6.89 |
| 2026-10-15T09:26:56+00:00 | audit | deepseek-flash | 5,137 / 22,603 | 2.52 |
| 2026-10-15T09:28:55+00:00 | audit | deepseek-flash | 8,722 / 26,037 | 2.98 |
| 2026-10-15T09:30:35+00:00 | audit | deepseek-flash | 6,812 / 21,183 | 2.42 |
| 2026-10-15T09:32:25+00:00 | audit | deepseek-flash | 5,317 / 22,661 | 2.53 |
| 2026-10-15T09:37:46+00:00 | audit | deepseek-flash | 4,299 / 64,000 | 6.87 |
| 2026-10-15T09:40:31+00:00 | audit | deepseek-flash | 4,299 / 33,871 | 3.69 |
| 2026-10-15T09:42:08+00:00 | audit | deepseek-flash | 15,448 / 12,832 | 1.76 |
| 2026-10-15T09:44:01+00:00 | audit | deepseek-flash | 12,361 / 25,859 | 3.06 |
| 2026-10-15T09:45:24+00:00 | audit | deepseek-flash | 12,907 / 17,709 | 2.21 |
| 2026-10-15T09:46:44+00:00 | audit | deepseek-flash | 12,116 / 16,165 | 2.03 |
| 2026-10-15T09:48:17+00:00 | audit | deepseek-flash | 14,079 / 21,118 | 2.60 |
| 2026-10-15T09:51:18+00:00 | audit | deepseek-flash | 12,895 / 34,839 | 4.02 |
| 2026-10-15T09:52:50+00:00 | audit | deepseek-flash | 10,699 / 19,918 | 2.39 |
| 2026-10-15T09:53:39+00:00 | audit | deepseek-flash | 9,340 / 10,728 | 1.38 |
| 2026-10-15T09:55:35+00:00 | audit | deepseek-flash | 15,618 / 24,735 | 3.02 |
| 2026-10-15T09:57:02+00:00 | audit | deepseek-flash | 7,558 / 18,429 | 2.15 |
| 2026-10-15T09:58:40+00:00 | audit | deepseek-flash | 3,945 / 21,626 | 2.39 |
| 2026-10-15T10:00:52+00:00 | audit | deepseek-flash | 2,722 / 14,573 | 1.61 |

Total: ₹144.19. Every request and reply is in `checks/transcripts/`. The lead model's work (plan, code, article, this report) ran in an interactive session and is not metered here.

### Last `desk check`

2026-10-15T10:01:04+00:00: plan_shape ok, plan_frozen ok, results_fresh ok, checks_passed ok, declared_checks ok, questions_answered ok, figures_fresh ok, figures_used ok, figures_complete ok, numbers_traced ok, headline_confirmatory ok, style ok, sections ok, reader_copy_clean ok, front_matter ok, recompute ok, review_answered ok, audit ok, report ok, budget ok, human_read pending

<!-- auto:end -->
