# tipsheet research

Finance research with the rigour of an academic paper, written for people who manage their own money. Studies are published on [tipsheet.markets](https://tipsheet.markets/research/). This repository holds everything behind them: the plans, the code, the results, every prompt sent to an AI model and every reply, and a report on how each study actually went, mistakes included.

## How a study is done

1. **Questions.** One big question a real investor has, broken into three to five sub-questions, each with the plausible answers either way. A person approves the plan, and it is frozen in git before any result is computed.
2. **Compute.** Code answers each frozen question, using tested calculations and recording checks for look-ahead bias, survivorship and robustness. Null results are reported like any others.
3. **Write.** An article for general readers. Every number in it is traced by code to the results.
4. **Check.** Free automated checks, an independent recalculation of the headline numbers by a second AI model working from the plan alone, a review and cold read by a third, an audit of every number in the text by a model, and a human read before publication.

The studies are planned, coded and drafted with AI models, and people at tipsheet read and sign off every one. Which model did what is recorded in each study.

## How to verify a study

Each study lives in `studies/<slug>/`:

| File | What it is |
|---|---|
| `plan.md` | The frozen plan. The tag `<slug>/plan-frozen` marks the commit; `## Amendments` logs every later change |
| `compute.py` | The code that produced every number |
| `results/` | Every citable number, every check and its outcome, and the hash of every input file |
| `recompute.md`, `checks/recompute*` | The independent recalculation: what the second model was told, its script and how its numbers compared |
| `checks/review.json`, `checks/responses.json` | The review's issues and how each was answered |
| `checks/transcripts/` | Every model prompt and reply, verbatim |
| `article.mdx` | The published article |
| `REPORT.md` | How the study actually went: findings, changes from the plan, mistakes and how they were caught, dead ends |

Source data is not redistributed (see `LICENSE-CONTENT.md`). Each study names its sources, and the input hashes let anyone holding the same files confirm they match.

## Working on the desk

- The protocol: `CLAUDE.md` (also `AGENTS.md`)
- Why it's built this way: `docs/DESIGN.md`
- The guides for each step: `guides/`
- Branches, tags and the rules for history: `CONTRIBUTING.md`

```
cp .env.example .env     # fill in paths and keys; chmod 600 .env
uv sync
uv run pytest
```

Code is MIT-licensed (`LICENSE`); writing, methods and results are CC BY 4.0 (`LICENSE-CONTENT.md`).
