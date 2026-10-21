"""Run the held-out questions (eval/holdout.csv) through the unchanged harness.

Each set of 15 held-out questions was written and committed before its first run. Sets 1 to 3 each exposed
a problem that was then fixed, so they are no longer independent; set 4 (holdout-4.csv) was never used for
any change. Same flags as run_eval.py:
  python3 eval/run_holdout.py --endpoint http://localhost:8004/chat --label holdout-fixed --out eval/holdout-fixed.csv --log
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_eval  # noqa: E402

# --set holdout-2 picks eval/holdout-2.csv (default: eval/holdout.csv).
name = "holdout"
if "--set" in sys.argv:
    i = sys.argv.index("--set")
    name = sys.argv[i + 1]
    del sys.argv[i:i + 2]
run_eval.TESTSET = Path(__file__).resolve().parent / f"{name}.csv"

if __name__ == "__main__":
    run_eval.main()
