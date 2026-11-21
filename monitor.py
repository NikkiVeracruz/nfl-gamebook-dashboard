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

def main():
    logging.basicConfig(level=logging.INFO,format="%(levelname)s %(message)s")
    # Seasonal guard: keep the website live but avoid report scraping in the offseason.
    # Broad calendar boundaries allow preseason and late postseason games; the
    # schedule source itself determines which games actually appear.
    if datetime.now(ET).month not in [7,8,9,10,11,12,1,2,3]:
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
    for slug,game in games.items():
        old=previous.get(slug,{})
        if old.get("pdf_url") and is_official(old["pdf_url"]) and verify_pdf(session,old["pdf_url"]):
            game["pdf_url"]=old["pdf_url"];continue
        try:
            html=get(session,game["game_url"]+"?tab=recap")
            text=BeautifulSoup(html,"html.parser").get_text(" ",strip=True)
            if not re.search(r"\\bFinal(?:/OT|/\\dOT)?\\b",text,re.I):continue
            pdf=gamebook_link(html,game["game_url"])
            if pdf and verify_pdf(session,pdf):
                game["pdf_url"]=pdf
                if slug not in state["notified"] and send_email(game):
                    state["notified"][slug]=datetime.now(timezone.utc).isoformat()
        except requests.RequestException as e:LOG.warning("Game page fetch failed %s: %s",slug,e)
    # Prevent state from growing indefinitely.
    state["notified"]={slug:ts for slug,ts in state["notified"].items() if slug in games}
    STATE.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    OUT.write_text(json.dumps({"window_label":f"{start:%b %d, %Y} – {(end-timedelta(days=1)):%b %d, %Y} (ET)","updated_at":datetime.now(timezone.utc).isoformat(),"games":sorted(games.values(),key=lambda g:(g["date"],g["label"]))},indent=2)+"\n")
    if not games:LOG.warning("No games discovered. Check NFL schedule markup before relying on this monitor.")

if __name__=="__main__":main()
