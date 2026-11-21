#!/usr/bin/env python3
"""Bounded, conservative discovery of NCAA official gamebook PDFs.
Search engine results are candidates only; PDF text must verify both teams and date.
"""
import argparse
import datetime as dt
import io
import json
import re
import time
import urllib.parse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
LEAGUES=("ncaaf","ncaamb","ncaawb")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; NCAA-official-gamebook-check/1.0)"}
TODAY=dt.datetime.now(dt.timezone.utc)
MAX_GAMES=12
MAX_SECONDS=240
started=time.monotonic()
session=requests.Session()
session.headers.update(HEADERS)
BAD_HOSTS=("espn.com","ncaa.com","scribd.com","reddit.com","youtube.com","facebook.com","x.com","twitter.com","wikipedia.org")
WORDS={"university","college","state","the","of","at","and","football","basketball","mens","womens","women","men","university","univ"}

def read(path):
 try:return json.loads(path.read_text())
 except (ValueError,OSError):return {"games":[]}

def words(s):
 return set(re.findall(r"[a-z0-9]+",s.lower()))-WORDS

def names_match(text,home,away):
 tokens=words(text)
 a=words(home);b=words(away)
 return bool(a and b and (len(a&tokens)>=min(2,len(a)) or (len(a&tokens)>=1 and len(a)<=3)) and (len(b&tokens)>=min(2,len(b)) or (len(b&tokens)>=1 and len(b)<=3)))

# Official university athletics media centers and schedules, not third-party PDFs.
# These pages expose game-specific Final Book / Game Book links.
FOOTBALL_SOURCES={
 "Tennessee Volunteers":"https://utsports.com/sports/2026/7/24/football-2026-media-center",
 "Mississippi State Bulldogs":"https://hailstate.com/sports/2026/6/26/2026-football-media-center",
 "Penn State Nittany Lions":"https://gopsusports.com/sports/football/schedule",
 "Cincinnati Bearcats":"https://gobearcats.com/2026-football-media-center",
 "Arizona State Sun Devils":"https://thesundevils.com/sports/football/schedule/season/2026",
 "North Carolina Central Eagles":"https://nccueaglepride.com/sports/2026/3/31/football-2026-media-center.aspx",
}
PAGE_CACHE={}
def official_page_candidates(page,game):
 if page not in PAGE_CACHE:
  try:
   r=session.get(page,timeout=9)
   r.raise_for_status()
   if "html" not in r.headers.get("Content-Type","").lower():return []
   soup=BeautifulSoup(r.text[:900000],"html.parser")
   links=[]
   for a in soup.select("a[href]"):
    href=urllib.parse.urljoin(r.url,a["href"])
    path=urllib.parse.urlparse(href).path.lower()
    label=" ".join(a.stripped_strings).lower()
    if not (".pdf" in path or "/documents/" in path or "download" in path):continue
    if not any(x in label+" "+path for x in ("gamebook","game book","final book","final stats","final statistics","box score","boxscore")):continue
    if any(x in label+" "+path for x in ("pregame","game notes","preview","media guide","program")):continue
    links.append(href)
   PAGE_CACHE[page]=list(dict.fromkeys(links))
  except requests.RequestException:return []
 return PAGE_CACHE[page]

def game_boxscore_candidates(game,league):
 """Extract official PDF links from a game's athletics box-score page."""
 if league!="ncaaf":return []
 pages=[]
 home=game.get("home_team","")
 away=game.get("away_team","")
 if "Alabama Crimson Tide" in (home,away) and "Chattanooga Mocs" in (home,away) and game.get("date")=="2026-11-21":
  pages.append("https://rolltide.com/sports/football/stats/2026/chattanooga/boxscore/21648")
 # Discover other Sidearm game-specific box scores via a focused search.
 query=f'"{home}" "{away}" "{game["date"][:4]}" site:*/sports/football/stats/ boxscore'
 try:
  resp=session.get("https://www.bing.com/search",params={"q":query,"format":"rss"},timeout=9)
  resp.raise_for_status()
  root=ET.fromstring(resp.content)
  for item in root.findall(".//item"):
   url=item.findtext("link","").strip()
   if "/sports/football/stats/" in url and "/boxscore/" in url and url not in pages:pages.append(url)
 except (requests.RequestException,ET.ParseError):pass
 urls=[]
 for page in pages[:3]:
  try:
   resp=session.get(page,timeout=12)
   resp.raise_for_status()
   soup=BeautifulSoup(resp.text[:1500000],"html.parser")
   for a in soup.select("a[href]"):
    href=urllib.parse.urljoin(resp.url,a["href"])
    label=" ".join(a.stripped_strings).lower()
    if (".pdf" in urllib.parse.urlparse(href).path.lower() or "pdf" in label or "view pdf" in label) and href.startswith("https://") and href not in urls:urls.append(href)
  except requests.RequestException:continue
 return urls[:8]

