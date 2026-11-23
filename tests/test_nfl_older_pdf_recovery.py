"""Ensure overdue NFL PDFs are recovered without polluting the current-week feed."""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import monitor


class OlderGamebookRecoveryTests(unittest.TestCase):
    def test_recovers_old_missing_pdf_only(self):
        today = datetime.now(monitor.ET).date()
        old = today - timedelta(days=8)
        current = today - timedelta(days=1)
        old_game = {
            "slug": "vikings-at-49ers-2026-reg-11",
            "date": old.isoformat(),
            "label": "Old game awaiting report",
            "game_url": "https://www.nfl.com/games/vikings-at-49ers-2026-reg-11",
        }
        current_game = {
            "slug": "another-at-team-2026-reg-11",
            "date": current.isoformat(),
            "game_url": "https://www.nfl.com/games/another-at-team-2026-reg-11",
        }
        future = {
            "slug": "future-at-team-2026-reg-12",
            "date": (today + timedelta(days=2)).isoformat(),
            "game_url": "https://www.nfl.com/games/future-at-team-2026-reg-12",
        }
        pdf_url = "https://static.www.nfl.com/gamecenter/official.pdf"
        html = f'<a href="{pdf_url}">Official Gamebook</a>'
        old_dir = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            try:
                os.chdir(temp)
                Path("archive.json").write_text(json.dumps(
                    {"updated_at": "old", "games": [old_game, current_game, future]}
                ))
                with patch.object(monitor, "get", return_value=html) as fetch, \
                        patch.object(monitor, "verify_pdf", return_value=True):
                    found = monitor.recover_older_missing_pdfs(
                        object(), today - timedelta(days=5)
                    )
                    saved = json.loads(Path("archive.json").read_text())
                    self.assertEqual(found, 1)
                    self.assertEqual(saved["games"][0]["pdf_url"], pdf_url)
                    self.assertNotIn("pdf_url", saved["games"][1])
                    self.assertNotIn("pdf_url", saved["games"][2])
                    self.assertEqual(fetch.call_count, 1)
                    self.assertEqual(
                        monitor.recover_older_missing_pdfs.__name__,
                        "recover_older_missing_pdfs",
                    )
            finally:
                os.chdir(old_dir)


if __name__ == "__main__":
    unittest.main()
