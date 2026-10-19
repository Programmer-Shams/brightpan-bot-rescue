"""Run the held-out questions (eval/holdout.csv) through the unchanged harness.

The 15 held-out questions were written after the fixes and were never used to tune the bot or its prompt;
they check that the fixes generalise beyond the 41 graded questions. Same flags as run_eval.py, e.g.:
  python3 eval/run_holdout.py --endpoint http://localhost:8004/chat --label holdout-fixed --out eval/holdout-fixed.csv --log
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402

run_eval.TESTSET = Path(__file__).resolve().parent / "holdout.csv"

if __name__ == "__main__":
    run_eval.main()
