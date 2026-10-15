# Charts

The article's figures are drawn by the site's chart kit (`@tipsheet/charts` in the portal; `components/kit/Figure.astro`). A study's `figures.py` writes `figures.json`: one entry per figure, holding the props `Figure` takes. The article draws one with `<Figure {...F.recovery} />`.

## A figure entry

```json
{
  "id": "fig-recovery",
  "title": "Of IPOs below the issue price at six months, 44% got back within a year",
  "sub": "What is plotted, the sample and the dates",
  "read": "How to read it: what one bar means and where to look",
  "source": "NSE bhavcopy (adjusted for splits and bonuses); tipsheet calculations",
  "spec": {"kind": "hbars", "room": "tall", "fmt": "pct", "digits": 0, "series": [{"col": "y1", "label": "Back within 1 year", "slot": 2}]},
  "data": {"categories": ["Below at 1 month", "Below at 6 months"], "series": {"y1": [61.4, 44.0]}},
  "job": "answer",
  "evidence": "tested",
  "big": true,
  "few": false,
  "legend": [{"label": "Back within 1 year", "slot": 2, "shape": "box"}]
}
```

Kinds available: time forms `line area band bars share fan calendar multiples curve spark states panes`; category forms `hbars dots range slope waterfall heat scatter outcomes`; research forms `histogram forest strip bump`. The full spec is `packages/charts/src/types.ts` in the portal. Time forms take `{"dates": [...], "series": {...}}`; category forms take `{"categories": [...], "series": {...}}`.

## Every chart has a job

Each figure gets one narrative job, and two figures never do the same job for the same question. Borrowed from This Indian Life's chart contract:

| Job | The reader's question |
|---|---|
| answer | What's the answer? (the headline chart of a section) |
| spread | What range of outcomes did real people get? Who does the average hide? |
| comparison | Compared with the realistic alternative (the index, a deposit, selling on day one)? |
| mechanism | Why does it happen? |
| conditioning | When is the answer different (size, valuation, era, depth of fall)? |
| robustness | Does it survive other start dates, benchmarks, eras? |
| caveat | What would make a reader misread the headline (a denominator, survivors only)? |
| case | One real example followed through time |

A figure with no job is cut. Record the job in the entry (`"job": "answer"`).

## Every chart has an evidence tag

`"evidence"` is one of the following. `figures.write` turns it into the first line of the figure's note, so the reader knows how solid the ground is before standing on it:

| Tag | Meaning |
|---|---|
| `tested` | answers a question frozen before results, with a stated test |
| `measured` | a descriptive count or distribution from the full sample |
| `exploratory` | found after the results, not tested in advance |
| `illustration` | hand-picked cases; shows what happened, proves nothing general |

## Rules

- **The title states the finding**, with its number, from `results.json`. The numeric gate checks titles, subtitles and read lines like prose.
- **One point per chart.** The subject is in colour; context and benchmarks are grey (`tone: "hist"` for the benchmark).
- **Big charts, as many as the question needs.** `big: true` for every figure in an article. Each section has one headline chart, plus as many supporting charts as it has distinct jobs (by index, by horizon, in rupees as well as percentages). Never two charts doing the same job with the same fact. The owner's rule (2026-10-15): where more charts help the reader understand, use them.
- **Show the spread, not just the centre**: `outcomes`, `range`, `fan` or `histogram` for anything with a distribution. A median alone hides the reader's real risk.
- **Show sample sizes** on the chart or in the subtitle when they differ between rows.
- **Uncertainty**: confidence intervals with `forest`, or a band, when the chart makes a comparison.
- **Labels inside the plot**, on their gridlines (the site default). Every axis has a unit. Nothing overlaps; check at phone width with the portal's preview build.
- **Every figure has a `read` line.** A reader who has never seen the form needs it.
