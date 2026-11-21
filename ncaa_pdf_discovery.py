#!/usr/bin/env python3
"""Bounded, conservative discovery of NCAA official gamebook PDFs.
Search engine results are candidates only; PDF text must verify both teams and date.
"""
import datetime as dt
import io
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
LEAGUES=("ncaaf","ncaamb","ncaawb")
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; NCAA-official-gamebook-check/1.0)"}
TODAY=dt.datetime.now(dt.timezone.utc)
MAX_GAMES=24
MAX_SECONDS=420
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
 return bool(a and b and len(a&tokens)>=min(2,len(a)) and len(b&tokens)>=min(2,len(b)))

def candidates(game,league):
 date=game["date"]
 home=game["home_team"];away=game["away_team"]
 sport="football" if league=="ncaaf" else "basketball"
 queries=[
  f'"{home}" "{away}" "{date[:4]}" {sport} "game notes" pdf',
  f'"{home}" "{away}" {sport} "box score" pdf',
 ]
 urls=[]
 for query in queries:
  try:
   r=session.get("https://www.bing.com/search",params={"q":query,"format":"rss"},timeout=12)
   r.raise_for_status()
   root=ET.fromstring(r.content)
   for item in root.findall(".//item"):
    link=item.findtext("link","").strip()
    if link and link not in urls:urls.append(link)
  except (requests.RequestException,ET.ParseError):
   pass
  if len(urls)>=12:break
 return urls[:12]

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
  date=dt.date.fromisoformat(game["date"])
  forms=[date.strftime("%B %d, %Y"),date.strftime("%b %d, %Y"),date.strftime("%m/%d/%Y"),date.strftime("%m/%d/%y"),date.strftime("%Y-%m-%d"),date.strftime("%B %-d, %Y"),date.strftime("%b %-d, %Y")]
  normalized=" ".join(text.lower().split())
  if not any(f.lower() in normalized for f in forms):return None
  return final
 except (requests.RequestException,ValueError,Exception):
  return None

def main():
 checked=0;found=0
 for league in LEAGUES:
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
     if elapsed<(3600 if (TODAY.date()-game_date).days<=2 else 86400):continue
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
