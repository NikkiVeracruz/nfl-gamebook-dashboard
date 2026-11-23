#!/usr/bin/env python3
"""Independent 2026 schedule-to-archive completeness check for all five leagues.

Read-only. Never treats a successful HTTP response or a nonempty archive as
proof of full coverage. Each expected game is matched by its official game ID
(or, for NFL, its date and teams); delayed and inapplicable reports are distinct.
"""
import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ET=ZoneInfo("America/New_York")
START={
    "NFL":date(2026,8,1),
    "NBA":date(2026,1,1),
    "WNBA":date(2026,4,1),
    "NHL":date(2026,1,1),
    "MLB":date(2026,2,1),
}
URLS={
    "NFL":"https://raw.githubusercontent.com/NikkiVeracruz/nfl-gamebook-dashboard/main/archive.json",
    "NBA":"https://raw.githubusercontent.com/NikkiVeracruz/nba-gamebook-dashboard/main/archive.json",
    "WNBA":"https://raw.githubusercontent.com/NikkiVeracruz/nba-gamebook-dashboard/main/wnba/archive.json",
    "NHL":"https://raw.githubusercontent.com/NikkiVeracruz/nhl-gamebook-dashboard/main/archive.json",
    "MLB":"https://raw.githubusercontent.com/NikkiVeracruz/mlb-gamebook-dashboard/main/archive.json",
}
ESPN="https://site.api.espn.com/apis/site/v2/sports/"
MLB_API="https://statsapi.mlb.com/api/v1/schedule"
MLB_TYPES="S,R,F,D,L,W,A,E"
NHL_TYPES={"01","02","03","04"}


