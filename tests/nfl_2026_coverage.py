#!/usr/bin/env python3
"""Read-only independent ESPN vs NFL.com game coverage audit for 2026 season.

Run only after scratch backfill has populated archive.json. Does not publish.
"""
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archive import ArchiveIntegrityError, validate_games
from monitor import HEADERS

ET = ZoneInfo("America/New_York")
START = date(2026, 8, 1)
END = date(2026, 11, 23)  # Exclusive: through November 22, 2026
API = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
SLUG = re.compile(r"^(.+)-at-(.+)-2026-(?:pre|reg|post)-\d+$", re.I)
PDF_HOSTS = {"static.www.nfl.com", "www.nfl.com", "nfl.com"}


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def archive_identity(game):
    slug = game.get("slug", "")
    match = SLUG.fullmatch(str(slug))
    if not match:
        raise ArchiveIntegrityError(f"Unrecognized 2026 NFL slug: {slug!r}")
    return game["date"], normalized(match.group(1)), normalized(match.group(2))


def get_expected(session, day, now):
    response = session.get(
        API, params={"dates": day.strftime("%Y%m%d"), "limit": 100},
        timeout=30,
    )
    response.raise_for_status()
    events = response.json().get("events")
    if not isinstance(events, list):
        raise ArchiveIntegrityError(f"Invalid ESPN game schedule for {day}")
    found = set()
    for event in events:
        if not isinstance(event, dict) or not event.get("date"):
            raise ArchiveIntegrityError(f"Invalid NFL event in ESPN response for {day}")
        kickoff = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        if kickoff.tzinfo is None:
            raise ArchiveIntegrityError(f"Timezone missing on kickoff for {day}")
        if kickoff.astimezone(ET).date() != day or kickoff > now:
            continue
        competitions = event.get("competitions")
        if not isinstance(competitions, list) or not competitions:
            raise ArchiveIntegrityError(f"Missing ESPN competition for {day}")
        sides = {}
        for competitor in competitions[0].get("competitors", []):
            name = (competitor.get("team") or {}).get("name")
            side = competitor.get("homeAway")
            if side in ("home", "away") and name:
                sides[side] = normalized(name)
        if not sides.get("home") or not sides.get("away"):
            raise ArchiveIntegrityError(f"Unmatched NFL competitor on {day}")
        found.add((day.isoformat(), sides["away"], sides["home"]))
    return found


def verify_coverage(proposed, expected, now):
    games = validate_games(proposed, "Proposed 2026 season NFL archive")
    actual = {}
    for game in games.values():
        if START.isoformat() <= game["date"] < END.isoformat():
            identity = archive_identity(game)
            if identity in actual:
                raise ArchiveIntegrityError(f"Duplicate NFL 2026 matchup: {identity}")
            actual[identity] = game
    missing = sorted(expected - set(actual))
    # The current week includes scheduled upcoming games. Only require games
    # that actually kicked off, identified by the independent schedule.
    report_missing = []
    for identity in sorted(expected & set(actual)):
        game = actual[identity]
        url = game.get("pdf_url")
        if url:
            from urllib.parse import urlparse
            p = urlparse(url)
            if p.scheme != "https" or p.hostname not in PDF_HOSTS or ".pdf" not in p.path.lower():
                raise ArchiveIntegrityError(f"Invalid official gamebook link {url}")
        else:
            # Older games should have gamebooks; newly completed games may not.
            game_day = date.fromisoformat(game["date"])
            if game_day < now.astimezone(ET).date() - timedelta(days=2):
                report_missing.append(identity)
    return {
        "independent_games_kicked_off": len(expected),
        "archived_2026_season_games": len(actual),
        "unarchived_games": missing,
        "older_games_without_pdf": report_missing,
        "2026_games_with_pdf": sum(bool(g.get("pdf_url")) for g in actual.values()),
        "months": dict(sorted(Counter(g["date"][:7] for g in actual.values()).items())),
    }


def main():
    now = datetime.now(timezone.utc)
    archive = json.loads(Path("archive.json").read_text())
    session = requests.Session()
    session.headers.update(HEADERS)
    expected = set()
    day = START
    while day < END:
        expected.update(get_expected(session, day, now))
        day += timedelta(days=1)
    if len(expected) < 100:
        raise ArchiveIntegrityError(
            f"ESPN expected only {len(expected)} NFL 2026 games since August; "
            "schedule coverage is implausibly low"
        )
    report = verify_coverage(archive, expected, now)
    print("NFL 2026 SEASON INDEPENDENT COVERAGE REPORT")
    print(json.dumps(report, indent=2))
    if report["unarchived_games"]:
        raise ArchiveIntegrityError(
            f"{len(report['unarchived_games'])} independent NFL games are missing"
        )
    if report["older_games_without_pdf"]:
        raise ArchiveIntegrityError(
            f"{len(report['older_games_without_pdf'])} older games lack official PDFs"
        )
    print("PASS: every independently scheduled 2026 NFL game played so far is archived")
    return report


if __name__ == "__main__":
    try:
        main()
    except (ArchiveIntegrityError, ValueError, OSError, requests.RequestException) as exc:
        sys.exit(f"NFL 2026 COVERAGE AUDIT FAILED: {exc}")
