# brightpan-bot-rescue

Before/after rescue of a small Python + LangChain support chatbot for Brightpan Kitchen Supply, an online store: an audit, five ranked findings, one fix per commit, and the same 41-question test after every fix.

**Portfolio project with planted faults.** The scenario: the bot was built quickly by someone else, the store then changed two policies (free shipping threshold $75 → $99, newsletter code WELCOME10 → WELCOME15) and the bot started giving wrong answers. The five faults were planted deliberately for this portfolio project.

- Audit report: [docs/audit.md](docs/audit.md)
- Architecture, before and after: [docs/architecture.html](docs/architecture.html) ([PNG](docs/architecture.png))
- Scores after every fix: [eval/results-log.md](eval/results-log.md)

## What changed

| Tag | Fix |
| --- | --- |
| `broken` | The bot as handed over (faults F1–F5) |
| `fix-1-privacy` | Order lookup needs the order number and the matching email; customer-facing fields only; lockout after 5 failed attempts |
| `fix-2-stale-index` | Index the current help center; per-article hashes; re-index automatically when the file changes; help-center version on every answer |
| `fix-3-grounded-prompt` | Grounded instructions ([bot/system_prompt.md](bot/system_prompt.md)) and an `escalate_to_human` tool |
| `fix-4-chunking` | One index document per help-center article; only changed articles are re-indexed |
| `fix-5-retrieval` | Top 4 articles with ids and titles; answers cite "(Source: …)"; cited articles returned with the reply |
| `fixed-final` | After an independent code review: hand-offs ask for a reply email and attach it to the same case; short conversation memory (fixed build only; the broken build keeps none); the help-center intro indexed as "About Brightpan"; capped agent runs; sturdier citation parsing and index rebuilds. |
| `fixed-final-2` … `fixed-final-5` | A reply that says it doesn't have the information always offers a person (instruction plus a code check); the "About Brightpan" article comes with every search and the bot searches again before giving up, citing it only when used; no yes/no answers the help center doesn't support. **The published final and held-out runs use `fixed-final-5`.** |

## Setup

Needs Python 3.13 with [uv](https://docs.astral.sh/uv/), Node 22 and an OpenAI API key.

```bash
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env               # add OPENAI_API_KEY
scripts/serve_builds.sh            # broken build on :8003, fixed build on :8004
```

`serve_builds.sh` checks out tag `broken` in `.worktrees/broken` and builds its index from the old help center. The fixed build indexes `kb/help-center-v2.md` by itself on first start. Both answer `POST /chat` with `{"session_id", "message", "today"}`.

### Chat page (Next.js + shadcn/ui)

Asks the broken and the fixed build the same question side by side. Each answer shows what it was based on: sources, order check, hand-off, tools used, latency, help-center version.

```bash
cd web && npm install
cp .env.example .env.local         # bot URLs: broken on :8003, fixed on :8004
npm run dev                        # http://127.0.0.1:3300
```

## Run the test

The eval harness is copied from the support agent project (`brightpan-support-agent`) with only its file paths changed. It sends each of the 41 questions in `eval/testset-v2.csv` as a fresh session and grades the reply.

```bash
python3 eval/run_eval.py --endpoint http://127.0.0.1:8004/chat --label rerun --out eval/results-rerun.csv
python3 eval/metrics.py eval/results-rerun.csv     # adds privacy leaks, citations, invented source titles
```

Write reruns to a new file: `results-broken.csv` and `results-fixed.csv` hold the hand-reviewed verdicts. Auto-grades are a first pass; the `manual_verdict` column is the final verdict.

Citations are measured two ways: answers that show a "(Source: …)" line, and answers whose citation the bot matched to an article its search actually returned ("verified source"). Cited titles that aren't real article titles are counted as invented.

### Held-out questions

Four sets of 15 new questions (`eval/holdout.csv`, `holdout-2.csv`, `holdout-3.csv`, `holdout-4.csv`), each committed before its first run. Sets 1 to 3 each exposed something that was then fixed (the next set was written first), so set 4 is the only one never used for any change. Hand-reviewed results on set 4: broken 10/15, fixed 15/15 (all four sets: broken 38/60, fixed 60/60).

```bash
python3 eval/run_holdout.py --set holdout-4 --endpoint http://127.0.0.1:8004/chat --label holdout-rerun --out eval/holdout-rerun.csv
```

### Unit tests

No model or embedding calls, and no API key needed:

```bash
.venv/bin/python -m unittest bot/test_bot.py
python3 -m unittest eval/test_run_eval.py
```

## Layout

```
bot/app.py            FastAPI /chat, LangChain agent, tools (search, order lookup, hand-off)
bot/ingest.py         help-center index: one document per article, hashes, change detection
bot/system_prompt.md  grounded instructions
data/orders.json      the store's test orders
kb/                   help center as indexed by the broken bot (v1) and as it is now (v2)
eval/                 test set, harness, results per run, results log
web/                  chat page (Next.js 16, shadcn/ui)
docs/                 audit report, architecture diagram
```

## Known limits

- Orders come from a local JSON file and hand-offs go to `logs/handoffs.jsonl`, standing in for a store API and a helpdesk.
- Conversation memory (last 10 turns, 30 minutes), the order-lookup lockout and the chat page's rate limit live in memory in one process and reset on restart.
- Five wrong emails lock an order number for 15 minutes, so someone who knows an order number can briefly lock its owner out of chat lookups; the owner can still reach the support team.
- Hand-offs without an email are saved and the bot asks for one; until the customer gives it, the support team has only the chat session id to go on.
- Whether a reply "declines" is recognised from its wording, so the code check that adds an offer of a person can miss an unusual phrasing (the instruction to offer one still applies) and occasionally adds an offer to a normal answer. In the published runs it added the offer to 5 of 30 refusals on the main test and 6 of 60 held-out answers; the model wrote it everywhere else.
- Change detection hashes the help-center file before every answer. That is cheap for one file and one process; several processes would need a shared index and manifest.
- Model answers vary a little between runs, and the auto-grader checks wording, so it can miss a correct answer or pass a wrong one. Results in this repo are as measured; manual verdicts are final.
