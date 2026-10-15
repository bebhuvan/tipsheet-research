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
  "big": true,
  "few": false,
  "legend": [{"label": "Back within 1 year", "slot": 2, "shape": "box"}]
}
```

Kinds available: time forms `line area band bars share fan calendar multiples curve spark states panes`; category forms `hbars dots range slope waterfall heat scatter outcomes`; research forms `histogram forest strip bump`. The full spec is `packages/charts/src/types.ts` in the portal. Time forms take `{"dates": [...], "series": {...}}`; category forms take `{"categories": [...], "series": {...}}`.

## Rules

- **The title states the finding**, with its number, from `results.json`. The numeric gate checks titles, subtitles and read lines like prose.
- **One point per chart.** The subject is in colour; context and benchmarks are grey (`tone: "hist"` for the benchmark).
- **Fewer, bigger charts.** `big: true` for every figure in an article. One headline chart per section, plus at most one supporting chart.
- **Show the spread, not just the centre**: `outcomes`, `range`, `fan` or `histogram` for anything with a distribution. A median alone hides the reader's real risk.
- **Show sample sizes** on the chart or in the subtitle when they differ between rows.
- **Uncertainty**: confidence intervals with `forest`, or a band, when the chart makes a comparison.
- **Labels inside the plot**, on their gridlines (the site default). Every axis has a unit. Nothing overlaps; check at phone width with the portal's preview build.
- **Every figure has a `read` line.** A reader who has never seen the form needs it.
