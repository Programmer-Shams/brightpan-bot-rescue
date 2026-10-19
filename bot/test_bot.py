"""Unit tests for the bot's tools (no model calls). Run: .venv/bin/python -m unittest bot/test_bot.py"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
