"""Checks a study runs inside compute.py. Each records its outcome in the Results and, for input checks,
stops the run on failure: a bad input is fixed or explicitly excluded with a reason, never patched silently.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd


class InputCheckFailed(RuntimeError):
    pass


def _record(R, name: str, ok: bool, detail: str, question: str | None = None, fatal: bool = False) -> bool:
    if R is not None:
        R.check(name, ok, detail, question)
    if fatal and not ok:
        raise InputCheckFailed(f"{name}: {detail}")
    return ok


# ---------------------------------------------------------------- inputs (fatal)


def no_duplicates(df: pd.DataFrame, keys: list[str], R=None, name: str | None = None) -> bool:
    n = int(df.duplicated(keys).sum())
    return _record(R, name or f"input_no_duplicates[{','.join(keys)}]", n == 0, f"{n} duplicate rows on {keys}", fatal=True)


def in_range(s: pd.Series, lo: float, hi: float, R=None, name: str | None = None, allow_null: bool = False) -> bool:
    bad = ~s.between(lo, hi)
    if allow_null:
        bad &= s.notna()
    n = int(bad.sum())
    return _record(R, name or f"input_range[{s.name}]", n == 0,
                   f"{n} of {len(s)} values outside [{lo}, {hi}]" + (f"; e.g. {s[bad].head(3).tolist()}" if n else ""), fatal=True)


def no_calendar_gaps(dates: pd.Series, max_gap_days: int, R=None, name: str | None = None) -> bool:
    d = pd.Series(pd.to_datetime(dates).sort_values().unique())
    gaps = d.diff().dt.days
    worst = int(gaps.max()) if len(gaps) > 1 else 0
    where = str(d[gaps.idxmax()].date()) if len(gaps) > 1 else ""
    return _record(R, name or "input_calendar_gaps", worst <= max_gap_days,
                   f"largest gap {worst} days (ending {where}); limit {max_gap_days}", fatal=True)


def fresh(dates: pd.Series, as_of: pd.Timestamp, max_age_days: int, R=None, name: str | None = None) -> bool:
    last = pd.to_datetime(dates).max()
    age = (as_of - last).days
    return _record(R, name or "input_fresh", age <= max_age_days, f"last row {last.date()}, {age} days before {as_of.date()}",
                   fatal=True)


# ---------------------------------------------------------------- results (recorded, declared in the plan)


def parts_sum(parts: list[float], whole: float, R=None, question: str | None = None, tol: float = 1e-9,
              name: str = "parts_sum") -> bool:
    s = float(np.sum(parts))
    return _record(R, name, abs(s - whole) <= tol, f"parts sum to {s}, whole is {whole}", question)


def truncation_stable(run: Callable[[pd.Timestamp | None], dict[str, float]], cut: pd.Timestamp, R=None,
                      question: str | None = None, tol: float = 1e-9) -> bool:
    """Look-ahead check. `run(cut)` computes results using only data up to `cut` (None = all data) and
    returns {key: value} for periods that end on or before `cut`. Those values must not change when
    later data is added."""
    full, short = run(None), run(cut)
    diffs = {k: (full.get(k), v) for k, v in short.items()
             if full.get(k) is None or abs(float(full[k]) - float(v)) > tol}
    return _record(R, "truncation_stable", not diffs,
                   f"{len(short)} pre-{cut.date()} values compared; {len(diffs)} changed"
                   + (f": {dict(list(diffs.items())[:3])}" if diffs else ""), question)


def placebo(effect: Callable[[np.random.Generator | None], float], R=None, question: str | None = None, n: int = 500,
            seed: int = 7, name: str = "placebo") -> dict:
    """`effect(rng)` returns the effect with the signal shuffled by rng, or the real effect when rng is
    None. Records where the real effect sits among the shuffled ones. Passes when the check ran; the
    reported share is the evidence the article uses."""
    rng = np.random.default_rng(seed)
    real = effect(None)
    fake = np.array([effect(rng) for _ in range(n)])
    share = float(np.mean(np.abs(fake) >= abs(real)))
    _record(R, name, True, f"real effect {real:.6g}; {share:.1%} of {n} shuffles at least as large", question)
    return {"real": real, "share_as_large": share, "n": n}
