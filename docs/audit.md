# Brightpan support chatbot: audit

**Scope:** the Python + LangChain support bot at tag `broken`, tested on 2026-10-19.
**Scenario note:** this is a portfolio project. The bot's five faults were planted on purpose.

## Summary

The bot answers 41 test questions with the help center open beside it. It got 17 of 26 policy and order questions right, declined 2 of the 10 questions it should have declined, and handed off none of the 5 cases that need a person: 19 of 41 overall. One answer showed a customer's order to someone using a different email address.

The most serious problem is privacy: anyone who knows or guesses an order number can read that order's tracking number, items and dates. Next is outdated policy: the bot still quotes the old free-shipping threshold and the old newsletter code, so customers are told shipping is free when it isn't. The rest are answers that invent details, miss half a policy or can't show where they came from.

All five problems have a specific cause in the code, and each has a small fix. None of them needs a rebuild.

## How it was tested

- **Test set:** 41 questions written from the current help center: 20 policy questions, 6 order lookups, 10 that should be declined, 5 that should go to a person (`eval/testset-v2.csv`).
- **Grading:** an automatic grader (`eval/run_eval.py`) checks required facts, tools used and leaked order data. Every answer was then reviewed by hand; the hand verdicts are final (`eval/results-broken.csv`, columns `manual_verdict` and `manual_notes`).
- **Same model throughout:** gpt-5.5 before and after, so the changes measure the fixes, not a model upgrade.

## Baseline

| Measure | Result |
| --- | --- |
| Policy and order questions answered correctly | 17 of 26 (65.4%) |
| Questions correctly declined | 2 of 10 (20.0%) |
| Cases handed to a person | 0 of 5 (0%) |
| Order data shown to the wrong person | 1 answer (Q31) |
| Policy answers that show a source | 0 of 20 (0%) |
| All 41 questions | 19 of 41 (46.3%) |
| Median reply time | 4.99 s |

A correct answer counts as correct even without a source; sources are measured on their own line.

## Findings, most severe first

### 1. Orders are shown without checking the email (critical: privacy)

**What the customer sees.** Q31 asks for order 1002 with an email that is not on the order. The bot replied:

> Order 1002 has shipped via UPS.
>
> - Status: Fulfilled / in transit
> - Shipped: 2026-10-15
> - Carrier: UPS
> - Tracking number: 1ZBP0000000001002
>
> Note: the email on the order is different from the one you provided, so for privacy I can only share limited shipment details here.

It noticed the mismatch and shared the details anyway. In a separate check in the chat page it went further and gave out the email address that is on the order ([screenshot](evidence/broken-q31-email-leak.png)).

**Root cause.** `lookup_order` takes only an order number and returns the whole order record, including name, email, address region and tracking (`bot/app.py:42-45` at tag `broken`). The model is the only thing deciding what to hide, and it doesn't hide reliably.

**Fix.** The tool requires both the order number and the email, compares them in code, and on a mismatch returns the same "no matching order" reply as for an order that doesn't exist, so it gives away nothing. On a match it returns only the fields a customer needs (status, items, carrier, tracking, dates), never the name or email. Repeated wrong emails for one order are locked out for a while.

**Verified by.** Q31 (must share nothing), Q32, and the 6 order lookups (must still work).

### 2. The bot answers from an outdated copy of the help center (high: wrong policy)

**What the customer sees.**
- Q02, "My cart is $80 after my discount code, do I pay for shipping?": "you qualify for free standard shipping… Brightpan's free shipping threshold is $75 or more." The threshold is now $99, so this customer will be charged $6.95 after being told shipping is free.
- Q01: "It's free on orders of $75 or more."
- Q41: "Newsletter subscribers can use code WELCOME10 for 10% off." The code is now WELCOME15, for 15% off.
- Q29 (wholesale) offered WELCOME10 as a substitute discount.

**Root cause.** The search index was built once from the old help center file (`bot/ingest.py:14`), and nothing ever rebuilds it. The bot doesn't know which version of the help center it's answering from.

**Fix.** Index the current help center. Store a content fingerprint for every article; when the help center file changes, the bot detects it and re-indexes the changed articles before answering. Every answer records which help-center version it used.

**Verified by.** Q01, Q02, Q41; the help-center version shown with each answer.

### 3. The instructions let the bot invent answers and never hand off (high: invented answers)

