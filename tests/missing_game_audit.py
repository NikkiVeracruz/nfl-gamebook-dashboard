#!/usr/bin/env python3
"""Read-only independent schedule completeness audit for all five dashboards.

Fetches published current feeds and independent official/ESPN schedule APIs.
Never modifies published data. Findings are potential discrepancies that require review.\nAny discrepancy or unavailable source fails the audit instead of showing a green check.
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
}
MAX_DAYS = 7

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "GamebookScheduleAudit/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def independent_games(league, day):
    if league == "MLB":
        # The dashboard stores MLB StatsAPI gamePk identifiers, not ESPN IDs.
        # Match the gameTypes filter used by the production MLB monitor.
        from urllib.parse import urlencode
        query = urlencode({"sportId": 1, "date": day, "gameTypes": "S,R,F,D,L,W,A,E"})
        data = fetch_json("https://statsapi.mlb.com/api/v1/schedule?" + query)
        dates = data.get("dates")
        if not isinstance(dates, list):
            raise ValueError("MLB schedule missing dates list")
        return {str(game["gamePk"]) for block in dates if isinstance(block, dict)
                for game in block.get("games", [])
                if isinstance(game, dict) and isinstance(game.get("gamePk"), int)}
    if league == "NHL":
        data = fetch_json("https://api-web.nhle.com/v1/score/" + day)
        games = data.get("games")
        if not isinstance(games, list):
            raise ValueError("NHL schedule missing games list")
        return {str(g["id"]) for g in games if isinstance(g, dict) and g.get("id")}
    url = "https://site.api.espn.com/apis/site/v2/sports/" + ESPN[league] + "/scoreboard?dates=" + day.replace("-", "") + "&limit=200"
    data = fetch_json(url)
    events = data.get("events")
    if not isinstance(events, list):
        raise ValueError("ESPN schedule missing events list")
    return {str(g["id"]) for g in events if isinstance(g, dict) and g.get("id")}

def audit(league, data):
    if not isinstance(data, dict) or not isinstance(data.get("games"), list):
        return ["invalid published games list"]
    if data.get("offseason"):
        print(f"SKIP {league}: offseason feed (no active schedule to compare)")
        return []
    games = data["games"]
    dates = sorted({g.get("date") for g in games
                    if isinstance(g, dict) and isinstance(g.get("date"), str)})
    if not dates:
        return ["active feed has no dated games; cannot establish completeness"]
    if len(dates) > MAX_DAYS:
        return [f"{len(dates)} dates in feed; audit limited to {MAX_DAYS} most recent dates"]
    issues = []
    for day in dates:
        day_games = [g for g in games if isinstance(g, dict) and g.get("date") == day]
        try:
            expected_ids = independent_games(league, day)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            issues.append(f"{day}: independent schedule unavailable ({exc}); inconclusive")
            continue
        if league == "NFL":
            # NFL dashboard keys are NFL.com slugs, not ESPN event IDs.
            # Do not compare incompatible identifiers or claim ID coverage.
            observed = len(day_games)
            expected = len(expected_ids)
            if observed != expected:
                issues.append(f"{day}: NFL count mismatch: published {observed}, independent {expected}; ID comparison unavailable (different identifier systems)")
            else:
                print(f"PASS NFL {day}: {observed}/{expected} games (COUNT ONLY; identifiers incompatible)")
            continue
        observed_ids = [str(g.get("id")) for g in day_games if g.get("id")]
        observed_set = set(observed_ids)
        if len(observed_ids) != len(day_games):
            issues.append(f"{day}: {len(day_games)-len(observed_ids)} published games lack an ID")
        if len(observed_ids) != len(observed_set):
            issues.append(f"{day}: duplicate published game IDs detected")
        missing = sorted(expected_ids - observed_set)
        extra = sorted(observed_set - expected_ids)
        if missing:
            issues.append(f"{day}: POSSIBLE MISSING GAME IDS ({len(missing)}): {', '.join(missing[:25])}")
        if extra:
            issues.append(f"{day}: UNMATCHED PUBLISHED GAME IDS ({len(extra)}): {', '.join(extra[:25])}")
        if not missing and not extra and len(observed_ids) == len(observed_set) == len(day_games):
            print(f"PASS {league} {day}: {len(observed_set)} game IDs match independent schedule")
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
            print(f"PASS {league}: no detectable schedule discrepancy")
    if warnings:
        for warning in warnings:
            print("AUDIT WARNING: " + warning)
        print(f"Audit finished with {len(warnings)} findings. Manual review required; no data changed.")\n        sys.exit(1)
    else:
        print("Audit finished without detected discrepancies. NFL remains count-only; offseason leagues were not checked.")

if __name__ == "__main__":
    main()
