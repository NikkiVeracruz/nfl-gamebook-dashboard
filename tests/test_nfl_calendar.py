"""Offline guardrails for schedule-aware NFL gamebook polling."""
import json
import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from nfl_calendar import (
    ET, compile_crons, fetch_game_days, include_saved_dates,
    missing_pdf_games, schedule_windows, should_poll, start_of_season,
    update_workflow_text,
)


class NFLCalendarTests(unittest.TestCase):
    def setUp(self):
        self.mon = date(2026, 11, 23)
        self.archive = {"games": []}
        self.day_state = {"game_days": ["2026-11-22", "2026-11-23", "2026-11-25"]}

    def local(self, day, hour, minute=0):
        return datetime(day.year, day.month, day.day, hour, minute, tzinfo=ET)

    def missing(self, day="2026-11-22"):
        return {"slug": "vikings-at-49ers-2026-reg-11",
                "date": day,
                "game_url": "https://www.nfl.com/games/vikings-at-49ers-2026-reg-11"}

    def test_game_day_and_unusual_wednesday(self):
        self.assertTrue(should_poll(self.local(self.mon, 13), self.day_state, self.archive))
        self.assertTrue(should_poll(self.local(date(2026, 11, 25), 14), self.day_state, self.archive))

    def test_overnight_cutoff_exactly_three_am(self):
        tue = date(2026, 11, 24)
        self.assertTrue(should_poll(self.local(tue, 2, 59), self.day_state, self.archive))
        self.assertFalse(should_poll(self.local(tue, 3), self.day_state, self.archive))

    def test_pending_pdf_overrides_cutoff(self):
        self.archive["games"].append(self.missing())
        tue = date(2026, 11, 24)
        self.assertTrue(should_poll(self.local(tue, 3, 1), self.day_state, self.archive))
        self.assertTrue(should_poll(self.local(tue, 23), self.day_state, self.archive))
        self.archive["games"][0]["pdf_url"] = "https://static.www.nfl.com/game.pdf"
        self.assertFalse(should_poll(self.local(tue, 3, 1), self.day_state, self.archive))

    def test_manually_requested_scan_can_run_on_idle_day(self):
        tue = date(2026, 11, 24)
        self.assertTrue(should_poll(self.local(tue, 13), self.day_state, self.archive, manual=True))

    def test_old_season_missing_does_not_force_daily_poll(self):
        self.archive["games"].append(self.missing("2025-11-23"))
        self.assertEqual(missing_pdf_games(self.archive, date(2026, 11, 24)), [])

    def test_past_current_season_pdf_is_pending(self):
        self.archive["games"].append(self.missing())
        self.assertEqual(len(missing_pdf_games(self.archive, date(2026, 11, 24))), 1)

    def test_full_game_dates_and_next_morning(self):
        days = {date(2026, 11, 23), date(2026, 11, 25)}
        full, overnight = schedule_windows(self.mon, days, [])
        self.assertEqual(full, days)
        self.assertEqual(overnight, {date(2026, 11, 24), date(2026, 11, 26)})
        crons = "\n".join(compile_crons(full, overnight))
        self.assertIn("*/5 * 23,25 11 *", crons)
        self.assertIn("*/5 0-2 24,26 11 *", crons)
        self.assertIn('timezone: "America/New_York"', crons)

    def test_missing_pdf_extends_at_least_three_full_days(self):
        full, overnight = schedule_windows(self.mon, set(), [self.missing()])
        for delta in range(4):
            self.assertIn(self.mon + timedelta(days=delta), full)

    def test_next_year_cron_groups_do_not_leak_into_this_year(self):
        d = date(2026, 12, 31)
        full, early = schedule_windows(d, {d}, [])
        text = "\n".join(compile_crons(full, early))
        self.assertIn("31 12 *", text)
        self.assertIn("1 1 *", text)
        self.assertNotIn("*/5 * 1 1 *", text)

    def test_generated_schedule_keeps_main_workflow_body(self):
        source = ("name: sample\non:\n  workflow_dispatch:\n"
                  "  # BEGIN NFL CALENDAR-MANAGED SCHEDULE\n"
                  "  schedule:\n    - cron: \"*/5 * * * *\"\n"
                  "  # END NFL CALENDAR-MANAGED SCHEDULE\n"
                  "jobs:\n  update:\n    runs-on: ubuntu-latest\n")
        full, early = schedule_windows(self.mon, {self.mon}, [])
        changed = update_workflow_text(source, full, early)
        self.assertIn("jobs:\n  update:", changed)
        self.assertNotIn('cron: "*/5 * * * *"', changed)
        self.assertEqual(changed, update_workflow_text(changed, full, early))

    def test_offseason_without_missing_games_removes_schedule(self):
        source = ("on:\n  workflow_dispatch:\n"
                  "  # BEGIN NFL CALENDAR-MANAGED SCHEDULE\n"
                  "  schedule:\n    - cron: \"*/5 * * * *\"\n"
                  "  # END NFL CALENDAR-MANAGED SCHEDULE\n")
        changed = update_workflow_text(source, set(), set())
        self.assertNotIn("\n  schedule:\n", changed)
        self.assertIn("workflow_dispatch", changed)

    def test_refuses_to_rewrite_unknown_workflow(self):
        with self.assertRaises(ValueError):
            update_workflow_text("on:\n  schedule: []", {self.mon}, set())

    def test_saved_future_wednesday_survives_empty_api_schedule(self):
        saved = {"games": [{"date": "2026-11-25", "slug": "x"}]}
        dates = include_saved_dates(set(), self.mon, saved, {"games": []})
        self.assertEqual(dates, {date(2026, 11, 25)})

    def test_fetch_normalizes_utc_to_eastern(self):
        class FakeResponse:
            def raise_for_status(self): pass
            def json(self):
                return {"events": [{"date": "2026-11-26T04:20:00Z"}]}
        class FakeSession:
            def get(self, *a, **k): return FakeResponse()
        days = fetch_game_days(FakeSession(), date(2026, 11, 25), horizon=0)
        self.assertEqual(days, {date(2026, 11, 25)})

    def test_missing_scoreboard_fails_closed(self):
        class BadResponse:
            def raise_for_status(self): pass
            def json(self): return {"no_events": True}
        class FakeSession:
            def get(self, *a, **k): return BadResponse()
        with self.assertRaises(ValueError):
            fetch_game_days(FakeSession(), self.mon, horizon=0)

    def test_dst_spring_forward_keeps_local_three_am_cutoff(self):
        spring = date(2027, 3, 14)
        state = {"game_days": ["2027-03-13"]}
        self.assertTrue(should_poll(self.local(spring, 1, 59), state, self.archive))
        self.assertFalse(should_poll(self.local(spring, 3), state, self.archive))


if __name__ == "__main__":
    unittest.main()
