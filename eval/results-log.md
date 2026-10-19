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

> Superseded by the run after review fixes below; `results-fixed.csv` now holds that newer run. This run's per-row file is in git at commit `98ded7a`.

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
