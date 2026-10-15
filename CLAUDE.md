# tipsheet research desk

Finance research with academic rigour, written for people who manage their own money. Published on tipsheet.markets under /research/. The design and its reasons are in `docs/DESIGN.md`.

## The steps

Every study lives in `studies/<slug>/`, worked on the branch `study/<slug>`. Start one with `uv run desk new <slug>`. This repository is public: branches, tags and the rules for history are in `CONTRIBUTING.md`.

1. **Questions.** Read `guides/questions.md` and follow it. Output: `plan.md`. A human approves it, then commit `plan.md` on its own: that commit is the freeze. Run `uv run desk freeze <slug>` (it records the commit and tags it), commit `freeze.json`, and push the branch and the tag at once.
2. **Compute.** Read `guides/stats.md`. Write `compute.py`, which loads inputs only through `desk.data`, uses `desk.calc` for standard calculations, records every citable number with `R.fact(...)`, every declared check with `R.check(...)`, and writes `results/`. Add a function to `desk/calc.py` only with a known-answer test in `tests/`.
3. **Write.** Read `guides/writing.md` and `guides/charts.md`. Write `figures.py` (builds `figures.json` from results) and `article.mdx`.
4. **Check.** `uv run desk check <slug>` until it passes, then `uv run desk recompute <slug>` and `uv run desk review <slug>`. Fix or answer every review issue in `checks/responses.json` and run `desk check` again.
5. **Report.** `uv run desk report <slug>` writes the record half of `REPORT.md`. As the lead researcher, write its narrative sections honestly: what changed, what went wrong and how it was caught, dead ends, the weakest link. Then a human reads the article, recomputes three numbers by hand and signs off. `uv run desk publish <slug>` copies the article into the portal and tags the version. It never commits in the portal.

## Rules that are never broken

- **Numbers come from code.** No number is typed into the article, a chart title or a caption that is not in `results.json`. The numeric gate enforces it.
- **The plan is frozen before results.** Changes after the freeze go under "Amendments" in `plan.md`, with a date and a reason. Questions added after the freeze are exploratory and tagged so.
- **Every frozen question gets answered**, including the ones whose answer is null or unwelcome.
- **Exploratory results never make the headline** (title, dek, finding box).
- **Inputs are read-only.** Never write to the Data bank or the portal's data. Never import portal code.
- **Citations are opened before they are cited.** A paper you have not opened by link or DOI is marked unverified and stays out of reader copy.
- **Voice is "I"**, never "we". Critics whose arguments a study tests are not named; their argument is stated in its strongest form.
- **No internal names in reader copy** ("Data bank", "desk", file paths, model roles).
- **Cash cap:** ₹250 of API spend per study. `desk/models.py` refuses calls past it. Don't add paid calls beyond recompute and review.
- **Never rewrite git history**, move a tag or force-push. Commit model transcripts and failed attempts as they are.
- **Nothing local in committed files**: no raw source data, no local paths, no keys.
- **Keys** live in `.env` (gitignored). Never print them, pass them on a command line or put them in a prompt.
- **Indian English:** lakh and crore, British spelling, ₹.

## Commands

```
uv run desk new <slug>          copy the template
uv run desk freeze <slug>       record the commit that froze plan.md
uv run python studies/<slug>/compute.py
uv run python studies/<slug>/figures.py
uv run desk check <slug>        all free checks; writes checks/status.json
uv run desk recompute <slug>    independent recompute (DeepSeek, sandboxed)
uv run desk review <slug>       method review and cold read (Gemini)
uv run desk report <slug>       regenerate the record half of REPORT.md
uv run desk publish <slug>      copy into the portal's content/posts/
uv run pytest
```

## Environment

`.env` (copy `.env.example`): `DATABANK_ROOT`, `PORTAL_ROOT`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, `INR_PER_USD`.

## No extra skills or subagents

The guides are this desk's skills: plain Markdown that Claude Code, Codex or a person can follow, read at the step they cover. Independence comes from other model families called through `desk/models.py`, not from subagents of the same model. Add a skill or agent only when a real study shows the guides aren't enough, and record why in `docs/DESIGN.md`.

## Keep current

When the protocol or a guide changes, update this file and `docs/DESIGN.md` in the same commit. Log each study's status in `studies/README.md`.
