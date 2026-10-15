"""`desk review <slug>`: one call to a model from another family (Google), doing two jobs in separate
parts of one reply: a method review against the plan and results, and a cold read as a non-specialist.

Every issue must quote the draft exactly; issues whose quote isn't in the draft are dropped as invented.
Issues get ids (r1, r2, …). Answer each must_fix and should_fix in checks/responses.json:
{"r1": "fixed: rewrote the sentence", "r2": "rejected: the plan defines it this way (Q2 estimand)"}.
"""

from __future__ import annotations

import json
import re

from .config import write_json
from .models import complete
from .study import Study, figure_text, prose_of

PROMPT = """You review a finance research article before publication. A different AI model wrote it; assume
nothing in it is right until the plan and results show it. Do two jobs and keep them separate.

PART A: METHOD REVIEW. Check the draft against the frozen plan and the results. Report only real problems:
1 wrong fact: a number attached to the wrong measure, period, sample, index or horizon
2 overclaiming: causal words without a design that supports them; a pattern generalised from few independent
  periods; overlapping windows treated as independent; anything that reads as a forecast or advice
3 missing caveat that changes the meaning (survivorship, look-ahead, small sample, price vs total return)
4 drift from the plan: a question answered differently from how the plan defined it, a frozen question
  missing, or an exploratory result presented as tested
5 the critique stated weaker than its strongest form

PART B: COLD READ. Now read as an intelligent adult in India who manages their own savings and has never
read a finance paper or taken a statistics course.
6 every term, statistic or abbreviation used before it is explained (quote the first use)
7 every chart whose point is not stated in words near it, or whose "how to read it" wouldn't help a novice
8 any passage you had to read twice
9 the "Still lost? Read this" section, read alone: does it leave a novice with one true, repeatable sentence
  without overclaiming? Quote it if not.
Then, for each sub-question in the plan, answer it in one sentence using ONLY the article. If the article
doesn't let you answer, say "cannot tell from the article".

Reply in JSON only:
{"issues": [{"quote": "<exact text from the draft, 5-40 words>", "category": <1-9>,
             "severity": "must_fix" | "should_fix" | "minor", "problem": "<one sentence>",
             "evidence": "<plan section or results key, for 1-5>", "fix": "<concrete rewrite or action>"}],
 "answers": {"q1": "<one sentence>", ...},
 "overall": "<two sentences: the article's biggest weakness and its biggest strength>"}
"""


def main(slug: str) -> int:
    S = Study(slug)
    R, art, figs = S.results(), S.article(), S.figures() or {}
    if R is None or art is None:
        raise SystemExit("need results.json and article.mdx first")
    fm, body = art
    draft = f"# {fm.get('title')}\n{fm.get('dek')}\nFinding: {fm.get('finding')}\n\n{body}"
    facts = "\n".join(f"{k}: {v['value']} {v['unit']}{' (exploratory)' if v.get('exploratory') else ''} {v.get('note', '')}"
                      for k, v in R["facts"].items())
    checks = "\n".join(f"{k}: {'passed' if v['passed'] else 'FAILED'} {v['detail']}" for k, v in R["checks"].items())
    user = (f"## Frozen plan\n{S.plan}\n\n## Results: facts\n{facts}\n\n## Results: checks\n{checks}\n\n"
            f"## Figures (title, subtitle, how to read)\n{figure_text(figs)}\n\n## Draft\n{draft}")
    out = None
    for attempt in range(2):                    # one retry if the reply is cut off or isn't valid JSON
        reply = complete(S.dir, "review", [{"role": "system", "content": PROMPT}, {"role": "user", "content": user}],
                         json_mode=True, purpose=f"review attempt {attempt}")
        m = re.search(r"\{.*\}", reply.text, re.S)
        try:
            out = json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            out = None
        if out is not None:
            break
        print(f"reply not valid JSON (finish reason {reply.finish}); {'retrying' if attempt == 0 else 'giving up'}")
    if out is None:
        raise SystemExit("review reply could not be parsed twice; the raw replies are in checks/transcripts/")
    norm = lambda t: re.sub(r"\s+", " ", re.sub(r"[*_`]", "", t)).strip()
    hay = norm(draft + " " + prose_of(body) + " " + figure_text(figs))
    kept, dropped = [], []
    for i in out.get("issues", []):
        (kept if i.get("quote") and norm(i["quote"]) in hay else dropped).append(i)
    for n, i in enumerate(kept, 1):
        i["id"] = f"r{n}"
    write_json(S.checks_dir / "review.json", {"model": reply.model, "inr": round(reply.inr, 2), "overall": out.get("overall"),
                                              "answers": out.get("answers", {}), "issues": kept,
                                              "dropped_invented_quotes": dropped})
    print(f"{reply.model} ₹{reply.inr:.1f}: {len(kept)} issues, {len(dropped)} dropped (quote not in the draft)")
    print("overall:", out.get("overall"))
    for i in kept:
        print(f"\n{i['id']} [{i['severity']}] cat {i['category']}: {i['problem']}\n  quote: {i['quote']}\n  fix: {i.get('fix', '')}")
    print("\nCold-read answers (compare with the article's own answers):")
    for q, a in out.get("answers", {}).items():
        print(f"  {q}: {a}")
    return 0
