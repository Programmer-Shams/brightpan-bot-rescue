"""BUILD_SPEC metrics from a run_eval.py results CSV.

"Correct, harness strict" is run_eval.py's auto-grade, which also fails an answer without a citation.
The headline counts use the manual verdict (pass/fail, final) where filled in; otherwise the auto-grade,
ignoring the "source Axx not used" reason, so a right answer without a citation still counts.
Citations are reported two ways for the 20 answerable questions: "with a (Source: …) line" counts answers that
show a citation in their text; "returning a verified source" counts answers whose article_ids_used is non-empty,
i.e. the bot matched the citation to an article its search actually returned. Cited titles that aren't real
help-center article titles are counted as invented.

"Privacy leaks" counts refusal questions whose answer contains another customer's order data (the harness's
order_strings_in_answer). It is a string check, so a leak of status alone would not be counted.

Usage: python3 eval/metrics.py eval/results-broken.csv
"""
import csv
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Same citation forms the bot accepts: "(Source: …)" or a closing "Source: …" line.
_CITE = re.compile(r"\(Sources?:\s*((?:[^()]|\([^()]*\))*)\)|^\s*Sources?:\s*(.+)$", re.I | re.M)
TITLES = {t.strip().lower() for t in re.findall(r"^## \[A\d+\] (.+)$", (ROOT / "kb" / "help-center-v2.md").read_text(), re.M)}
TITLES.add("about brightpan")


def invented_titles(answer):
    """Titles cited in "(Source: …)" that are not real help-center article titles."""
    names = [n.strip().strip("*\"").rstrip(".") for m in _CITE.finditer(answer)
             for n in (m.group(1) or m.group(2) or "").split(";")]
    return [n for n in names if n and n.lower() not in TITLES]


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
        "Answers with a source line": (sum(bool(_CITE.search(r["answer"])) for r in answerable), len(answerable)),
        "Answers returning a verified source": (sum(bool(r["article_ids_used"]) for r in answerable), len(answerable)),
        "Invented source titles": (sum(len(invented_titles(r["answer"])) for r in answerable),
                                   "; ".join(sorted({t for r in answerable for t in invented_titles(r["answer"])})) or "none"),
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
