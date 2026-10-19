# brightpan-bot-rescue

Before/after rescue of a small Python + LangChain support chatbot for Brightpan Kitchen Supply, a fictional demo store: an audit, five ranked findings, one fix per commit, and the same 41-question test after every fix.

**Staged faults on a demo bot.** The scenario: the bot was built quickly by someone else, the store then changed two policies (free shipping threshold $75 → $99, newsletter code WELCOME10 → WELCOME15) and the bot started giving wrong answers. The five faults were planted deliberately for this demo; there is no real client.

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
| `fixed-final` | After an independent code review: hand-offs ask for a reply email and attach it to the same case; short conversation memory (fixed build only; the broken build keeps none); the help-center intro indexed as "About Brightpan"; capped agent runs; sturdier citation parsing and index rebuilds. The published final and held-out runs use this tag. |

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

The eval harness is copied from Demo 1 (`brightpan-support-agent`) with only its file paths changed. It sends each of the 41 questions in `eval/testset-v2.csv` as a fresh session and grades the reply.

```bash
python3 eval/run_eval.py --endpoint http://127.0.0.1:8004/chat --label rerun --out eval/results-rerun.csv
python3 eval/metrics.py eval/results-rerun.csv     # adds privacy leaks, citations, invented source titles
```

Write reruns to a new file: `results-broken.csv` and `results-fixed.csv` hold the hand-reviewed verdicts. Auto-grades are a first pass; the `manual_verdict` column is the final verdict.

Citations are measured two ways: answers that show a "(Source: …)" line, and answers whose citation the bot matched to an article its search actually returned ("verified source"). Cited titles that aren't real article titles are counted as invented.

### Held-out questions

`eval/holdout.csv` has 15 questions written after the fixes and never used for tuning (paraphrases and help-center facts the main test doesn't ask about). They were committed before their first run. On them, policy accuracy did not improve: both builds get the facts about equally right. The gains that carry over are refusals, hand-offs, privacy and verified sources.

```bash
python3 eval/run_holdout.py --endpoint http://127.0.0.1:8004/chat --label holdout-rerun --out eval/holdout-rerun.csv
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
data/orders.json      the demo store's fictional orders
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
- Retrieval can still miss a short article: on the held-out set, "Which US state do your orders ship from?" did not retrieve the "About Brightpan" article (H01).
- Change detection hashes the help-center file before every answer. That is cheap for one file and one process; several processes would need a shared index and manifest.
- Model answers vary a little between runs, and the auto-grader checks wording, so it can miss a correct answer or pass a wrong one. Results in this repo are as measured; manual verdicts are final.
