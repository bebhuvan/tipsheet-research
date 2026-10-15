"""A study folder and the conventions that make its files machine-checkable.

plan.md      sub-questions are headed `### Q1. …`; each has a line `- **Checks:** name, name` (or `none`
             with a reason). Everything from `## Amendments` down may change after the freeze.
article.mdx  YAML front matter (the portal's post contract) and an MDX body; each sub-question's section
             has `id="q1"`; a `## References` section, if any, is excluded from the numeric gate.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import yaml

from .config import ROOT, read_json, sha256_file, study_dir

KNOWN_CHECKS = {"truncation_stable", "placebo", "robustness", "parts_sum", "era_split"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def above_amendments(plan: str) -> str:
    return re.split(r"^## Amendments\b", plan, maxsplit=1, flags=re.M)[0].rstrip()


@dataclass
class Question:
    id: str            # "q1"
    title: str
    checks: list[str]


class Study:
    def __init__(self, slug: str):
        self.slug = slug
        self.dir = study_dir(slug)
        self.plan_path = self.dir / "plan.md"
        self.article_path = self.dir / "article.mdx"
        self.results_path = self.dir / "results" / "results.json"
        self.figures_path = self.dir / "figures.json"
        self.checks_dir = self.dir / "checks"
        self.freeze_path = self.dir / "freeze.json"

    # ------------------------------------------------------------ plan

    @cached_property
    def plan(self) -> str:
        return self.plan_path.read_text()

    def questions(self) -> list[Question]:
        out = []
        parts = re.split(r"^### (Q\d+)\.\s*(.*)$", above_amendments(self.plan), flags=re.M)
        for i in range(1, len(parts), 3):
            qid, title, body = parts[i].lower(), parts[i + 1].strip(), parts[i + 2]
            m = re.search(r"^\s*-\s*\*\*Checks:\*\*\s*(.+)$", body, flags=re.M)
            names = re.findall(r"[a-z_]+", m.group(1)) if m else []
            checks = [] if (not names or names[0] == "none") else [n for n in names if n in KNOWN_CHECKS]
            out.append(Question(qid, title, checks))
        return out

    def plan_problems(self) -> list[str]:
        probs = []
        qs = self.questions()
        if not 1 <= len(qs) <= 6:
            probs.append(f"plan has {len(qs)} sub-questions; the desk wants three to five")
        for q in qs:
            sec = re.search(rf"^### {q.id.upper()}\..*?(?=^### |^## |\Z)", self.plan, flags=re.M | re.S).group(0)
            if not re.search(r"\*\*Checks:\*\*", sec):
                probs.append(f"{q.id}: no '- **Checks:**' line")
            m = re.search(r"\*\*Checks:\*\*\s*(.+)", sec)
            if m:
                unknown = [n for n in re.findall(r"[a-z_]+", m.group(1).split("(")[0]) if n not in KNOWN_CHECKS | {"none"}]
                if unknown:
                    probs.append(f"{q.id}: unknown checks {unknown}; known: {sorted(KNOWN_CHECKS)}")
        return probs

    # ------------------------------------------------------------ freeze

    def freeze(self) -> dict | None:
        return read_json(self.freeze_path) if self.freeze_path.is_file() else None

    def frozen_plan(self) -> str | None:
        f = self.freeze()
        if not f:
            return None
        rel = self.plan_path.relative_to(ROOT).as_posix()
        return git("show", f"{f['commit']}:{rel}")

    # ------------------------------------------------------------ results and article

    def results(self) -> dict | None:
        return read_json(self.results_path) if self.results_path.is_file() else None

    def results_sha(self) -> str | None:
        return sha256_file(self.results_path) if self.results_path.is_file() else None

    def article(self) -> tuple[dict, str] | None:
        if not self.article_path.is_file():
            return None
        text = self.article_path.read_text()
        m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.S)
        if not m:
            raise ValueError("article.mdx has no YAML front matter")
        return yaml.safe_load(m.group(1)) or {}, m.group(2)

    def figures(self) -> dict | None:
        return read_json(self.figures_path) if self.figures_path.is_file() else None


def prose_of(body: str) -> str:
    """The reader-visible prose of an MDX body: no imports, no JSX/HTML tags, no References section."""
    body = re.split(r"^## References\b", body, maxsplit=1, flags=re.M)[0]
    body = re.sub(r"^(?:import|export) .*$", "", body, flags=re.M)
    body = re.sub(r"<[A-Z]\w*\s[^>]*?/>", " ", body, flags=re.S)       # self-closing components
    body = re.sub(r"<[^>]+>", " ", body)                                # other tags, keeping their text
    return body


def figure_text(figs: dict) -> str:
    return "\n\n".join(f"{x.get('title', '')}. {x.get('sub', '')} {x.get('read', '')} {x.get('note', '')}"
                       for x in figs.values())


def gate_bundle(results: dict, confirmatory_only: bool = False) -> dict:
    """results.json in the numeric gate's bundle format."""
    fam = {"fraction": "fraction", "pct": "pct", "ratio": "ratio", "rupees": "rupees", "crore": "crore"}
    facts = {}
    for k, v in results["facts"].items():
        x = v["value"]
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            continue
        if confirmatory_only and v.get("exploratory"):
            continue
        facts[k] = {"value": float(x), "unit": fam.get(v["unit"], "plain")}
    labels = dict(results.get("labels", {}))
    labels.update({k: v["value"] for k, v in results["facts"].items() if isinstance(v["value"], str)})
    return {"facts": facts, "context_numbers": results.get("context_numbers", {}), "labels": labels,
            "allow_phrases": results.get("allow_phrases", [])}
