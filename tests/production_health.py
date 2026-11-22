#!/usr/bin/env python3
"""Read-only production health probe for all five league feeds.
No files are written, no source workflows are triggered, and no archives are modified.
A failing probe makes the GitHub Actions run red for administrator notification.
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

MAX_AGE_MINUTES = 180
FEEDS = {
    "NFL": "https://nikkiveracruz.github.io/nfl-gamebook-dashboard/gamebooks.json",
    "NBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/gamebooks.json",
    "WNBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/wnba/gamebooks.json",
    "NHL": "https://nikkiveracruz.github.io/nhl-gamebook-dashboard/gamebooks.json",
    "MLB": "https://nikkiveracruz.github.io/mlb-gamebook-dashboard/gamebooks.json",
}

def check_feed(league, url):
    req = urllib.request.Request(url, headers={"User-Agent": "GamebookHealthCheck/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read(10_000_001)
        if len(payload) > 10_000_000:
            raise ValueError("Feed larger than 10MB")
    data = json.loads(payload)
    if not isinstance(data, dict) or not isinstance(data.get("games"), list):
        raise ValueError("Missing games array")
    stamp = data.get("updated_at")
    if not isinstance(stamp, str):
        raise ValueError("Missing updated_at timestamp")
    updated = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if updated.tzinfo is None:
        raise ValueError("Timestamp lacks timezone")
    age = (datetime.now(timezone.utc) - updated).total_seconds() / 60
    if age > MAX_AGE_MINUTES or age < -10:
        raise ValueError(f"Stale or future-dated feed: {age:.0f} minutes old (limit {MAX_AGE_MINUTES})")
    games = data["games"]
    for i, game in enumerate(games):
        if not isinstance(game, dict) or not isinstance(game.get("date"), str):
            raise ValueError(f"Invalid game at index {i}")
    if not data.get("offseason") and not games:
        raise ValueError("Active feed has zero games")
    print(f"PASS {league}: {len(games)} games; {age:.0f} min old; offseason={bool(data.get('offseason'))}")

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
