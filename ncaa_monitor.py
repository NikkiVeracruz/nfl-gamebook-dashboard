#!/usr/bin/env python3
"""Forward-only NCAA scoreboard monitor. Do not label ESPN summaries as official gamebooks."""
import json,datetime,requests,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPORTS={"NCAAF":"football/college-football","NCAAMB":"basketball/mens-college-basketball","NCAAWB":"basketball/womens-college-basketball"}
START=datetime.date(2026,11,21)
TODAY=datetime.datetime.now(datetime.timezone.utc).date()
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; NCAA-gamebook-monitor/1.0)"}
def read(path,default):
 try:return json.loads(path.read_text())
 except (FileNotFoundError,ValueError):return default
def main():
 for league,sport in SPORTS.items():
  folder=ROOT/league.lower();folder.mkdir(exist_ok=True)
  live=folder/"gamebooks.json";archive=folder/"archive.json"
  old=read(archive,{"games":[]});stored={str(g["id"]):g for g in old.get("games",[]) if g.get("id")}
  recent={}
  for offset in range(-2,3):
   day=TODAY+datetime.timedelta(days=offset)
   if day<START:continue
   url=f"https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard"
   response=requests.get(url,params={"dates":day.strftime("%Y%m%d"),"limit":500,"groups":50 if league=="NCAAF" else 50},headers=HEADERS,timeout=30)
   response.raise_for_status()
   for event in response.json().get("events",[]):
    comp=(event.get("competitions") or [{}])[0]
    sides=comp.get("competitors") or []
    home=next((x for x in sides if x.get("homeAway")=="home"),{})
    away=next((x for x in sides if x.get("homeAway")=="away"),{})
    if not home or not away:continue
    event_id=str(event.get("id") or "")
    if not event_id:continue
    game_date=str(event.get("date") or "")[:10]
    if game_date<START.isoformat():continue
    status=event.get("status",{}).get("type",{})
    game={"id":event_id,"date":game_date,"label":f"{away.get('team',{}).get('displayName','Away')} @ {home.get('team',{}).get('displayName','Home')}","status":status.get("description","Unknown"),"state":status.get("state","unknown"),"game_url":f"https://www.espn.com/{'college-football' if league=='NCAAF' else 'mens-college-basketball' if league=='NCAAMB' else 'womens-college-basketball'}/game/_/gameId/{event_id}","home_team":home.get("team",{}).get("displayName",""),"away_team":away.get("team",{}).get("displayName","")}
    if league=="NCAAF":
     groups=event.get("groups",{})
     game["subdivision"]="FBS/FCS (unverified)"
    recent[event_id]=game
    stored[event_id]={**stored.get(event_id,{}),**game}
   time.sleep(.3)
  stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
  live.write_text(json.dumps({"league":league,"updated_at":stamp,"games":sorted(recent.values(),key=lambda g:g["date"],reverse=True)},indent=2)+"\n")
  archive.write_text(json.dumps({"league":league,"updated_at":stamp,"games":sorted(stored.values(),key=lambda g:(g["date"],g["label"]),reverse=True)},indent=2)+"\n")
  print(league,len(recent),"current",len(stored),"archived")
if __name__=="__main__":main()
