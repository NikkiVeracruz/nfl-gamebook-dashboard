#!/usr/bin/env python3
"""Read-only freshness decision for a separate NFL update watchdog.

The watchdog never starts workflows itself. The production Actions workflow
checks this script's output, verifies no update is already running or recently
dispatched, and only then requests the existing update.yml on main.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

MAX_AGE_MINUTES = 90  # Based on the throttled successful-poll heartbeat
FEED_URL = "https://raw.githubusercontent.com/NikkiVeracruz/nfl-gamebook-dashboard/main/gamebooks.json"


def read_feed(url=FEED_URL):
    req = urllib.request.Request(
        url, headers={"User-Agent": "NFLWatchdog/1.0", "Cache-Control": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        content = response.read(2_000_001)
    if len(content) > 2_000_000:
        raise ValueError("NFL feed exceeds 2 MB")
    return json.loads(content)


def decide(feed, now=None, last_checked_at=None):
    """Return (dispatch_needed, reason); never dispatch on invalid inputs."""
    if not isinstance(feed, dict) or not isinstance(feed.get("games"), list):
        raise ValueError("Invalid NFL feed; refusing automatic dispatch")
    if feed.get("offseason") is True:
        return False, "Offseason feed; no backup run needed"
    stamp = last_checked_at or feed.get("updated_at")
    if not isinstance(stamp, str):
        raise ValueError("Missing updated_at; refusing automatic dispatch")
    try:
        updated = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid updated_at; refusing automatic dispatch") from exc
    if updated.tzinfo is None:
        raise ValueError("Timezone missing from updated_at")
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Reference time requires timezone")
    age = (current - updated).total_seconds() / 60
    if age < -10:
        raise ValueError("NFL feed timestamp is in the future; investigate first")
    if age > MAX_AGE_MINUTES:
        return True, f"NFL publication is {age:.0f} minutes old; threshold {MAX_AGE_MINUTES}"
    return False, f"NFL publication is {age:.0f} minutes old; healthy"


def main():
    try:
        from pathlib import Path
        from nfl_calendar import should_poll
        current = datetime.now(timezone.utc)
        calendar = json.loads(Path("nfl-calendar.json").read_text())
        archive = json.loads(Path("archive.json").read_text())
        if not should_poll(current, calendar, archive):
            trigger, reason = False, "NFL idle: no scheduled game or overdue PDF"
        else:
            state = json.loads(Path("monitor-state.json").read_text())
            trigger, reason = decide(
                read_feed(), now=current,
                last_checked_at=state.get("last_checked_at"),
            )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"WATCHDOG ERROR: {exc}", file=sys.stderr)
        return 1
    print(("BACKUP UPDATE NEEDED: " if trigger else "NO BACKUP NEEDED: ") + reason)
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output:
            output.write(f"trigger={'true' if trigger else 'false'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
