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
import monitor
import backfill


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


    def test_discover_preseason_week_two_and_hall_of_fame(self):
        from unittest.mock import patch

        def schedule(_session, url):
            if url.endswith("/by-week/preseason-week-2"):
                return ('<a href="/games/seahawks-at-titans-2026-pre-2">'
                        'Seahawks 16, Titans 19, Sunday, August 23</a>'
                        '<a href="/games/packers-at-lions-2026-reg-12">'
                        'Sunday, August 23</a>')
            if url.endswith("/by-week/hall-of-fame-game"):
                return ('<a href="/games/panthers-at-cardinals-2026-pre-0">'
                        'Panthers 33, Cardinals 30, Thursday, August 6</a>')
            return ""

        with patch.object(monitor, "get", side_effect=schedule):
            found = monitor.discover(None, 2026, "2026-08-01", "2026-08-29")
        self.assertEqual(found["seahawks-at-titans-2026-pre-2"]["date"],
                         "2026-08-23")
        self.assertEqual(found["panthers-at-cardinals-2026-pre-0"]["date"],
                         "2026-08-06")
        self.assertNotIn("packers-at-lions-2026-reg-12", found)

    def test_preseason_schedule_pages_skipped_in_november(self):
        from unittest.mock import patch
        observed = []

        def schedule(_session, url):
            observed.append(url)
            return ""

        with patch.object(monitor, "get", side_effect=schedule):
            monitor.discover(None, 2026, "2026-11-01", "2026-11-29")
        self.assertFalse(any("/by-week/preseason-week-" in x for x in observed))


    def test_already_archived_sunday_game_counts_when_nfl_com_temporarily_misses_it(self):
        from datetime import date
        sunday = date(2026, 11, 22)
        discovered = {
            f"new-{i}": {
                "slug": f"team{i}-at-home{i}-2026-reg-11",
                "date": sunday.isoformat(),
            }
            for i in range(10)
        }
        previous = {
            **discovered,
            "saved-eleventh": {
                "slug": "vikings-at-49ers-2026-reg-11",
                "date": sunday.isoformat(),
            },
        }
        backfill.validate_discovery(
            None, sunday, date(2026, 11, 23), discovered,
            get_expected=lambda _session, _day: 11,
            previous=previous,
        )

    def test_genuinely_missing_sunday_game_still_blocks_cursor(self):
        from datetime import date
        sunday = date(2026, 11, 22)
        discovered = {
            f"new-{i}": {
                "slug": f"team{i}-at-home{i}-2026-reg-11",
                "date": sunday.isoformat(),
            }
            for i in range(10)
        }
        with self.assertRaisesRegex(ArchiveIntegrityError, "incomplete"):
            backfill.validate_discovery(
                None, sunday, date(2026, 11, 23), discovered,
                get_expected=lambda _session, _day: 11,
                previous=discovered,
            )

    def test_wrong_season_or_duplicate_slug_cannot_fake_completeness(self):
        from datetime import date
        sunday = date(2026, 11, 22)
        discovered = {
            "one": {"slug": "vikings-at-49ers-2026-reg-11", "date": sunday.isoformat()}
        }
        previous = {
            "same": discovered["one"],
            "wrong-year": {"slug": "vikings-at-49ers-2025-reg-11", "date": sunday.isoformat()},
        }
        with self.assertRaisesRegex(ArchiveIntegrityError, "incomplete"):
            backfill.validate_discovery(
                None, sunday, date(2026, 11, 23), discovered,
                get_expected=lambda _session, _day: 2,
                previous=previous,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
