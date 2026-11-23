#!/usr/bin/env python3
"""Backfill NFL previous/current seasons up to four schedule weeks per run."""
import json,requests
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from monitor import discover,get,gamebook_link,is_official,verify_pdf,HEADERS
from archive import ArchiveIntegrityError, load_payload, atomic_write_json
ARCHIVE=Path("archive.json")
PROGRESS=Path("archive-progress.json")
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
ET = ZoneInfo("America/New_York")


def independent_sunday_games(session, day):
    """Count NFL events on a date using ESPN, separate from NFL.com scraping."""
    response = session.get(
        ESPN_SCOREBOARD, params={"dates": day.strftime("%Y%m%d"), "limit": 100},
        timeout=25,
    )
    response.raise_for_status()
    events = response.json().get("events")
    if not isinstance(events, list):
        raise ArchiveIntegrityError(f"Independent NFL schedule invalid for {day}")
    count = 0
    for event in events:
        if not isinstance(event, dict) or not isinstance(event.get("date"), str):
            raise ArchiveIntegrityError(f"Independent NFL game date missing for {day}")
        try:
            kickoff = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
            if kickoff.tzinfo is None:
                raise ValueError("Kickoff has no timezone")
        except ValueError as exc:
            raise ArchiveIntegrityError(f"Invalid independent NFL kickoff for {day}") from exc
        if kickoff.astimezone(ET).date() == day:
            count += 1
    return count


def validate_discovery(session, start, end, discovered, get_expected=independent_sunday_games, previous=None):
    """Require ESPN's Sunday count across unique newly discovered OR saved NFL games.

    A scheduled game that's already archived must not block a historical
    catch-up just because NFL.com temporarily fails to rediscover it.
    However a game missing from both sources still blocks cursor advancement.
    """
    from re import fullmatch
    prior = previous or {}
    sunday = start + timedelta(days=(6-start.weekday()) % 7)
    while sunday < end:
        expected = get_expected(session, sunday)
        retained = {}
        for game in list(discovered.values()) + list(prior.values()):
            slug = str(game.get("slug", ""))
            if game.get("date") != sunday.isoformat():
                continue
            # Never credit a game from a different season, or a malformed
            # record, toward the count for this Sunday.
            if not fullmatch(r".+-at-.+-20\\d{2}-(?:reg|pre|post)-\\d+", slug):
                continue
            if int(slug.rsplit("-", 3)[1]) != sunday.year:
                # January-February postseason belongs to prior NFL season.
                if not (sunday.month <= 2 and int(slug.rsplit("-", 3)[1]) == sunday.year - 1):
                    continue
            retained[slug] = game
        observed = len(retained)
        if observed < expected:
            raise ArchiveIntegrityError(
                f"NFL backfill incomplete for {sunday}: {len(discovered)} newly discovered "
                f"records in this window, {observed} distinct Sunday games including "
                f"already archived records, ESPN has {expected}; "
                "archive and progress cursor NOT advanced"
            )
        sunday += timedelta(days=7)


def main():
    existing=load_payload(ARCHIVE, "NFL historical archive")
    records={g.get("slug",g.get("date","")+"|"+g.get("label","")):g for g in existing.get("games",[])}
    p=json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    start=date.fromisoformat(p.get("next_date","2025-08-01"))
    end=min(start+timedelta(days=28),date.today()+timedelta(days=1))
    if start>=end:
        print("NFL archive backfill caught up")
        return
    session=requests.Session();session.headers.update(HEADERS)
    discovered={}
    for season in {start.year,start.year-1}:
        discovered.update(discover(session,season,start.isoformat(),end.isoformat()))
    validate_discovery(session,start,end,discovered,previous=records)
    for slug,g in discovered.items():
        old=records.get(slug,{})
        item={**old,**g}
        if not item.get("pdf_url") and g["date"]<=date.today().isoformat():
            try:
                html=get(session,g["game_url"]+"?tab=recap")
                url=gamebook_link(html,g["game_url"])
                if url and is_official(url) and verify_pdf(session,url):item["pdf_url"]=url
            except requests.RequestException as e:print("Gamebook lookup failed:",slug,e)
        records[slug]=item
    existing["games"]=sorted(records.values(),key=lambda g:(g.get("date",""),g.get("label","")),reverse=True)
    existing["updated_at"]=datetime.now(timezone.utc).isoformat()
    atomic_write_json(ARCHIVE, existing)
    atomic_write_json(PROGRESS, {"next_date":end.isoformat(),"complete":end>date.today(),"updated_at":existing["updated_at"]})
    print("NFL archive now contains",len(records),"games; next",end)
if __name__=="__main__":main()
