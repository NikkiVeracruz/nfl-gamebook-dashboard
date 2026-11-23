#!/usr/bin/env python3
"""Independent read-only audit of 2026 archived games across all five leagues.

Compares the union of archive/current records to independent league schedules.
Does not write game files or treat a link's appearance as evidence the report exists.
Missing games, malformed source responses and incomplete audits exit nonzero.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BASE = "https://raw.githubusercontent.com/NikkiVeracruz/"
REPOSITORIES = {
    "NFL": ("nfl-gamebook-dashboard", ""),
    "NBA": ("nba-gamebook-dashboard", ""),
    "WNBA": ("nba-gamebook-dashboard", "wnba/"),
    "NHL": ("nhl-gamebook-dashboard", ""),
    "MLB": ("mlb-gamebook-dashboard", ""),
}
ESPN = {"NFL": "football/nfl", "NBA": "basketball/nba", "WNBA": "basketball/wnba"}
START = {
    "NFL": date(2026, 8, 1),
    "NBA": date(2026, 1, 1),
    "WNBA": date(2026, 4, 1),
    "NHL": date(2026, 1, 1),
    "MLB": date(2026, 2, 1),
}
END = date(2026, 12, 31)
NHL_INTERNATIONAL = "international_hockey"
NFL_SLUG = re.compile(r"^(.+)-at-(.+)-2026-(?:pre|reg|post)-\d+$", re.I)


class AuditError(Exception):
    pass


def fetch_json(url):
    """Fail closed if a service cannot provide an independently usable response."""
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "IndependentGameArchiveAudit/2.0",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
            })
            with urllib.request.urlopen(req, timeout=25) as res:
                raw = res.read(24_000_001)
            if len(raw) > 24_000_000:
                raise AuditError("Response exceeds 24MB: " + url)
            return json.loads(raw)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last = exc
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))
    raise AuditError(f"Schedule/download unavailable after retries: {url}: {last}")


def each_day(start, end):
    while start <= end:
        yield start
        start += timedelta(days=1)


def source_url(repo, prefix, file):
    return BASE + repo + "/main/" + prefix + file


def archive_games(league):
    repo, prefix = REPOSITORIES[league]
    combined = {}
    for name in ("archive.json", "gamebooks.json"):
        payload = fetch_json(source_url(repo, prefix, name))
        if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
            raise AuditError(f"{league} {name}: invalid games list")
        within_file = set()
        for item in payload["games"]:
            if not isinstance(item, dict) or not isinstance(item.get("date"), str):
                raise AuditError(f"{league} {name}: invalid game/date")
            raw_id = item.get("slug") if league == "NFL" else item.get("id")
            if not raw_id:
                raise AuditError(f"{league} {name}: game without identity")
            key = str(raw_id)
            if key in within_file:
                raise AuditError(f"{league} {name}: duplicated game ID {key}")
            within_file.add(key)
            if key in combined:
                prev = combined[key]
                if prev["date"] != item["date"]:
                    raise AuditError(f"{league}: record {key} has conflicting dates")
                # Favor the record with richer verified links while leaving both source files untouched.
                if len(item) > len(prev):
                    combined[key] = item
            else:
                combined[key] = item
    return list(combined.values())


def normalized(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def nfl_archive_key(game):
    m = NFL_SLUG.fullmatch(str(game.get("slug", "")))
    if not m:
        raise AuditError("Unrecognized NFL 2026 slug " + str(game.get("slug")))
    return (game["date"], normalized(m.group(1)), normalized(m.group(2)))


def espn_day(league, day):
    q = urllib.parse.urlencode({"dates": day.strftime("%Y%m%d"), "limit": 500})
    url = "https://site.api.espn.com/apis/site/v2/sports/" + ESPN[league] + "/scoreboard?" + q
    payload = fetch_json(url)
    events = payload.get("events") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        raise AuditError(f"{league} {day}: ESPN returned no events list")
    ids = set()
    for event in events:
        if not isinstance(event, dict) or not event.get("id"):
            raise AuditError(f"{league} {day}: ESPN event missing ID")
        if league == "NFL":
            stamp = event.get("date")
            if not stamp:
                raise AuditError(f"ESPN NFL kickoff timestamp missing for {event['id']}")
            kickoff = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if kickoff.tzinfo is None:
                raise AuditError(f"ESPN NFL kickoff timezone missing for {event['id']}")
            if kickoff.astimezone(ET).date() != day:
                continue
            comps = event.get("competitions") or []
            sides = {}
            if comps:
                for c in comps[0].get("competitors", []):
                    if c.get("homeAway") in ("away", "home"):
                        sides[c["homeAway"]] = normalized((c.get("team") or {}).get("name"))
            if not sides.get("away") or not sides.get("home"):
                raise AuditError(f"ESPN NFL teams missing for {event['id']}")
            key = (day.isoformat(), sides["away"], sides["home"])
        else:
            key = str(event["id"])
        if key in ids:
            raise AuditError(f"{league} {day}: duplicated independent event {key}")
        ids.add(key)
    return ids


def nhl_week(day):
    payload = fetch_json("https://api-web.nhle.com/v1/schedule/" + day.isoformat())
    weeks = payload.get("gameWeek") if isinstance(payload, dict) else None
    if not isinstance(weeks, list):
        raise AuditError(f"NHL {day}: invalid official gameWeek")
    result = {}
    for block in weeks:
        if not isinstance(block, dict) or not isinstance(block.get("games"), list):
            raise AuditError(f"NHL {day}: malformed schedule day")
        block_day = block.get("date")
        if not isinstance(block_day, str):
            raise AuditError(f"NHL {day}: missing schedule date")
        result.setdefault(block_day, set())
        for game in block["games"]:
            if not isinstance(game, dict) or game.get("id") is None:
                raise AuditError(f"NHL {block_day}: missing official game ID")
            result.setdefault(block_day, set()).add(str(game["id"]))
    return result


def mlb_month(day, through):
    # Include All-Star and exhibitions; they were previously omitted.
    first = day.replace(day=1)
    if first.month == 12:
        end = first.replace(day=31)
    else:
        end = first.replace(month=first.month + 1, day=1) - timedelta(days=1)
    end = min(end, through)
    q = urllib.parse.urlencode({
        "sportId": 1, "startDate": first.isoformat(),
        "endDate": end.isoformat(), "gameTypes": "S,R,F,D,L,W,A,E",
    })
    payload = fetch_json("https://statsapi.mlb.com/api/v1/schedule?" + q)
    dates = payload.get("dates") if isinstance(payload, dict) else None
    if not isinstance(dates, list):
        raise AuditError(f"MLB {first}: invalid official schedule")
    result = {}
    for block in dates:
        if not isinstance(block, dict) or not isinstance(block.get("games"), list):
            raise AuditError(f"MLB {first}: malformed official schedule day")
        block_day = block.get("date")
        if not isinstance(block_day, str):
            raise AuditError(f"MLB {first}: missing official schedule date")
        for game in block["games"]:
            if not isinstance(game, dict) or game.get("gamePk") is None:
                raise AuditError(f"MLB {block_day}: missing official gamePk")
            result.setdefault(block_day, set()).add(str(game["gamePk"]))
    return result


def expected_games(league, through, workers=8):
    start = START[league]
    if through < start:
        return {}, 0
    jobs = []
    if league in ESPN:
        jobs = [(day, day) for day in each_day(start, through)]
        query = lambda day: {day.isoformat(): espn_day(league, day)}
    elif league == "NHL":
        jobs = [(day, day) for day in each_day(start, through) if (day - start).days % 7 == 0]
        query = nhl_week
    else:
        jobs = [(day, day) for day in each_day(start, through) if day.day == 1]
        # MLB starts February 1, so monthly boundaries align naturally.
        query = lambda day: mlb_month(day, through)
    output = {}
    errors = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(query, day): day for day, _ in jobs}
        for future in as_completed(futures):
            day = futures[future]
            try:
                group = future.result()
                if not isinstance(group, dict):
                    raise AuditError("Invalid source group")
                for block_day, ids in group.items():
                    if not isinstance(ids, set):
                        raise AuditError(f"{league} {block_day}: invalid schedule IDs")
                    if start.isoformat() <= block_day <= through.isoformat():
                        if block_day in output and output[block_day] != ids:
                            raise AuditError(f"{league} {block_day}: conflicting schedule results")
                        output[block_day] = ids
            except (AuditError, ValueError, TypeError, KeyError, OSError) as exc:
                errors.append(f"{day}: {exc}")
    if errors:
        raise AuditError(f"{league}: {len(errors)} source queries failed: " + " | ".join(errors[:6]))
    # A healthy service can return no fixtures on many days; completed queries still count.
    return output, len(jobs)


def compare(league, observed, expected, through):
    actual = {}
    duplicates = []
    for game in observed:
        game_day = game["date"]
        if not (START[league].isoformat() <= game_day <= through.isoformat()):
            continue
        key = nfl_archive_key(game) if league == "NFL" else str(game["id"])
        if key in actual:
            duplicates.append(str(key))
        actual[key] = game_day

    missing = []
    mismatched_dates = []
    rescheduled_for_review = []
    expected_keys = set()
    for day, ids in sorted(expected.items()):
        for key in ids:
            expected_keys.add(key)
            if key not in actual:
                missing.append((day, str(key)))
            elif actual[key] != day:
                different_date = (day, str(key), actual[key])
                if league == "MLB":
                    # Postponed/suspended games legitimately retain official gamePk
                    # while moving to their actual play date. Flag for review,
                    # not as an absent game or destructive archive correction.
                    rescheduled_for_review.append(different_date)
                else:
                    mismatched_dates.append(different_date)

    # Unmatched archive records might be valid special events or source omissions:
    # report them for review rather than erasing records or declaring them fabricated.
    unmatched = [str(key) for key in actual if key not in expected_keys]
    return {
        "independent_games": len(expected_keys),
        "stored_2026_games": len(actual),
        "missing": sorted(missing),
        "date_mismatches": sorted(mismatched_dates),
        "rescheduled_dates_for_review": sorted(rescheduled_for_review),
        "duplicate_ids": sorted(duplicates),
        "extra_for_review": sorted(unmatched),
    }


def run(now=None, leagues=None, workers=8):
    now = now or datetime.now(timezone.utc)
    through = min(now.astimezone(ET).date() - timedelta(days=1), END)
    selected = leagues or list(REPOSITORIES)
    failures = []
    for league in selected:
        try:
            stored = archive_games(league)
            scheduled, checked = expected_games(league, through, workers)
            if not checked:
                raise AuditError(f"No {league} schedule queries were executed")
            report = compare(league, stored, scheduled, through)
            if (report["stored_2026_games"] >= 30 and
                    report["independent_games"] < report["stored_2026_games"] // 2):
                raise AuditError(
                    f"{league}: independent schedule implausibly incomplete: "
                    f"{report['independent_games']} IDs vs "
                    f"{report['stored_2026_games']} archived/current games"
                )
            print(json.dumps({
                "league": league, "through": through.isoformat(),
                "days_or_weeks_queried": checked,
                "independent_source": "ESPN" if league in ESPN else league + " official API",
                **{key: len(value) if isinstance(value, list) else value
                   for key, value in report.items()},
                "missing_samples": report["missing"][:15],
                "date_mismatch_samples": report["date_mismatches"][:15],
                "rescheduled_samples": report["rescheduled_dates_for_review"][:15],
                "duplicate_samples": report["duplicate_ids"][:15],
            }, sort_keys=True), flush=True)
            if report["missing"] or report["duplicate_ids"] or report["date_mismatches"]:
                failures.append(f"{league}: missing={len(report['missing'])}, "
                                f"duplicates={len(report['duplicate_ids'])}, "
                                f"date mismatches={len(report['date_mismatches'])}")
        except (AuditError, OSError, ValueError, TypeError, KeyError) as exc:
            failures.append(f"{league}: INCONCLUSIVE audit: {exc}")
            print("AUDIT INCONCLUSIVE: " + str(exc), file=sys.stderr, flush=True)
    if failures:
        print("ARCHIVE AUDIT FAILED (no data changed): " + " | ".join(failures),
              file=sys.stderr)
        return 1
    print(f"PASS: independent 2026 schedule coverage confirmed through {through}; "
          "archive and current feeds were only read, never modified.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--league", choices=[*REPOSITORIES, "ALL"], default="ALL")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    selected = list(REPOSITORIES) if args.league == "ALL" else [args.league]
    sys.exit(run(leagues=selected, workers=max(1, min(12, args.workers))))


if __name__ == "__main__":
    main()
