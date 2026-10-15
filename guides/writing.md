# Step 3: writing the article

The reader manages their own money, is intelligent, and has never read a finance paper or taken a statistics course. The test: **they finish the piece understanding it, and can say something true about it to a friend.** When in doubt, explain once more.

## The exemplars

The owner's own sites set the bar for explanation. Read the guides below before a first article, and one published piece before every article.

- **This Indian Life** (thisindianlife.today). Read its `docs/EDITORIAL_NORTH_STAR.md` and `docs/academy/VOICE.md` (in the project's own repository; on the owner's machine, the sibling folder `THis Indian Life`). Take from it: an answer thesis before drafting, answer types, a narrative job for every chart, specific Indian particulars, and the no-overclaim rule.
- **Hope and Despair** (hopeanddespair.world). Read its `WRITING.md` and `EXPLAINERS.md` (sibling folder `hope and despair`). Take from it: lead with the point and complicate it at once, a human scale for every number, caveats before the evidence, weighing rather than splitting, the evidence tag, and the "Still lost? Read this" box.

The rules below are those ideas adapted to finance research.

## Before drafting: the thesis and the answer types

Once results are in, write the article's **thesis in one sentence**, no caveat pile-up. If you can't, the study hasn't found its argument yet. Go back to the results, not the prose.

Then give every sub-question an **answer type**:

| Type | When | Shape |
|---|---|---|
| Direct | the evidence answers it | "Yes. Waiting cost the typical applicant about 11 points against the index." |
| Qualified | it answers part, and limits the claim | "Usually, but only for IPOs less than a tenth under water." |
| Null | we looked properly and found no difference | "No. Being under water at six months told you nothing about the next year, and the sample was big enough to see a gap of 5 points." |
| Can't tell | the data can't answer it honestly | "The data shows the pattern. It can't show why." |

Null and can't-tell answers get the same care and the same space as direct ones.

## The shape of an article

1. **Title**: the thesis, in plain words. ("Your IPO is below the issue price. Waiting usually costs you.")
2. **Dek**: the question and the answer in one or two sentences.
3. **Finding box** (`finding`): one sentence. Confirmatory results only.
4. **Opening** (150–300 words): a real case with real dates and rupees, putting the reader in the decision. Then the big question, and why intuition gets it wrong.
5. **Before you read** (`id="caveats"`): the two or three things that could make a reader misuse the numbers, stated before the evidence. Examples: price returns without dividends, mainboard IPOs only, history rather than forecast. The rest of the limits go at the end.
6. **In brief**: each sub-question's answer in one line, with its number and its answer type.
7. **One section per sub-question** (`id="q1"`, `id="q2"`, …), in the plan's order, each answering the question the last one raised.
8. **What I found when I dug further** (`id="further"`): exploratory results, labelled, with the count of things tried. Only if there are any.
9. **What this means for you** (`id="meaning"`): what the reader should now believe, and what they should *not* conclude. No advice to buy, hold or sell.
10. **What would change my mind**: the evidence that would overturn the finding.
11. **Limits** (`id="limits"`): the remaining caveats, each once.
12. **How I did it** (`id="method"`): data, sample, definitions, methods, the checks run and their results, the frozen plan's link, amendments. Complete and visible.
13. **Still lost? Read this** (`id="still-lost"`): two to four warm, jargon-free paragraphs that explain the whole piece from zero. A reader who bounced off every chart reads only this and still leaves with one true thing they can say out loud. It simplifies; it never overclaims.

## The shape of a section

- **The heading is the question** in the reader's words.
- **The first sentence is the answer**, with its number. No wind-up.
- **Complicate it at once.** The next beat gives the catch, the exception or the other reading. A finding never stands alone.
- **The chart**, big, with the finding as its title and an evidence tag (`guides/charts.md`).
- **How to read it**: the axes, what one mark means, where to look first. Assume the reader has never seen this kind of chart.
- **Why it happens**: the mechanism, as far as the evidence goes. Without a causal design, say "this proves the pattern, not the cause", then give the candidate explanations.
- **A human scale for every big number.** "11 points" means little; "₹1 lakh became ₹93,000 instead of ₹1.04 lakh" lands. In the headline sections, use a real case: a real IPO, a real SIP start month, with dates.
- **How sure I am**, once, in words and numbers.
- **Two readings**, where the same chart supports both an optimist's and a sceptic's story. Show both, then **weigh them**: say which is heavier and why. Splitting the difference is its own dishonesty.

## Specificity kills the AI smell

Generic prose reads as machine prose; specific prose reads as a person who looked. Name the IPO, the month, the index, the rupee amount. "Paytm, 18 November 2021, ₹2,150 a share" beats "a high-profile listing". Never invent an example: every name, date and number comes from the results or a source you opened.

Explain each term in the sentence where it first appears. "The median IPO (the middle one, with half doing better and half worse)". "Excess return over the Nifty 500 (how far ahead of or behind the index)". Link a hard concept to Wikipedia the first time it matters, at most once per concept.

Round as a person speaks: 44%, about ₹3.3 lakh crore. Give provenance and vintage where they matter ("NSE bhavcopy, to 8 October 2026").

## Argue

The early pilots read as results logs: "X% did Y" sentence after sentence, sixteen questions at equal depth. An article is an argument. Lead with tension: the common belief, the critique, the reader's fear. Each section moves the argument forward. Go deep on three or four findings; secondary results go in a short table ("Other things I measured"). State conclusions with conviction where the evidence is strong, and plainly when it isn't. Have a view.

## Before and after

**Before** (the IPO pilot, accurate and flat):
> Of those below at six months, 44% closed at or above the issue price at some point within a year, and 75% within three years. Yet 53% were below it at the three-year mark.

**After** (same numbers, explained):
> Most IPOs that fall below their issue price do climb back to it, which is why waiting feels sensible. Three in four touched it again within three years. But touching isn't staying. At the three-year mark, more than half were under water again, because many reached the issue price and then slid back under it. The price you paid behaves less like a floor and more like a ceiling the stock keeps bumping into.

The second version leads with the reader's belief, uses the same numbers, explains the mechanism and leaves an image the reader can repeat.

## House style

- First person singular, "I". Plain Indian English, British spelling, lakh and crore, ₹.
- Short paragraphs, one idea each. Vary sentence length; a short sentence lands a point.
- Don't make "the chart shows" the verb of every paragraph.
- No em-dash chains, no "not X but Y", no "X? Y." reveals, no filler hedges, no tidy moral at the end of every section, no triads by reflex. The style gate catches most of this; read the draft aloud for the rest.
- No internal names: no "desk", "Data bank", file paths or model names in reader copy. AI involvement is disclosed in the front matter's `ai` block.
- Don't name critics. State their argument in its strongest form as "the critique".
- Every number comes from `results.json`.

## Before running desk check

- Can you state the article's argument in one sentence, and is it the title?
- Could someone who has never invested follow every section?
- Does every chart have a sentence telling the reader what to see?
- Is every frozen question answered, with its answer type, including the inconvenient ones?
- Would the "Still lost?" box alone leave a reader with one true, repeatable sentence?
