#!/usr/bin/env python3
"""Backfill NFL previous/current seasons up to four schedule weeks per run."""
import json,requests
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from monitor import discover,get,gamebook_link,is_official,verify_pdf,HEADERS
ARCHIVE=Path("archive.json")
PROGRESS=Path("archive-progress.json")
def main():
    existing=json.loads(ARCHIVE.read_text()) if ARCHIVE.exists() else {"games":[]}
    records={g.get("slug",g.get("date","")+"|"+g.get("label","")):g for g in existing.get("games",[])}
    p=json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    start=date.fromisoformat(p.get("next_date","2025-08-01"))
    end=min(start+timedelta(days=28),date.today()+timedelta(days=1))
    if start>=end:
        print("NFL archive backfill caught up")
        return
    session=requests.Session();session.headers.update(HEADERS)
    for season in {start.year,start.year-1}:
        for slug,g in discover(session,season,start.isoformat(),end.isoformat()).items():
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
    ARCHIVE.write_text(json.dumps(existing,indent=2)+"\n")
    PROGRESS.write_text(json.dumps({"next_date":end.isoformat(),"complete":end>date.today(),"updated_at":existing["updated_at"]},indent=2)+"\n")
    print("NFL archive now contains",len(records),"games; next",end)
if __name__=="__main__":main()
