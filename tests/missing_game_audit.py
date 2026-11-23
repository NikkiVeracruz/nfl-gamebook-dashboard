#!/usr/bin/env python3
"""Read-only independent schedule completeness audit for all five dashboards.

Fetches published current feeds and independent official/ESPN schedule APIs.
Never modifies published data. Findings are warnings, not proof of missing games.
"""
import json
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

FEEDS = {
    "NFL": "https://nikkiveracruz.github.io/nfl-gamebook-dashboard/gamebooks.json",
    "NBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/gamebooks.json",
    "WNBA": "https://nikkiveracruz.github.io/nba-gamebook-dashboard/wnba/gamebooks.json",
    "NHL": "https://nikkiveracruz.github.io/nhl-gamebook-dashboard/gamebooks.json",
    "MLB": "https://nikkiveracruz.github.io/mlb-gamebook-dashboard/gamebooks.json",
}
ESPN = {
    "NFL": "football/nfl",
    "NBA": "basketball/nba",
    "WNBA": "basketball/wnba",
    "MLB": "baseball/mlb",
}
MAX_DAYS = 7

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "GamebookScheduleAudit/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def independent_count(league, day):
    if league == "NHL":
        data = fetch_json("https://api-web.nhle.com/v1/score/" + day)
        games = data.get("games")
        if not isinstance(games, list):
            raise ValueError("NHL schedule missing games list")
        return len({str(g["id"]) for g in games if g.get("id")})
    url = "https://site.api.espn.com/apis/site/v2/sports/" + ESPN[league] + "/scoreboard?dates=" + day.replace("-", "") + "&limit=200"
    data = fetch_json(url)
    events = data.get("events")
    if not isinstance(events, list):
        raise ValueError("ESPN schedule missing events list")
    return len({str(g["id"]) for g in events if g.get("id")})

def audit(league, data):
    if not isinstance(data, dict) or not isinstance(data.get("games"), list):
        return ["invalid published games list"]
    if data.get("offseason"):
        return []
    games = data["games"]
    counts = Counter(g.get("date") for g in games if isinstance(g, dict) and isinstance(g.get("date"), str))
    if not counts:
        return ["active feed has no dated games; cannot establish completeness"]
    dates = sorted(counts)
    if len(dates) > MAX_DAYS:
        return [f"{len(dates)} dates in feed; audit limited to {MAX_DAYS} most recent dates"]
    issues = []
    for day in dates:
        try:
            expected = independent_count(league, day)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append(f"{day}: independent schedule unavailable ({exc}); inconclusive")
            continue
        observed = counts[day]
        if expected > observed:
            issues.append(f"{day}: POSSIBLE MISSING GAMES: published {observed}, independent schedule {expected}")
        elif observed > expected:
            issues.append(f"{day}: published {observed}, independent schedule {expected}; sources disagree")
        else:
            print(f"PASS {league} {day}: {observed}/{expected} scheduled games")
    return issues

def main():
    warnings = []
    for league, url in FEEDS.items():
        try:
            data = fetch_json(url)
            issues = audit(league, data)
        except (OSError, ValueError, TypeError) as exc:
            issues = [f"published feed unavailable ({exc})"]
        if issues:
            warnings.extend(f"{league}: {issue}" for issue in issues)
        else:
            print(f"PASS {league}: no schedule-count discrepancy detected")
    if warnings:
        for warning in warnings:
            print("AUDIT WARNING: " + warning)
        print(f"Audit finished with {len(warnings)} warnings. Manual review required; no data changed.")
    else:
        print("Audit finished without detected discrepancies. This does not prove full completeness.")

if __name__ == "__main__":
    main()
