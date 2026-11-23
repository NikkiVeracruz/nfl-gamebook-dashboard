#!/usr/bin/env python3
"""Offline tests for exact game-ID comparisons and honest NFL fallback."""
import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import missing_game_audit as audit

class GameIDAuditTests(unittest.TestCase):
    def check(self, league, published, independent):
        data = {"games": [{"date": "2026-11-22", "id": x} for x in published]}
        with patch.object(audit, "independent_games", return_value=set(independent)):
            return audit.audit(league, data)

    def test_equal_counts_but_wrong_id_detected(self):
        findings = self.check("NBA", ["1", "3"], ["1", "2"])
        self.assertTrue(any("MISSING GAME IDS" in f and "2" in f for f in findings))
        self.assertTrue(any("UNMATCHED PUBLISHED" in f and "3" in f for f in findings))

    def test_matching_ids_pass(self):
        self.assertEqual(self.check("NHL", ["1", "2"], ["2", "1"]), [])

    def test_duplicate_id_detected(self):
        self.assertTrue(any("duplicate" in f for f in self.check("MLB", ["1", "1"], ["1"])))

    def test_missing_id_detected(self):
        data = {"games": [{"date": "2026-11-22", "label": "Away @ Home"}]}
        with patch.object(audit, "independent_games", return_value={"1"}):
            self.assertTrue(any("lack an ID" in f for f in audit.audit("WNBA", data)))

    def test_mlb_uses_official_statsapi_ids(self):
        official = {"dates": [{"games": [{"gamePk": 780001}, {"gamePk": 780002}]}]}
        with patch.object(audit, "fetch_json", return_value=official) as fetch:
            ids = audit.independent_games("MLB", "2026-06-17")
        self.assertEqual(ids, {"780001", "780002"})
        url = fetch.call_args.args[0]
        self.assertIn("statsapi.mlb.com/api/v1/schedule", url)
        self.assertIn("date=2026-06-17", url)
        self.assertIn("gameTypes=S%2CR%2CF%2CD%2CL%2CW", url)

    def test_mlb_missing_dates_response_is_inconclusive(self):
        with patch.object(audit, "fetch_json", return_value={}):
            with self.assertRaises(ValueError):
                audit.independent_games("MLB", "2026-06-17")

    def test_nfl_is_count_only(self):
        self.assertEqual(self.check("NFL", ["nfl-slug"], ["espn-id"]), [])

    def test_offseason_skips(self):
        with patch.object(audit, "independent_games", side_effect=AssertionError("should not fetch")):
            self.assertEqual(audit.audit("MLB", {"offseason": True, "games": []}), [])

if __name__ == "__main__":
    unittest.main()