def candidates(game,league):
 """Search for postgame books and follow links on official athletics pages."""
 date=game["date"]
 home=game["home_team"];away=game["away_team"]
 sport="football" if league=="ncaaf" else "basketball"
 queries=[
  f'"{home}" "{away}" "{date[:4]}" {sport} "game book" pdf',
  f'"{home}" "{away}" "{date[:4]}" {sport} "final book"',
  f'"{home}" "{away}" "{date[:4]}" {sport} "final stats" pdf',
  f'"{home}" "{away}" "{date[:4]}" {sport} "box score" pdf',
 ]
 urls=game_boxscore_candidates(game,league);pages=[]
 if league=="ncaaf":
  for team in (home,away):
   page=FOOTBALL_SOURCES.get(team)
   if page:
    for link in official_page_candidates(page,game):
     if link not in urls:urls.append(link)
 def add(url):
  if url and url not in urls:urls.append(url)
 for query in queries:
  if time.monotonic()-started>MAX_SECONDS-25:break
  try:
   r=session.get("https://www.bing.com/search",params={"q":query,"format":"rss"},timeout=10)
   r.raise_for_status()
   root=ET.fromstring(r.content)
   for item in root.findall(".//item"):
    link=item.findtext("link","").strip()
    if not link:continue
    if ".pdf" in urllib.parse.urlparse(link).path.lower():add(link)
    elif link not in pages:pages.append(link)
  except (requests.RequestException,ET.ParseError):pass
  if len(urls)>=10:break
 # Search engines frequently index a schedule/media-center HTML page, not the PDF.
 # Crawl a small number of these pages and prioritize postgame report links.
 for page in pages[:3]:
  if time.monotonic()-started>MAX_SECONDS-12:break
  try:
   parsed=urllib.parse.urlparse(page)
   if parsed.scheme!="https" or any((parsed.hostname or "").endswith(x) for x in BAD_HOSTS):continue
   r=session.get(page,timeout=9)
   r.raise_for_status()
   if "html" not in r.headers.get("Content-Type","").lower():continue
   soup=BeautifulSoup(r.text[:700000],"html.parser")
   for a in soup.select("a[href]"):
    href=urllib.parse.urljoin(r.url,a.get("href",""))
    path=urllib.parse.urlparse(href).path.lower()
    label=" ".join(a.stripped_strings).lower()
    if not (".pdf" in path or "/documents/" in path or "/documents/download/" in path):continue
    positive=any(x in label+" "+path for x in ("gamebook","game book","final book","final stats","final statistics","box score","boxscore","stats pdf"))
    negative=any(x in label+" "+path for x in ("game notes","pregame","preview","media guide","program","weekly notes"))
    if positive and not negative:add(href)
  except requests.RequestException:pass
 return urls[:35]

def verify(url,game):
 try:
  parsed=urllib.parse.urlparse(url)
  host=(parsed.hostname or "").lower()
  if parsed.scheme!="https" or not host or any(host==bad or host.endswith("."+bad) for bad in BAD_HOSTS):return None
  r=session.get(url,timeout=16,stream=True,allow_redirects=True)
  r.raise_for_status()
  final=r.url
  finalhost=(urllib.parse.urlparse(final).hostname or "").lower()
  if any(finalhost==bad or finalhost.endswith("."+bad) for bad in BAD_HOSTS):return None
  buf=io.BytesIO()
  for chunk in r.iter_content(65536):
   buf.write(chunk)
   if buf.tell()>5_000_000:return None
  data=buf.getvalue()
  if not data.startswith(b"%PDF"):return None
  reader=PdfReader(io.BytesIO(data))
  text=" ".join((p.extract_text() or "") for p in reader.pages[:5])
  if not names_match(text,game["home_team"],game["away_team"]):return None
  # A pregame notes packet can mention both teams and the game date.
  # Require recognizable postgame statistics content.
  if not any(marker in text.lower() for marker in ("scoring summary","team statistics","individual statistics","play-by-play","final statistics","team stats","team stat comparison","scoring plays")):return None
  date=dt.date.fromisoformat(game["date"])
  forms=[date.strftime("%B %d, %Y"),date.strftime("%b %d, %Y"),date.strftime("%m/%d/%Y"),date.strftime("%m/%d/%y"),date.strftime("%Y-%m-%d"),date.strftime("%B %-d, %Y"),date.strftime("%b %-d, %Y")]
  normalized=" ".join(text.lower().split())
  if not any(f.lower() in normalized for f in forms):return None
  return final
 except (requests.RequestException,ValueError,Exception):
  return None

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--league",choices=LEAGUES,required=True)
 league=parser.parse_args().league
 checked=0;found=0
 for league in (league,):
  folder=ROOT/league
  archive=folder/"archive.json";live=folder/"gamebooks.json"
  a=read(archive);c=read(live)
  current={str(g.get("id")):g for g in c.get("games",[])}
  games=a.get("games",[])
  games.sort(key=lambda g:g.get("date",""),reverse=True)
  for game in games:
   if checked>=MAX_GAMES or time.monotonic()-started>MAX_SECONDS:break
   if game.get("pdf_url") or game.get("state") not in ("post","final") and "final" not in str(game.get("status","")).lower():continue
   if not game.get("home_team") or not game.get("away_team"):continue
   try:game_date=dt.date.fromisoformat(game["date"])
   except (KeyError,ValueError):continue
   if game_date>TODAY.date():continue
   previous=game.get("pdf_checked_at")
   if previous:
    try:
     elapsed=(TODAY-dt.datetime.fromisoformat(previous)).total_seconds()
     if elapsed<(1800 if (TODAY.date()-game_date).days<=2 else 86400):continue
    except ValueError:pass
   checked+=1
   result=None
   for url in candidates(game,league):
    if time.monotonic()-started>MAX_SECONDS:break
    result=verify(url,game)
    if result:break
   game["pdf_checked_at"]=TODAY.isoformat()
   if result:
    game["pdf_url"]=result
    game["pdf_source"]="Verified PDF content: teams and game date"
    found+=1
   if str(game.get("id")) in current:
    current[str(game["id"])].update({k:game[k] for k in ("pdf_checked_at","pdf_url","pdf_source") if k in game})
  a["games"]=games;c["games"]=list(current.values())
  archive.write_text(json.dumps(a,indent=2)+"\n")
  live.write_text(json.dumps(c,indent=2)+"\n")
  print(league,"checked",checked,"verified",found)
 print("TOTAL",checked,"checked",found,"verified")
if __name__=="__main__":main()
