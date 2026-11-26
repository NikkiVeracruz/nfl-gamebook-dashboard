"""Read-only proof against exact previously tracked Rams matchup; never writes data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import requests
import monitor
from nfl_pending import SEED,read_board,event_match,refresh_game
session=requests.Session()
session.headers.update(monitor.HEADERS)
game=dict(SEED)
matches=[e for e in read_board(session,game["date"]) if event_match(game["slug"],e)]
assert len(matches)==1,"Independent Rams matchup unavailable"
game=refresh_game(game,matches[0])
assert game["status"]=="Final" and (game["away_score"],game["home_score"])==(13,26),game
assert monitor.fetch_gamebook(session,game),"No verified gamebook"
print("LIVE RAMS GAMEBOOK VERIFIED",game["pdf_url"],game.get("pdf_verification","official central NFL link"))
