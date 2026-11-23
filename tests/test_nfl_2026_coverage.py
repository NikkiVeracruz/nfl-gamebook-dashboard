#!/usr/bin/env python3
"""Offline regression tests for 2026-only NFL coverage validation."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nfl_2026_coverage import (
    archive_identity, get_expected, verify_coverage,
)
from archive import ArchiveIntegrityError


NOW = datetime(2026, 11, 23, 4, 0, tzinfo=timezone.utc)


def game(pdf=True):
    x = {
        "slug": "jets-at-patriots-2026-reg-1",
        "date": "2026-09-13", "label": "Jets @ Patriots",
    }
    if pdf:
        x["pdf_url"] = "https://static.www.nfl.com/games/jets-patriots.pdf"
    return x


def match():
    return ("2026-09-13", "jets", "patriots")


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, data):
        self.data = data

    def get(self, url, params=None, timeout=None):
        return FakeResponse(self.data)


class Nfl2026CoverageTests(unittest.TestCase):
    def test_correct_slug_team_matching(self):
        self.assertEqual(archive_identity(game()), match())

    def test_complete_game_with_pdf_passes(self):
        stats = verify_coverage({"games": [game()]}, {match()}, NOW)
        self.assertFalse(stats["unarchived_games"])
        self.assertFalse(stats["older_games_without_pdf"])

    def test_independent_game_missing_from_archive_fails_audit(self):
        stats = verify_coverage({"games": []}, {match()}, NOW)
        self.assertEqual(stats["unarchived_games"], [match()])

    def test_old_game_without_pdf_is_detected(self):
        stats = verify_coverage({"games": [game(False)]}, {match()}, NOW)
        self.assertEqual(stats["older_games_without_pdf"], [match()])

    def test_2025_history_does_not_count_as_2026(self):
        previous = {
            "slug": "jets-at-patriots-2025-reg-1", "date": "2025-09-13",
            "label": "Jets @ Patriots",
        }
        stats = verify_coverage({"games": [previous]}, {match()}, NOW)
        self.assertEqual(stats["unarchived_games"], [match()])

    def test_nonofficial_pdf_rejected(self):
        record = game()
        record["pdf_url"] = "https://example.com/not-official.pdf"
        with self.assertRaisesRegex(ArchiveIntegrityError, "Invalid official"):
            verify_coverage({"games": [record]}, {match()}, NOW)

    def test_espn_scoreboard_checks_team_names_and_kickoff(self):
        response = {"events": [{
            "date": "2026-09-13T17:00:00Z",
            "competitions": [{"competitors": [
                {"homeAway": "away", "team": {"name": "Jets"}},
                {"homeAway": "home", "team": {"name": "Patriots"}},
            ]}],
        }]}
        from datetime import date
        found = get_expected(
            FakeSession(response), date(2026, 9, 13), NOW
        )
        self.assertEqual(found, {match()})

    def test_future_espn_games_not_required(self):
        response = {"events": [{
            "date": "2026-11-24T00:00:00Z",
            "competitions": [{"competitors": [
                {"homeAway": "away", "team": {"name": "Jets"}},
                {"homeAway": "home", "team": {"name": "Patriots"}},
            ]}],
        }]}
        from datetime import date
        found = get_expected(
            FakeSession(response), date(2026, 11, 23), NOW
        )
        self.assertEqual(found, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
