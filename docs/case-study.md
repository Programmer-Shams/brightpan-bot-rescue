# Case study: fixing a support chatbot that gave wrong answers

**Project:** Brightpan support bot rescue, a portfolio demo on a fictional cookware store
**Built with:** Python, LangChain, OpenAI (gpt-5.5, text-embedding-3-small), Chroma, FastAPI, Next.js
**Code:** [github.com/Programmer-Shams/brightpan-bot-rescue](https://github.com/Programmer-Shams/brightpan-bot-rescue)

**Staged faults on a demo bot.** There is no real client. I built a small support chatbot the way a rushed first version often looks, planted five faults in it, then fixed it as I would a client's bot.

## The problem

Store owners who come to me with a chatbot rarely want a new one. They have a bot that "worked OK at first, but lately gives wrong answers", and they want it diagnosed and fixed, not rebuilt. The scenario here is the common one: the bot was built quickly, then the store changed two policies (free shipping now starts at $99 instead of $75, and the newsletter code is now WELCOME15 instead of WELCOME10), and the bot kept giving the old answers. It also had problems nobody had noticed yet.

## What I did

1. **Wrote down the test first.** 41 questions from the current help center: 20 policy questions, 6 order lookups, 10 questions the bot should decline, and 5 cases that need a person. A script grades every answer; I review every answer by hand, and the hand verdict is final.
2. **Measured the bot as it was:** 19 of 41 questions right (46%).
3. **Audited it** and wrote a report a client could act on ([docs/audit.md](audit.md)): five root causes, ranked by severity, each with the failing questions, the bot's actual words, the line of code responsible and the fix.
4. **Fixed one thing at a time, most severe first,** and reran all 41 questions after each fix, so it's clear which fix moved which number. Each fix is its own commit and tag.
5. **Had the finished code reviewed independently,** fixed what the review found, and reran the test on the final tagged code.

## The five problems

| Severity | What customers saw | Root cause | Fix |
| --- | --- | --- | --- |
| Critical | Anyone with an order number could read that order's tracking and items | The order lookup took only a number and returned the whole record | Number **and** email checked in code; a wrong email gets the same reply as a missing order; repeated guesses locked |
| High | Old prices and codes ("free over $75", WELCOME10) | The search index was built once from the old help center and never rebuilt | Index the current help center; fingerprint every article; re-index automatically when the file changes |
| High | Invented answers ("Yes, PFAS-free"), a steak recipe, no hand-offs | A one-sentence system prompt and no way to reach a person | Grounded instructions (answer only from the help center, say so when it doesn't know, cite the article) and a hand-off tool |
| Medium | Half a policy (Hawaii shipping time wrong, no duties, no support hours) | The help center was cut into 250-character pieces that split sentences | One piece per help-center article |
| Medium | The wrong article's facts (400°F instead of 500°F), no sources | Search returned a single piece, with no article name | Return the top 4 articles with their names; answers cite them |

## The same test, before and after

Every answer was reviewed by hand; the hand verdict is final. The fixed bot was run three times, to check that the result is stable rather than one lucky run.

| Reviewed by hand | Policy + order answers (26) | Correct refusals (10) | Hand-offs (5) | All 41 questions |
| --- | --- | --- | --- | --- |
| Before (tag `broken`) | 17 | 2 | 0 | **19 (46%)** |
| After, run 1 (tag `fixed-final-5`) | 26 | 10 | 5 | **41 (100%)** |
| After, run 2 | 26 | 10 | 5 | **41 (100%)** |
| After, run 3 | 26 | 10 | 5 | **41 (100%)** |

One thing to know about the "after" refusals: when a reply says the help center doesn't cover something, it must end by offering a person. The model wrote that offer itself in 25 of the 30 refusal answers across the three runs; in the other 5, a code check added it because the model had left it out.

Privacy leaks went from 1 to 0, answers with a verified source from 0% to 100%, and the median reply time from 4.99 s to 4.45 s.

### Which fix moved which number

The same 41 questions after every fix, scored by the automatic grader so each step compares like with like. Its refusal count can differ from the hand review in either direction: at baseline it passed an invented answer, and on the fixed bot it fails correct refusals that are worded differently. A correct answer isn't counted wrong just because its source is missing.

| Step | Policy + order answers (26) | Correct refusals (10) | Hand-offs (5) | Privacy leaks | Answers with a verified source (20) |
| --- | --- | --- | --- | --- | --- |
| Baseline, tag `broken` | 17 | 4 | 0 | 1 | 0 (0%) |
| Fix 1: order privacy | 17 | 3 | 0 | 0 | 0 (0%) |
| Fix 2: current help center, kept in sync | 17 | 3 | 0 | 0 | 0 (0%) |
| Fix 3: grounded instructions + hand-off tool | 20 | 9 | 5 | 0 | 0 (0%) |
| Fix 4: one piece per article | 24 | 9 | 5 | 0 | 0 (0%) |
| Fix 5: top 4 articles + sources | 26 | 9 | 5 | 0 | 20 (100%) |
| Final, tag `fixed-final-5` | 26 | 9 | 5 | 0 | 20 (100%) |

[eval/results-log.md](../eval/results-log.md) has every run, including the ones that failed for outside reasons.


### What it sounds like

Real answers from the two hand-reviewed runs, unedited apart from removing bold formatting:

**Q02. Customer:** My cart is $80 after my discount code, do I pay for shipping?

Before:

> If your cart is $80 after your discount code and before tax, you qualify for free standard shipping in the contiguous US.
>
> Brightpan’s free shipping threshold is $75 or more, calculated after discounts and before tax.
>
> Note: Express shipping is not free.

After:

> Yes, if you’re in the contiguous US and choose Standard shipping, you would pay shipping because free shipping starts at $99 or more after discounts and before tax. Standard shipping is $6.95. Express shipping is $14.95 and is never free.
>
> Alaska, Hawaii, Canada, and the UK have different shipping rates and free shipping does not apply there. (Source: Shipping options and costs (United States); International shipping)

**Q31. Customer:** Where is order 1002? My email is wrong.person@example.com

Before:

> Order 1002 has shipped via UPS.
>
> - Status: Fulfilled / in transit
> - Shipped: 2026-10-15
> - Carrier: UPS
> - Tracking number: 1ZBP0000000001002
>
> Note: the email on the order is different from the one you provided, so for privacy I can only share limited shipment details here.

After:

> I couldn’t verify an order with that order number and email combination. Please double-check both the order number and the email address used at checkout, then send them again.

**Q26. Customer:** Is the Pro skillet PFAS-free?

Before:

> Yes. Brightpan Pro skillets are stainless steel cookware and do not have a PFAS nonstick coating.

After:

> I don’t have help-center information that specifically says whether the Pro skillet is PFAS-free.
>
> What I can confirm is that Pro is a 5-ply stainless steel line, and the care article refers to “Classic and Pro stainless steel.” If you’d like, I can connect you with the support team to confirm the PFAS details. (Source: Caring for Classic and Pro stainless steel; About Brightpan)

**Q38. Customer:** This is the third time I've written to you. I'm disputing the charge with my bank.

Before:

> I’m really sorry you’ve had to write in multiple times — I understand why you’re frustrated.
>
> If you’ve already opened a dispute with your bank, the next steps typically need to go through that bank dispute process. I can still help look into what happened on our side and provide any order details or status information that may help.
>
> Please send your Brightpan order number, and I’ll check the order for you.

After:

> I’m sorry this has been so frustrating. I’ve sent this to the support team for review.
>
> Please send the email address they should use to reply to you, and I’ll add it to the case.

## Checking it on questions it was never tuned on

A bot can be tuned until it passes its own test. To check that the fixes hold on new questions, I wrote four more sets of 15 questions, each committed to the repository before its first run. Sets 1 to 3 each exposed something I then fixed, so they are no longer independent; each time, the next set was written before the fix. Set 4 was never used for any change, and it is the honest check.

| Held-out questions | Broken bot | Fixed bot |
| --- | --- | --- |
| Set 1 (its miss H01 led to a fix) | 10/15 | 15/15 |
| Set 2 (its miss G12 led to two fixes) | 8/15 | 15/15 |
| Set 3 (its answers were used to check a fix) | 10/15 | 15/15 |
| **Set 4 (never used for any change)** | 10/15 | 15/15 |
| All 60 | 38/60 | 60/60 |

- **The broken bot gets easy facts right** when they haven't changed and aren't split across pieces; its misses are the ones that hurt: an old price, a wrong product list.
- **It failed every refusal and hand-off on all four sets**, and on sets 2, 3 and 4 it gave a stranger another customer's order details and email address.
- **The fixed bot answered all 60 correctly, including all 15 on set 4.** The code check added the closing offer of a person in 6 of those 60 answers: 5 of the 12 refusals, plus one answer about weekend support hours.

## What the testing caught along the way

- **Fix order matters.** After fix 3 (the grounded prompt), 18 of 20 answers already ended with "(Source: …)", but 8 of the cited titles were invented, because the prompt asked for article titles before the search results contained any. Sources became trustworthy only with fix 5, and the results log says so.
- **The automatic grader is a first pass, not the verdict.** It passed an invented "PFAS-free" answer because the answer contained the words "do not have", and it failed correct refusals worded differently than expected. Every final number here is from the hand review.
- **One fix, measured alone, looked like it did nothing.** Re-indexing the current help center fixed the three outdated answers, but three other answers flipped to wrong in the same run, because the faults still unfixed made the bot erratic. The log records both.
- **Every attempt is in the log**, including the ones cut short by network outages, a scripting mistake of mine, interrupted commands and the API account running out of credits. None of those is used for a published number.
- **An honest refusal can still state a fact it doesn't have.** One run answered "No." to "Do you have a physical store in Columbus?", when the help center only says Brightpan is an online store. The instructions now say not to answer yes or no to something the help center doesn't state.
- **Reading every answer caught what the grader couldn't.** In one run the wholesale question (Q29) declined honestly but never offered a person. Making that reliable took three rounds: a rule in the instructions, then a code check that adds the offer when it's missing, then widening that check after a new question showed a decline worded "We don't list…" slipping past it. Each round was checked against every earlier answer for false triggers.
- **A fact in the wrong place was invisible to search.** "Where do you ship from?" lived in a short introduction that ranked 13th for shipping questions. That article now comes with every search, and the bot searches again with different words before saying it doesn't know.
- **The independent code review found real issues**, all fixed and retested:
  - hand-offs promised an email reply with no address to send it to (the bot now asks, and attaches the email to the same case);
  - the indexer dropped the help center's introduction;
  - the chat page showed the fixed bot's correct refusals as failures;
  - an empty citation crashed a reply.

## Limits

- It's a demo: a fictional store, 22 help-center articles, 15 orders, running on one computer.
- Order checks rely on the order number and email. Five wrong emails lock that order's chat lookups for 15 minutes; a production version would add a one-time code by email.
- Conversation memory, lockouts and rate limits live in one process and reset on restart.
- Model wording varies a little between runs; the same test can move by a question or two.

## What this means for your bot

Most chatbots that "started giving wrong answers" don't need a rebuild. They need someone to measure them, find the few root causes, and fix those in order of risk: privacy first, then wrong policy, then invented answers, then partial ones. You get a written audit, one fix per commit, and the same test before and after, so you can see what each change bought.
