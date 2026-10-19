"""Unit tests for the bot's tools (no model calls). Run: .venv/bin/python -m unittest bot/test_bot.py"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app  # noqa: E402
import ingest  # noqa: E402


def lookup(number, email):
    return json.loads(app.lookup_order.invoke({"order_number": number, "email": email}))


class LookupOrder(unittest.TestCase):
    def setUp(self):
        app.failed_lookups.clear()

    def test_match_returns_customer_fields_only(self):
        r = lookup("1002", "maria.lopez@example.com")
        self.assertEqual(r["result"], "match")
        self.assertEqual(r["order"]["tracking_number"], "1ZBP0000000001002")
        for private in ("email", "name", "state"):
            self.assertNotIn(private, r["order"])
        self.assertNotIn("sku", r["order"]["items"][0])

    def test_email_is_case_and_space_insensitive(self):
        self.assertEqual(lookup("#1002", "  Maria.Lopez@Example.com ")["result"], "match")

    def test_wrong_email_reveals_nothing(self):
        wrong = app.lookup_order.invoke({"order_number": "1002", "email": "wrong.person@example.com"})
        unknown = app.lookup_order.invoke({"order_number": "2050", "email": "sam.reed@example.com"})
        self.assertEqual(wrong, unknown)
        self.assertNotIn("1ZBP", wrong)

    def test_lockout_after_repeated_failures(self):
        for _ in range(app.MAX_FAILED_LOOKUPS):
            self.assertEqual(lookup("1002", "guess@example.com")["result"], "no_match")
        self.assertEqual(lookup("1002", "maria.lopez@example.com")["result"], "locked")

    def test_success_resets_failures(self):
        for _ in range(app.MAX_FAILED_LOOKUPS - 1):
            lookup("1002", "guess@example.com")
        self.assertEqual(lookup("1002", "maria.lopez@example.com")["result"], "match")
        self.assertNotIn("1002", app.failed_lookups)


class CitedArticles(unittest.TestCase):
    RETRIEVED = {"A01": "Shipping options and costs (United States)", "A05": "Returns policy", "A06": "Refunds"}

    def test_title_with_parentheses(self):
        answer = "It's $6.95. (Source: Shipping options and costs (United States))"
        self.assertEqual(app.cited_articles(answer, self.RETRIEVED), ["A01"])

    def test_two_sources_and_prefix(self):
        answer = "Within 30 days, refunded in 5 to 7 days. (Sources: Returns policy; Refunds.)"
        self.assertEqual(app.cited_articles(answer, self.RETRIEVED), ["A05", "A06"])
        self.assertEqual(app.cited_articles("(Source: Shipping options and costs)", self.RETRIEVED), ["A01"])

    def test_only_retrieved_articles_count(self):
        self.assertEqual(app.cited_articles("(Source: Warranty)", self.RETRIEVED), [])
        self.assertEqual(app.cited_articles("No citation here.", self.RETRIEVED), [])


class EscalateToHuman(unittest.TestCase):
    def test_saves_handoff_and_returns_id(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(app, "HANDOFFS", Path(tmp) / "handoffs.jsonl"):
            r = json.loads(app.escalate_to_human.invoke(
                {"summary": "Kettle arrived with a cracked lid", "reason": "damaged_or_wrong_item",
                 "email": "tom.walsh@example.com", "order_number": "#1012"}))
            saved = json.loads(app.HANDOFFS.read_text().splitlines()[0])
        self.assertEqual(r["result"], "saved")
        self.assertEqual(saved["handoff_id"], r["handoff_id"])
        self.assertEqual(saved["order_number"], "1012")

    def test_prompt_has_date_placeholder(self):
        self.assertIn("{{TODAY}}", app.SYSTEM_PROMPT)


class FakeStore:
    def __init__(self):
        self.docs, self.resets, self.added = {}, 0, []

    def reset_collection(self):
        self.docs, self.resets = {}, self.resets + 1

    def delete(self, ids):
        for i in ids:
            self.docs.pop(i, None)

    def add_documents(self, docs, ids):
        self.added += ids
        self.docs.update(zip(ids, docs))


class EnsureIndex(unittest.TestCase):
    KB = "# Help\n\n## [A01] Shipping\n\nFree over $75.\n\n## [A02] Returns\n\n30 days.\n"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        self.patches = [mock.patch.object(ingest, "KB_FILE", tmp / "kb.md"),
                        mock.patch.object(ingest, "MANIFEST", tmp / "manifest.json")]
        for p in self.patches:
            p.start()
        ingest.KB_FILE.write_text(self.KB)
        self.store = FakeStore()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_builds_once_then_reuses(self):
        v1 = ingest.ensure_index(self.store)
        self.assertEqual(ingest.ensure_index(self.store), v1)
        self.assertEqual(self.store.resets, 1)

    def test_one_document_per_article(self):
        ingest.ensure_index(self.store)
        self.assertEqual(sorted(self.store.docs), ["A01", "A02"])
        self.assertEqual(self.store.docs["A01"].metadata["title"], "Shipping")
        self.assertIn("Free over $75.", self.store.docs["A01"].page_content)

    def test_file_change_reindexes_only_changed_articles(self):
        v1 = ingest.ensure_index(self.store)
        self.store.added.clear()
        ingest.KB_FILE.write_text(self.KB.replace("$75", "$99"))
        v2 = ingest.ensure_index(self.store)
        self.assertNotEqual(v1, v2)
        self.assertEqual(self.store.resets, 1)
        self.assertEqual(self.store.added, ["A01"])
        self.assertEqual(ingest.read_manifest()["changed_articles"], ["A01"])
        self.assertIn("$99", self.store.docs["A01"].page_content)

    def test_removed_article_is_deleted(self):
        ingest.ensure_index(self.store)
        ingest.KB_FILE.write_text(self.KB.split("## [A02]")[0])
        ingest.ensure_index(self.store)
        self.assertEqual(sorted(self.store.docs), ["A01"])


if __name__ == "__main__":
    unittest.main()
