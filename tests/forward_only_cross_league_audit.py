#!/usr/bin/env python3
"""Read-only forward-only policy audit for all five active archives.

Never rewrites games. Scheduled/live fixtures remain allowed in current feeds.
Only archives are required to contain fully documented completed games.
"""
import json
import sys
import urllib.request

ROOT = "https://raw.githubusercontent.com/NikkiVeracruz/"
ARCHIVES = {
    "NFL": ("nfl-gamebook-dashboard", "archive.json", "2026-11-19"),
    "NBA": ("nba-gamebook-dashboard", "archive.json", "2026-11-22"),
    "WNBA": ("nba-gamebook-dashboard", "wnba/archive.json", "2026-11-22"),
    "NHL": ("nhl-gamebook-dashboard", "archive.json", "2026-11-22"),
    "MLB": ("mlb-gamebook-dashboard", "archive.json", "2026-11-22"),
}
BACKFILL = {
    "NFL": ("nfl-gamebook-dashboard", ".github/workflows/backfill.yml"),
    "NBA": ("nba-gamebook-dashboard", ".github/workflows/backfill.yml"),
    "WNBA": ("nba-gamebook-dashboard", ".github/workflows/wnba-backfill.yml"),
    "NHL": ("nhl-gamebook-dashboard", ".github/workflows/backfill.yml"),
    "MLB": ("mlb-gamebook-dashboard", ".github/workflows/backfill.yml"),
}


def get_text(repo, path):
    url = ROOT + repo + "/main/" + path
    req = urllib.request.Request(
        url, headers={"User-Agent": "ForwardOnlyGamebookAudit/1.0",
                      "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = r.read(12_000_001)
    if len(data) > 12_000_000:
        raise ValueError(f"{repo}/{path}: implausibly large response")
    return data.decode("utf-8")


def complete(game, league):
    s = str(game.get("status", "")).lower()
    if league == "NFL":
        return bool(game.get("pdf_url") and
                    (not s or "final" in s or s == "completed"))
    if league in ("NBA", "WNBA"):
        return "final" in s and bool(game.get("pdf_url"))
    if league == "NHL":
        return s in ("off", "final") and bool(game.get("gs_url") and game.get("es_url"))
    if league == "MLB":
        return ("final" in s and game.get("link_verification") == "verified_api"
                and bool(game.get("box_url") and game.get("plays_url")))
    raise ValueError(league)


def audit(league, payload, start):
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError(f"{league}: archive malformed")
    keys = set()
    for g in payload["games"]:
        if not isinstance(g, dict):
            raise ValueError(f"{league}: malformed game record")
        ident = g.get("slug") if league == "NFL" else g.get("id")
        if not ident or str(ident) in keys:
            raise ValueError(f"{league}: absent/duplicate game identity {ident}")
        keys.add(str(ident))
        if not isinstance(g.get("date"), str) or g["date"] < start:
            raise ValueError(f"{league}: old out-of-scope game retained: {ident}")
        if not complete(g, league):
            raise ValueError(f"{league}: incomplete or unverified game retained: {ident}")
    return len(keys)


def run():
    results = {}
    failures = []
    for league, (repo, path, start) in ARCHIVES.items():
        try:
            obj = json.loads(get_text(repo, path))
            results[league] = audit(league, obj, start)
            wf_repo, wf_path = BACKFILL[league]
            yaml = get_text(wf_repo, wf_path)
            if "ENABLE_HISTORICAL_BACKFILL" not in yaml:
                raise ValueError("Historical backfill workflow missing manual guard")
            if "\n  schedule:" in yaml:
                raise ValueError("Historical backfill still has an automatic schedule")
            print(f"PASS {league}: {results[league]} complete forward-only games; historical backfill suspended")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            failures.append(f"{league}: {exc}")
    if failures:
        print("FORWARD_ONLY_AUDIT_FAILED: " + " | ".join(failures), file=sys.stderr)
        return 1
    print("PASS all five archives: forward-only complete reports enforced; current feeds untouched")
    return 0


if __name__ == "__main__":
    sys.exit(run())
