"""{{slug}}: build figures.json from results. Every plotted value and every number in a title comes from results.

Run from the repo root:  uv run python studies/{{slug}}/figures.py
"""

from __future__ import annotations

from desk import figures

R, F, chart = figures.load(__file__)
SOURCE = "…; tipsheet calculations"


def pct(key: str, d: int = 0) -> str:
    return f"{F[key]['value'] * 100:.{d}f}%"


FIGS = {
    # "q1": {
    #     "title": f"… {pct('q1_share')} …",
    #     "sub": "what is plotted, the sample and dates",
    #     "read": "how to read it",
    #     "source": SOURCE,
    #     "job": "answer",          # guides/charts.md: answer spread comparison mechanism conditioning robustness caveat case
    #     "evidence": "tested",     # tested measured exploratory illustration
    #     "spec": {"kind": "hbars", "fmt": "pct", "digits": 0, "series": [{"col": "v", "label": "…", "slot": 2}]},
    #     "data": {"categories": [...], "series": {"v": [...]}},
    # },
}

if __name__ == "__main__":
    figures.write(__file__, FIGS)
