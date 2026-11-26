"""Known-game recovery outside the display window; never a historical backfill."""
import json, re, io
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
CUTOFF = "2026-11-19"
SLUG = re.compile(r"^([a-z0-9-]+)-at-([a-z0-9-]+)-(20\d{2})-(pre|reg|post)-(\d+)$")
API = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
# Exact already-tracked live record from a1ca3c084c70b6a201f1d72f79a07abc06c810a7.
# Rollover occurred before this repair; restore only its pending eligibility.
SEED = {"slug":"packers-at-rams-2026-reg-12","date":"2026-11-25",
        "label":"Packers at Rams, Wednesday, November 25th, 8:00 PM, NETFLIX",
        "game_url":"https://www.nfl.com/games/packers-at-rams-2026-reg-12"}

def known(game):
    slug = game.get("slug", "")
    return (isinstance(slug,str) and SLUG.fullmatch(slug)
            and game.get("game_url") == "https://www.nfl.com/games/" + slug
            and isinstance(game.get("date"),str) and game["date"] >= CUTOFF
            and re.fullmatch(r"\d{4}-\d{2}-\d{2}", game["date"]))

def pending_games(state, feed, archive):
    saved = {g["slug"] for g in archive["games"] if g.get("slug") and g.get("pdf_url")}
    saved.update(g["slug"] for g in feed["games"] if g.get("slug") and g.get("pdf_url"))
    old = state.get("pending_games", {})
    if not isinstance(old,dict) or any(not isinstance(g,dict) or not known(g) or k!=g["slug"] for k,g in old.items()):
        raise ValueError("Invalid NFL pending queue; refusing to lose unresolved games")
    result = dict(old)
    for g in [SEED, *feed["games"]]:
        if known(g) and not g.get("pdf_url") and g["slug"] not in saved:
            # Preserve independent final status/score observations on later no-op polls.
            result[g["slug"]] = {**result.get(g["slug"],{}), **g}
    return {k:g for k,g in result.items() if k not in saved and not g.get("pdf_url")}

def load_queue():
    state = json.loads(Path("monitor-state.json").read_text())
    feed = json.loads(Path("gamebooks.json").read_text())
    archive = json.loads(Path("archive.json").read_text())
    return pending_games(state,feed,archive)

def due_games(pending, today):
    return [g for g in pending.values() if g["date"] < today.isoformat()
            and g.get("status") not in ("Canceled","Cancelled","Postponed")]

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

def event_match(slug,event):
    m=SLUG.fullmatch(slug)
    if not m:return False
    sides={c.get("homeAway"):c.get("team",{}) for c in event.get("competitions",[{}])[0].get("competitors",[])}
    for side, word in (("away",m[1]),("home",m[2])):
        team=sides.get(side,{})
        if norm(word) not in {norm(team.get(k,"")) for k in ("name","shortDisplayName","displayName","abbreviation")}:
            return False
    season=event.get("season",{})
    if season.get("year") and str(season["year"])!=m[3]:return False
    if season.get("type") and str(season["type"])!={"pre":"1","reg":"2","post":"3"}[m[4]]:return False
    # NFL postseason week numbers may differ between sources; same-pair
    # ambiguities are rejected by the caller instead of guessing.
    return True

def read_board(session,day):
    r=session.get(API,params={"dates":day.replace("-",""),"limit":100},timeout=20)
    r.raise_for_status()
    events=r.json().get("events")
    if not isinstance(events,list) or len(events)>=100:raise ValueError("Incomplete ESPN scoreboard "+day)
    return [e for e in events if datetime.fromisoformat(e["date"].replace("Z","+00:00")).astimezone(ET).date().isoformat()==day]

