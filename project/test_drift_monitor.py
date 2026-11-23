"""Offline regression tests for the scheduled project governance monitor."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "project"))
from drift_monitor import (
    REPO, LEGACY_WORKFLOWS, audit_archive, audit_backfill,
    audit_registry, inspect, markdown, valid_archived_game,
)
from render_register import SOURCE


def sample_record(league):
    row = {"id": "123", "slug": "bears-at-bills-2026-reg-11",
           "date": "2026-11-23", "status": "Final", "label": "Away @ Home"}
    if league in ("NFL", "NBA", "WNBA"):
        row["pdf_url"] = "https://official.example/game.pdf"
    if league == "NHL":
        row.update(gs_url="https://www.nhl.com/GS", es_url="https://www.nhl.com/ES",
                   status="OFF")
    if league == "MLB":
        row.update(box_url="https://www.mlb.com/box",
                   plays_url="https://www.mlb.com/plays", link_verification="verified_api")
    return row


class DriftMonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_archive_accepts_completed_documents_only(self):
        for league in REPO:
            with self.subTest(league=league):
                g = sample_record(league)
                self.assertIsNone(valid_archived_game(g, league, "2026-11-19"))
                self.assertEqual(audit_archive(league, {"games": [g]}, "2026-11-19"), 1)

    def test_missing_documents_and_old_records_are_detected(self):
        g = sample_record("NHL")
        g.pop("es_url")
        with self.assertRaises(ValueError):
            audit_archive("NHL", {"games": [g]}, "2026-11-22")
        g = sample_record("MLB")
        g["date"] = "2026-06-01"
        with self.assertRaises(ValueError):
            audit_archive("MLB", {"games": [g]}, "2026-11-22")

    def test_backfill_guard_and_no_schedule_required(self):
        audit_backfill("on:\n  workflow_dispatch:\nENABLE_HISTORICAL_BACKFILL", "ENABLE_HISTORICAL_BACKFILL")
        with self.assertRaises(ValueError):
            audit_backfill("on:\n  workflow_dispatch:\n  schedule:\n    - cron: '* * * * *'\nENABLE_HISTORICAL_BACKFILL",
                           "ENABLE_HISTORICAL_BACKFILL")
        with self.assertRaises(ValueError):
            audit_backfill("on:\n  workflow_dispatch:\n", "ENABLE_HISTORICAL_BACKFILL")

    def test_unapproved_feature_cannot_be_implemented(self):
        x = copy.deepcopy(self.registry)
        for row in x["features"]:
            if row["id"] == "IDEA-001":
                row["state"] = "implemented"
        with self.assertRaises(ValueError):
            audit_registry(x)

    def test_five_league_end_to_end_drift_detection_with_fake_sources(self):
        board = "NFL NBA WNBA NHL MLB history-disclosure How to Use This Dashboard leagueFilter statusFilter"
        paths = {}
        for league, (repo, archive, live, backfill) in REPO.items():
            paths[(repo, archive)] = json.dumps({"games": [sample_record(league)]})
            paths[(repo, live)] = json.dumps({"games": []})
            paths[(repo, "forward_only.py")] = (
                self.registry["project"]["operating_policy"]["archive_start_date_by_league"][league]
                + "\nfilter_archive complete")
            paths[(repo, backfill)] = "workflow_dispatch:\nENABLE_HISTORICAL_BACKFILL"
        paths[("nfl-gamebook-dashboard", "command-center/index.html")] = board
        paths[("nfl-gamebook-dashboard", ".github/workflows/archive-2026-completeness.yml")] = (
            "workflow_dispatch:\nENABLE_HISTORICAL_BACKFILL")
        for repo, file in LEGACY_WORKFLOWS:
            paths[(repo, file)] = "ENABLE_HISTORICAL_BACKFILL"
        paths[("nfl-gamebook-dashboard", ".github/workflows/missing-game-audit.yml")] = "schedule:"
        paths[("nfl-gamebook-dashboard", ".github/workflows/document-level-verification.yml")] = "schedule:"
        def read(repo, path):
            return paths.get((repo, path), "# existing implementation evidence")
        ok = inspect(self.registry, read=read)
        self.assertEqual(ok["status"], "pass", ok["failures"])
        self.assertIn("PASS", markdown(ok))
        paths[("mlb-gamebook-dashboard", "archive.json")] = json.dumps({
            "games": [{**sample_record("MLB"), "link_verification": "needs_review"}]})
        fail = inspect(self.registry, read=read)
        self.assertEqual(fail["status"], "drift_or_inconclusive")
        self.assertTrue(any("MLB" in x for x in fail["failures"]))


if __name__ == "__main__":
    unittest.main()
