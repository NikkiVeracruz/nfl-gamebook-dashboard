#!/usr/bin/env python3
"""Offline tests for the controlled 2025 NFL recovery publication gate."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_nfl_nov_2025_recovery import inspect_batch, EXPECTED_NEW
from archive import ArchiveIntegrityError


def fixture():
    old = {"games": [
        {"slug": "old-current-game", "date": "2026-11-22", "label": "Old",
         "pdf_url": "https://static.www.nfl.com/old.pdf"}
    ]}
    new = {"games": old["games"] + [
        {"slug": f"new-2025-{i}", "date": "2025-11-02", "label": f"Game {i}",
         "pdf_url": f"https://static.www.nfl.com/reports/{i}.pdf"}
        for i in range(EXPECTED_NEW)
    ]}
    return old, new


class RestorationGateTests(unittest.TestCase):
    def test_exact_60_official_pdfs_and_unchanged_old_records_pass(self):
        old, proposed = fixture()
        records, before, after = inspect_batch(old, proposed)
        self.assertEqual((len(records), before, after), (60, 1, 61))

    def test_missing_game_fails(self):
        old, proposed = fixture()
        proposed["games"].pop()
        with self.assertRaisesRegex(ArchiveIntegrityError, "exactly 60"):
            inspect_batch(old, proposed)

    def test_existing_record_modification_fails(self):
        old, proposed = fixture()
        proposed["games"][0] = {**proposed["games"][0], "label": "Changed"}
        with self.assertRaisesRegex(ArchiveIntegrityError, "previously archived"):
            inspect_batch(old, proposed)

    def test_old_game_removal_fails(self):
        old, proposed = fixture()
        proposed["games"].pop(0)
        with self.assertRaises(ArchiveIntegrityError):
            inspect_batch(old, proposed)

    def test_games_outside_reviewed_batch_fail(self):
        old, proposed = fixture()
        proposed["games"][1]["date"] = "2025-12-01"
        with self.assertRaisesRegex(ArchiveIntegrityError, "outside recovery window"):
            inspect_batch(old, proposed)

    def test_missing_pdf_fails(self):
        old, proposed = fixture()
        proposed["games"][1].pop("pdf_url")
        with self.assertRaisesRegex(ArchiveIntegrityError, "missing a verified NFL PDF"):
            inspect_batch(old, proposed)

    def test_nonofficial_link_fails(self):
        old, proposed = fixture()
        proposed["games"][1]["pdf_url"] = "https://example.net/book.pdf"
        with self.assertRaisesRegex(ArchiveIntegrityError, "Nonofficial"):
            inspect_batch(old, proposed)

    def test_duplicate_pdf_fails(self):
        old, proposed = fixture()
        proposed["games"][1]["pdf_url"] = proposed["games"][2]["pdf_url"]
        with self.assertRaisesRegex(ArchiveIntegrityError, "Duplicate gamebook PDF"):
            inspect_batch(old, proposed)

    def test_malformed_records_fail(self):
        old, proposed = fixture()
        proposed["games"].append(proposed["games"][-1].copy())
        with self.assertRaisesRegex(ArchiveIntegrityError, "duplicate game identity"):
            inspect_batch(old, proposed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
