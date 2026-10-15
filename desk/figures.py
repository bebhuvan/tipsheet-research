"""Helpers for a study's figures.py: load results, write figures.json with a record of which results built it."""

from __future__ import annotations

import json
from pathlib import Path

from .config import read_json, sha256_file, write_json


def load(figures_file: str | Path) -> tuple[dict, dict, callable]:
    """(results, facts, chart) for the study that owns figures_file. chart(name) reads results/charts/<name>.json."""
    study = Path(figures_file).resolve().parent
    res = read_json(study / "results" / "results.json")
    return res, res["facts"], lambda name: json.loads((study / "results" / "charts" / f"{name}.json").read_text())


def write(figures_file: str | Path, figs: dict[str, dict]) -> Path:
    study = Path(figures_file).resolve().parent
    for k, f in figs.items():
        f.setdefault("id", f"fig-{k}")
        f.setdefault("big", True)
    path = write_json(study / "figures.json", figs)
    write_json(study / "checks" / "figures_meta.json", {"results_sha256": sha256_file(study / "results" / "results.json")})
    print(f"{len(figs)} figures -> {path}")
    return path
