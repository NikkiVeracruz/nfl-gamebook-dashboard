"""The NFL calendar's intentional idle time must not create false health alerts."""
import unittest
from datetime import datetime, timedelta, timezone

import monitor
import nfl_update_watchdog
import production_health


class NFLAdaptiveHealthTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 24, 10, tzinfo=timezone.utc)

    def test_heartbeat_throttles_no_op_checks(self):
        state = {"notified": {}}
        self.assertTrue(monitor.record_heartbeat(state, now=self.now))
        old = state["last_checked_at"]
        self.assertFalse(monitor.record_heartbeat(state, now=self.now + timedelta(minutes=39)))
        self.assertEqual(old, state["last_checked_at"])
        self.assertTrue(monitor.record_heartbeat(state, now=self.now + timedelta(minutes=41)))
        self.assertNotEqual(old, state["last_checked_at"])

    def test_active_freshness_uses_heartbeat_not_unchanged_feed(self):
        feed = {"games": [], "updated_at": (self.now - timedelta(hours=10)).isoformat()}
        actual, reason = nfl_update_watchdog.decide(
            feed, self.now, last_checked_at=(self.now - timedelta(minutes=30)).isoformat()
        )
        self.assertFalse(actual)
        self.assertIn("healthy", reason)

    def test_missing_heartbeat_triggers_backup_on_active_day(self):
        feed = {"games": [], "updated_at": (self.now - timedelta(hours=4)).isoformat()}
        actual, _ = nfl_update_watchdog.decide(
            feed, self.now, last_checked_at=(self.now - timedelta(minutes=120)).isoformat()
        )
        self.assertTrue(actual)

    def test_idle_day_accepts_old_feed_but_checks_timestamp_validity(self):
        stamp = (self.now - timedelta(days=5)).isoformat()
        age, limit = production_health.validate_freshness(
            "NFL", stamp, now=self.now, skip_age=True
        )
        self.assertGreater(age, limit)
        with self.assertRaises(ValueError):
            production_health.validate_freshness("NFL", stamp, now=self.now)
        with self.assertRaises(ValueError):
            production_health.validate_freshness("NFL", "not-a-timestamp", now=self.now, skip_age=True)

    def test_other_league_freshness_remains_strict(self):
        stamp = (self.now - timedelta(hours=4)).isoformat()
        with self.assertRaises(ValueError):
            production_health.validate_freshness("NBA", stamp, now=self.now)


if __name__ == "__main__":
    unittest.main()
