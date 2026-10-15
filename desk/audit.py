"""`desk audit <slug>`: every number in the article checked against the fact it should be, by a model from another
family (DeepSeek). It replaces the hand spot-check of three numbers (owner's decision, 2026-10-15).

The numeric gate proves each printed number exists somewhere in the results at its precision. It cannot tell
whether the sentence describes the *right* fact: a 10-year median quoted as a 5-year one, a 5th percentile as a
median, the Nifty 50 as the Nifty 500, or a number that happens to match an unrelated fact (the 8.4% slip in the
first SIP study). This audit gives the model each sentence, the numbers in it, and the facts each number matched
(key, value, unit, note), and asks whether the sentence uses them correctly.

Sentences are sent in batches. Issues get ids (a1, a2, …) and are answered in checks/responses.json like review
issues. Output: checks/audit.json, with the article's hash so `desk check` can tell when it is stale.
"""

from __future__ import annotations

import json
import re

from .config import sha256_file, write_json
from .gates import numeric
from .models import complete
from .study import Study, figure_text, gate_bundle, prose_of

PROMPT = """You audit numbers in a finance article. For each sentence you get the numbers it prints and, for each
number, the result facts it matched (key, value, unit, note). Fact keys are structured: q16_n500_red_p50 means
question 16, Nifty 500, the group of SIPs in the red, the median (p50); 10y means ten-year; m12 means at 12 months;
p5 is the 5th percentile; 'fraction' 0.143 prints as 14.3%; 'rupees' 1482046 prints as ₹14.8 lakh.

For every sentence, decide whether each number is described correctly: the right measure (median against
percentile against worst), horizon, index or asset, group, period, sign and unit. If a number matched several
facts, judge whether at least one of them fits the sentence's wording. Rounding to the printed precision is fine.

Report only real problems. Reply in JSON only:
{"issues": [{"sentence_id": "<id>", "number": "<the number as printed>", "severity": "must_fix" | "should_fix",
             "problem": "<one sentence>", "right_fact": "<the key that fits, if any>"}],
 "checked": <number of sentences you checked>}
"""


def _items(S: Study) -> list[dict]:
    R = S.results()
    fm, body = S.article()
    figs = S.figures() or {}
    head = "\n\n".join(str(fm.get(k, "")) for k in ("title", "dek", "finding"))
    text = head + "\n\n" + prose_of(body) + "\n\n" + figure_text(figs)
    rep = numeric.check(text, gate_bundle(R))
    facts = R["facts"]
    by_sentence: dict[str, dict] = {}
    for m in rep["mentions"]:
        # Number words ("ten-year", "one in twenty") describe rather than claim, and every fact the number matched
        # is passed on: capping the list once hid the right fact and produced false alarms (first SIP study).
        keys = [k for k in m["matches"] if k in facts][:60]
        if m["kind"] in ("year", "date", "word") or not keys:
            continue
        s = by_sentence.setdefault(m["sentence"], {"sentence": m["sentence"], "numbers": []})
        s["numbers"].append({"printed": m["text"] + (m["unit"] or ""),
                             "matched": [{"key": k, "value": facts[k]["value"], "unit": facts[k]["unit"],
                                          **({"note": facts[k]["note"]} if facts[k].get("note") else {})} for k in keys]})
    items = list(by_sentence.values())
    for i, it in enumerate(items, 1):
        it["id"] = f"s{i}"
    return items


def main(slug: str, batch: int = 20, full: bool = False) -> int:
    """Audit sentences not audited before (unless full=True). A sentence whose text and matched facts are unchanged
    keeps its earlier verdict and issue ids, so a small edit costs one small call, not a full rerun."""
    S = Study(slug)
    items = _items(S)
    prev_path = S.checks_dir / "audit.json"
    prev = json.loads(prev_path.read_text()) if prev_path.is_file() and not full else {}
    done = {json.dumps([d["sentence"], d["numbers"]], ensure_ascii=False, sort_keys=True) for d in prev.get("audited", [])}
    fp = lambda it: json.dumps([it["sentence"], it["numbers"]], ensure_ascii=False, sort_keys=True)
    current = {fp(it) for it in items}
    carried = [i for i in prev.get("issues", []) if any(fp(it) in done and it["sentence"] == i["sentence"] for it in items)]
    audited = [d for d in prev.get("audited", []) if json.dumps([d["sentence"], d["numbers"]], ensure_ascii=False, sort_keys=True) in current]
    todo = [it for it in items if fp(it) not in done]
    print(f"{len(items)} sentences with numbers; {len(items) - len(todo)} unchanged since the last audit; {len(todo)} to audit")
    issues, checked = [], 0
    next_id = 1 + max([int(i["id"][1:]) for i in prev.get("issues", [])] or [0])
    for b in range(0, len(todo), batch):
        chunk = todo[b:b + batch]
        out = None
        for attempt in range(2):
            reply = complete(S.dir, "audit", [{"role": "system", "content": PROMPT},
                                                  {"role": "user", "content": json.dumps(chunk, ensure_ascii=False)}],
                             json_mode=True, purpose=f"audit batch {b // batch + 1}, attempt {attempt}")
            m = re.search(r"\{.*\}", reply.text, re.S)
            try:
                out = json.loads(m.group(0)) if m else None
            except json.JSONDecodeError:
                out = None
            if out is not None:
                break
        if out is None:
            raise SystemExit("an audit batch reply could not be parsed twice; see checks/transcripts/")
        checked += int(out.get("checked", len(chunk)))
        known = {it["id"]: it for it in chunk}
        for iss in out.get("issues", []):
            if iss.get("sentence_id") in known:
                iss["sentence"] = known[iss["sentence_id"]]["sentence"]
                issues.append(iss)
    for n, iss in enumerate(issues, next_id):
        iss["id"] = f"a{n}"
    audited += [{"sentence": it["sentence"], "numbers": it["numbers"]} for it in todo]
    all_issues = carried + issues
    write_json(S.checks_dir / "audit.json", {"article_sha256": sha256_file(S.article_path),
                                             "figures_sha256": sha256_file(S.figures_path) if S.figures_path.is_file() else None,
                                             "sentences": len(items), "checked": checked, "audited": audited, "issues": all_issues})
    print(f"{len(todo)} sentences audited now; {len(issues)} new issues; {len(carried)} carried forward")
    issues = issues
    for iss in issues:
        print(f"\n{iss['id']} [{iss['severity']}] {iss['number']}: {iss['problem']}\n  in: {iss['sentence'][:160]}\n  right fact: {iss.get('right_fact', '')}")
    return 0
