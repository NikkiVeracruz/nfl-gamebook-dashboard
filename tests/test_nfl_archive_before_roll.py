"""An NFL week cannot roll away without preserving the previous feed first."""
import json
import tempfile
import unittest
from pathlib import Path

import archive
import monitor


class NFLArchiveBeforeRolloverTests(unittest.TestCase):
    def test_existing_pdf_is_preserved_even_if_game_leaves_live_week(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            feed, history=root/"feed.json",root/"archive.json"
            previously={"slug":"vikings-at-49ers-2026-reg-11","date":"2026-11-22",
                        "label":"Vikings @ 49ers",
                        "game_url":"https://www.nfl.com/games/vikings-at-49ers-2026-reg-11",
                        "pdf_url":"https://static.www.nfl.com/game.pdf"}
            feed.write_text(json.dumps({"games":[previously]}))
            history.write_text(json.dumps({"games":[
                {"slug":"previous-at-other-2026-reg-10","date":"2026-11-14",
                 "label":"Previous","pdf_url":"https://static.www.nfl.com/prev.pdf"}
            ]}))
            self.assertEqual(monitor.protect_current_feed_before_update(feed,history),1)
            saved=json.loads(history.read_text())["games"]
            self.assertEqual(len(saved),2)
            self.assertEqual(next(x for x in saved if x["slug"]==previously["slug"])["pdf_url"],previously["pdf_url"])
            unchanged=history.read_text()
            monitor.protect_current_feed_before_update(feed,history)
            self.assertEqual(history.read_text(),unchanged)

    def test_corrupt_archive_fails_closed_without_changing_feed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            feed,history=root/"feed.json",root/"archive.json"
            feed.write_text(json.dumps({"games":[
                {"slug":"old","date":"2026-11-22","label":"Old"}
            ]}))
            original=feed.read_text()
            history.write_text("{broken")
            with self.assertRaises(archive.ArchiveIntegrityError):
                monitor.protect_current_feed_before_update(feed,history)
            self.assertEqual(feed.read_text(),original)

    def test_archival_prior_copy_preserves_already_recorded_report_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);feed=root/"feed.json";history=root/"archive.json"
            feed.write_text(json.dumps({"games":[{"slug":"one","date":"2026-11-22","label":"Game"}]}))
            history.write_text(json.dumps({"games":[{"slug":"one","date":"2026-11-22","label":"Game",
                          "pdf_url":"https://static.www.nfl.com/known.pdf"}]}))
            monitor.protect_current_feed_before_update(feed,history)
            self.assertEqual(json.loads(history.read_text())["games"][0]["pdf_url"],"https://static.www.nfl.com/known.pdf")


if __name__=="__main__":
    unittest.main()
