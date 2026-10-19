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
- Note: Q03, Q05, Q13, Q18, Q19 now complete. Q07 and Q12 say "I don't have that information": with k=1 the single article retrieved was not the returns or Classic care article. Q34 is again a correct refusal the auto-grader's wording check misses.
