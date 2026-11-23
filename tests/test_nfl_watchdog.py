#!/usr/bin/env python3
"""Offline regression tests for an NFL backup update watchdog."""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nfl_update_watchdog as watchdog

NOW = datetime(2026, 11, 23, 4, 0, tzinfo=timezone.utc)

def sample(minutes, offseason=False):
    return {
        "updated_at": (NOW - timedelta(minutes=minutes)).isoformat(),
        "offseason": offseason,
        "games": [{"slug": "raiders-at-broncos-2026-reg-11", "date": "2026-11-22"}],
    }

class WatchdogTests(unittest.TestCase):
    def test_fresh_update_does_not_trigger(self):
        self.assertFalse(watchdog.decide(sample(30), NOW)[0])

    def test_just_below_threshold_does_not_trigger(self):
        self.assertFalse(watchdog.decide(sample(60), NOW)[0])

    def test_missed_updates_trigger_backup(self):
        self.assertTrue(watchdog.decide(sample(61), NOW)[0])

    def test_offseason_does_not_trigger_even_if_old(self):
        self.assertFalse(watchdog.decide(sample(240, offseason=True), NOW)[0])

    def test_future_data_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "future"):
            watchdog.decide(sample(-15), NOW)

    def test_missing_and_unparseable_timestamps_fail_closed(self):
        with self.assertRaises(ValueError):
            watchdog.decide({"games": []}, NOW)
        with self.assertRaises(ValueError):
            watchdog.decide({"games": [], "updated_at": "not-a-date"}, NOW)

    def test_malformed_game_feed_fails_closed(self):
        with self.assertRaises(ValueError):
            watchdog.decide({"games": "not an array", "updated_at": NOW.isoformat()}, NOW)

    def test_observation_never_dispatches_by_itself(self):
        with patch.object(watchdog, "read_feed", return_value=sample(75)), \
             patch.object(watchdog, "decide", return_value=(True, "overdue")), \
             patch.dict("os.environ", {}, clear=True):
            self.assertEqual(watchdog.main(), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
