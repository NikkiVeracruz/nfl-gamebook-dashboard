#!/usr/bin/env python3
"""Offline tests: NFL feed freshness and final-but-missing gamebook alerts."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import production_health as health
import nfl_final_gamebooks as reports

NOW = datetime(2026, 11, 23, 3, 30, tzinfo=timezone.utc)
DAY = "2026-11-22"
KICKOFF = "2026-11-22T21:25:00Z"


def scheduled_event(final=True, away="Raiders", home="Broncos", kickoff=KICKOFF):
    return {
        "id": "example-espn-event",
        "date": kickoff,
        "status": {"type": {"completed": final, "state": "post" if final else "in"}},
        "competitions": [{"competitors": [
            {"homeAway": "away", "team": {"name": away, "displayName": "Las Vegas " + away}},
            {"homeAway": "home", "team": {"name": home, "displayName": "Denver " + home}}
        ]}],
    }


def game(pdf_url=None):
    entry = {
        "slug": "raiders-at-broncos-2026-reg-11",
        "date": DAY,
        "label": "Raiders @ Broncos",
    }
    if pdf_url is not None:
        entry["pdf_url"] = pdf_url
    return entry


class FreshnessTests(unittest.TestCase):
    def test_nfl_59_minutes_is_acceptable(self):
        stamp = (NOW - timedelta(minutes=59)).isoformat()
        self.assertEqual(health.validate_freshness("NFL", stamp, NOW)[1], 60)

    def test_nfl_61_minutes_triggers_failure(self):
        stamp = (NOW - timedelta(minutes=61)).isoformat()
        with self.assertRaisesRegex(ValueError, "limit 60"):
            health.validate_freshness("NFL", stamp, NOW)

    def test_other_leagues_keep_three_hour_limit(self):
        stamp = (NOW - timedelta(minutes=120)).isoformat()
        self.assertEqual(health.validate_freshness("NBA", stamp, NOW)[1], 180)

    def test_future_and_unzoned_timestamps_rejected(self):
        with self.assertRaises(ValueError):
            health.validate_freshness("NFL", (NOW + timedelta(minutes=11)).isoformat(), NOW)
        with self.assertRaises(ValueError):
            health.validate_freshness("NFL", "2026-11-23T03:00:00", NOW)


class MissingGamebookTests(unittest.TestCase):
    def run_audit(self, entry, events=None, now=NOW):
        sample = {"games": [entry]}
        response = [scheduled_event()] if events is None else events
        return reports.audit(sample, get_scoreboard=lambda day: response, now=now)

    def test_final_overdue_without_pdf_triggers_alert(self):
        alerts, notes = self.run_audit(game())
        self.assertEqual(len(alerts), 1)
        self.assertIn("raiders-at-broncos", alerts[0])
        self.assertIn("since kickoff", alerts[0])

    def test_final_with_official_pdf_does_not_trigger(self):
        alerts, notes = self.run_audit(game("https://static.www.nfl.com/image/upload/example.pdf"))
        self.assertEqual(alerts, [])

    def test_not_final_never_alerts(self):
        alerts, notes = self.run_audit(game(), [scheduled_event(final=False)])
        self.assertEqual(alerts, [])

    def test_five_hour_grace_period(self):
        alerts, notes = self.run_audit(
            game(), now=datetime(2026, 11, 23, 1, 24, tzinfo=timezone.utc)
        )
        self.assertEqual(alerts, [])

    def test_wrong_matchup_not_assigned(self):
        alerts, notes = self.run_audit(game(), [scheduled_event(away="Chargers")])
        self.assertEqual(alerts, [])
        self.assertTrue(any("matched 0" in text for text in notes))

    def test_ambiguous_match_is_inconclusive(self):
        events = [scheduled_event(), scheduled_event()]
        alerts, notes = self.run_audit(game(), events)
        self.assertEqual(alerts, [])
        self.assertTrue(any("matched 2" in text for text in notes))

    def test_scoreboard_outage_is_inconclusive_not_false_alert(self):
        def unavailable(day):
            raise OSError("offline")
        alerts, notes = reports.audit({"games": [game()]}, get_scoreboard=unavailable, now=NOW)
        self.assertEqual(alerts, [])
        self.assertTrue(any("unavailable" in text for text in notes))

    def test_espn_date_is_formatted_without_hyphens(self):
        with patch.object(reports, "fetch_json", return_value={"events": []}) as fetch:
            self.assertEqual(reports.scoreboard("2026-11-22"), [])
        self.assertIn("dates=20261122", fetch.call_args.args[0])

    def test_offseason_skips_gamebook_check(self):
        def forbidden(day):
            raise AssertionError("offseason must not query ESPN")
        alerts, notes = reports.audit(
            {"offseason": True, "games": []}, get_scoreboard=forbidden, now=NOW
        )
        self.assertEqual(alerts, [])
        self.assertIn("Offseason", notes[0])

    def test_untrusted_non_official_url_does_not_mask_gap(self):
        alerts, notes = self.run_audit(game("https://untrusted.example/report.pdf"))
        self.assertEqual(len(alerts), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
