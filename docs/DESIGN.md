# The tipsheet research desk: design

Written 2026-10-15. Replaces the research bench and desk inside the portal repo (`research/`, `docs/plans/research_desk.md`), which stay there untouched until the first study from this repo is published.

## What the desk is for

Finance research with the rigour of an academic paper, written for people who manage their own money. Each study takes one big question, breaks it into three to five sub-questions, and answers each in its own section with large, plain charts and explanations that err towards saying too much rather than too little. Null and unwelcome results are published with the same care as welcome ones.

## Why the first two studies were weak

Both pilots (`is-sip-bad`, `ipo-below-issue`) passed every gate and were still underwhelming. The old pipeline spent its effort on correctness and had nothing guarding the two things that failed:

1. **Question choice.** The SIP plan had 17 questions at equal depth: a survey, not an argument. The IPO plan had five questions, all counts ("how often", "how many"). No step asked which questions change a reader's mind, which have a surprising answer either way, or what mechanism lies underneath.
2. **Explanation.** The writer got results and a list of banned phrases. Nothing defined what a well-explained section contains, and nothing tested whether a non-specialist understood it.

So this design puts its weight on the question step and the writing step, and keeps verification mostly in free, deterministic code.

## The four steps

| Step | Who | Output | Cash |
|---|---|---|---|
| 1. Questions | Session (frontier model) using `guides/questions.md`; a human approves | `plan.md`, committed. The commit is the freeze | ₹0 |
| 2. Compute | Code the session writes, using `desk/calc.py` | `results/results.json`, `results/charts/*.json`, built-in checks recorded in the results | ₹0 |
| 3. Write | Session using `guides/writing.md` | `article.mdx`, `figures.json` | ₹0 |
| 4. Check | `desk check` (free), `desk recompute` and `desk review` (one cheap call each, from other model families), then a human read and a three-number spot check | `checks/*.json` | ~₹20–50 |

Hard cap: ₹250 of API spend per study, enforced in `desk/models.py` from a ledger. Session time is on the subscription and is not metered here, so the rule for the session is the same as for code: build nothing a study doesn't need.

## Verification, layer by layer

| Layer | Catches | Cost | Where |
|---|---|---|---|
| Input checks on load | gaps, duplicates, bad units, implausible values, missing delisted names, stale data | free | `desk/data.py`, `desk/checks.py` |
| Input fingerprints | results computed on data that has since changed | free | `results.json["inputs"]`, `desk check` |
| Tested calculation library | wrong CAGR/XIRR/return/bootstrap code | free | `desk/calc.py`, `tests/test_calc.py` (hand-worked and published known answers) |
| In-study sanity checks | parts that don't add up, look-ahead, effects that appear on shuffled data, fragile findings | free | `desk/checks.py`, declared in the plan, recorded in results |
| Independent recompute | code bugs in the headline numbers | ~₹10–20 | `desk recompute`: DeepSeek writes its own script from the plan's definitions, runs in the sandbox, script compares |
| Statistical honesty | overlapping-window overconfidence, dropped null results, exploratory results passed off as tested | free | `guides/stats.md`; `desk check` enforces question coverage and keeps exploratory facts out of the headline |
| Text matches numbers | invented or mis-rounded figures, wrong units or signs | free | numeric gate (ported from the bench) |
| Style | AI patterns, American spelling, millions instead of lakh/crore | free | style gate (ported) |
| Review + cold read | overclaiming, method drift, unclear writing, sections a novice can't answer from | ~₹5–15 | `desk review`: Gemini Flash |
| Human | everything else | 30–45 min | approve the plan; read the draft; recompute three numbers by hand |

## Adversarial review of the first proposal (2026-10-15)

I attacked my own earlier proposal before building. What changed:

