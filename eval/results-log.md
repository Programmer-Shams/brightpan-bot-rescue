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
