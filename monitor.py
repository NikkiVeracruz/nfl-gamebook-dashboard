#!/usr/bin/env python3
"""Publish a Thursday-to-Thursday dashboard of NFL.com gamebook PDF links."""
import json, os, re, logging, smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

BASE="https://www.nfl.com"
STATE=Path("monitor-state.json")
OUT=Path("gamebooks.json")
ET=ZoneInfo("America/New_York")
LOG=logging.getLogger("nfl-gamebooks")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; NFLGamebookDashboard/1.0)","Accept":"text/html,application/pdf,*/*"}
MONTHS="January February March April May June July August September October November December".split()
TEAM_WORDS={"ari":"Arizona Cardinals","atl":"Atlanta Falcons","bal":"Baltimore Ravens","buf":"Buffalo Bills","car":"Carolina Panthers","chi":"Chicago Bears","cin":"Cincinnati Bengals","cle":"Cleveland Browns","dal":"Dallas Cowboys","den":"Denver Broncos","det":"Detroit Lions","gb":"Green Bay Packers","hou":"Houston Texans","ind":"Indianapolis Colts","jax":"Jacksonville Jaguars","kc":"Kansas City Chiefs","lv":"Las Vegas Raiders","lac":"Los Angeles Chargers","lar":"Los Angeles Rams","mia":"Miami Dolphins","min":"Minnesota Vikings","ne":"New England Patriots","no":"New Orleans Saints","nyg":"New York Giants","nyj":"New York Jets","phi":"Philadelphia Eagles","pit":"Pittsburgh Steelers","sf":"San Francisco 49ers","sea":"Seattle Seahawks","tb":"Tampa Bay Buccaneers","ten":"Tennessee Titans","was":"Washington Commanders"}

def window():
    today=datetime.now(ET).date()
    start=today-timedelta(days=(today.weekday()-3)%7)
    return start,start+timedelta(days=7)

def load_state():
    try:return json.loads(STATE.read_text())
    except (FileNotFoundError,ValueError):return {"notified":{}}

def record_heartbeat(state, now=None):
    """Record a successful NFL poll at most once per 40 minutes, not every run."""
    current = now or datetime.now(timezone.utc)
    previous = state.get("last_checked_at")
    try:
        parsed = datetime.fromisoformat(str(previous).replace("Z", "+00:00"))
        if parsed.tzinfo and timedelta(0) <= current - parsed < timedelta(minutes=40):
            return False
    except ValueError:
        pass
    state["last_checked_at"] = current.isoformat()
    return True


def get(session,url):
    r=session.get(url,timeout=25)
    r.raise_for_status()
    return r.text

def parse_date(text,season):
    m=re.search(r"\b("+"|".join(MONTHS)+r")\s+(\d{1,2})(?:,?\s+(20\d{2}))?",text,re.I)
    if not m:return None
    month=next(i for i,x in enumerate(MONTHS,1) if x.lower()==m.group(1).lower())
    year=int(m.group(3)) if m.group(3) else season+(month<=2)
    try:return datetime(year,month,int(m.group(2))).date().isoformat()
    except ValueError:return None

def discover(session,season,start,end):
    games={}
    start_date=datetime.fromisoformat(start).date()
    end_date=datetime.fromisoformat(end).date()
    phases=[f"PRE{i}" for i in range(1,4)]+[f"REG{i}" for i in range(1,19)]+[f"POST{i}" for i in range(1,5)]
    # Scan the full season to avoid relying on an assumed NFL week number.
    for phase in phases:
        url=f"{BASE}/schedules/{season}/{phase}"
        try:html=get(session,url)
        except requests.RequestException as e:
            LOG.warning("Schedule fetch failed %s: %s",url,e);continue
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.select('a[href*="/games/"]'):
            link=urljoin(BASE,a.get("href","").split("?")[0])
            if urlparse(link).hostname not in ("www.nfl.com","nfl.com"):continue
            slug=urlparse(link).path.rstrip("/").split("/")[-1]
            if not slug:continue
            # Some schedule pages expose links from other seasons beside a
            # nearby date. Never relabel a 2026 game as a 2025 game.
            slug_season=re.search(r"-(20\d{2})-(?:pre|reg|post)-\d+$",slug,re.I)
            if slug_season and int(slug_season.group(1))!=season:continue
            texts=[a.get_text(" ",strip=True)]
            node=a
            for _ in range(5):
                node=node.parent
                if node is None:break
                txt=node.get_text(" ",strip=True)
                if txt and len(txt)<1200:texts.append(txt)
            date=next((d for t in texts if (d:=parse_date(t,season))),None)
            if not date or not (start<=date<end):continue
            label=a.get("aria-label") or a.get_text(" ",strip=True)
            if not label or len(label)>100:label=slug.replace("-"," ").title()
            games[slug]={"slug":slug,"date":date,"label":label[:140],"game_url":link}
    # NFL's by-week schedule uses a different page structure from REG pages.
    # Scan adjacent weeks too: the Thursday-to-Thursday window can cross weeks.
    kickoff=datetime(season,9,4).date()
    kickoff+=timedelta(days=(3-kickoff.weekday())%7)
    current_week=max(1,min(18,((start_date-kickoff).days//7)+1))
    last_week=max(1,min(18,(((end_date-timedelta(days=1))-kickoff).days//7)+1))
    # A historical backfill spans up to 28 days, not the single-week live window.
    # Include both ends of the requested interval, plus adjacent schedule weeks.
    for week in range(max(1,current_week-1),min(18,last_week+1)+1):
        url=f"{BASE}/schedules/{season}/by-week/week-{week}"
        try:html=get(session,url)
        except requests.RequestException as e:
            LOG.warning("By-week schedule fetch failed %s: %s",url,e)
            continue
        soup=BeautifulSoup(html,"html.parser")
        for a in soup.select('a[href*="/games/"]'):
            link=urljoin(BASE,a.get("href","").split("?")[0])
            if urlparse(link).hostname not in ("www.nfl.com","nfl.com"):continue
            slug=urlparse(link).path.rstrip("/").split("/")[-1]
            if not slug:continue
            # Some schedule pages expose links from other seasons beside a
            # nearby date. Never relabel a 2026 game as a 2025 game.
            slug_season=re.search(r"-(20\d{2})-(?:pre|reg|post)-\d+$",slug,re.I)
            if slug_season and int(slug_season.group(1))!=season:continue
            texts=[a.get_text(" ",strip=True)]
            node=a
            for _ in range(6):
                node=node.parent
                if node is None:break
                txt=node.get_text(" ",strip=True)
                if txt and len(txt)<1200:texts.append(txt)
            date=next((d for t in texts if (d:=parse_date(t,season))),None)
            if not date or not (start<=date<end):continue
            label=a.get("aria-label") or a.get_text(" ",strip=True)
            if not label or len(label)>100:label=slug.replace("-"," ").title()
            games[slug]={"slug":slug,"date":date,"label":label[:140],"game_url":link}
    # NFL preseason games use separate public by-week pages; the legacy
    # PRE1/PRE2/PRE3 URL guesses can silently omit games. Include the
    # Hall of Fame (pre-0) as well as all three preseason weeks.
    preseason_start=datetime(season,8,1).date()
    preseason_end=datetime(season,9,9).date()
    if start_date<preseason_end and end_date>preseason_start:
        sources=[("hall-of-fame-game",0)]+[
            (f"preseason-week-{i}",i) for i in range(1,4)
        ]
        for page_name,week in sources:
            url=f"{BASE}/schedules/{season}/by-week/{page_name}"
            try:html=get(session,url)
            except requests.RequestException as e:
                LOG.warning("Preseason schedule fetch failed %s: %s",url,e)
                continue
            soup=BeautifulSoup(html,"html.parser")
            for a in soup.select('a[href*="/games/"]'):
                link=urljoin(BASE,a.get("href","").split("?")[0])
                if urlparse(link).hostname not in ("www.nfl.com","nfl.com"):
                    continue
                slug=urlparse(link).path.rstrip("/").split("/")[-1]
                # Limit to the correct season AND page week; otherwise
                # neighboring navigation games can acquire the wrong date.
                if not slug.endswith(f"-{season}-pre-{week}"):
                    continue
                texts=[a.get_text(" ",strip=True)]
                node=a
                for _ in range(6):
                    node=node.parent
                    if node is None:break
                    txt=node.get_text(" ",strip=True)
                    if txt and len(txt)<1200:texts.append(txt)
                day=next((d for t in texts if (d:=parse_date(t,season))),None)
                if not day or not (start<=day<end):
                    continue
                label=a.get("aria-label") or a.get_text(" ",strip=True)
                if not label or len(label)>100:
                    label=slug.replace("-"," ").title()
                games[slug]={"slug":slug,"date":day,"label":label[:140],"game_url":link}
    return games

def gamebook_link(html,page):
    soup=BeautifulSoup(html,"html.parser")
    for a in soup.select("a[href]"):
        label=(a.get_text(" ",strip=True)+" "+a.get("aria-label","")).lower()
        href=urljoin(page,a["href"])
        if ("gamebook" in label or "game book" in label) and ".pdf" in href.lower():
            if is_official(href):return href
    # Do not use generic page-data PDFs: NFL embeds unrelated gamebook URLs.
    return None

def is_official(url):
    parsed=urlparse(url)
    return parsed.scheme=="https" and parsed.hostname in ("static.www.nfl.com","www.nfl.com","nfl.com")

def verify_pdf(session,url):
    try:
        r=session.get(url,timeout=35,headers={"Range":"bytes=0-15"},stream=True)
        r.raise_for_status()
        return next(r.iter_content(16),b"").startswith(b"%PDF-")
    except (requests.RequestException,StopIteration):return False

def send_email(game):
    host=os.getenv("SMTP_HOST");user=os.getenv("SMTP_USER")
    password=os.getenv("SMTP_PASSWORD");recipient=os.getenv("NOTIFY_EMAIL")
    if not all((host,user,password,recipient)):return False
    msg=EmailMessage()
    msg["Subject"]="NFL gamebook available: "+game["label"]
    msg["From"]=user;msg["To"]=recipient
    msg.set_content("Official NFL gamebook published:\n"+game["label"]+"\n"+game["pdf_url"]+"\n\nDashboard: https://nikkiveracruz.github.io/nfl-gamebook-dashboard/")
    try:
        with smtplib.SMTP(host,int(os.getenv("SMTP_PORT","587")),timeout=30) as server:
            server.starttls();server.login(user,password);server.send_message(msg)
        return True
    except Exception:
        LOG.exception("Notification failed");return False

def recover_older_missing_pdfs(session, start):
    """Continue checking unsatisfied gamebooks even after Thursday's window rolls."""
    from archive import load_payload, atomic_write_json
    from nfl_calendar import missing_pdf_games

    path = Path("archive.json")
    archived = load_payload(path, "NFL historical archive")
    today = datetime.now(ET).date()
    found = 0
    for game in missing_pdf_games(archived, today):
        # Current-week games are checked by the normal live loop.
        if game["date"] >= start.isoformat():
            continue
        try:
            url = game["game_url"]
            html = get(session, url + "?tab=recap")
            pdf = gamebook_link(html, url)
            if pdf and verify_pdf(session, pdf):
                game["pdf_url"] = pdf
                found += 1
                LOG.info("Recovered overdue NFL gamebook: %s", game["slug"])
        except requests.RequestException as exc:
            LOG.warning("Historical NFL gamebook fetch failed %s: %s",
                        game["slug"], exc)
    if found:
        archived["updated_at"] = datetime.now(timezone.utc).isoformat()
        atomic_write_json(path, archived)
    return found


def main():
    logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
    # Seasonal guard: keep the website live but avoid report scraping in the offseason.
    # Broad calendar boundaries allow preseason and late postseason games; the
    # schedule source itself determines which games actually appear.
    if datetime.now(ET).month not in [8,9,10,11,12,1,2]:
        now = datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps({"window_label": "Offseason", "updated_at": now, "offseason": True, "games": []}, indent=2) + "\n")
        LOG.info("Offseason: skipping gamebook checks")
        return

    session=requests.Session();session.headers.update(HEADERS)
    start,end=window();state=load_state()
    # Week resets every Thursday (Eastern Time), retaining no old dashboard entries.
    season=start.year if start.month>=3 else start.year-1
    games=discover(session,season,start.isoformat(),end.isoformat())
    LOG.info("Found %d scheduled games for %s to %s",len(games),start,end)
    previous={}
    try:
        prior=json.loads(OUT.read_text())
        previous={g["slug"]:g for g in prior.get("games",[]) if g.get("slug")}
    except (FileNotFoundError,ValueError):pass
    # A temporary schedule scrape failure must not erase known games.
    missing_from_source = [slug for slug,old in previous.items() if start.isoformat() <= old.get("date","") < end.isoformat() and slug not in games]
    if missing_from_source:
        LOG.warning("SCHEDULE COMPLETENESS ALERT: %d previously known NFL games absent from discovery: %s", len(missing_from_source), ", ".join(missing_from_source))
    for slug,old in previous.items():
        if start.isoformat()<=old.get("date","")<end.isoformat() and slug not in games:
            games[slug]=old.copy()
    for slug,game in games.items():
        old=previous.get(slug,{})
        if old.get("pdf_url") and is_official(old["pdf_url"]) and verify_pdf(session,old["pdf_url"]):
            game["pdf_url"]=old["pdf_url"];continue
        try:
            html=get(session,game["game_url"]+"?tab=recap")
            text=BeautifulSoup(html,"html.parser").get_text(" ",strip=True)
            # A verified official PDF is sufficient; NFL pages may say Watch Replay instead of Final.
            pdf=gamebook_link(html,game["game_url"])
            if pdf and verify_pdf(session,pdf):
                game["pdf_url"]=pdf
                if slug not in state["notified"] and send_email(game):
                    state["notified"][slug]=datetime.now(timezone.utc).isoformat()
        except requests.RequestException as e:LOG.warning("Game page fetch failed %s: %s",slug,e)
    # The current Thursday-to-Thursday feed must stay current-week only.
    # Missing gamebooks from earlier weeks are recovered directly into the archive.
    recover_older_missing_pdfs(session, start)
    # Export a lightweight activity flag for the public freshness display.
    from nfl_calendar import missing_pdf_games
    state["pending_overdue_pdf"] = bool(missing_pdf_games(
        json.loads(Path("archive.json").read_text()), datetime.now(ET).date()
    ))
    # Prevent state from growing indefinitely.
    state["notified"]={slug:ts for slug,ts in state["notified"].items() if slug in games}
    record_heartbeat(state)
    STATE.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    payload={"window_label":f"{start:%b %d, %Y} – {(end-timedelta(days=1)):%b %d, %Y} (ET)","games":sorted(games.values(),key=lambda g:(g["date"],g["label"]))}
    try:
        prior_feed=json.loads(OUT.read_text())
    except (OSError,ValueError):
        prior_feed={}
    if any(prior_feed.get(key)!=value for key,value in payload.items()):
        payload["updated_at"]=datetime.now(timezone.utc).isoformat()
        OUT.write_text(json.dumps(payload,indent=2)+"\n")
    else:
        LOG.info("NFL live feed unchanged; skipping timestamp-only write")
    if not games:LOG.warning("No games discovered. Check NFL schedule markup before relying on this monitor.")

if __name__=="__main__":main()
