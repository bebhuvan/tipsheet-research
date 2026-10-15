# Step 3: writing the article

The reader manages their own money, is intelligent, and has never read a finance paper. They will read carefully if every paragraph earns its place. When in doubt, explain once more. Never assume they know a term, a statistic or why a chart looks the way it does.

## The shape of an article

1. **Title**: the finding, in plain words. ("Your IPO is below the issue price. Waiting usually costs you.")
2. **Dek**: one or two sentences: the question and the answer.
3. **Finding box** (`finding` in the front matter): the result in one sentence. Confirmatory results only.
4. **Opening** (150–300 words): a concrete case or a rupee story that puts the reader in the decision, then the big question, then why it's hard to answer from intuition.
5. **In brief**: the answer to each sub-question, one line each, with its number.
6. **One section per sub-question**, in the plan's order. Heading ids `q1`, `q2`, … match the plan (`<h2 id="q1">`).
7. **What I found when I dug further**: exploratory results, labelled, with the count of things tried. Only if there are any.
8. **What this means for you**: evidence-based implications. No advice to buy, hold or sell.
9. **Limits**: the caveats that change meaning, each stated once.
10. **How I did it**: data, sample, definitions, methods, checks run, the frozen plan's link, amendments. Complete and visible: the appendix for the sceptical reader.

## The shape of a section

Required in every section:
- **The question**, as the heading, in the reader's words.
- **The short answer**, in the first two sentences, with its number.
- **The chart**, big, with the finding as its title.
- **How to read the chart**: walk the reader through it. What the axes are, what one mark means, where to look first, and what the eye should notice. Many readers have never read a chart like it.
- **Why it happens**: the mechanism, as far as the evidence goes. If we don't know why, say so and give the candidate explanations.

Required in the headline sections, optional elsewhere:
- **A rupee example**: ₹1 lakh, or a ₹10,000 monthly SIP, followed through a real period with real dates. Specific beats average.
- **How sure I am**: in words and numbers, once. "In 9 of 10 resamples the gap was between 2 and 6 points." Name the caveat that matters and skip the ones that don't.

Explain every term the first time it appears, in the sentence itself or the next one. "The median (the middle IPO, with half doing better and half worse)". "Excess return over the Nifty 500 (how far ahead of or behind the index the stock was)". Re-explain briefly if the term returns after a long gap.

## Argue

An article is an argument, not a results log. The early pilots read as "X% did Y" sentence after sentence. Each section should move the argument forward: what did we believe, what does the data say, what follows. Lead with tension: the common belief, the critique, the reader's fear. State conclusions with conviction where the evidence is strong, and say plainly when it isn't.

Go deep on three or four findings rather than evenly across everything. Secondary results go in a short table ("Other things I measured") with one line each.

## House style

- First person singular, "I". Plain Indian English, British spelling, lakh and crore, ₹.
- Short paragraphs. Sentences under about 30 words where possible.
- No em-dash chains, no "not X but Y", no "X? Y." reveals, no filler hedges, no "In this article". The style gate enforces most of this.
- No internal names: no "desk", "Data bank", file paths or model names in reader copy. AI involvement is disclosed in the front matter's `ai` block.
- Don't name critics. State their argument in its strongest form as "the critique".
- Every number comes from `results.json` and is written at sensible precision: 44%, not 43.87%.

## Exemplars

The bar for explanation. Read one before writing.

- *(owner to choose: two or three pieces whose explaining the desk should match)*

## Before running desk check

Read the draft as the reader:
- Could someone who has never invested follow every section?
- Does each chart have a sentence telling the reader what to see?
- Does the article make an argument you could state in one sentence?
- Is every frozen question answered, including the inconvenient ones?
