"""`desk recompute <slug>`: an independent recalculation of the study's headline numbers.

A model from another family (DeepSeek) reads only recompute.md (inputs, definitions, the keys to compute)
and writes its own script. The script runs in the sandbox on the inputs compute.py's `recompute_inputs`
writes, and its numbers are compared with results.json within each key's tolerance. The model never sees
compute.py or the results. Up to three attempts if the script crashes; a mismatch is not retried, it is
investigated.

recompute.md ends with a fenced block listing keys and absolute tolerances (in the fact's own unit):

    ```keys
    q1_share_back_3y 0.005
    q1_n_below 0
    ```
"""

from __future__ import annotations

import importlib.util
import re
import shutil

from .config import CACHE, read_json, scrub, write_json
from .models import complete
from .sandbox import run_python
from .study import Study

RULES = """You are recalculating headline numbers for a published finance study, independently of its authors.
Work only from the specification below. Write ONE self-contained Python 3 script.

Rules:
- Read inputs only from the directory in the INPUT_DIR environment variable; write only to OUTPUT_DIR.
- Allowed: the standard library, numpy, pandas, pyarrow, duckdb (duckdb.connect() only). No network, no subprocesses.
- Write OUTPUT_DIR/facts.json: a flat JSON object {key: number} with exactly the keys listed at the end.
- Fractions stay as fractions (0.75, not 75) unless the specification says otherwise.
- Where a definition is ambiguous, choose the reading that uses no future information, and record each such
  choice in OUTPUT_DIR/ambiguities.json as a list of strings.

Reply with the script only, in one ```python block.
"""


def _keys(spec: str) -> dict[str, float]:
    m = re.search(r"```keys\n(.*?)```", spec, flags=re.S)
    if not m:
        raise SystemExit("recompute.md needs a ```keys block: one 'key tolerance' per line")
    out = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, tol = line.split()
            out[k] = float(tol)
    return out


def _code(text: str) -> str:
    m = re.search(r"```python\n(.*?)```", text, flags=re.S)
    return m.group(1) if m else text


def main(slug: str) -> int:
    S = Study(slug)
    spec = (S.dir / "recompute.md").read_text()
    keys = _keys(spec)
    results = S.results()
    if results is None:
        raise SystemExit("no results.json: run compute.py first")
    missing = [k for k in keys if k not in results["facts"]]
    if missing:
        raise SystemExit(f"keys not in results.json: {missing}")

    work = CACHE / "recompute" / slug
    inputs, out = work / "inputs", work / "out"
    if inputs.exists():
        for f in inputs.iterdir():
            f.chmod(0o644)
        shutil.rmtree(inputs)
    inputs.mkdir(parents=True)
    mod_spec = importlib.util.spec_from_file_location(f"{slug}_compute", S.dir / "compute.py")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    if not hasattr(mod, "recompute_inputs"):
        raise SystemExit("compute.py must define recompute_inputs(out_dir)")
    mod.recompute_inputs(inputs)

    msgs = [{"role": "system", "content": RULES}, {"role": "user", "content": spec}]
    attempts = []
    for attempt in range(3):
        reply = complete(S.dir, "recompute", msgs, purpose=f"attempt {attempt}")
        script = work / f"script_{attempt}.py"
        script.write_text(_code(reply.text))
        r = run_python(script, inputs, out)
        ok = r.ok and (out / "facts.json").is_file()
        attempts.append({"attempt": attempt, "model": reply.model, "inr": round(reply.inr, 2), "ok": ok,
                         "error": "" if ok else scrub(r.stderr[-1500:] + " " + "; ".join(r.violations))})
        if ok:
            break
        msgs += [{"role": "assistant", "content": reply.text},
                 {"role": "user", "content": f"The script failed:\n{r.stderr[-3000:]}\n{r.violations}\nReply with the full corrected script."}]

    theirs = read_json(out / "facts.json") if (out / "facts.json").is_file() else {}
    amb = read_json(out / "ambiguities.json") if (out / "ambiguities.json").is_file() else []
    rows = []
    for k, tol in keys.items():
        a, b = results["facts"][k]["value"], theirs.get(k)
        same = isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(float(a) - float(b)) <= tol + 1e-12
        rows.append({"key": k, "ours": a, "theirs": b, "tolerance": tol, "match": bool(same)})
    S.checks_dir.mkdir(exist_ok=True)
    shutil.copy(work / f"script_{attempts[-1]['attempt']}.py", S.checks_dir / "recompute_script.py")
    write_json(S.checks_dir / "recompute.json", {"results_sha256": S.results_sha(), "attempts": attempts,
                                                 "ambiguities": amb, "rows": rows})
    for r in rows:
        print(("  ok   " if r["match"] else "  DIFF "), r["key"], r["ours"], r["theirs"])
    for a in amb:
        print("  ambiguity:", a)
    n = sum(r["match"] for r in rows)
    print(f"{n}/{len(rows)} matched; ₹{sum(a['inr'] for a in attempts):.1f}")
    return 0 if n == len(rows) else 1
