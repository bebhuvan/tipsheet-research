"""`desk check <slug>`: every free check on a study, in order, written to checks/status.json.

Each item is ok, fail or pending (not yet reached: no results, no article, no recompute…). The command
exits 0 when nothing fails; `--strict` (used by `desk publish`) also requires nothing pending.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .config import CAP_INR_PER_STUDY, read_json, sha256_file, write_json
from .data import changed_inputs
from .gates import numeric, style
from .models import spent_inr
from .study import Study, above_amendments, figure_text, gate_bundle, prose_of

INTERNAL = [r"\bData ?bank\b", r"\b\w+\.py\b", r"\bresults\.json\b", r"\bstudies/", r"\bcompute step\b",
            r"\bDeepSeek\b", r"\bGemini\b", r"\bunverified\b"]


def run(slug: str) -> list[dict]:
    S = Study(slug)
    items: list[dict] = []

    def add(name: str, status: str, detail: str = "", **extra):
        items.append({"check": name, "status": status, "detail": detail, **extra})

    # ---- plan
    probs = S.plan_problems()
    add("plan_shape", "fail" if probs else "ok", "; ".join(probs) or f"{len(S.questions())} sub-questions")
    fz = S.freeze()
    if not fz:
        add("plan_frozen", "pending", "run `desk freeze` after the plan is approved and committed")
    else:
        same = above_amendments(S.frozen_plan() or "") == above_amendments(S.plan)
        add("plan_frozen", "ok" if same else "fail",
            f"frozen at {fz['commit'][:7]}" if same else "plan.md changed above '## Amendments' since the freeze")

    # ---- results
    R = S.results()
    if R is None:
        add("results", "pending", "run compute.py")
    else:
        stale = []
        if fz and R.get("plan_commit") != fz["commit"]:
            stale.append("computed before the freeze (or under another freeze)")
        if R.get("compute_sha256") != sha256_file(S.dir / "compute.py"):
            stale.append("compute.py changed since the results were written")
        stale += changed_inputs(R.get("inputs", {}))
        if not R.get("inputs"):
            stale.append("no inputs recorded: load data through desk.data")
        add("results_fresh", "fail" if stale else "ok", "; ".join(stale) or f"computed {R['computed_at']}")

        failed = [k for k, v in R.get("checks", {}).items() if not v["passed"]]
        add("checks_passed", "fail" if failed else "ok", ", ".join(failed) or f"{len(R.get('checks', {}))} checks passed")
        missing = []
        for q in S.questions():
            for c in q.checks:
                if f"{q.id}:{c}" not in R.get("checks", {}) and c not in R.get("checks", {}):
                    missing.append(f"{q.id}:{c}")
        add("declared_checks", "fail" if missing else "ok",
            ("declared in the plan but not recorded: " + ", ".join(missing)) if missing else "every declared check recorded")
        no_facts = [q.id for q in S.questions() if not any(k.startswith(q.id + "_") for k in R["facts"])]
        add("questions_answered", "fail" if no_facts else "ok",
            ("no facts for " + ", ".join(no_facts)) if no_facts else "every sub-question has facts")
        if any(v.get("exploratory") for v in R["facts"].values()) and not R.get("exploratory_tried"):
            add("exploration_logged", "fail", "exploratory facts exist but R.tried_variant() logged nothing")

    # ---- figures and article
    figs = S.figures()
    if figs is None:
        add("figures", "pending", "run figures.py")
    else:
        meta = S.checks_dir / "figures_meta.json"
        fresh = meta.is_file() and read_json(meta).get("results_sha256") == S.results_sha()
        add("figures_fresh", "ok" if fresh else "fail", "" if fresh else "figures.json was not built from the current results")
        bad = [k for k, x in figs.items() if not all(x.get(f) for f in ("title", "read", "spec", "data"))]
        add("figures_complete", "fail" if bad else "ok",
            ("missing title/read/spec/data: " + ", ".join(bad)) if bad else f"{len(figs)} figures")

    art = S.article()
    if art is None:
        add("article", "pending", "write article.mdx")
    elif R is not None:
        fm, body = art
        prose = prose_of(body) + "\n\n" + figure_text(figs or {})
        rep = numeric.check(prose, gate_bundle(R))
        add("numbers_traced", "ok" if rep["ok"] else "fail", f"{rep['checked']} figures checked, {len(rep['failures'])} untraced",
            failures=rep["failures"][:40], warnings=rep["warnings"][:20])
        head = "\n\n".join(str(fm.get(k, "")) for k in ("title", "dek", "finding"))
        rep_h = numeric.check(head, gate_bundle(R, confirmatory_only=True))
        add("headline_confirmatory", "ok" if rep_h["ok"] else "fail",
            "title, dek and finding use only confirmatory facts" if rep_h["ok"] else "headline cites an exploratory or untraced number",
            failures=rep_h["failures"])
        st = style.check(prose)
        add("style", "ok" if st["ok"] else "fail", f"{len(st['errors'])} errors, {len(st['warnings'])} warnings",
            errors=st["errors"][:40], warnings=st["warnings"][:40])
        missing = [q.id for q in S.questions() if not re.search(rf'id=["\']{q.id}["\']', body)]
        add("sections", "fail" if missing else "ok",
            ("no section with id for " + ", ".join(missing)) if missing else "a section per sub-question")
        hits = sorted({m.group(0) for p in INTERNAL for m in re.finditer(p, prose_of(body) + head, flags=re.I)})
        add("reader_copy_clean", "fail" if hits else "ok", ", ".join(hits) or "no internal names or unverified citations")
        for k in ("title", "dek", "finding", "topic", "date"):
            if not fm.get(k):
                add("front_matter", "fail", f"missing {k}")
                break
        else:
            add("front_matter", "ok", "")

    # ---- paid checks
    rc = S.checks_dir / "recompute.json"
    if not rc.is_file():
        add("recompute", "pending", "run `desk recompute`")
    else:
        r = read_json(rc)
        if r.get("results_sha256") != S.results_sha():
            add("recompute", "fail", "recompute ran on older results; run it again")
        else:
            diffs = [x["key"] for x in r["rows"] if not x["match"]]
            add("recompute", "fail" if diffs else "ok", ("mismatch: " + ", ".join(diffs)) if diffs else
                f"{len(r['rows'])} headline numbers matched")
    rv = S.checks_dir / "review.json"
    if not rv.is_file():
        add("review", "pending", "run `desk review`")
    else:
        issues = read_json(rv)["issues"]
        resp_path = S.checks_dir / "responses.json"
        resp = read_json(resp_path) if resp_path.is_file() else {}
        open_ = [i["id"] for i in issues if i["severity"] in ("must_fix", "should_fix") and not resp.get(i["id"])]
        add("review_answered", "fail" if open_ else "ok",
            ("no response in checks/responses.json for " + ", ".join(open_)) if open_ else f"{len(issues)} issues handled")

    spent = spent_inr(S.dir)
    add("budget", "ok" if spent <= CAP_INR_PER_STUDY else "fail", f"₹{spent:.0f} of ₹{CAP_INR_PER_STUDY:.0f}")

    if art is not None:
        so = (art[0].get("signed_off") or {}).get("by")
        add("human_read", "ok" if so else "pending", f"signed off by {so}" if so else
            "a person reads the article, recomputes three numbers by hand, and sets signed_off")

    write_json(S.checks_dir / "status.json", {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "items": items})
    return items


def main(slug: str, strict: bool = False, verbose: bool = False) -> int:
    items = run(slug)
    mark = {"ok": "  ok   ", "fail": "  FAIL ", "pending": "  ...  "}
    for it in items:
        print(f"{mark[it['status']]}{it['check']:<22} {it['detail']}")
        if it["status"] == "fail" or verbose:
            for f in it.get("failures", [])[:15]:
                print(f"         untraced {f['text']!r}: {f['sentence'][:140]}")
            for e in it.get("errors", [])[:15]:
                print(f"         style {e['rule']} line {e['line']}: {e['text'][:120]}")
        if verbose:
            for w in it.get("warnings", [])[:15]:
                print(f"         warn {w.get('rule', '')} {w.get('text', '')[:120]}")
    fails = sum(i["status"] == "fail" for i in items)
    pend = sum(i["status"] == "pending" for i in items)
    print(f"\n{slug}: {fails} failing, {pend} pending")
    return 1 if fails or (strict and pend) else 0
