"""Unit tests for the bot's tools and index (no model or embedding calls, no API key needed).
Run: .venv/bin/python -m unittest bot/test_bot.py"""
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
    RETRIEVED = {"A01": "Shipping options and costs (United States)", "A05": "Returns policy", "A06": "Refunds",
                 "A10": "Caring for Everyday nonstick pans", "A11": "Caring for Classic and Pro stainless steel"}

    def cite(self, answer):
        return app.cited_articles(answer, self.RETRIEVED)

    def test_title_with_parentheses(self):
        self.assertEqual(self.cite("It's $6.95. (Source: Shipping options and costs (United States))"), ["A01"])

    def test_two_sources(self):
        self.assertEqual(self.cite("(Sources: Returns policy; Refunds.)"), ["A05", "A06"])
        self.assertEqual(self.cite("(Sources: Returns policy, Refunds)"), ["A05", "A06"])
        self.assertEqual(self.cite("(Sources: Returns policy and Refunds)"), ["A05", "A06"])

    def test_title_containing_and(self):
        self.assertEqual(self.cite("(Source: Caring for Classic and Pro stainless steel)"), ["A11"])

    def test_markdown_quotes_and_bare_line(self):
        self.assertEqual(self.cite("(Source: **Returns policy**)"), ["A05"])
        self.assertEqual(self.cite('(Source: "Returns policy")'), ["A05"])
        self.assertEqual(self.cite("30 days.\n\nSource: Returns policy"), ["A05"])

    def test_short_or_ambiguous_prefix_rejected(self):
        self.assertEqual(self.cite("(Source: Refu)"), [])
        self.assertEqual(self.cite("(Source: Caring for)"), [])
        self.assertEqual(self.cite("(Source: Shipping options and costs)"), ["A01"])

    def test_only_retrieved_articles_count(self):
        self.assertEqual(self.cite("(Source: Warranty)"), [])
        self.assertEqual(self.cite("No citation here."), [])


class EscalateToHuman(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = mock.patch.object(app, "HANDOFFS", Path(self.tmp.name) / "handoffs.jsonl")
        self.patch.start()
        app.session_handoffs.clear()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def escalate(self, session, **args):
        args = {"summary": "Kettle arrived with a cracked lid", "reason": "damaged_or_wrong_item", **args}
        return json.loads(app.make_escalate_tool(session).invoke(args))

    def saved(self):
        return [json.loads(line) for line in app.HANDOFFS.read_text().splitlines()]

    def test_saves_handoff_with_contact(self):
        r = self.escalate("s1", email="tom.walsh@example.com", order_number="#1012")
        self.assertEqual((r["result"], r["contact"]), ("saved", "email"))
        self.assertEqual(self.saved()[0]["order_number"], "1012")
        self.assertEqual(self.saved()[0]["session_id"], "s1")

    def test_missing_email_is_saved_and_flagged(self):
        r = self.escalate("s1")
        self.assertEqual((r["result"], r["contact"]), ("saved", "missing"))
        self.assertIn("Ask the customer for the email", r["message"])

    def test_email_added_later_in_same_session_only(self):
        first = self.escalate("s1")
        added = self.escalate("s1", handoff_id=first["handoff_id"], email="tom.walsh@example.com")
        self.assertEqual((added["handoff_id"], added["contact"]), (first["handoff_id"], "email"))
        other = self.escalate("s2", handoff_id=first["handoff_id"], email="attacker@example.com")
        self.assertEqual(other["result"], "unknown_handoff")
        self.assertEqual(len(self.saved()), 2)


class History(unittest.TestCase):
    def setUp(self):
        app._history.clear()

    def test_keeps_last_turns_per_session(self):
        for i in range(app.HISTORY_TURNS + 3):
            app.save_turn("s1", f"q{i}", f"a{i}")
        h = app.get_history("s1")
        self.assertEqual(len(h), 2 * app.HISTORY_TURNS)
        self.assertEqual(h[-1], {"role": "assistant", "content": f"a{app.HISTORY_TURNS + 2}"})
        self.assertEqual(app.get_history("s2"), [])

    def test_expired_sessions_are_dropped(self):
        app.save_turn("s1", "q", "a")
        with mock.patch.object(app.time, "time", return_value=app.time.time() + app.HISTORY_TTL + 1):
            self.assertEqual(app.get_history("s1"), [])


class StoreToday(unittest.TestCase):
    def test_valid_date_kept(self):
        self.assertEqual(app.store_today("2026-10-18"), "2026-10-18")

    def test_invalid_dates_fall_back_to_store_date(self):
        for bad in (None, "", "2026-99-99", "yesterday", "2026-10-18T00:00"):
            self.assertRegex(app.store_today(bad), r"^\d{4}-\d{2}-\d{2}$")
            self.assertNotEqual(app.store_today(bad), "2026-99-99")

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

    def test_intro_becomes_about_article(self):
        ingest.KB_FILE.write_text("# Help\n\nWe ship from Ohio.\n\n" + self.KB.split("\n\n", 1)[1])
        ingest.ensure_index(self.store)
        self.assertEqual(self.store.docs["A00"].metadata["title"], "About Brightpan")
        self.assertIn("We ship from Ohio.", self.store.docs["A00"].page_content)
        self.assertNotIn("# Help", self.store.docs["A00"].page_content)

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

    def test_broken_file_keeps_last_good_index(self):
        v1 = ingest.ensure_index(self.store)
        for bad in ("# Help\n\nNo articles any more.\n", self.KB + "\n## [A02] Returns again\n\nDup.\n"):
            ingest.KB_FILE.write_text(bad)
            with mock.patch("sys.stderr"):
                self.assertEqual(ingest.ensure_index(self.store), v1)
            self.assertEqual(sorted(self.store.docs), ["A01", "A02"])

    def test_broken_file_without_index_raises(self):
        ingest.KB_FILE.write_text("# Help\n\nNothing here.\n")
        with self.assertRaises(ValueError):
            ingest.ensure_index(self.store)


if __name__ == "__main__":
    unittest.main()
