"""sip-in-the-red: compute every question in plan.md (frozen at the commit in freeze.json).

Run from the repo root:  uv run python studies/sip-in-the-red/compute.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from desk import calc, checks, data
from desk.results import Results


def load(R: Results | None = None) -> dict[str, pd.DataFrame]:
    """Every input, through desk.data so it is fingerprinted."""
    return {
        # "prices": data.load("portal:equity_prices_adjusted", R, columns=[...]),
    }


def recompute_inputs(out_dir: Path) -> None:
    """Write the inputs recompute.md describes, as Parquet files in out_dir."""
    D = load()
    # D["prices"][[...]].to_parquet(out_dir / "prices.parquet", index=False)


def main() -> None:
    R = Results(__file__)
    D = load(R)
    # input checks: checks.no_duplicates(D["prices"], ["canon", "d"], R)

    # ---- Q1
    # R.fact("q1_...", value, "fraction", note="...")
    # R.check("robustness", True, "detail", question="q1")
    # R.chart("q1_main", rows)

    # ---- exploratory follow-ups (tag exploratory=True; log every variant with R.tried_variant)

    R.write()


if __name__ == "__main__":
    main()
