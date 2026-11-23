"""Offline tests for actual document verification and archive nonmutation."""
import io
import tempfile
import unittest
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from pypdf import PdfWriter
from document_level_verification import (
    archive_documents, bounded_get, fresh, inspect_nhl, inspect_pdf,
    make_report, valid_url, inspect_mlb, pdf_date_match, select_due,
)


def sample(**kwargs):
    base = {"league": "NBA", "id": "401900001", "kind": "PDF",
            "date": "2026-11-05", "label": "Boston Celtics @ Denver Nuggets",
            "url": "https://statsdmz.nba.com/pdfs/20261105/20261105_BOSDEN_book.pdf",
            "key": "NBA:401900001:PDF"}
    base.update(kwargs)
    return base


class DocumentVerificationTests(unittest.TestCase):
    def test_only_final_old_games_require_documents(self):
        games = [{"id": "one", "date": "2026-07-25", "status": "Final", "label": "A @ B"},
                 {"id": "two", "date": "2026-11-23", "status": "Scheduled", "label": "A @ B"},
                 {"id": "three", "date": "2026-11-22", "status": "Final", "label": "A @ B"}]
        links, missing = archive_documents("WNBA", games, date(2026, 11, 23))
        self.assertEqual(links, [])
        self.assertEqual([i["id"] for i in missing], ["one"])

    def test_international_hockey_not_required_as_regular_nhl_reports(self):
        games = [{"id": "2025090001", "date": "2026-02-11",
                  "status": "FINAL", "competition": "international_hockey"}]
        links, missing = archive_documents("NHL", games, date(2026, 11, 23))
        self.assertEqual((links, missing), ([], []))

    def test_nhl_club_game_requires_both_report_types(self):
        games = [{"id": "2026010002", "date": "2026-09-19", "status": "FINAL",
                  "gs_url": "https://www.nhl.com/scores/htmlreports/20262027/GS010002.HTM"}]
        links, missing = archive_documents("NHL", games, date(2026, 11, 23))
        self.assertEqual([i["kind"] for i in links], ["GS"])
        self.assertEqual([i["kind"] for i in missing], ["ES"])

    def test_only_expected_official_urls_are_accepted(self):
        self.assertTrue(valid_url(sample()))
        self.assertFalse(valid_url(sample(url="https://evil.example/game.pdf")))
        self.assertFalse(valid_url(sample(url="http://statsdmz.nba.com/pdf.pdf")))
        nhl = {"league": "NHL", "id": "2026010002", "kind": "GS",
               "url": "https://www.nhl.com/scores/htmlreports/20262027/GS010002.HTM"}
        self.assertTrue(valid_url(nhl))
        self.assertFalse(valid_url({**nhl, "url": nhl["url"].replace("GS", "ES")}))

    def test_invalid_pdf_is_not_reported_verified(self):
        status, detail = inspect_pdf(sample(), b"<html>access denied</html>")
        self.assertEqual(status, "invalid_format")

    def test_parseable_pdf_without_team_or_date_is_not_claimed_matched(self):
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        body = io.BytesIO()
        writer.write(body)
        status, detail = inspect_pdf(sample(), body.getvalue())
        self.assertEqual(status, "readable_identity_unconfirmed")

    def test_nfl_short_date_formats_are_recognized(self):
        self.assertTrue(pdf_date_match("Thursday 9/10/26", "2026-09-10"))
        self.assertTrue(pdf_date_match("Thursday September 10, 2026", "2026-09-10"))
        self.assertFalse(pdf_date_match("Thursday 9/11/26", "2026-09-10"))

    def test_nhl_wrong_report_type_rejected(self):
        item = {"kind": "GS", "id": "2026020384"}
        status, _ = inspect_nhl(item, b"<html>Event Summary</html>")
        self.assertEqual(status, "invalid_report_content")
        status, _ = inspect_nhl(item, b"<html>Game Summary</html>")
        self.assertEqual(status, "verified_report")

    def test_due_selection_retries_unconfirmed_without_starving_unseen(self):
        now = datetime(2026, 11, 23, tzinfo=timezone.utc)
        items = [sample(key=f"NBA:{n}:PDF", id=str(n)) for n in range(10)]
        retry = items[0]
        previous = {retry["key"]: {
            "url": retry["url"], "status": "readable_identity_unconfirmed",
            "checked_at": (now - timedelta(days=2)).isoformat()}}
        chosen, count = select_due(items, previous, now, limit=5)
        self.assertEqual(count, 10)
        self.assertEqual(chosen[0]["key"], retry["key"])
        self.assertEqual(len(chosen), 5)
        self.assertTrue(any(it["key"] != retry["key"] for it in chosen))

    def test_stale_or_changed_url_rechecked(self):
        item = sample()
        now = datetime(2026, 11, 23, tzinfo=timezone.utc)
        fresh_record = {"url": item["url"], "status": "verified_match",
                        "checked_at": (now - timedelta(days=2)).isoformat()}
        self.assertTrue(fresh(fresh_record, item, now))
        self.assertFalse(fresh({**fresh_record, "url": "https://different.example"}, item, now))
        self.assertFalse(fresh({**fresh_record, "status": "source_unavailable"}, item, now))

    def test_report_preserves_old_evidence_and_counts_pending(self):
        item = sample()
        older = {"results": {"NFL:old:PDF": {"status": "verified_match", "url": "x"}}}
        report = make_report([item], [], older, {}, datetime(2026, 11, 23, tzinfo=timezone.utc))
        self.assertEqual(report["summary"]["linked"], 1)
        self.assertEqual(report["summary"]["statuses"]["not_yet_checked"], 1)
        self.assertIn("NFL:old:PDF", report["results"])

    @patch("document_level_verification.fetch_json")
    def test_mlb_inspects_actual_stats_structure(self, fetch):
        item = {"league": "MLB", "id": "823543", "kind": "BOX"}
        fetch.return_value = {"gameData": {"game": {"pk": 823543}},
                              "liveData": {"boxscore": {"teams": {"home": {}, "away": {}}},
                                           "plays": {"allPlays": [{"about": {}}]}}}
        status, _ = inspect_mlb(item)
        self.assertEqual(status, "verified_official_stats")
        status, _ = inspect_mlb({**item, "kind": "PLAYS"})
        self.assertEqual(status, "verified_official_stats")
        fetch.return_value = {"gameData": {"game": {"pk": 823544}}}
        status, _ = inspect_mlb(item)
        self.assertEqual(status, "mismatched_game_id")


if __name__ == "__main__":
    unittest.main()
