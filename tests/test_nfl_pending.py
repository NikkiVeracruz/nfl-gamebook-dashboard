import unittest
from datetime import date,datetime,timezone,timedelta
from nfl_pending import *
from nfl_calendar import should_poll
from unittest.mock import patch
import monitor
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import nfl_update_watchdog
class PendingTests(unittest.TestCase):
    def setUp(self):
        self.game=dict(SEED)
        self.event={"date":"2026-11-26T01:00:00Z","season":{"year":2026,"type":2},
          "status":{"type":{"state":"post","name":"STATUS_FINAL","completed":True}},
          "competitions":[{"competitors":[{"homeAway":"away","score":"13","team":{"name":"Packers","displayName":"Green Bay Packers"}},{"homeAway":"home","score":"26","team":{"name":"Rams","displayName":"Los Angeles Rams"}}]}]}
    def test_seed_retains_already_tracked_game_after_roll(self):
        q=pending_games({},{"games":[]},{"games":[]})
        self.assertEqual(q[self.game["slug"]]["date"],"2026-11-25")
        self.assertTrue(should_poll(datetime(2026,11,27,16,tzinfo=timezone.utc),{"game_days":[]},{"games":[]},pending=q))
        self.assertFalse(pending_games({"pending_games":q},{"games":[]},{"games":[dict(self.game,pdf_url="https://static.www.nfl.com/test.pdf")]}))
    def test_independent_wednesday(self):
        out=reconcile({}, {self.game["slug"]:self.game["game_url"]},{},{"2026-11-25":[self.event]},"2026-11-19","2026-11-26")
        self.assertEqual(out[self.game["slug"]]["status"],"Final")
        self.assertEqual(out[self.game["slug"]]["home_score"],26)
        self.assertEqual(reconcile({}, {},{},{"2026-11-25":[self.event]},"2026-11-19","2026-11-26"),{})
    def test_wrong_match_not_recovered(self):
        self.event["competitions"][0]["competitors"][0]["team"]["name"]="Bears"
        self.event["competitions"][0]["competitors"][0]["team"]["displayName"]="Chicago Bears"
        self.assertFalse(event_match(self.game["slug"],self.event))
    def test_club_url_and_identity(self):
        url="https://static.clubs.nfl.com/image/upload/packers/abc"
        g=refresh_game(self.game,self.event)
        text="National Football League Game Summary\nDate: Wednesday, 11/25/2026\nVISITOR: Green Bay Packers 3 10 0 0 0 13\nHOME: Los Angeles Rams 6 7 7 6 0 26\n"
        self.assertTrue(identity_text(text,g))
        self.assertFalse(identity_text(text.replace("26","27"),g))
        self.assertFalse(identity_text(text,dict(g,status="Scheduled")))
        self.assertEqual(club_candidate(f'<a href="{url}">Gamebook (PDF)</a>',packers_page(g)),url)
        self.assertIsNone(club_candidate(f'<a href="{url}">Other document</a>',packers_page(g)))
        self.assertFalse(club_url("https://static.clubs.nfl.com.evil.com/image/upload/packers/abc"))
    def test_final_backup_despite_fresh_heartbeat(self):
        now=datetime(2026,11,26,5,tzinfo=timezone.utc)
        feed={"games":[],"updated_at":now.isoformat()}
        self.assertTrue(nfl_update_watchdog.decide(feed,now,last_checked_at=now.isoformat(),unresolved_final_games=[self.game["slug"]])[0])
        self.assertFalse(nfl_update_watchdog.decide(feed,now,last_checked_at=now.isoformat())[0])
    def test_pending_queue_invalid_fails_closed(self):
        with self.assertRaises(ValueError):
            pending_games({"pending_games":{"bad":{"slug":"bad"}}},{"games":[]},{"games":[]})

    def test_duplicate_events_do_not_create_unobserved_identity(self):
        out=reconcile({}, {self.game["slug"]:self.game["game_url"]},{},{"2026-11-25":[self.event,self.event]},"2026-11-19","2026-11-26")
        self.assertEqual(out,{})
    def test_final_identity_uses_independent_regular_week_when_present(self):
        self.event["week"]={"number":11}
        self.assertFalse(event_match(self.game["slug"],self.event))
    def test_queue_preserves_final_observation_and_removes_verified_report(self):
        final=refresh_game(self.game,self.event)
        q=pending_games({"pending_games":{final["slug"]:final}},{"games":[self.game]},{"games":[]})
        self.assertEqual(q[final["slug"]]["status"],"Final")
        self.assertEqual(q[final["slug"]]["home_score"],26)
        self.assertEqual(pending_games({"pending_games":q},{"games":[dict(final,pdf_url="https://static.www.nfl.com/verified.pdf")]},{"games":[]}),{})