def refresh_game(game,event):
    g=dict(game)
    typ=event.get("status",{}).get("type",{})
    state=typ.get("state")
    name=typ.get("name","")
    if "CANCEL" in name or "POSTPON" in name:
        g["status"]="Postponed" if "POSTPON" in name else "Canceled"
        return g
    if state=="post" and typ.get("completed") is True and "FINAL" in name:
        sides={c["homeAway"]:c for c in event["competitions"][0]["competitors"]}
        a,h=sides["away"],sides["home"]
        try: scores=[int(a["score"]),int(h["score"])]
        except (KeyError,TypeError,ValueError):return g
        if min(scores)<0:return g
        g.update(status="Final",away_score=scores[0],home_score=scores[1],
                 away_name=a["team"]["displayName"],home_name=h["team"]["displayName"],
                 label=f"Watch Replay, {a['team']['name']} {scores[0]}, {h['team']['name']} {scores[1]}, {date.fromisoformat(g['date']):%A, %B %d}")
    return g

def reconcile(games,observed,prior,boards,start,end):
    """Use independent exact matchup/day to recover observed NFL URLs with missing date labels."""
    out=dict(games)
    candidates={**observed,**{g["slug"]:g["game_url"] for g in prior.values() if known(g)}}
    for day,events in boards.items():
        for e in events:
            matches=[k for k in candidates if event_match(k,e)]
            existing=[k for k in matches if (k in prior and prior[k].get("date")==day) or (k in out and out[k].get("date")==day)]
            if len(existing)==1:matches=existing
            if len(matches)!=1:continue
            k=matches[0]
            old=out.get(k) or prior.get(k)
            # Only reconcile an observed link; do not relabel conflicting dates.
            if old and old.get("date")!=day:continue
            if not start<=day<end:continue
            g=old or {"slug":k,"date":day,"label":k.replace("-"," ").title(),"game_url":candidates[k]}
            out[k]=refresh_game(g,e)
    return out

def club_url(url):
    p=urlparse(url)
    return (p.scheme=="https" and p.netloc=="static.clubs.nfl.com"
            and re.fullmatch(r"/image/upload/packers/[A-Za-z0-9_-]+(?:\.pdf)?",p.path)
            and not p.query and not p.fragment)

def packers_page(game):
    m=SLUG.fullmatch(game.get("slug",""))
    if not m or m[4]!="reg" or "packers" not in (m[1],m[2]):return None
    return f"https://www.packers.com/game-day/{m[3]}/reg-week{m[5]}/{m[1]}-at-{m[2]}/"

def club_candidate(html,page):
    from bs4 import BeautifulSoup
    urls=set()
    for a in BeautifulSoup(html,"html.parser").select("a[href]"):
        label=a.get_text(" ",strip=True)+" "+a.get("aria-label","")
        url=urljoin(page,a["href"])
        if re.search(r"\bgame\s*book\b",label,re.I) and club_url(url):urls.add(url)
    return next(iter(urls)) if len(urls)==1 else None

def identity_text(text,game):
    if game.get("status")!="Final":return False
    d=date.fromisoformat(game["date"])
    if not re.search(rf"\b0?{d.month}/0?{d.day}/{d.year}\b",text):return False
    if "national football league game summary" not in " ".join(text.lower().split()):return False
    for side,role in (("away","VISITOR"),("home","HOME")):
        name=game.get(side+"_name")
        score=game.get(side+"_score")
        if not name or not isinstance(score,int):return False
        # Layout-preserving extraction keeps team name and quarter totals on
        # the same row. Fail closed rather than use an unrelated score.
        rows=re.findall(rf"(?im)^\s*{role}:\s*{re.escape(name)}\s+((?:\d+\s+)*\d+)\s*$",text)
        if len(rows)!=1 or int(rows[0].split()[-1])!=score:return False
    return True

def verify_club_pdf(session,url,game):
    if not club_url(url):return False
    try:
        from pypdf import PdfReader
        with session.get(url,timeout=(10,25),stream=True,allow_redirects=False) as r:
            if r.status_code!=200:return False
            raw=bytearray()
            for chunk in r.iter_content(65536):
                raw.extend(chunk)
                if len(raw)>16_000_000:return False
        if not raw.startswith(b"%PDF-"):return False
        reader=PdfReader(io.BytesIO(raw),strict=False)
        return bool(len(reader.pages)>0 and identity_text(reader.pages[0].extract_text(extraction_mode="layout") or "",game))
    except Exception as exc:
        import logging
        logging.getLogger("nfl-gamebooks").warning("Club PDF identity not verified for %s: %s",game.get("slug"),exc)
        return False
