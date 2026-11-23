"""Offline tests: user decisions cannot silently become implementation."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "project"))
from render_register import SOURCE, render, validate

class ProjectRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_complete_register_is_parseable_and_unique(self):
        rows = validate(self.data)
        self.assertGreaterEqual(len(rows), 40)
        self.assertEqual(len(rows), len({r["id"] for r in rows}))

    def test_declined_features_are_never_active(self):
        for row in self.data["features"]:
            with self.subTest(id=row["id"]):
                if row["decision"] == "declined":
                    # A declined feature can have been removed, paused, or never
                    # started. Never allow it to be presented as implemented.
                    self.assertIn(row["state"], ("removed", "paused", "not_started"))
                    if row["state"] == "not_started":
                        self.assertEqual(row["evidence"], [])
                if row["decision"] == "not_decided":
                    self.assertIn(row["state"], ("proposed", "not_started"))
                if row["decision"] == "deferred":
                    self.assertEqual(row["state"], "deferred")
                if row["area"] == "known_risk":
                    self.assertEqual(row["state"], "open")

    def test_mandatory_leagues_and_explicitly_declined_items(self):
        self.assertEqual(self.data["project"]["supported_leagues"],
                         ["NFL", "NBA", "WNBA", "NHL", "MLB"])
        by_id = {r["id"]: r for r in self.data["features"]}
        for ident in ("DEC-001", "DEC-002", "DEC-003", "DEC-004", "DEC-005"):
            self.assertEqual(by_id[ident]["decision"], "declined")
        for ident in ("IDEA-001", "IDEA-003", "IDEA-004", "IDEA-005",
                      "IDEA-006", "IDEA-007", "IDEA-009", "IDEA-011"):
            self.assertEqual(by_id[ident]["decision"], "declined")
            self.assertEqual(by_id[ident]["state"], "not_started")
            self.assertIn("Do not implement or proactively suggest", by_id[ident]["notes"])
        self.assertIn("exclude player-statistics", by_id["PRJ-001"]["notes"])
        self.assertEqual(by_id["PRJ-017"]["state"], "implemented")

    def test_renderer_includes_key_user_decisions_and_evidence(self):
        result = render(self.data)
        for term in ("Forward-only", "NCAA", "player-level statistics",
                     "archive", "not_decided", "backup/pre-forward-only-2026-11-23"):
            self.assertIn(term.lower(), result.lower())

    def test_duplicate_feature_rejected(self):
        d = copy.deepcopy(self.data)
        d["features"].append(copy.deepcopy(d["features"][0]))
        with self.assertRaises(ValueError):
            validate(d)

    def test_unknown_approval_state_rejected(self):
        d = copy.deepcopy(self.data)
        d["features"][0]["decision"] = "approved_by_bot"
        with self.assertRaises(ValueError):
            validate(d)

if __name__ == "__main__":
    unittest.main()
