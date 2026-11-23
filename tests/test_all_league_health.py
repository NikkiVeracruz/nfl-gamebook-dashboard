"""League-specific activity statuses must not create false stale warnings."""
import unittest
from datetime import datetime, timedelta, timezone

from production_health import polling_expected, validate_freshness


class MultiLeagueHealthTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 24, 10, tzinfo=timezone.utc)

    def test_idle_month_exempts_age_but_validates_timestamp(self):
        calendar = {"game_days": []}
        self.assertFalse(polling_expected(calendar, {"pending_recent": 0}, self.now))
        old = (self.now - timedelta(days=15)).isoformat()
        age, limit = validate_freshness("WNBA", old, self.now, skip_age=True)
        self.assertGreater(age, limit)
        with self.assertRaises(ValueError):
            validate_freshness("WNBA", "invalid", self.now, skip_age=True)

    def test_recent_missing_report_continues_after_three_am(self):
        self.assertTrue(polling_expected({"game_days": []}, {"pending_recent": 1}, self.now))

    def test_following_day_until_three_am_eastern(self):
        calendar = {"game_days": ["2026-11-23"]}
        before = datetime(2026, 11, 24, 7, 59, tzinfo=timezone.utc)
        after = datetime(2026, 11, 24, 8, tzinfo=timezone.utc)
        self.assertTrue(polling_expected(calendar, {}, before))
        self.assertFalse(polling_expected(calendar, {}, after))

    def test_heartbeat_staleness_with_active_limit(self):
        stamp = (self.now - timedelta(minutes=80)).isoformat()
        age, limit = validate_freshness(
            "NHL", stamp, self.now, limit_override=110)
        self.assertLess(age, limit)
        with self.assertRaises(ValueError):
            validate_freshness(
                "NHL", (self.now-timedelta(minutes=130)).isoformat(),
                self.now, limit_override=110)

    def test_calendar_must_have_a_real_game_days_list(self):
        with self.assertRaises(ValueError):
            polling_expected({}, {}, self.now)


if __name__ == "__main__":
    unittest.main()
