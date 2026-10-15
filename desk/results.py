"""The results recorder a study's compute.py writes through.

    R = Results(__file__)
    R.fact("q1_share_back_3y", 0.75, "fraction", note="...")      # citable numbers
    R.context("checkpoint_6m_sessions", 126)                       # fixed numbers from the plan
    R.label("data_end", "8 October 2026")                          # dates and names the text may quote
    R.check("truncation_stable", True, "detail", question="q1")    # declared checks
    R.chart("recovery", rows)                                      # data behind a figure
    R.write()

results/results.json records the plan's freeze commit, compute.py's hash and every input's fingerprint,
so `desk check` can tell when the results are stale.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .config import read_json, sha256_file, write_json

UNITS = {"fraction", "pct", "ratio", "rupees", "crore", "count", "sessions", "days", "months", "years", "plain", "text"}


def _clean(v):
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        v = float(v)
        return None if math.isnan(v) else round(v, 8)
    return v


class Results:
    def __init__(self, compute_file: str | Path):
        self.compute = Path(compute_file).resolve()
        self.study = self.compute.parent
        self.slug = self.study.name
        freeze = self.study / "freeze.json"
        self.plan_commit = read_json(freeze)["commit"] if freeze.is_file() else None
        self.facts: dict[str, dict] = {}
        self.contexts: dict[str, float] = {}
        self.labels: dict[str, str] = {}
        self.checks: dict[str, dict] = {}
        self.inputs: dict[str, dict] = {}
        self.allow_phrases: list[str] = []
        self.charts: dict[str, object] = {}
        self.tried: list[str] = []

    def fact(self, key: str, value, unit: str, note: str = "", exploratory: bool = False) -> None:
        if unit not in UNITS:
            raise ValueError(f"unit {unit!r} for {key}; use one of {sorted(UNITS)}")
        if key in self.facts:
            raise ValueError(f"fact {key} recorded twice")
        self.facts[key] = {"value": _clean(value), "unit": unit, **({"note": note} if note else {}),
                           **({"exploratory": True} if exploratory else {})}

    def context(self, key: str, value: float) -> None:
        self.contexts[key] = _clean(value)

    def label(self, key: str, text: str) -> None:
        self.labels[key] = str(text)

    def allow(self, *phrases: str) -> None:
        """Names containing digits that the numeric gate should not read as figures (e.g. 'Smallcap 250')."""
        self.allow_phrases.extend(phrases)

    def check(self, name: str, passed: bool, detail: str = "", question: str | None = None) -> None:
        key = f"{question}:{name}" if question else name
        self.checks[key] = {"passed": bool(passed), "detail": detail}

    def tried_variant(self, description: str) -> None:
        """Log an exploratory test or variant, kept or not, so the article can say how many were tried."""
        self.tried.append(description)

    def input(self, name: str, fp: dict) -> None:
        self.inputs[name] = fp

    def chart(self, name: str, data) -> None:
        self.charts[name] = data

    def write(self) -> Path:
        out = self.study / "results"
        charts = out / "charts"
        charts.mkdir(parents=True, exist_ok=True)
        for old in charts.glob("*.json"):
            old.unlink()
        for name, data in self.charts.items():
            if hasattr(data, "to_dict"):
                data = data.to_dict(orient="records")
            (charts / f"{name}.json").write_text(json.dumps(data, default=_clean, indent=0))
        doc = {
            "study": self.slug,
            "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "plan_commit": self.plan_commit,
            "compute_sha256": sha256_file(self.compute),
            "inputs": self.inputs,
            "facts": self.facts,
            "context_numbers": self.contexts,
            "labels": self.labels,
            "allow_phrases": self.allow_phrases,
            "checks": self.checks,
            "exploratory_tried": self.tried,
        }
        path = write_json(out / "results.json", doc)
        failed = [k for k, v in self.checks.items() if not v["passed"]]
        print(f"{self.slug}: {len(self.facts)} facts, {len(self.checks)} checks"
              + (f", FAILED: {', '.join(failed)}" if failed else ", all passed") + f" -> {path}")
        return path
