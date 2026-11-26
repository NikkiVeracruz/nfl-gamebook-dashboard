#!/usr/bin/env python3
"""Read-only NFL final-gamebook audit, independent of the dashboard publisher.

A missing book is actionable only when an ESPN game is independently confirmed
final AND at least five hours have elapsed since scheduled kickoff. Five hours
is a conservative approximation, not a measured "time since final" timestamp.
Unknown team matches or unavailable scoreboards are reported as inconclusive.
This script never writes dashboard files or triggers update workflows.
"""
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
NFL_FEED = "https://nikkiveracruz.github.io/nfl-gamebook-dashboard/gamebooks.json"
SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
MIN_KICKOFF_AGE = timedelta(hours=5)
SLUG = re.compile(r"^(.+)-at-(.+)-20\d{2}-(?:reg|pre|post)-\d+$", re.I)


def fetch_json(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "GamebookFinalReportAudit/1.0", "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        payload = response.read(5_000_001)
        if len(payload) > 5_000_000:
            raise ValueError("Response exceeded 5MB")
    return json.loads(payload)


def scoreboard(day):
    url = SCOREBOARD + "?" + urlencode({"dates": day.replace("-", ""), "limit": 100})
    events = fetch_json(url).get("events")
    if not isinstance(events, list):
        raise ValueError("ESPN scoreboard lacks an events list")
    return events


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())


def teams_match(game, event):
    match = SLUG.fullmatch(str(game.get("slug", "")))
    if not match:
        return False
    competition = (event.get("competitions") or [{}])[0]
    competitors = competition.get("competitors") or []
    sides = {c.get("homeAway"): c.get("team") or {} for c in competitors
             if isinstance(c, dict)}
    for side, nickname in (("away", match.group(1)), ("home", match.group(2))):
        team = sides.get(side, {})
        if not team:
            return False
        names = (team.get("name"), team.get("shortDisplayName"),
                 team.get("displayName"), team.get("abbreviation"))
        # Use exact normalized nicknames; never infer a match from scores
        # or from substring matches such as Jets vs. another team name.
        if normalized(nickname) not in {normalized(x) for x in names if x}:
            return False
    return True


def is_final(event):
    status = event.get("status") or {}
    kind = status.get("type") or {}
    return kind.get("completed") is True or kind.get("state") == "post"


def parse_kickoff(event):
    raw = event.get("date")
    if not isinstance(raw, str):
        raise ValueError("Missing independent kickoff time")
    kickoff = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if kickoff.tzinfo is None:
        raise ValueError("Kickoff lacks timezone")
    return kickoff


def has_official_pdf(game):
    url = game.get("pdf_url")
    if isinstance(url,str) and game.get("pdf_verification")=="official_club_identity":
        from urllib.parse import urlparse
        p=urlparse(url)
        if p.scheme=="https" and p.netloc=="static.clubs.nfl.com" and re.fullmatch(r"/image/upload/packers/[A-Za-z0-9_-]+(?:\.pdf)?",p.path):return True
    return isinstance(url, str) and url.startswith((
        "https://static.www.nfl.com/", "https://www.nfl.com/", "https://nfl.com/"
    )) and ".pdf" in url.lower()


def audit(feed, get_scoreboard=scoreboard, now=None):
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Reference time must have timezone")
    if not isinstance(feed, dict) or not isinstance(feed.get("games"), list):
        raise ValueError("NFL published feed missing games array")
    if feed.get("offseason"):
        return [], ["Offseason: no final-gamebook checks"]
    alerts, notes, boards = [], [], {}
    today_et = current.astimezone(ET).date()
    for game in feed["games"]:
        if not isinstance(game, dict) or has_official_pdf(game):
            continue
        day = game.get("date")
        slug = game.get("slug")
        if not isinstance(day, str) or not SLUG.fullmatch(str(slug or "")):
            notes.append(f"Inconclusive: unrecognized game record {slug!r}")
            continue
        try:
            game_date = date.fromisoformat(day)
        except ValueError:
            notes.append(f"Inconclusive: invalid date for {slug}")
            continue
        # Avoid probing future games and previously archived seasons.
        if game_date > today_et or game_date < today_et - timedelta(days=7):
            continue
        if day not in boards:
            try:
                boards[day] = get_scoreboard(day)
                if not isinstance(boards[day], list):
                    raise ValueError("Scoreboard did not return a list")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                boards[day] = None
                notes.append(f"Inconclusive: ESPN schedule for {day} unavailable ({exc})")
        events = boards[day]
        if events is None:
            continue
        matches = [e for e in events if isinstance(e, dict) and teams_match(game, e)]
        if len(matches) != 1:
            notes.append(f"Inconclusive: {slug} matched {len(matches)} independent games")
            continue
        event = matches[0]
        if not is_final(event):
            continue
        try:
            kickoff = parse_kickoff(event)
        except ValueError as exc:
            notes.append(f"Inconclusive: {slug}: {exc}")
            continue
        age = current - kickoff
        if age >= MIN_KICKOFF_AGE:
            alerts.append(
                f"{day} {slug}: final according to ESPN; "
                f"no verified PDF link; {age.total_seconds()/3600:.1f}h since kickoff"
            )
    return alerts, notes


def main():
    try:
        feed = fetch_json(NFL_FEED)
        # The current display no longer contains unresolved games after rollover.
        from pathlib import Path
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
        from nfl_pending import load_queue
        known={g["slug"]:g for g in load_queue().values()}
        known.update({g["slug"]:g for g in feed["games"] if g.get("slug")})
        alerts, notes = audit({**feed,"games":list(known.values())})
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"FINAL GAMEBOOK AUDIT ERROR: {exc}", file=sys.stderr)
        return 1
    for note in notes:
        print("AUDIT NOTE: " + note)
    for alert in alerts:
        print("MISSING FINAL GAMEBOOK: " + alert, file=sys.stderr)
    if alerts:
        print(f"ALERT: {len(alerts)} finished NFL games missing official PDF links.", file=sys.stderr)
        return 1
    print("PASS: no overdue final-gamebook links detected (inconclusive items listed above)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
