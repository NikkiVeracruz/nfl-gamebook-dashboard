"""Offline regression tests: no network or archive mutations."""
import unittest
from datetime import date
from unittest.mock import patch

from archive_2026_schedule_audit import (
    AuditError, compare, espn_day, mlb_month, nfl_archive_key,
    nhl_week,
)


class HistoricalArchiveAuditTests(unittest.TestCase):
    def test_nfl_normalizes_matchup_from_slug(self):
        game = {"date": "2026-11-22", "slug": "giants-at-bears-2026-reg-11"}
        self.assertEqual(nfl_archive_key(game), ("2026-11-22", "giants", "bears"))
        report = compare("NFL", [game],
                         {"2026-11-22": {("2026-11-22", "giants", "bears")}},
                         date(2026, 11, 22))
        self.assertEqual(report["missing"], [])

    def test_absent_game_is_failure_candidate(self):
        report = compare("NBA", [
            {"id": "41", "date": "2026-02-16"}],
            {"2026-02-16": {"41", "42"}}, date(2026, 2, 16))
        self.assertEqual(report["missing"], [("2026-02-16", "42")])

    def test_wrong_date_is_distinct_from_missing(self):
        report = compare("WNBA", [{"id": "7", "date": "2026-07-25"}],
                         {"2026-07-26": {"7"}}, date(2026, 7, 26))
        self.assertEqual(report["missing"], [])
        self.assertEqual(report["date_mismatches"],
                         [("2026-07-26", "7", "2026-07-25")])

    def test_international_hockey_does_not_create_false_nhl_extra(self):
        games = [{"id": "2025090001", "date": "2026-02-01",
                  "competition": "international_hockey"}]
        report = compare("NHL", games, {}, date(2026, 11, 22))
        self.assertEqual(report["extra_for_review"], [])

    def test_unmatched_regular_games_are_reported_not_deleted(self):
        report = compare("NHL", [{"id": "2026020001", "date": "2026-10-11"}],
                         {}, date(2026, 11, 22))
        self.assertEqual(report["extra_for_review"], ["2026020001"])

    @patch("archive_2026_schedule_audit.fetch_json")
    def test_espn_missing_events_list_is_inconclusive_not_pass(self, fetch):
        fetch.return_value = {"message": "temporarily unavailable"}
        with self.assertRaises(AuditError):
            espn_day("NBA", date(2026, 11, 22))

    @patch("archive_2026_schedule_audit.fetch_json")
    def test_mlb_completeness_includes_special_game_types(self, fetch):
        fetch.return_value = {"dates": [{"date": "2026-07-14",
                                          "games": [{"gamePk": 12345}]}]}
        result = mlb_month(date(2026, 7, 1), date(2026, 7, 31))
        self.assertEqual(result["2026-07-14"], {"12345"})
        url = fetch.call_args.args[0]
        self.assertIn("gameTypes=", url)
        self.assertIn("A%2CE", url)

    @patch("archive_2026_schedule_audit.fetch_json")
    def test_nhl_week_parses_official_gameweek(self, fetch):
        fetch.return_value = {"gameWeek": [
            {"date": "2026-10-01", "games": [{"id": 2026020001}]},
            {"date": "2026-10-02", "games": []}
        ]}
        result = nhl_week(date(2026, 10, 1))
        self.assertEqual(result["2026-10-01"], {"2026020001"})
        self.assertEqual(result["2026-10-02"], set())


if __name__ == "__main__":
    unittest.main()