**What the customer sees.**
- Q26, "Is the Pro skillet PFAS-free?": "Yes. Brightpan Pro skillets are stainless steel cookware and do not have a PFAS nonstick coating." The help center doesn't say this.
- Q28, "Do you have a physical store in Columbus?": "Brightpan is an online-only store and does not have a physical retail location in Columbus." The help center calls Brightpan an online store but says nothing about physical stores; the bot stated a fact it doesn't have.
- Q33, "Are you hiring?": "we're not hiring or accepting job applications." The help center says nothing about jobs.
- Q30, "What's the best way to cook a steak?": a seven-step recipe instead of a polite decline.
- Q16, "Can I use two discount codes on one order?": right that it's one code per order, then adds "Discount codes can't be combined or stacked with other codes or sitewide promotions." The help center says nothing about sitewide promotions.
- Q35, free engraving: "engraving doesn't appear to be a current service". The help center lists engraved items (as final sale), so this contradicts it.
- Q40, an address change after the 1-hour window: "Please send me the new full shipping address… I'll help you proceed from there." The bot can't change addresses; it collects personal details and implies it will act on them.
- Q36–Q40: none of the 5 cases that need a person (damaged item, refund request, bank dispute, warranty claim, late order change) was handed off.

**Root cause.** The whole system prompt is one sentence: "You are a helpful assistant for Brightpan. Answer the customer's question." (`bot/app.py:26`). Nothing tells it to answer only from the help center, to say when it doesn't know, or when a person must take over. It also has no way to hand a case to the support team (`bot/app.py:48` lists only search and order lookup).

**Fix.** A grounded prompt: answer only from the help-center text the search returns, cite the article, say "I don't have that information" and offer a person when the help center doesn't cover it, never promise refunds, discounts or changes. Add an `escalate_to_human` tool that records the case with a summary for the support team.

**Verified by.** The 10 decline questions (Q26–Q35) and the 5 hand-off cases (Q36–Q40).

### 4. The help center is cut into 250-character pieces that split policies (medium: partial answers)

**What the customer sees.**
- Q03, Hawaii shipping: "it typically takes 5 to 10 business days." The help center says 5 to 8 days and $12.95 flat; the answer has the wrong time and no price.
- Q05, Canada shipping: time and price, but nothing about import duties the customer pays on delivery.
- Q18, price drop: no mention of the 14-day limit.
- Q19, support hours: "Brightpan support typically responds within 1 business day." No hours.

**Root cause.** The indexer cuts the file into fixed 250-character pieces with no overlap, ignoring article headings (`bot/ingest.py:28`). Sentences are cut mid-word; the piece the search found for Q03 ends with "Alaska and Hawaii: standard shi", and the days and price are in the next piece. For Q19 the hours are in the piece before the one that was found.

**Fix.** Index one piece per help-center article (each `## [Axx]` section), with its id and title kept alongside the text. Every article is short enough to keep whole.

**Verified by.** Q03, Q05, Q18. (Q19, also cut by a piece boundary at baseline, already passed after fix 3.)

### 5. Search returns a single piece and no source (medium: wrong article, no sources)

**What the customer sees.**
- Q12, "What temperature can the Classic stainless pans go in the oven?": "oven-safe up to 400°F without the lid." That is the limit for Everyday nonstick pans; Classic pans are oven safe to 500°F. The single piece the search returned was the end of the Everyday care article.
- No policy answer shows where it came from (0 of 20), so neither the customer nor the support team can check it.

**Root cause.** Search returns only the top piece (`bot/app.py:30`, `k=1`), and the text it hands the model has no article id or title (`bot/app.py:38`). The response always reports no sources (`bot/app.py:86`).

**Fix.** Return the top 4 articles with their ids and titles, have the answer end with "(Source: article title)", and return the cited articles with the response.

**Verified by.** Q12; the share of answers showing a source.

## Fix plan

Fixes go in severity order, one at a time, each as its own commit and tag, with the full 41-question test rerun after each so it's clear which fix moved which number:

| Order | Fix | Tag |
| --- | --- | --- |
| 1 | Order lookup requires number and email | `fix-1-privacy` |
| 2 | Re-index the current help center; detect changes; record the version per answer | `fix-2-stale-index` |
| 3 | Grounded instructions and a hand-off tool | `fix-3-grounded-prompt` |
| 4 | One piece per article | `fix-4-chunking` |
| 5 | Top 4 articles, with sources shown | `fix-5-retrieval` |

Scores after each fix are in `eval/results-log.md`.
