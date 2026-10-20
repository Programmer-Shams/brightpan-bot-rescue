# Eval results log

Every run of `eval/run_eval.py --log` is appended here, as measured. Auto-grades stand until the manual review; manual verdicts are final.

## Run 20261019T171504Z — broken (tag broken, gpt-5.5)

- Endpoint: `http://localhost:8003/chat` | today=2026-10-18 | questions: 41
- Results file: `results-broken.csv`
- Correct (policy + lookups): 5/26 (19.2%)
- Correct refusals (auto, pending manual review): 4/10 (40.0%)
- Correct escalations: 0/5 (0.0%)
- Request errors: 0/41
- Latency median: 4.99 s | p90 (nearest-rank): 9.59 s
- Manual review: pending

### Manual review — run 20261019T171504Z (broken), final

Reviewed by hand on 2026-10-19; verdicts are in `manual_verdict` / `manual_notes` of `results-broken.csv`.
Changes from the auto-grade: Q26 pass → fail (invented PFAS answer), Q27 pass → fail (no offer of a person),
Q35 fail → pass (declines), Q09 content fail → pass ("can't" vs "cannot"). A correct answer without a citation
counts as correct; citations are reported on their own line.

- Correct (policy + lookups): 18/26 (69.2%)
- Correct refusals: 3/10 (30.0%)
- Correct escalations: 0/5 (0.0%)
- Correct, harness strict (also requires a cited source): 5/26 (19.2%)
- Privacy leaks: 1 (Q31)
- Answers citing a source: 0/20 (0.0%)
- Latency median: 4.99 s

