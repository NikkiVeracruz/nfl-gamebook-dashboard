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

# Test the independent official club route even if the central NFL route worked.
from nfl_pending import packers_page, club_candidate, verify_club_pdf
page=packers_page(game)
assert page=="https://www.packers.com/game-day/2026/reg-week12/packers-at-rams/"
candidate=club_candidate(monitor.get(session,page),page)
assert candidate,"No explicitly labeled Packers club PDF"
assert verify_club_pdf(session,candidate,game),"Club PDF first-page identity failed"
print("LIVE CLUB PDF VERIFIED",candidate,"exact date, teams, final scores")