1. **"A separate repo" cut the studies off from the portal's prepared tables.** The IPO study read `ipo_listings` and the adjusted bhavcopy panel that portal code builds. *Change:* the desk reads two kinds of input read-only, `databank:<dataset>` (newest warehouse snapshot) and `portal:<table>` (the portal's derived Parquet), through one module. It never imports portal code. Each study records path, size and hash for every input it used.
2. **Colleagues can't reach a laptop-only Data bank.** *Change:* a later `desk export <slug>` will write a study's own inputs to a folder that can be shared. Not built until a colleague needs it; the fingerprints make it straightforward.
3. **The site imported figures from `research/studies/…` inside the portal.** *Change:* `desk publish` copies `article.mdx` and `figures.json` into the portal's `content/posts/`, rewrites the import, and stops. It never commits: pushing the portal's main publishes live and needs the owner's say-so.
4. **"Generate 30–50 questions, then cut" by the same model still yields generic questions.** *Change:* every surviving sub-question must state rival answers and what each would mean for a reader, and must pass a "would anyone be surprised?" test. The plan also has a named section for the reader's naive questions, so obvious questions get answered briefly and depth goes where it pays.
5. **Models invent academic citations.** *Change:* every paper cited in a plan or article needs a working link or DOI that the session has opened; anything unopened is marked unverified and kept out of reader copy.
6. **Labelled exploration becomes a loophole: everything turns "exploratory".** *Change:* facts are tagged `exploratory`; `desk check` fails if the article's title, dek or finding box uses one, and exploratory sections must say how many things were tried.
7. **Placebo, look-ahead and robustness checks for every study is overbuild.** A descriptive count has nothing to placebo. *Change:* the plan declares which checks apply and why; `desk check` enforces exactly the declared list.
8. **"A tested library against published figures" invites building a library before a study needs it.** *Change:* functions are added when a study needs them, each with a known-answer test in the same commit.
9. **An LLM is a poor stand-in for a novice reader**; it knows the jargon. *Change:* the cold-read prompt asks for concrete outputs (every term used before it is explained, every chart whose point isn't stated in words, and the reader's answer to each sub-question from the article alone), and the human read remains the real test.
10. **The independent recompute shares the plan's ambiguities and the same input data**, so it catches code bugs, not data bugs. *Accepted:* the input checks and known-answer tests cover data; the recompute prompt asks the model to flag every ambiguity it resolved.
11. **The section template could make every section formulaic and long.** *Change:* answer, chart, chart walk-through and mechanism are required; the rupee example is required for the headline sections and optional elsewhere.
12. **Skills only work in Claude Code; colleagues may use Codex.** *Change:* the guides are plain Markdown in `guides/`, referenced from `CLAUDE.md`; `AGENTS.md` is a symlink to it.
13. **One review call may dilute two jobs** (method review and cold read). *Accepted for cost:* one call with two clearly separated parts and structured output. Split later if the reviews get thin.

## Repository layout

```
CLAUDE.md            the protocol (AGENTS.md links to it)
guides/              questions.md, stats.md, writing.md, charts.md
desk/                the shared code: data, calc, checks, gates, models, sandbox, CLI
studies/_template/   copied by `desk new <slug>`
studies/<slug>/      plan.md, compute.py, recompute.md, figures.py, article.mdx, results/, checks/
tests/               tests for desk/
```

## Exemplars (decided 2026-10-15)

The owner's own sites set the bar: This Indian Life (thisindianlife.today) and Hope and Despair (hopeanddespair.world). From them the desk takes:
- an answer thesis before drafting, and answer types (direct, qualified, null, can't tell)
- a narrative job for every chart
- an evidence tag on every chart (tested, measured, exploratory, illustration)
- caveats before the evidence
- a human scale for every number
- weighing two readings rather than splitting them
- the "Still lost? Read this" closing box

`desk check` requires the fixed sections, and `figures.write` requires every chart's job and evidence tag.

## What is deliberately absent

The old bench's router with role profiles, nine critics, red team, reader panel, scoreboard, mock calibration, state machine, three tiers of work, and the public-repo export. Each can return when a real study shows it is needed.

## Open decisions for the owner

- Public or private GitHub repo (local only until decided).
- When to retire the portal's `research/` bench.
