"""Offline tests for hourly read-only audit. Never call public APIs."""
import unittest
from unittest.mock import patch

from missing_game_audit import audit, main, independent_games


class CurrentScheduleAuditTests(unittest.TestCase):
    @patch("missing_game_audit.independent_games")
    def test_detects_missing_nba_id_even_if_games_list_is_nonempty(self, schedule):
        schedule.return_value = {"1", "2"}
        warnings = audit("NBA", {"games": [
            {"id": "1", "date": "2026-11-22", "status": "Final"}]})
        self.assertTrue(any("MISSING GAME" in item for item in warnings))

    @patch("missing_game_audit.independent_games")
    def test_detects_wrong_nfl_matchup_even_with_matching_count(self, schedule):
        schedule.return_value = {("2026-11-22", "bears", "packers")}
        warnings = audit("NFL", {"games": [
            {"slug": "bears-at-lions-2026-reg-11", "date": "2026-11-22"}]})
        self.assertTrue(any("missing NFL matchups" in item for item in warnings))
        self.assertTrue(any("unmatched NFL matchups" in item for item in warnings))

    def test_offseason_has_no_current_game_requirement(self):
        self.assertEqual(audit("WNBA", {"offseason": True, "games": []}), [])

    @patch("missing_game_audit.fetch_json")
    def test_source_unavailable_exits_nonzero(self, fetch):
        fetch.side_effect = OSError("upstream unavailable")
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

    @patch("missing_game_audit.fetch_json")
    def test_mlb_scoreboard_asks_for_all_star_and_exhibition(self, fetch):
        fetch.return_value = {"dates": []}
        self.assertEqual(independent_games("MLB", "2026-07-14"), set())
        self.assertIn("A%2CE", fetch.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