def normalize(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def nfl_archive_id(game):
    token=str(game.get("slug") or "")
    match=re.fullmatch(r"(.+)-at-(.+)-2026-(?:pre|reg|post)-\d+",token)
    if not match:return None
    return (game.get("date"),normalize(match.group(1)),normalize(match.group(2)))


def nfl_event_id(event, day):
    competitors=event.get("competitions") or []
    if not competitors:return None
    sides={}
    for item in competitors[0].get("competitors",[]):
        side=item.get("homeAway")
        name=(item.get("team") or {}).get("name")
        if side in ("home","away") and name:sides[side]=normalize(name)
    if not sides.get("home") or not sides.get("away"):
        raise ValueError(f"Invalid NFL team pairing on {day}")
    return (day.isoformat(),sides["away"],sides["home"])


def official_events(league,day,session=None):
    """A single day's independent schedule, with strict schema checks."""
    session=session or requests
    if league in ("NBA","WNBA","NFL"):
        sport={"NBA":"basketball/nba","WNBA":"basketball/wnba","NFL":"football/nfl"}[league]
        r=session.get(ESPN+sport+"/scoreboard",
                      params={"dates":day.strftime("%Y%m%d"),"limit":100},timeout=28)
        r.raise_for_status()
        events=r.json().get("events")
        if not isinstance(events,list):raise ValueError(f"{league} schedule malformed on {day}")
        rows=[]
        for e in events:
            if not isinstance(e,dict) or not e.get("date"):
                raise ValueError(f"{league} event malformed on {day}")
            utc=datetime.fromisoformat(e["date"].replace("Z","+00:00"))
            if utc.tzinfo is None:raise ValueError("Scoreboard event missing timezone")
            if utc.astimezone(ET).date()!=day:continue
            key=nfl_event_id(e,day) if league=="NFL" else str(e.get("id") or "")
            if not key:raise ValueError(f"{league}: missing official event identity on {day}")
            status=(e.get("status") or {}).get("type") or {}
            rows.append({"key":key,"date":day.isoformat(),
                         "completed":bool(status.get("completed")),
                         "status":status.get("description") or status.get("name") or ""})
        return rows
    if league=="NHL":
        r=session.get(f"https://api-web.nhle.com/v1/score/{day.isoformat()}",timeout=28)
        r.raise_for_status()
        games=r.json().get("games")
        if not isinstance(games,list):raise ValueError(f"NHL schedule malformed on {day}")
        rows=[]
        for g in games:
            token=str(g.get("id",""))
            if len(token)!=10 or not token.isdigit():raise ValueError("NHL event missing valid ID")
            if token[4:6] not in NHL_TYPES:continue
            rows.append({"key":token,"date":day.isoformat(),
                         "completed":str(g.get("gameState","")).upper() in ("OFF","FINAL")})
        return rows
    raise ValueError("MLB uses range queries")


def mlb_events(start,end,session=None):
    session=session or requests
    day=start
    result=[]
    while day<=end:
        last=min(day+timedelta(days=29),end)
        r=session.get(MLB_API,params={"sportId":1,"startDate":day.isoformat(),
                      "endDate":last.isoformat(),"gameTypes":MLB_TYPES},timeout=35)
        r.raise_for_status()
        blocks=r.json().get("dates")
        if not isinstance(blocks,list):raise ValueError("MLB range schedule malformed")
        for group in blocks:
            d=group.get("date")
            if not d or not(start.isoformat()<=d<=end.isoformat()):
                raise ValueError("MLB schedule returned unexpected date")
            for g in group.get("games",[]):
                identifier=g.get("gamePk")
                if not isinstance(identifier,int):raise ValueError("MLB game has no ID")
                result.append({"key":str(identifier),"date":d,
                               "completed":(g.get("status") or {}).get("abstractGameState")=="Final",
                               "game_type":g.get("gameType")})
        day=last+timedelta(days=1)
    return result


def nhl_weekly_events(start,end,session=None):
    """Official seven-day schedules, modest request rate and strict coverage."""
    import time
    session=session or requests
    found={}
    days_covered=set()
    cursor=start
    while cursor<=end:
        url=f"https://api-web.nhle.com/v1/schedule/{cursor.isoformat()}"
        response=None
        for attempt in range(5):
            response=session.get(url,timeout=35)
            if response.status_code in (429,500,502,503,504):
                time.sleep(min(12,2**attempt))
                continue
            response.raise_for_status()
            break
        else:
            raise RuntimeError(f"NHL schedule unavailable after retries: {cursor}")
        blocks=response.json().get("gameWeek")
        if not isinstance(blocks,list) or not blocks:
            raise ValueError(f"NHL weekly schedule missing gameWeek for {cursor}")
        for block in blocks:
            day=block.get("date")
            if not isinstance(day,str):
                raise ValueError("NHL weekly schedule block lacks date")
            if start.isoformat()<=day<=end.isoformat():
                days_covered.add(day)
                games=block.get("games")
                if not isinstance(games,list):
                    raise ValueError(f"NHL weekly schedule missing games on {day}")
                for g in games:
                    token=str(g.get("id",""))
                    if len(token)!=10 or not token.isdigit():
                        raise ValueError(f"NHL game has invalid ID on {day}")
                    if token[4:6] not in NHL_TYPES:continue
                    expected={
                        "key":token,"date":day,
                        "completed":str(g.get("gameState","")).upper() in ("OFF","FINAL")
                    }
                    if token in found and found[token]["date"]!=day:
                        raise ValueError(f"NHL game {token} appears on incompatible dates")
                    found[token]=expected
        # A five-day step overlaps the seven-day NHL response and avoids holes.
        cursor+=timedelta(days=5)
        time.sleep(0.4)
    wanted={(start+timedelta(days=i)).isoformat()
            for i in range((end-start).days+1)}
    if wanted-days_covered:
        raise ValueError(f"NHL weekly schedule failed to cover {len(wanted-days_covered)} dates, e.g. {sorted(wanted-days_covered)[:4]}")
    return list(found.values())


def expected_schedule(league,start,end,session=None,workers=6):
    if league=="MLB":return mlb_events(start,end,session)
    if league=="NHL":return nhl_weekly_events(start,end,session)
    dates=[]
    day=start
    while day<=end:
        dates.append(day)
        day+=timedelta(days=1)
    result=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(official_events,league,day,session):day for day in dates}
        for future in as_completed(futures):
            result.extend(future.result())
    return result


def classify_missing_report(league,game,event,today,verified_mlb_links=None):
    if not event["completed"]:return None
    game_day=date.fromisoformat(event["date"])
    age=(today-game_day).days
    if age<=2:return None
    if league in ("NFL","NBA","WNBA") and game.get("pdf_url"):return None
    if league=="NHL" and game.get("gs_url") and game.get("es_url"):return None
    if league=="MLB" and ((game.get("box_url") or game.get("boxscore_url"))
                            and (game.get("plays_url") or game.get("play_url"))):
        verified = (game.get("link_verification")=="verified_api" or
                    (verified_mlb_links or {}).get(str(game.get("id")))=="verified_api")
        return None if verified else "link_needs_independent_verification"
    if league=="NBA" and game.get("competition")=="nba_all_star":
        return "all_star_official_report_needs_review"
    if league=="WNBA" and game.get("competition") in ("wnba_exhibition","wnba_all_star"):
        return "special_event_official_report_needs_review"
    if league=="WNBA" and "JAPAN" in str(game.get("label","")).upper():
        return "exhibition_needs_review"
    if league=="NHL" and str(game.get("id",""))[4:6] in ("01","04"):
        return "preseason_or_special_event_needs_review"
    if league=="MLB" and event.get("game_type") in ("A","E"):
        return "special_game_needs_review"
    return "missing_required_report"


