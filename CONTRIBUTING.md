# How work happens in this repository

Everything here is public: the plans, the code, the results, every model prompt and reply, and the mistakes. The git history is part of the record, so it is never rewritten.

## Branches

- `main` holds the desk (`desk/`, `guides/`, `docs/`) and every finished study.
- Each study is worked on a branch named `study/<slug>`, created from `main`.
- Changes to the desk itself go on a branch named `desk/<topic>`.
- Everything reaches `main` through a pull request. A study's pull request is merged when the study is published.

## A study's commits, in order

1. `plan.md` drafted and reviewed on the study branch. Commit as often as you like.
2. **Freeze.** After a person approves the plan, commit `plan.md` on its own, then run `uv run desk freeze <slug>`. It records the commit in `freeze.json` and creates the tag `<slug>/plan-frozen`. Commit `freeze.json` and **push the branch and the tag straight away**: GitHub's record of when the tag arrived is the public evidence that the plan existed before the results. Commit dates alone can be set to anything.
3. Compute, write, check: commit as you go. Results are committed with the code that made them.
4. `desk recompute` and `desk review` save their prompts, replies and scripts under `checks/`. Commit them as they are, including the bad ones.
5. `desk report <slug>`, then the lead researcher writes the report's narrative sections.
6. `desk publish <slug>` copies the article to the site and tags `<slug>/published-<date>`. Open the pull request, push the tag, merge.

## Rules

- **Never rewrite history** on a study branch after the freeze, or on `main` at all. No force-pushes, no amended or squashed commits. Merge pull requests with a merge commit.
- **Never move or delete a tag.**
- **Corrections after publication** go in a new commit on a branch `fix/<slug>-<what>`. Add a dated line to the study's `REPORT.md` under "What changed from the plan", and to the article, saying what changed and why. The published tag stays where it was; the corrected version gets a new `<slug>/published-<date>` tag.
- **Changes to the plan after the freeze** go under `## Amendments` in `plan.md`, with a date and a reason. `desk check` fails if anything above that heading changes.
- **No secrets, no raw source data, no local paths.** Keys live in `.env` (gitignored). Raw inputs stay out of the repo (see `LICENSE-CONTENT.md`). Transcripts and errors have local paths scrubbed; check before committing anything new.

## Commit messages

Plain sentences saying what changed and why. A commit that changes a result says which numbers moved.
