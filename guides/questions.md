# Step 1: choosing the questions

This step decides whether a study is worth reading. Both early pilots failed here: one asked seventeen questions at equal depth and argued nothing; the other asked five counting questions and found no mechanism. Spend most of the study's thinking on this step.

## What a good study looks like

One big question a real investor has, broken into three to five sub-questions. Together the answers make an argument: by the end the reader believes something they didn't, or believes it for better reasons. Each sub-question is either a real test, with a plausible answer either way, or a needed step towards one.

## Two shapes

- **A study** (the default): one big question, three to five sub-questions, one argument.
- **A canonical study**: the site's reference piece on a big topic (SIPs, IPOs, index funds). It takes as many questions as the topic honestly demands, organised so it still argues rather than lists:
  - **Chapters** (`## Chapter 1. …`, two to seven), each making one claim the reader can repeat. The chapters in order form the argument.
  - **Sub-questions** inside chapters (`### Q1.`, numbered through the whole plan, at most 24).
  - **Headline findings** (`## Headline findings`): the three to five questions that get the deep treatment in the article (mechanism, rupee story, the big chart). Every other question is answered compactly: one chart, a short answer, its number.
  - **Status per question**: `new` (frozen here, with a prediction) or `known` (already computed elsewhere: say where, give the earlier value as a replication target, no prediction). A canonical study often re-verifies a lot of known results with fresh code; that is useful, as long as it is labelled.
  - **No silent gaps.** Every obvious question on the topic is either in a chapter, answered as naive context, or listed under "Questions I won't ask" with its reason.

The October SIP article failed as a canonical piece: seventeen questions at equal depth, no chapters, no argument. The chapter claims and the headline findings exist to prevent that.

## The procedure

### 1. State the big question in the reader's words

Write it as an investor would ask it: "My IPO is below the issue price. Should I wait?" Then write who asks it, what they are deciding and what they believe now. If you can't name the decision, the study has no reader.

### 2. Gather what's already known (one sitting, no data)

- **The literature.** Find the main academic papers on the question, India first, then global. For each: the claim, the sample, the method, and whether it would hold in India today. Open every paper you cite by link or DOI. Anything you have not opened is marked `(unverified)` and stays out of reader copy.
- **The common wisdom and the strongest critique.** What do advisers, forums and finfluencers say? What is the best argument against it? Write the critique in its strongest form. Don't name the people who make it.
- **What the site already answers.** Check tipsheet.markets so the study doesn't repeat a page; link to it instead.
- **The data we hold.** List the inputs that could answer the question, their dates and their traps (survivorship, adjustments, publication lags).

### 3. Generate many questions, then cut hard

Write 30 or more candidate questions without judging them. Push past the obvious ones:
- **Mechanism:** *why* would the answer be what it is? What would have to be true?
- **Conditioning:** when is the answer different? By size, valuation, era, holding period, entry point.
- **Counterfactual:** compared with what? The reader's realistic alternative, never a straw man.
- **Rupees and time:** what does it mean for ₹1 lakh, or for a ₹10,000 monthly SIP, over a horizon a person actually holds?
- **The other side:** who is on the other side of the reader's trade, and do they do better?
- **What would surprise:** which answer would make the owner say "I didn't know that"?

Then score each candidate on four tests. Keep a question only if it passes all four:

| Test | Ask |
|---|---|
| So what | Would the answer change what a reader does or believes? |
| Rival answers | Is there a plausible answer each way? Write both and what each would mean for the reader. If only one answer is plausible, it's a fact to state, not a question to study |
| Mechanism | Does it get at why, or condition on something that matters, rather than only count? |
| Answerable | Can our data answer it without look-ahead or survivorship bias, with enough independent observations? |

### 4. Build the tree

- **Big question → 3 to 5 sub-questions**, ordered so each answer sets up the next. The last one is usually "so what should a reader do with this?" answered with evidence, not advice.
- **Naive questions**: the obvious things a first-time reader will ask ("how many IPOs fall below the issue price at all?"). Answer them briefly as context in the article. They don't count towards the three to five.
- **Questions I won't ask**, with a reason each. This is where tempting but unanswerable or off-topic questions go.

### 5. Write plan.md

Use the template. For each sub-question:
- the question in plain words, and why a reader cares
- the rival answers and what each would mean
- the **estimand**: exactly what number answers it, on what sample, over what dates
- the **method**, the comparison and the test, if any (see `guides/stats.md`)
- a **prediction**, written before any result
- the **checks** that apply (placebo, look-ahead, robustness) and why; or "none, descriptive" with the reason
- the **headline figure**: what it shows and what the reader should see in it

Plus: the data and its traps, what would change my mind, and the questions I won't ask.

### 5b. Plan the charts by job

For each sub-question, list its figures and each one's job (answer, spread, comparison, mechanism, conditioning, robustness, caveat, case; see `guides/charts.md`). Walk the list of jobs and include each one that helps the reader. No two figures do the same job. This happens before any result is seen, so the charts follow the questions and not whatever looks striking.

### 6. Stress-test the plan before showing it

Read it as a sceptical reader would and answer in the plan:
- Is any sub-question answerable in one sentence from common knowledge? Cut it or fold it into context.
- Do the sub-questions add up to an argument, or a list? Could you write the article's title from them?
- Is there at least one question where you honestly don't know the answer?
- Is the comparison the reader's real alternative?
- Where could the data mislead (survivors only, overlapping windows, one decade doing all the work)?
- Is any question causal ("why") when the data can only show a pattern? Rephrase it, or plan to answer "can't tell" honestly.

### 7. Human approval, then freeze

The owner or a colleague reads the plan. Their time here is better spent than anywhere else in the study. After approval, commit `plan.md` on its own and run `uv run desk freeze <slug>`.

## An example of the difference

The IPO pilot asked: "How often does an IPO below its issue price get back to it?" That is a count, and its answer changes nothing by itself.

Better sub-questions for the same reader:
- "If my IPO is below the issue price at six months, is holding it any worse than switching the money into an index fund?" (a decision, with a real alternative, and a plausible answer either way)
- "Does the price an IPO is under water at tell you anything, or is the issue price just an anchor in my head?" (mechanism: anchoring against information)
- "Do the IPOs that fall below their issue price share something you could see on the day of listing: subscription, issue size, the first day's move, the year?" (conditioning on what the reader knew at the time, if we hold the data)
- "Did applicants who sold on listing day do better than those who held?" (the other choice the reader actually had)
