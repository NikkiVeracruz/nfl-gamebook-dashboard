#!/usr/bin/env python3
"""Offline safety regressions for manual 2026 NFL catch-up publishing."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_nfl_2026_restoration import validate_candidate
from archive import ArchiveIntegrityError


def sample():
    old = {"games": [
        {"slug": "vikings-at-49ers-2026-reg-11", "date": "2026-11-22",
         "label": "Saved game", "pdf_url": "https://static.www.nfl.com/saved.pdf"},
        {"slug": "vikings-at-bears-2025-reg-11", "date": "2025-11-20",
         "label": "2025 game", "pdf_url": "https://static.www.nfl.com/2025.pdf"},
    ]}
    added = {
        "slug": "jets-at-patriots-2026-reg-1", "date": "2026-09-13",
        "label": "Recovered", "pdf_url": "https://static.www.nfl.com/new.pdf",
    }
    return old, {"games": old["games"] + [added]}


class Nfl2026RestorationTests(unittest.TestCase):
    def test_additional_2026_games_preserve_old_records(self):
        a,b=sample()
        self.assertEqual(validate_candidate(a,b,b"cursor",b"cursor"),(2,1,3))

    def test_changed_cursor_is_blocked(self):
        a,b=sample()
        with self.assertRaisesRegex(ArchiveIntegrityError,"progress cursor"):
            validate_candidate(a,b,b"original",b"modified")

    def test_changed_existing_game_is_blocked(self):
        a,b=sample()
        b["games"][0] = {**b["games"][0], "label":"Changed"}
        with self.assertRaisesRegex(ArchiveIntegrityError,"previously archived"):
            validate_candidate(a,b,b"cursor",b"cursor")

    def test_deleted_old_game_is_blocked(self):
        a,b=sample()
        b["games"].pop(0)
        with self.assertRaises(ArchiveIntegrityError):
            validate_candidate(a,b,b"cursor",b"cursor")

    def test_wrong_season_is_blocked(self):
        a,b=sample()
        b["games"][-1]["slug"] = "jets-at-patriots-2025-reg-1"
        with self.assertRaisesRegex(ArchiveIntegrityError,"wrong season"):
            validate_candidate(a,b,b"cursor",b"cursor")

    def test_unreviewed_date_is_blocked(self):
        a,b=sample()
        b["games"][-1]["date"] = "2026-12-01"
        with self.assertRaisesRegex(ArchiveIntegrityError,"outside reviewed"):
            validate_candidate(a,b,b"cursor",b"cursor")

    def test_unofficial_pdf_is_blocked(self):
        a,b=sample()
        b["games"][-1]["pdf_url"] = "https://example.org/unverified.pdf"
        with self.assertRaisesRegex(ArchiveIntegrityError,"nonofficial"):
            validate_candidate(a,b,b"cursor",b"cursor")

    def test_duplicate_import_does_not_publish(self):
        a,_=sample()
        with self.assertRaisesRegex(ArchiveIntegrityError,"No new"):
            validate_candidate(a,a,b"cursor",b"cursor")

    def test_manual_publisher_cannot_publish_archive_cursor(self):
        y = (Path(__file__).resolve().parents[1] /
             ".github/workflows/restore-nfl-2026-season.yml").read_text()
        self.assertIn("workflow_dispatch:",y)
        self.assertNotIn("  schedule:",y)
        self.assertIn("if: github.ref == 'refs/heads/main'",y)
        self.assertIn("group: update-gamebooks",y)
        self.assertIn("git add archive.json",y)
        self.assertNotIn("git add archive-progress.json",y)
        self.assertIn("python tests/validate_nfl_2026_restoration.py FETCH_HEAD",y)
        self.assertIn("python tests/nfl_2026_coverage.py",y)


if __name__ == "__main__":
    unittest.main(verbosity=2)
