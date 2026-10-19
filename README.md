# brightpan-bot-rescue

Before/after rescue of a small Python + LangChain support chatbot for Brightpan Kitchen Supply, a fictional demo store.

**Staged faults on a demo bot.** The scenario: the bot was built quickly by someone else, the store then changed two policies (free shipping threshold $75 → $99, newsletter code WELCOME10 → WELCOME15) and the bot started giving wrong answers. The faults were planted deliberately for this demo; there is no real client.

## Setup

```bash
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env          # add OPENAI_API_KEY
.venv/bin/python bot/ingest.py                 # build the local Chroma index
.venv/bin/uvicorn bot.app:app --port 8003      # POST http://localhost:8003/chat
```

## Run the test

The eval harness is copied from Demo 1 (`brightpan-support-agent`) with only its file paths changed.

```bash
python3 eval/run_eval.py --endpoint http://localhost:8003/chat --label broken --out eval/results-broken.csv --log
python3 eval/metrics.py eval/results-broken.csv
```
