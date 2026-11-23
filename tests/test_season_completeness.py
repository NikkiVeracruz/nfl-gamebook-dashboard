"""Season schedule-to-archive regression tests, no external network calls."""
import sys
import unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import season_completeness as m


class Response:
    def __init__(self,data): self.data=data
    def raise_for_status(self): pass
    def json(self): return self.data


class Session:
    def __init__(self,data): self.data=data
    def get(self,*a,**kw): return Response(self.data)


class CoverageTests(unittest.TestCase):
    def test_missing_game_is_a_failure(self):
        e={"key":"1","date":"2026-06-12","completed":True}
        row=m.audit_one("WNBA",{"games":[]},[e],date(2026,11,23))
        self.assertEqual(row["missing_game_count"],1)
        self.assertTrue(m.has_failures({"leagues":{"WNBA":row}}))

    def test_report_grace_period_and_overdue(self):
        e={"key":"1","date":"2026-11-22","completed":True}
        g={"id":"1","date":e["date"],"status":"Final"}
        self.assertEqual(m.audit_one("WNBA",{"games":[g]},[e],date(2026,11,23))["missing_report_count"],0)
        e["date"]=g["date"]="2026-06-12"
        self.assertEqual(m.audit_one("WNBA",{"games":[g]},[e],date(2026,11,23))["missing_report_count"],1)

    def test_wnba_japan_is_needs_review(self):
        e={"key":"1","date":"2026-04-29","completed":True}
        g={"id":"1","date":e["date"],"label":"JAPAN @ Phoenix Mercury"}
        row=m.audit_one("WNBA",{"games":[g]},[e],date(2026,11,23))
        self.assertEqual(row["missing_report_count"],0)
        self.assertEqual(row["review_or_unverified_count"],1)

    def test_nhl_international_is_not_nhl_schedule(self):
        rows=m.official_events("NHL",date(2026,11,22),Session({"games":[
            {"id":2025090001,"gameState":"FINAL"},
            {"id":2026010044,"gameState":"FINAL"},
            {"id":2026020381,"gameState":"OFF"}]}))
        self.assertEqual({x["key"] for x in rows},{"2026010044","2026020381"})

    def test_nhl_preseason_not_mistaken_for_regular_missing_report(self):
        e={"key":"2026010044","date":"2026-09-24","completed":True}
        row=m.audit_one("NHL",{"games":[{"id":e["key"],"date":e["date"]}]},[e],date(2026,11,23))
        self.assertEqual(row["missing_report_count"],0)
        self.assertEqual(row["review_or_unverified_count"],1)

    def test_mlb_includes_all_star_and_exhibition(self):
        events=m.mlb_events(date(2026,7,14),date(2026,7,14),Session({
            "dates":[{"date":"2026-07-14","games":[
                {"gamePk":123456,"gameType":"A","status":{"abstractGameState":"Final"}},
                {"gamePk":234567,"gameType":"E","status":{"abstractGameState":"Final"}}]}]}))
        self.assertEqual({x["key"] for x in events},{"123456","234567"})

    def test_nfl_date_and_team_identity(self):
        e={"key":("2026-11-22","vikings","49ers"),"date":"2026-11-22","completed":True}
        g={"slug":"vikings-at-49ers-2026-reg-11","date":"2026-11-22","pdf_url":"https://static.www.nfl.com/gamebook.pdf"}
        row=m.audit_one("NFL",{"games":[g]},[e],date(2026,11,23))
        self.assertEqual(row["missing_game_count"],0)

    def test_pattern_only_mlb_link_is_not_verified(self):
        e={"key":"123456","date":"2026-06-12","completed":True,"game_type":"R"}
        g={"id":"123456","date":e["date"],"box_url":"https://www.mlb.com/gameday/123456/box-score",
           "plays_url":"https://www.mlb.com/gameday/123456/play-by-play"}
        self.assertEqual(m.audit_one("MLB",{"games":[g]},[e],date(2026,11,23))["review_or_unverified_count"],1)
        g["link_verification"]="verified_api"
        self.assertEqual(m.audit_one("MLB",{"games":[g]},[e],date(2026,11,23))["review_or_unverified_count"],0)

    def test_international_records_remain_in_archive(self):
        g={"id":"2025090001","date":"2026-02-11","competition":"international_hockey"}
        row=m.audit_one("NHL",{"games":[g]},[],date(2026,11,23))
        self.assertEqual(row["non_nhl_international_preserved"],1)


if __name__=="__main__":unittest.main()
