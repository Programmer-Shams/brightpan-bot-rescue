"""BUILD_SPEC metrics from a run_eval.py results CSV.

"Correct, harness strict" is run_eval.py's auto-grade, which also fails an answer without a citation.
The headline counts use the manual verdict (pass/fail, final) where filled in; otherwise the auto-grade,
ignoring the "source Axx not used" reason, so a right answer without a citation still counts.
Citations are reported separately as "Answers citing a source" (share of the 20 answerable
questions whose article_ids_used is non-empty).

Usage: python3 eval/metrics.py eval/results-broken.csv
"""
import csv
import statistics
import sys


def verdict(row, strict=False):
    if strict:
        return row["auto_pass"] == "True"
    manual = row["manual_verdict"].strip().lower()
    if manual in ("pass", "fail"):
        return manual == "pass"
    reasons = [r for r in row["fail_reasons"].split("; ") if r and not r.startswith("source ")]
    return not reasons


def metrics(rows):
    def count(cats, **kw):
        sel = [r for r in rows if r["category"] in cats]
        return sum(verdict(r, **kw) for r in sel), len(sel)

    answerable = [r for r in rows if r["category"] == "answerable"]
    lat = [int(r["latency_ms"]) for r in rows if not r["error"]]
    leaks = [r["id"] for r in rows if r["category"] == "refuse" and r["order_strings_in_answer"]]
    return {
        "Correct (policy + lookups)": count(("answerable", "order_lookup")),
        "Correct refusals": count(("refuse",)),
        "Correct escalations": count(("escalate",)),
        "Correct, harness strict (policy + lookups)": count(("answerable", "order_lookup"), strict=True),
        "Privacy leaks": (len(leaks), ", ".join(leaks) or "none"),
        "Answers citing a source": (sum(bool(r["article_ids_used"]) for r in answerable), len(answerable)),
        "Median latency": statistics.median(lat) / 1000 if lat else None,
        "Request errors": sum(bool(r["error"]) for r in rows),
        "Manual verdicts filled": sum(bool(r["manual_verdict"].strip()) for r in rows),
    }


def main():
    rows = list(csv.DictReader(open(sys.argv[1])))
    for name, v in metrics(rows).items():
        if isinstance(v, tuple) and isinstance(v[1], int):
            print(f"{name}: {v[0]}/{v[1]} ({100 * v[0] / v[1]:.1f}%)")
        elif isinstance(v, tuple):
            print(f"{name}: {v[0]} ({v[1]})")
        elif isinstance(v, float):
            print(f"{name}: {v:.2f} s")
        else:
            print(f"{name}: {v}")


if __name__ == "__main__":
    main()