def audit_one(league,archive,events,today,verified_mlb_links=None):
    games=archive.get("games")
    if not isinstance(games,list):raise ValueError(f"{league} archive missing games list")
    seen={}
    for game in games:
        key=nfl_archive_id(game) if league=="NFL" else str(game.get("id") or "")
        if key is None and league=="NFL" and game.get("date","")>="2026-08-01":
            raise ValueError("Invalid NFL 2026 game identity")
        if not key:continue
        if key in seen:raise ValueError(f"{league} duplicate archive game identity {key}")
        seen[key]=game
    expected={}
    for event in events:
        key=event["key"]
        if key in expected and event["date"]==expected[key]["date"]:
            raise ValueError(f"{league} duplicate official game ID {key}")
        expected[key]=event
    missing=[e for key,e in expected.items() if key not in seen]
    gaps=[]
    for key,event in expected.items():
        if key not in seen:continue
        issue=classify_missing_report(league,seen[key],event,today,verified_mlb_links)
        if issue:gaps.append({"id":str(key),"date":event["date"],
                             "label":seen[key].get("label",""),"classification":issue})
    actual=[g for g in games if str(g.get("date",""))[:4]=="2026"]
    return {
        "league":league,
        "independently_expected_games":len(expected),
        "archived_2026_records":len(actual),
        "missing_game_count":len(missing),
        "missing_games":sorted(missing,key=lambda x:x["date"],reverse=True)[:80],
        "missing_report_count":sum(g["classification"]=="missing_required_report" for g in gaps),
        "review_or_unverified_count":sum(g["classification"]!="missing_required_report" for g in gaps),
        "report_findings":sorted(gaps,key=lambda x:x["date"],reverse=True)[:100],
        "non_nhl_international_preserved":(
            sum(str(g.get("id",""))[4:6]=="09" for g in games) if league=="NHL" else 0
        ),
    }


def load_archive(league,session=None):
    session=session or requests
    r=session.get(URLS[league],timeout=35)
    r.raise_for_status()
    return r.json()


def read_mlb_link_review(session=None):
    session=session or requests
    try:
        r=session.get(
            "https://raw.githubusercontent.com/NikkiVeracruz/mlb-gamebook-dashboard/main/link-review.json",
            timeout=20)
        r.raise_for_status()
        data=r.json()
        if data.get("validator_version")!=2:
            return {}
        return data.get("games",{}) if isinstance(data.get("games"),dict) else {}
    except (requests.RequestException, ValueError, TypeError):
        return {}


def run(scope="recent",session=None,today=None,archive_loader=None,schedule_loader=None):
    today=today or datetime.now(ET).date()
    session=session or requests
    result={"scope":scope,"date":today.isoformat(),"leagues":{}}
    for league in START:
        start=START[league] if scope=="full" else max(START[league],today-timedelta(days=10))
        end=today
        archive=archive_loader(league) if archive_loader else load_archive(league,session)
        expected=(schedule_loader(league,start,end) if schedule_loader else
                  expected_schedule(league,start,end,session))
        row=audit_one(league,archive,expected,today,
                      read_mlb_link_review(session) if league=="MLB" else None)
        row["checked_from"]=start.isoformat()
        row["checked_through"]=end.isoformat()
        result["leagues"][league]=row
        if row["missing_games"]:
            print(f"{league} MISSING ID EXAMPLES: "+
                  json.dumps(row["missing_games"][:15],ensure_ascii=False))
        if row["report_findings"]:
            print(f"{league} REPORT EXAMPLES: "+
                  json.dumps(row["report_findings"][:8],ensure_ascii=False))
        print(f"{league}: {row['independently_expected_games']} expected, "
              f"{row['missing_game_count']} missing games, "
              f"{row['missing_report_count']} overdue missing official reports, "
              f"{row['review_or_unverified_count']} needing further verification")
    return result


def has_failures(summary):
    return any(v["missing_game_count"] or v["missing_report_count"]
               for v in summary["leagues"].values())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--scope",choices=("recent","full"),default="recent")
    parser.add_argument("--output",default="coverage/season-check.json")
    args=parser.parse_args()
    result=run(scope=args.scope)
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as stream:
            stream.write("## Official 2026 game completeness ("+args.scope+")\n\n")
            stream.write("| League | Scheduled games | Missing games | Missing reports | Needs review |\n")
            stream.write("|---|---:|---:|---:|---:|\n")
            for l,g in result["leagues"].items():
                stream.write(f"| {l} | {g['independently_expected_games']} | "
                             f"{g['missing_game_count']} | {g['missing_report_count']} | "
                             f"{g['review_or_unverified_count']} |\n")
    if has_failures(result):
        sys.exit("COVERAGE FAILURE: missing game IDs or overdue official reports; review attached JSON.")
    print("PASS: no unexplained missing games or overdue required reports in independently checked schedules")


if __name__=="__main__":
    main()
