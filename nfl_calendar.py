#!/usr/bin/env python3
"""Compile actual NFL game dates into GitHub Actions polls; skip inactive days."""
import argparse
import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ET = ZoneInfo("America/New_York")
API = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
CALENDAR = Path("nfl-calendar.json")
ARCHIVE = Path("archive.json")
FEED = Path("gamebooks.json")
WORKFLOW = Path(".github/workflows/update.yml")
BEGIN = "  # BEGIN NFL CALENDAR-MANAGED SCHEDULE"
END = "  # END NFL CALENDAR-MANAGED SCHEDULE"
HORIZON = 21


def start_of_season(today):
    year = today.year if today.month >= 8 else today.year - 1
    return date(year, 8, 1)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def missing_pdf_games(archive, today):
    """Past-season games without PDFs, including those outside the current week."""
    start = start_of_season(today)
    return [
        g for g in archive["games"]
        if g.get("slug") and "-20" in g["slug"]
        and start.isoformat() <= g.get("date", "") < today.isoformat()
        and not g.get("pdf_url")
        and g.get("game_url", "").startswith("https://www.nfl.com/games/")
    ]


def fetch_game_days(session, today, horizon=HORIZON):
    days = set()
    for offset in range(-1, horizon + 1):
        day = today + timedelta(days=offset)
        resp = session.get(
            API, params={"dates": day.strftime("%Y%m%d"), "limit": 100},
            timeout=30,
        )
        resp.raise_for_status()
        events = resp.json().get("events")
        if not isinstance(events, list):
            raise ValueError(f"Invalid NFL schedule on {day}; existing schedule preserved")
        for event in events:
            raw = event.get("date")
            if not isinstance(raw, str):
                raise ValueError(f"NFL game missing kickoff on {day}")
            kickoff = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if kickoff.tzinfo is None:
                raise ValueError(f"NFL kickoff lacks time zone on {day}")
            eastern_day = kickoff.astimezone(ET).date()
            if eastern_day == day:
                days.add(day)
    return days


def include_saved_dates(days, today, archive, feed):
    """A failed or late external schedule change may not erase known game dates."""
    cutoff = today + timedelta(days=HORIZON)
    for source in (archive, feed):
        for game in source["games"]:
            value = game.get("date", "")
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                day = date.fromisoformat(value)
                if today - timedelta(days=1) <= day <= cutoff:
                    days.add(day)
    return days


def schedule_windows(today, game_days, pending):
    """Full game days, 00:00-02:59 on following days, and missing-PDF extensions."""
    limit = today + timedelta(days=HORIZON)
    full = {d for d in game_days if today <= d <= limit}
    early = {
        d + timedelta(days=1) for d in game_days
        if today <= d + timedelta(days=1) <= limit
    }
    if pending:
        # Safeguard against a missed daily calendar refresh.
        full.update(today + timedelta(days=i) for i in range(4))
    early -= full
    return full, early


def compile_crons(full, early):
    """Group dates within months. Use New York local time and avoid DST offsets."""
    months = defaultdict(set)
    for hours, days in (("*", full), ("0-2", early)):
        for day in days:
            months[(day.year, day.month, hours)].add(day.day)
    lines = []
    for (_, month, hours), dates in sorted(months.items()):
        dom = ",".join(str(d) for d in sorted(dates))
        lines.extend([
            f'    - cron: "*/5 {hours} {dom} {month} *"',
            '      timezone: "America/New_York"',
        ])
    return lines


def update_workflow_text(text, full, early):
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("NFL schedule markers missing; refusing to rewrite workflow")
    b = text.index(BEGIN)
    e = text.index(END) + len(END)
    crons = compile_crons(full, early)
    schedule = "  schedule:\n" + "\n".join(crons) + "\n" if crons else ""
    generated = BEGIN + "\n" + schedule + END
    return text[:b] + generated + text[e:]


def should_poll(now, calendar, archive, manual=False, pending=None):
    if manual:
        return True
    today = now.astimezone(ET).date()
    days = {date.fromisoformat(x) for x in calendar["game_days"]}
    return (
        today in days
        or (now.astimezone(ET).hour < 3 and today - timedelta(days=1) in days)
        or bool(missing_pdf_games(archive, today))
        or bool(pending and __import__('nfl_pending').due_games(pending,today))
    )


def refresh(today=None, session=None):
    today = today or datetime.now(ET).date()
    archive, feed = read_json(ARCHIVE), read_json(FEED)
    if session is None:
        import requests
        session = requests.Session()
    days = fetch_game_days(session, today)
    days = include_saved_dates(days, today, archive, feed)
    from nfl_pending import load_queue, due_games
    pending = missing_pdf_games(archive, today) + due_games(load_queue(), today)
    full, early = schedule_windows(today, days, pending)
    calendar = {"game_days": sorted(d.isoformat() for d in days)}
    changed = not CALENDAR.exists() or read_json(CALENDAR) != calendar
    if changed:
        CALENDAR.write_text(json.dumps(calendar, indent=2) + "\n", encoding="utf-8")
    print(
        f"NFL calendar: {len(days)} game days, {len(pending)} missing PDFs; "
        f"next windows cover {len(full)} full days and {len(early)} overnights; "
        f"calendar {'updated' if changed else 'unchanged'}. "
        "The coordinator toggles GitHub Actions through the Actions API."
    )


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("command", choices=("refresh", "should-poll"))
    args = cli.parse_args()
    if args.command == "refresh":
        refresh()
    else:
        manual = os.getenv("NFL_FORCE_SCAN", "").lower() == "true"
        if not CALENDAR.exists():
            # Missing calendar should never silently suppress checks.
            raise SystemExit("Missing NFL calendar; refusing to silently skip monitoring")
        from nfl_pending import load_queue
        ok = should_poll(
            datetime.now(timezone.utc), read_json(CALENDAR),
            read_json(ARCHIVE), manual=manual, pending=load_queue()
        )
        print("NFL monitor " + ("ACTIVE" if ok else "IDLE: no scheduled or overdue PDFs"))
        raise SystemExit(0 if ok else 3)


if __name__ == "__main__":
    main()
