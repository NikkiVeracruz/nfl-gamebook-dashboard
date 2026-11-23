#!/usr/bin/env python3
"""Offline tests: NFL historical discovery must not falsely declare completion."""
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backfill
import monitor
from archive import ArchiveIntegrityError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        return FakeResponse(self.payload)


def event(day):
    return {"date": day + "T18:00:00Z"}


class NflBackfillCompletenessTests(unittest.TestCase):
    def test_espn_counts_only_games_on_eastern_date(self):
        response = {"events": [
            event("2025-11-02"),
            {"date": "2025-11-03T02:30:00Z"},  # Sunday evening ET
            event("2025-11-03"),
        ]}
        result = backfill.independent_sunday_games(
            FakeSession(response), date(2025, 11, 2)
        )
        self.assertEqual(result, 2)

    def test_invalid_independent_schedule_fails_closed(self):
        with self.assertRaises(ArchiveIntegrityError):
            backfill.independent_sunday_games(
                FakeSession({"events": None}), date(2025, 11, 2)
            )

    def test_missing_sunday_games_blocks_cursor(self):
        with self.assertRaisesRegex(ArchiveIntegrityError, "incomplete"):
            backfill.validate_discovery(
                None, date(2025, 11, 1), date(2025, 11, 29),
                {"a": {"date": "2025-11-02"}},
                get_expected=lambda _session, _day: 2,
            )

    def test_complete_sundays_pass(self):
        dates = ["2025-11-02", "2025-11-09", "2025-11-16", "2025-11-23"]
        found = {str(i): {"date": day} for i, day in enumerate(dates)}
        backfill.validate_discovery(
            None, date(2025, 11, 1), date(2025, 11, 29),
            found, get_expected=lambda _session, _day: 1,
        )

    def test_offseason_with_no_independent_games_passes(self):
        backfill.validate_discovery(
            None, date(2026, 4, 1), date(2026, 4, 29),
            {}, get_expected=lambda _session, _day: 0,
        )

    def test_real_writer_leaves_existing_data_untouched_when_discovery_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = {"games": [{
                "slug": "previous-game", "date": "2025-10-26",
                "label": "Existing", "pdf_url": "https://www.nfl.com/old.pdf",
            }]}
            archive = root / "archive.json"
            progress = root / "archive-progress.json"
            archive.write_text(json.dumps(old))
            progress.write_text(json.dumps({"next_date": "2025-11-02"}))
            prior_archive = archive.read_bytes()
            prior_progress = progress.read_bytes()
            espn = FakeSession({"events": [event("2025-11-02")]})
            with (
                patch.object(backfill, "ARCHIVE", archive),
                patch.object(backfill, "PROGRESS", progress),
                patch.object(backfill.requests, "Session", return_value=espn),
                patch.object(backfill, "discover", return_value={}),
            ):
                with self.assertRaisesRegex(ArchiveIntegrityError, "incomplete"):
                    backfill.main()
            self.assertEqual(archive.read_bytes(), prior_archive)
            self.assertEqual(progress.read_bytes(), prior_progress)


    def test_discovery_covers_final_weeks_in_long_historical_window(self):
        # A four-week backfill starting Nov 2 includes games on Nov 23.
        # The previous fixed two-week lookahead did not fetch week 12.
        queried = []

        def fake_get(_session, url):
            queried.append(url)
            if url.endswith("/by-week/week-12"):
                return (
                    '<a href="/games/cowboys-at-giants-2025-reg-12">'
                    'Sunday, November 23</a>'
                )
            return ""

        with patch.object(monitor, "get", side_effect=fake_get):
            found = monitor.discover(
                None, 2025, "2025-11-02", "2025-11-30"
            )
        self.assertIn("cowboys-at-giants-2025-reg-12", found)
        self.assertEqual(found["cowboys-at-giants-2025-reg-12"]["date"],
                         "2025-11-23")
        self.assertTrue(any(url.endswith("/by-week/week-12") for url in queried))

    def test_discovery_does_not_need_future_weeks_for_short_live_window(self):
        queried = []

        def fake_get(_session, url):
            queried.append(url)
            return ""

        with patch.object(monitor, "get", side_effect=fake_get):
            monitor.discover(None, 2025, "2025-11-02", "2025-11-09")
        self.assertFalse(any(url.endswith("/by-week/week-14") for url in queried))


    def test_2026_game_link_never_overwrites_a_2025_history_record(self):
        # NFL schedule markup may associate a 2025 date with a neighboring
        # 2026 game link. Both scanning paths must reject the wrong season.
        observed = []

        def fake_get(_session, url):
            observed.append(url)
            if url.endswith("/REG11") or url.endswith("/by-week/week-12"):
                return (
                    '<a href="/games/bengals-at-commanders-2026-reg-11">'
                    'Sunday, November 23, 2025</a>'
                    '<a href="/games/patriots-at-jets-2025-reg-12">'
                    'Sunday, November 23, 2025</a>'
                )
            return ""

        with patch.object(monitor, "get", side_effect=fake_get):
            found = monitor.discover(None, 2025, "2025-11-02", "2025-11-30")
        self.assertIn("patriots-at-jets-2025-reg-12", found)
        self.assertNotIn("bengals-at-commanders-2026-reg-11", found)
        self.assertTrue(any(url.endswith("/REG11") for url in observed))
        self.assertTrue(any(url.endswith("/by-week/week-12") for url in observed))



if __name__ == "__main__":
    unittest.main(verbosity=2)
