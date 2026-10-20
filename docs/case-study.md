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

Every answer in the first and last runs was reviewed by hand; the hand verdict is final.

| Reviewed by hand | Policy + order answers (26) | Correct refusals (10) | Hand-offs (5) | All 41 questions |
| --- | --- | --- | --- | --- |
| Before (tag `broken`) | 17 | 2 | 0 | **19 (46%)** |
| After (tag `fixed-final`) | 26 | 9 | 5 | **40 (98%)** |

Privacy leaks went from 1 to 0, answers with a verified source from 0% to 100%, and the median reply time from 4.99 s to 4.18 s.

### Which fix moved which number

The same 41 questions after every fix, scored by the automatic grader so each step compares like with like (it is a little more generous on refusals than the hand review, and it doesn't count a correct answer as wrong just because the source is missing):

| Step | Policy + order answers (26) | Correct refusals (10) | Hand-offs (5) | Privacy leaks | Answers with a verified source (20) |
| --- | --- | --- | --- | --- | --- |
| Baseline, tag `broken` | 17 | 4 | 0 | 1 | 0 (0%) |
| Fix 1: order privacy | 17 | 3 | 0 | 0 | 0 (0%) |
| Fix 2: current help center, kept in sync | 17 | 3 | 0 | 0 | 0 (0%) |
| Fix 3: grounded instructions + hand-off tool | 20 | 9 | 5 | 0 | 0 (0%) |
| Fix 4: one piece per article | 24 | 9 | 5 | 0 | 0 (0%) |
| Fix 5: top 4 articles + sources | 26 | 9 | 5 | 0 | 20 (100%) |
| Final, tag `fixed-final` | 26 | 9 | 5 | 0 | 20 (100%) |

[eval/results-log.md](../eval/results-log.md) has every run, including the ones that failed for outside reasons.

The one remaining miss (Q29) declines a wholesale question correctly but doesn't offer to connect the customer with a person, which the test asks for.

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

> Yes, if you’re in the contiguous US, standard shipping is $6.95 because free standard shipping starts at $99 or more, calculated after discounts and before tax. Express shipping is $14.95 and is never free.
>
> For Alaska, Hawaii, Canada, or the UK, different shipping rates apply and free shipping does not apply. (Source: Shipping options and costs (United States); International shipping)

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

> I couldn’t verify that order with the order number and email provided. Please double-check both the order number and the email address used at checkout, then send them again.

**Q26. Customer:** Is the Pro skillet PFAS-free?

Before:

> Yes. Brightpan Pro skillets are stainless steel cookware and do not have a PFAS nonstick coating.

After:

> I don’t have information saying whether the Pro skillet is PFAS-free. I can connect you with the support team if you’d like.

**Q38. Customer:** This is the third time I've written to you. I'm disputing the charge with my bank.

Before:

> I’m really sorry you’ve had to write in multiple times — I understand why you’re frustrated.
>
> If you’ve already opened a dispute with your bank, the next steps typically need to go through that bank dispute process. I can still help look into what happened on our side and provide any order details or status information that may help.
>
> Please send your Brightpan order number, and I’ll check the order for you.

After:

> I’m sorry this has been so frustrating. I’ve sent your case to the support team for review.
>
> Please share the email address they should use to reply to you. If you have your order number too, please include it.

## Checking it on questions it was never tuned on

After the fixes I wrote 15 new questions and committed them before running them once on each build. Overall: 10/15 before, 14/15 after. The honest reading:

- **Facts didn't improve on new questions** (10/11 both before and after). The broken bot handles easy facts well when they aren't split across pieces and haven't changed. Its one miss was quoting the old $75 threshold. The fixed bot's one miss is a retrieval gap: asked "Which US state do your orders ship from?", its search didn't surface the short "About Brightpan" article.
- **What carried over is everything that keeps a store out of trouble:** declining instead of inventing (0/3 → 3/3), handing a warranty claim to a person, never touching another customer's order, and showing a verifiable source.

## What the testing caught along the way

- **Fix order matters.** After fix 3 (the grounded prompt), 18 of 20 answers already ended with "(Source: …)", but 8 of the cited titles were invented, because the prompt asked for article titles before the search results contained any. Sources became trustworthy only with fix 5, and the results log says so.
- **The automatic grader is a first pass, not the verdict.** It passed an invented "PFAS-free" answer because the answer contained the words "do not have", and it failed correct refusals worded differently than expected. Every final number here is from the hand review.
- **One fix, measured alone, looked like it did nothing.** Re-indexing the current help center fixed the three outdated answers, but three other answers flipped to wrong in the same run, because the faults still unfixed made the bot erratic. The log records both.
- **Runs that failed for outside reasons are kept, marked invalid:** a network outage, and a scripting mistake of mine that sent requests to the wrong port. Each was rerun.
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
