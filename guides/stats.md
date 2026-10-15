# Step 2: computing and checking

How to compute a study so the numbers can be trusted. Read before writing `compute.py`.

## The shape of compute.py

```python
from desk import calc, checks, data
from desk.results import Results

R = Results(__file__)                      # knows the study folder and the plan's freeze commit
px = data.load("portal:equity_prices_adjusted", R)   # every input goes through data.load, which fingerprints it
checks.no_duplicates(px, ["canon", "d"], R)          # input checks record into R and raise on failure
...
R.fact("q1_share_back_3y", 0.75, "fraction", note="below at 6m, back within 3y")
R.fact("x1_by_year_spread", 0.12, "fraction", exploratory=True)
R.check("lookahead_truncation", passed=True, detail="results before 2022 unchanged when data cut at 2022-12-31")
R.chart("recovery", rows)                  # data behind a figure
R.write()
```

Units for facts: `fraction` (0.75 means 75%), `pct` (already ×100), `ratio`, `rupees`, `crore`, `count`, `sessions`, `years`, `plain`.

## Inputs

- Load only through `desk.data.load("databank:<dataset>")` or `desk.data.load("portal:<table>")`. Both are read-only, and the path, size and hash are written into `results.json`. `desk check` fails if an input has changed since the results were computed.
- Run the input checks that fit: duplicates, gaps in a calendar, plausible ranges, units, and delisted or merged names still present. A failed input check stops the run. Fix the cause or exclude it explicitly with a recorded reason; never patch silently.
- Record the data end date as a fact or context number.

## Biases to rule out

- **Look-ahead.** Every decision in a backtest uses only what was known at the time, including publication lags (macro data, index constituents, fund categories). For anything time-based, run the truncation check: cut the data at an earlier date, rerun, and confirm results for periods before the cut don't change (`checks.truncation_stable`).
- **Survivorship.** The sample includes companies and funds that died, merged or were delisted. Say how they were treated.
- **Selection after the fact.** "Famous IPOs" or "funds still running" are illustrations, not samples. Label them so.

## Statistics

- **Overlapping windows.** Monthly-start 10-year SIPs over 25 years are not 180 independent observations; they share most of their months. Never quote a t-test or p-value on overlapping windows as if they were independent. Use `calc.block_bootstrap_ci` with a block at least as long as the window, or count independent (non-overlapping) periods and say how many there are.
- **Medians and spreads beat means** for skewed outcomes such as stock returns and SIP values. Report the middle half (25th to 75th percentile) alongside the median.
- **Effect size first, significance second.** Say how big the difference is in rupees or points, then how sure we are.
- **How many things were tested.** Count every test and variant run, including the ones that didn't make the article, and state the count. With many tests, some will look significant by chance; say so, or adjust (Holm).
- **Nulls are results.** "No difference we could detect, and with this sample we could have detected a difference of X" is a finding. "Can't tell" is also a finding. Say which it is.
- **Causal language** ("because", "drives", "causes") only with a design that supports it. Otherwise "went with", "was followed by".
- **One decade doing all the work.** Split the sample by era for every headline result and report whether the finding holds in each.

## Checks the plan can declare

| Check | When it applies | Helper |
|---|---|---|
| `truncation_stable` | anything time-based | `checks.truncation_stable` |
| `placebo` | any claimed effect or predictive signal: shuffle the signal or the dates, the effect should vanish | `checks.placebo` |
| `robustness` | every headline result: shift start dates, swap the benchmark, change the window; report if the sign flips | record with `R.check` |
| `parts_sum` | any breakdown: groups add up to the whole | `checks.parts_sum` |
| `era_split` | every headline result | record with `R.check` |

The plan lists the checks for each question. `desk check` fails if a declared check is missing from the results or did not pass. A robustness check that "fails" because the finding is fragile is recorded as passed with the detail, and the article says the finding is fragile. The check is that we looked.

## Exploration

After the frozen questions are answered, the results will raise new questions. Follow them up in the same `compute.py`, tag every fact `exploratory=True`, and keep a count of what you tried. In the article they go in their own clearly labelled section, with that count. They never reach the title, dek or finding box.

## The independent recompute

Write `recompute.md`: the inputs (columns and meaning), the definitions, and 5 to 10 headline fact keys with tolerances. Write it from the plan, not from `compute.py`. The recomputing model sees only this file and the inputs. `compute.py` exposes `recompute_inputs(out_dir)` to write those inputs. A mismatch is investigated until the cause is known. Never resolve one by picking the answer you prefer.
