"""Run the held-out questions (eval/holdout.csv) through the unchanged harness.

The 15 held-out questions were written after the fixes and were never used to tune the bot or its prompt.
They show which gains carry over to new questions: on them, policy accuracy did not improve (both builds get
the facts about equally right); refusals, hand-offs, privacy and verified sources did. Same flags as run_eval.py:
  python3 eval/run_holdout.py --endpoint http://localhost:8004/chat --label holdout-fixed --out eval/holdout-fixed.csv --log
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402

run_eval.TESTSET = Path(__file__).resolve().parent / "holdout.csv"

if __name__ == "__main__":
    run_eval.main()
