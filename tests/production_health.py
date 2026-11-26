#!/usr/bin/env python3
"""Read-only production health probe for all five league feeds.
No files are written, no source workflows are triggered, and no archives are modified.
A failing probe makes the GitHub Actions run red for administrator notification.
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

MAX_AGE_MINUTES = 180
ACTIVE_LEAGUE_MAX_AGE_MINUTES = 110
ET = ZoneInfo("America/New_York")
NFL_MAX_AGE_MINUTES = 90  # Successful NFL poll heartbeat is throttled to 40 minutes.
FEEDS = {
    "NFL": "https://nikkiveracruz.github.io/nfl-gamebook-dashboard/gamebooks.json",
    "NBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/gamebooks.json",
    "WNBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/wnba/gamebooks.json",
    "NHL": "https://nikkiveracruz.github.io/nhl-gamebook-dashboard/gamebooks.json",
    "MLB": "https://nikkiveracruz.github.io/mlb-gamebook-dashboard/gamebooks.json",
}

METADATA = {
    "NBA": ("nba-gamebook-dashboard/nba-poll-status.json",
            "nba-gamebook-dashboard/nba-calendar.json"),
    "WNBA": ("nba-gamebook-dashboard/wnba/poll-status.json",
             "nba-gamebook-dashboard/wnba/calendar.json"),
    "NHL": ("nhl-gamebook-dashboard/poll-status.json",
            "nhl-gamebook-dashboard/league-calendar.json"),
    "MLB": ("mlb-gamebook-dashboard/poll-status.json",
            "mlb-gamebook-dashboard/league-calendar.json"),
}


def read_metadata(path):
    url = "https://raw.githubusercontent.com/NikkiVeracruz/" + path.replace("/", "/main/", 1)
    req = urllib.request.Request(
        url, headers={"User-Agent": "GamebookHealthCheck/1.0",
                      "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read(1_000_001)
    if len(payload) > 1_000_000:
        raise ValueError("League monitoring status unexpectedly large")
    return json.loads(payload)


def polling_expected(calendar, status, now=None):
    current = (now or datetime.now(timezone.utc)).astimezone(ET)
    today = current.date()
    dates = calendar.get("game_days")
    if not isinstance(dates, list):
        raise ValueError("League calendar is missing game_days")
    return (today.isoformat() in dates
            or (current.hour < 3 and
                (today - timedelta(days=1)).isoformat() in dates)
            or bool(status.get("pending_recent", 0)))


def validate_freshness(league, timestamp, now=None, skip_age=False, limit_override=None):
    """Validate a UTC-aware update timestamp; use a tighter limit for NFL only."""
    if not isinstance(timestamp, str):
        raise ValueError("Missing updated_at timestamp")
    try:
        updated = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid updated_at timestamp") from exc
    if updated.tzinfo is None:
        raise ValueError("Timestamp lacks timezone")
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Reference time lacks timezone")
    age = (current - updated).total_seconds() / 60
    limit = limit_override or (NFL_MAX_AGE_MINUTES if league == "NFL" else MAX_AGE_MINUTES)
    if (not skip_age and age > limit) or age < -10:
        raise ValueError(f"Stale or future-dated {league} feed: {age:.0f} minutes old (limit {limit})")
    return age, limit

def check_feed(league, url):
    req = urllib.request.Request(url, headers={"User-Agent": "GamebookHealthCheck/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read(10_000_001)
        if len(payload) > 10_000_000:
            raise ValueError("Feed larger than 10MB")
    data = json.loads(payload)
    if not isinstance(data, dict) or not isinstance(data.get("games"), list):
        raise ValueError("Missing games array")
    if league == "NFL":
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from nfl_calendar import read_json, should_poll
        calendar = read_json(Path("nfl-calendar.json"))
        archive = read_json(Path("archive.json"))
        from nfl_pending import load_queue
        active = should_poll(datetime.now(timezone.utc), calendar, archive, pending=load_queue())
        if active:
            state = read_json(Path("monitor-state.json"))
            stamp = state.get("last_checked_at") or data.get("updated_at")
            age, limit = validate_freshness(league, stamp)
        else:
            age, limit = validate_freshness(
                league, data.get("updated_at"), skip_age=True
            )
    else:
        status_path, calendar_path = METADATA[league]
        status, calendar = read_metadata(status_path), read_metadata(calendar_path)
        active = polling_expected(calendar, status)
        if active:
            stamp = status.get("last_checked_at") or data.get("updated_at")
            age, limit = validate_freshness(
                league, stamp, limit_override=ACTIVE_LEAGUE_MAX_AGE_MINUTES
            )
        else:
            age, limit = validate_freshness(
                league, data.get("updated_at"), skip_age=True
            )
    games = data["games"]
    for i, game in enumerate(games):
        if not isinstance(game, dict) or not isinstance(game.get("date"), str):
            raise ValueError(f"Invalid game at index {i}")
    if active and data.get("offseason"):
        raise ValueError("League actively scheduled but feed is in offseason mode")
    if not data.get("offseason") and not games:
        raise ValueError("Active feed has zero games")
    print(f"PASS {league}: {len(games)} games; {age:.0f} min since last change/check; calendar_active={active}; offseason={bool(data.get('offseason'))}")

def main():
    failures = []
    for league, url in FEEDS.items():
        try:
            check_feed(league, url)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            failures.append(f"{league}: {exc}")
            print(f"FAIL {league}: {exc}", file=sys.stderr)
    if failures:
        print("HEALTH ALERT: " + " | ".join(failures), file=sys.stderr)
        sys.exit(1)
    print("PASS all five league feeds")

if __name__ == "__main__":
    main()