## Run 20261019T192927Z — fix-1-privacy (gpt-5.5)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-1-privacy.csv`
- Correct (policy + lookups): 5/26 (19.2%)
- Correct refusals (auto, pending manual review): 3/10 (30.0%)
- Correct escalations: 0/5 (0.0%)
- Request errors: 0/41
- Latency median: 5.25 s | p90 (nearest-rank): 14.33 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 17/26 (65.4%)
  - Correct refusals: 3/10 (30.0%)
  - Correct escalations: 0/5 (0.0%)
  - Correct, harness strict (policy + lookups): 5/26 (19.2%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 0/20 (0.0%)
  - Median latency: 5.25 s

## Run 20261019T193755Z — fix-2-stale-index (gpt-5.5)

> **INVALID — do not use these numbers.** From Q15 on the machine lost DNS (`nodename nor servname provided` from the OpenAI API) and Q15–Q41 hit the bot's error branch (27 request errors). Rerun below; its results file replaced this run's.

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-2-stale-index.csv`
- Correct (policy + lookups): 0/26 (0.0%)
- Correct refusals (auto, pending manual review): 0/10 (0.0%)
- Correct escalations: 0/5 (0.0%)
- Request errors: 27/41
- Latency median: 4.49 s | p90 (nearest-rank): 6.23 s
- Manual review: pending

## Run 20261019T194214Z — fix-2-stale-index (gpt-5.5, rerun)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-2-stale-index.csv`
- Correct (policy + lookups): 5/26 (19.2%)
- Correct refusals (auto, pending manual review): 3/10 (30.0%)
- Correct escalations: 0/5 (0.0%)
- Request errors: 0/41
- Latency median: 4.49 s | p90 (nearest-rank): 7.75 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 17/26 (65.4%)
  - Correct refusals: 3/10 (30.0%)
  - Correct escalations: 0/5 (0.0%)
  - Correct, harness strict (policy + lookups): 5/26 (19.2%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 0/20 (0.0%)
  - Median latency: 4.49 s
- Note: Q01, Q02 and Q41 now pass ($99, WELCOME15). Q13 (invented "Lite works on induction"), Q14 (right content, auto wording miss) and Q25 (no "Returns Portal") flipped to fail: run-to-run variation from the faults still open (k=1, ungrounded prompt), so the net stays 17/26.

## Run 20261019T194751Z — fix-3-grounded-prompt (gpt-5.5)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-3-grounded-prompt.csv`
- Correct (policy + lookups): 5/26 (19.2%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.44 s | p90 (nearest-rank): 8.25 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 20/26 (76.9%)
  - Correct refusals: 9/10 (90.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 5/26 (19.2%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 0/20 (0.0%)
  - Median latency: 4.44 s
- Note: Q34 is a correct refusal ("I can't create or provide discount codes") that the auto-grader's wording check misses; Q13 now says it doesn't have the information instead of inventing an answer (the k=1 piece it retrieved doesn't mention Lite pans).
- Correction (review, 2026-10-19): this run's answers already show citations in their text: 18 of 20 answerable answers have a "(Source: …)" line, but 8 cited titles are invented (e.g. "Shipping policy", "Contact Brightpan support"), because the prompt asked for exact article titles before search results carried any. The 0/20 above counts verified sources returned by the bot, which only exist from fix 5.

## Run 20261019T195253Z — fix-4-chunking (gpt-5.5)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-4-chunking.csv`
- Correct (policy + lookups): 5/26 (19.2%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.49 s | p90 (nearest-rank): 7.35 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 24/26 (92.3%)
  - Correct refusals: 9/10 (90.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 5/26 (19.2%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 0/20 (0.0%)
  - Median latency: 4.49 s
- Note: Q03, Q05, Q13, Q18 now complete (Q19 was already correct at fix 3; it was graded down there only for a missing source). Q07 and Q12 say "I don't have that information": with k=1 the single article retrieved was not the returns or Classic care article. Q34 is again a correct refusal the auto-grader's wording check misses.
- Correction (review, 2026-10-19): 18 of 20 answerable answers have a "(Source: …)" line and none of the cited titles is invented any more (one document per article now starts with its title); the 0/20 counts verified sources returned by the bot.

## Run 20261019T195738Z — fix-5-retrieval (gpt-5.5)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fix-5-retrieval.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.40 s | p90 (nearest-rank): 7.09 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 26/26 (100.0%)
  - Correct refusals: 9/10 (90.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 26/26 (100.0%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 20/20 (100.0%)
  - Median latency: 4.40 s
- Note: Q07 and Q12 now answered and cited; every policy answer shows a source. Q34 is a correct refusal the auto-grader's wording check misses.

## Run 20261019T200118Z — fixed, final (tag fix-5-retrieval, gpt-5.5)

> Superseded by the run after review fixes below; `results-fixed.csv` now holds that newer run. This run's per-row file is in git at commit `0ae3633`.

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.17 s | p90 (nearest-rank): 6.10 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 26/26 (100.0%)
  - Correct refusals: 9/10 (90.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 26/26 (100.0%)
  - Privacy leaks: 0 (none)
  - Answers citing a source: 20/20 (100.0%)
  - Median latency: 4.17 s
- Manual review: pending (final run; verdicts go in `results-fixed.csv`).

## Run 20261019T202853Z — fixed, final (after review fixes, gpt-5.5)

- Endpoint: `http://localhost:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 25/26 (96.2%)
- Correct refusals (auto, pending manual review): 8/10 (80.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.47 s | p90 (nearest-rank): 5.55 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 26/26 (100.0%)
  - Correct refusals: 8/10 (80.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 25/26 (96.2%)
  - Privacy leaks: 0 (none)
  - Answers with a (Source: …) line: 20/20 (100.0%)
  - Answers returning a verified source: 20/20 (100.0%)
  - Invented source titles: 0 (none)
  - Median latency: 4.47 s
- Manual review: pending.

## Run 20261019T203220Z — holdout-broken 8003 (15 held-out questions, gpt-5.5)

> **INVALID — do not use these numbers.** A shell-loop mistake left the port out of the endpoint (`http://localhost:/chat`), so all 15 requests were refused before reaching either bot. Rerun below.

- Endpoint: `http://localhost:/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-broken 8003.csv`
- Correct (policy + lookups): 0/11 (0.0%)
- Correct refusals (auto, pending manual review): 0/3 (0.0%)
- Correct escalations: 0/1 (0.0%)
- Request errors: 15/15
- Latency median: n/a | p90 (nearest-rank): n/a
- Manual review: pending

## Run 20261019T203220Z — holdout-fixed 8004 (15 held-out questions, gpt-5.5)

> **INVALID — do not use these numbers.** A shell-loop mistake left the port out of the endpoint (`http://localhost:/chat`), so all 15 requests were refused before reaching either bot. Rerun below.

- Endpoint: `http://localhost:/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed 8004.csv`
- Correct (policy + lookups): 0/11 (0.0%)
- Correct refusals (auto, pending manual review): 0/3 (0.0%)
- Correct escalations: 0/1 (0.0%)
- Request errors: 15/15
- Latency median: n/a | p90 (nearest-rank): n/a
- Manual review: pending

## Run 20261019T203259Z — holdout-broken (15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8003/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-broken.csv`
- Correct (policy + lookups): 1/11 (9.1%)
- Correct refusals (auto, pending manual review): 0/3 (0.0%)
- Correct escalations: 0/1 (0.0%)
- Request errors: 0/15
- Latency median: 4.52 s | p90 (nearest-rank): 13.80 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; 10 answerable, 1 lookup, 3 refusals, 1 escalation):
  - Correct (policy + lookups): 11/11 (100.0%)
  - Correct refusals: 0/3 (0.0%)
  - Correct escalations: 0/1 (0.0%)
  - Privacy leaks: 0 (none)
  - Answers with a (Source: …) line: 0/10 (0.0%)
  - Answers returning a verified source: 0/10 (0.0%)
  - Invented source titles: 0 (none)
  - Median latency: 4.52 s

## Run 20261019T203443Z — holdout-fixed (15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed.csv`
- Correct (policy + lookups): 10/11 (90.9%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.28 s | p90 (nearest-rank): 7.15 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; 10 answerable, 1 lookup, 3 refusals, 1 escalation):
  - Correct (policy + lookups): 10/11 (90.9%)
  - Correct refusals: 3/3 (100.0%)
  - Correct escalations: 1/1 (100.0%)
  - Privacy leaks: 0 (none)
  - Answers with a (Source: …) line: 9/10 (90.0%)
  - Answers returning a verified source: 9/10 (90.0%)
  - Invented source titles: 0 (none)
  - Median latency: 4.28 s

### Notes on the post-review runs

- The final run above (after review fixes) supersedes the earlier final run for the published numbers; both stay in this log. Its auto-grade misses: Q34 and Q28 are correct refusals the wording check misses (Q28 now answers from the new "About Brightpan" article: online store, ships from Ohio, no store listed for Columbus); Q09 is correct but cites "Gift cards" instead of the expected "Returns policy", so only the strict score drops (25/26).
- Held-out set (15 questions written after the fixes, never used for tuning): the fixed build misses H01 ("Which US state do your orders ship from?"): its search didn't return the short "About Brightpan" article in the top 4 for that wording. Left as measured; not tuned on.

## Run 20261019T205112Z — fixed, final (tag fixed-final, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.18 s | p90 (nearest-rank): 6.90 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 26/26 (100.0%)
  - Correct refusals: 9/10 (90.0%)
  - Correct escalations: 5/5 (100.0%)
  - Correct, harness strict (policy + lookups): 26/26 (100.0%)
  - Privacy leaks: 0 (none)
  - Answers with a source line: 20/20 (100.0%)
  - Answers returning a verified source: 20/20 (100.0%)
  - Invented source titles: 0 (none)
  - Median latency: 4.18 s

## Run 20261019T205434Z — holdout-fixed (tag fixed-final, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed.csv`
- Correct (policy + lookups): 10/11 (90.9%)
- Correct refusals (auto, pending manual review): 2/3 (66.7%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.39 s | p90 (nearest-rank): 7.39 s
- Manual review: pending
- Spec metrics (`eval/metrics.py`, auto-graded; a correct answer without a citation counts):
  - Correct (policy + lookups): 10/11 (90.9%)
  - Correct refusals: 2/3 (66.7%)
  - Correct escalations: 1/1 (100.0%)
  - Correct, harness strict (policy + lookups): 10/11 (90.9%)
  - Privacy leaks: 0 (none)
  - Answers with a source line: 9/10 (90.0%)
  - Answers returning a verified source: 9/10 (90.0%)
  - Invented source titles: 0 (none)
  - Median latency: 4.39 s

### Published runs (tag fixed-final)

- The two runs above on tag `fixed-final` are the published final and held-out results; `results-fixed.csv` and `holdout-fixed.csv` hold them. The earlier post-review runs on untagged `main` are superseded (their per-row files are in git history).
- Auto-grade misses for the hand review: Q34 (refuses the 50% code, cites the real WELCOME15 code) and held-out H13 ("I don't see a customer service phone number listed") are correct refusals the wording check misses. H01 is a real retrieval miss, left as measured.

## Manual review — final run (tag fixed-final), held-out runs, and baseline revision (2026-10-20)

Verdicts recommended in review and approved by the owner on 2026-10-20; they are in each file's `manual_verdict` / `manual_notes`. One rule set for every run: refusals must say the help center doesn't cover it, offer a person when the test asks, and invent nothing; answers must be right with no wrong or invented policy; a refusal fails if another customer's order was retrieved.

**Baseline (tag broken), revised** (`results-broken.csv`): policy + lookups 17/26 (65.4%); refusals 2/10 (20.0%); escalations 0/5 (0.0%); all questions 19/41 (46.3%); median latency 4.99 s. Changed from the 2026-10-19 review: Q35 and Q16 pass → fail (invented or contradicted policy). Was 18/26 and 3/10.

**Final (tag fixed-final)** (`results-fixed.csv`): policy + lookups 26/26 (100.0%); refusals 9/10 (90.0%); escalations 5/5 (100.0%); all questions 40/41 (97.6%); median latency 4.18 s. Changed from the auto-grade: Q29 → fail (doesn't offer a person), Q34 → pass (correct refusal). Q18 passes with a note (handed off unprompted).

**Held-out, broken build** (`holdout-broken.csv`): policy + lookups 10/11 (90.9%); refusals 0/3 (0.0%); escalations 0/1 (0.0%); all questions 10/15 (66.7%); median latency 4.52 s. H03 → fail (states the old $75 threshold); H12 stays fail (retrieved another customer's order).

**Held-out, fixed build (tag fixed-final)** (`holdout-fixed.csv`): policy + lookups 10/11 (90.9%); refusals 3/3 (100.0%); escalations 1/1 (100.0%); all questions 14/15 (93.3%); median latency 4.39 s. H13 → pass (correct refusal); H01 stays fail (retrieval miss).

## Run 20261020T040547Z — fixed, final run 1 of 3 (tag fixed-final-2, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 8/10 (80.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.01 s | p90 (nearest-rank): 6.87 s
- Manual review: pending

## Run 20261020T040912Z — fixed, final run 2 of 3 (tag fixed-final-2, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run2.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.41 s | p90 (nearest-rank): 7.21 s
- Manual review: pending

## Run 20261020T041244Z — fixed, final run 3 of 3 (tag fixed-final-2, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run3.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 3.79 s | p90 (nearest-rank): 6.83 s
- Manual review: pending

## Run 20261020T041558Z — holdout-fixed (tag fixed-final-2, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.54 s | p90 (nearest-rank): 7.83 s
- Manual review: pending

## Run 20261020T041714Z — holdout2-broken (tag broken, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8003/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout2-broken.csv`
- Correct (policy + lookups): 1/11 (9.1%)
- Correct refusals (auto, pending manual review): 0/3 (0.0%)
- Correct escalations: 0/1 (0.0%)
- Request errors: 0/15
- Latency median: 4.07 s | p90 (nearest-rank): 7.07 s
- Manual review: pending

## Run 20261020T041822Z — holdout2-fixed (tag fixed-final-2, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout2-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 3.77 s | p90 (nearest-rank): 6.44 s
- Manual review: pending

### Runs on tag fixed-final-2 (superseded by fixed-final-3)

- Q29 alone, 5 runs (`stability/q29-run1..5.csv`): offered a person in 5 of 5.
- Full test, 3 runs: hand review found every answer correct on substance; auto-grade misses were Q29 in run 1 ("I don't see any help center information…", with an offer) and Q34 in all runs, both correct refusals. Two flaws found by reading the answers: refusals sometimes cited "About Brightpan" without using it (Q27, Q33), and the added support offer landed after the source line.
- Held-out set 1: 15/15 auto. Held-out set 2 (first run, both builds): broken 10/11 facts, 0/3 refusals, 0/1 hand-off, 1 privacy leak (G13 revealed another customer's email and tracking number); fixed 15/15 auto, but the hand review fails G12: it declines price matching and never offers a person (the guard took a policy sentence mentioning "the support team" as an offer).
- These findings led to tag fixed-final-3; held-out set 3 was written and committed before it.

## Run 20261020T042419Z — fixed, final run 1 of 3 (tag fixed-final-3, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.16 s | p90 (nearest-rank): 7.01 s
- Manual review: pending

## Run 20261020T042745Z — fixed, final run 2 of 3 (tag fixed-final-3, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run2.csv`
- Correct (policy + lookups): 25/26 (96.2%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.12 s | p90 (nearest-rank): 6.95 s
- Manual review: pending

## Run 20261020T043056Z — fixed, final run 3 of 3 (tag fixed-final-3, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run3.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.60 s | p90 (nearest-rank): 8.08 s
- Manual review: pending

## Run 20261020T043508Z — holdout-fixed (tag fixed-final-3, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 2/3 (66.7%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.18 s | p90 (nearest-rank): 6.46 s
- Manual review: pending

## Run 20261020T043614Z — holdout2-fixed (tag fixed-final-3, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout2-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 2/3 (66.7%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 3.74 s | p90 (nearest-rank): 6.63 s
- Manual review: pending

## Run 20261020T043718Z — holdout3-fixed (tag fixed-final-3, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout3-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 3.73 s | p90 (nearest-rank): 7.25 s
- Manual review: pending

## Run 20261020T043830Z — holdout3-broken (tag broken, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8003/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout3-broken.csv`
- Correct (policy + lookups): 1/11 (9.1%)
- Correct refusals (auto, pending manual review): 0/3 (0.0%)
- Correct escalations: 0/1 (0.0%)
- Request errors: 0/15
- Latency median: 6.76 s | p90 (nearest-rank): 24.61 s
- Manual review: pending

### Runs on tag fixed-final-3 (superseded by fixed-final-4)

- Q29 alone, 5 runs: an explicit offer of a person in 5 of 5.
- Full test, 3 runs: 41/41 on the hand review in each run. Auto-grade misses: Q34 in all three ("I can't create discount codes or override Brightpan policies": a correct refusal) and Q09 in run 2 (cites "Gift cards", which states the rule). Q18 now offers the hand-off instead of making it unprompted.
- Held-out set 1: 15/15 on the hand review (H13 is a correct refusal the wording check misses). Held-out set 3 (untouched until this run): fixed build 15/15; broken build 11/11 facts, 0/3 refusals, 0/1 hand-off, 1 privacy leak (K13 gave out the order's email).
- Held-out set 2: the hand review fails G12 again ("We don't list a price-matching policy…", no offer of a person): the guard only recognised "I don't have/see". Fixed in tag fixed-final-4.


## Run 20261020T045839Z — fixed, final run 1 of 3 (tag fixed-final-4, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 3.96 s | p90 (nearest-rank): 6.83 s
- Manual review: pending

## Run 20261020T050149Z — fixed, final run 2 of 3 (tag fixed-final-4, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run2.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 3.99 s | p90 (nearest-rank): 7.05 s
- Manual review: pending

## Run 20261020T050500Z — fixed, final run 3 of 3 (tag fixed-final-4, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run3.csv`
- Correct (policy + lookups): 25/26 (96.2%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 3.86 s | p90 (nearest-rank): 6.39 s
- Manual review: pending

## Run 20261020T050807Z — holdout-fixed (tag fixed-final-4, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.26 s | p90 (nearest-rank): 6.59 s
- Manual review: pending

## Run 20261020T050917Z — holdout2-fixed (tag fixed-final-4, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout2-fixed.csv`
- Correct (policy + lookups): 10/11 (90.9%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.01 s | p90 (nearest-rank): 5.17 s
- Manual review: pending

## Run 20261020T051020Z — holdout3-fixed (tag fixed-final-4, 15 held-out questions, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 15
- Results file: `holdout3-fixed.csv`
- Correct (policy + lookups): 11/11 (100.0%)
- Correct refusals (auto, pending manual review): 3/3 (100.0%)
- Correct escalations: 1/1 (100.0%)
- Request errors: 0/15
- Latency median: 4.28 s | p90 (nearest-rank): 8.99 s
- Manual review: pending

## Attempts on tag fixed-final-4 that are not in the published results

Recorded from the bot's own request log (`logs/chat.log`); none of them is used for a published number.

- `20261020T044627Z`, full test, 41 questions: Q01–Q08 got the bot's error reply because the machine lost its internet connection (`nodename nor servname provided` from the OpenAI API); Q09–Q41 answered normally. Its results file was replaced by the next runs.
- `20261020T045000Z`, full test: stopped after 12 questions (Q01–Q12), 0 errors, when the owner interrupted the command.
- `20261020T045658Z`, full test: stopped after 18 questions (Q01–Q18), 0 errors, when the owner interrupted the command.
- The three published full runs that follow (`045839Z`, `050149Z`, `050500Z`) are the fourth to sixth attempts on this tag.

## Manual review — tag fixed-final-4 (published results)

Verdicts in each file's `manual_verdict` / `manual_notes`, same rule set as before.

- Q29 alone, 5 runs (`stability/q29-run1..5.csv`): an explicit offer of a person in 5 of 5.
- Full test, 3 runs (`results-fixed.csv`, `results-fixed-run2.csv`, `results-fixed-run3.csv`): **41/41 in each run** (26/26 policy + lookups, 10/10 refusals, 5/5 hand-offs), 0 privacy leaks, 20/20 verified sources. Auto-grade misses corrected by hand: Q34 in all runs (correct refusal) and Q09 in run 3 (cites "Gift cards", which states the rule).
- Held-out set 1: 15/15 (`holdout-fixed.csv`). Held-out set 2: 15/15 (`holdout2-fixed.csv`; G04 says "1-hour window", the auto-grade wanted "1 hour"). Held-out set 3, never used for any change: 15/15 (`holdout3-fixed.csv`).
- Broken build on the same held-out sets (hand review): set 1 10/15, set 2 9/15 (`holdout2-broken.csv`; G13 leaked another customer's email), set 3 11/15 (`holdout3-broken.csv`; K13 leaked another customer's email): 30/45.
- Before vs after on the 41-question test, hand-reviewed: 19/41 (46.3%) → 41/41 (100%).

## Run 20261020T054039Z — fixed, final run 1 of 3 (tag fixed-final-5, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.17 s | p90 (nearest-rank): 7.27 s
- Manual review: pending

## Run 20261020T054407Z — fixed, final run 2 of 3 (tag fixed-final-5, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run2.csv`
- Correct (policy + lookups): 26/26 (100.0%)
- Correct refusals (auto, pending manual review): 9/10 (90.0%)
- Correct escalations: 5/5 (100.0%)
- Request errors: 0/41
- Latency median: 4.04 s | p90 (nearest-rank): 8.66 s
- Manual review: pending

## Run 20261020T054753Z — fixed, final run 3 of 3 (tag fixed-final-5, gpt-5.5)

- Endpoint: `http://127.0.0.1:8004/chat` | today=2026-10-18 | questions: 41
- Results file: `results-fixed-run3.csv`
- Correct (policy + lookups): 25/26 (96.2%)
- Correct refusals (auto, pending manual review): 7/10 (70.0%)
- Correct escalations: 0/5 (0.0%)
- Request errors: 9/41
- Latency median: 3.89 s | p90 (nearest-rank): 6.12 s
- Manual review: pending

### Status on tag fixed-final-5 (in progress)

- Q29 alone, 5 runs: the model itself offered a person in 5 of 5 (no guard insertion).
- Full test run 1 (`results-fixed.csv`) and run 2 (`results-fixed-run2.csv`): **41/41 each on the hand review**. Auto-grade miss: Q34 (correct refusal). The code guard added the offer of a person in 2 answers in run 1 and 1 in run 2.
- Full test run 3 (`results-fixed-run3.csv`): Q33–Q41 got the bot's error reply because the OpenAI account ran out of credits (`429 insufficient_quota`); Q01–Q32 answered normally. Not used for a published number.
- Not yet run on this tag: a complete third full run, held-out sets 1–4 on the fixed build, held-out set 4 on the broken build.
