# Forward-only Mega Board retention (effective November 23, 2026)

## Active behavior
- **No historical backfill.** NFL, NBA, WNBA, NHL and MLB backfill workflows remain in GitHub but have their hourly schedules removed and their jobs are gated by `ENABLE_HISTORICAL_BACKFILL`, which must explicitly be set to `true` before manual use.
- **Active archive data intentionally starts with the current display window.** NFL: November 19, 2026 (current NFL week). NBA, WNBA, NHL and MLB: November 22, 2026 (yesterday in the 3 AM Eastern rolling window).
- **Only completed games with all league-required verified report links are saved in the active archive.** NFL, NBA and WNBA need an official gamebook PDF; NHL needs both GS and ES; MLB needs an official box score, play-by-play and verified API game ID.
- **Upcoming and live game schedules remain displayed.** The current `gamebooks.json` feeds were deliberately not purged, so agents can still see scheduled, live and awaiting-report games. A game without its complete report stays out of the cumulative archive.
- **New games and complete reports continue to be saved automatically.** The normal monitoring, archive/writing protections and three-day rollovers remain active.
- **No old archive games are silently reintroduced**: tracked production archive writes are filtered by `forward_only.py`. The ordinary archive integrity checks continue to protect *retained* current/new records. Test fixtures are intentionally exempt from this filter.
- **Document-level verification stays available for forward-only records.** The central historical verification report was pruned to active eligible document identities; it no longer stores older URLs.
- **Independent safety check**: `.github/workflows/forward-only-safety.yml` audits all five archives daily without changing them.

## Backup and reactivation

Before the one-time archive purge, each source repository received a branch named:

`backup/pre-forward-only-2026-11-23`

Repositories:
- `NikkiVeracruz/nfl-gamebook-dashboard`
- `NikkiVeracruz/nba-gamebook-dashboard` (includes WNBA)
- `NikkiVeracruz/nhl-gamebook-dashboard`
- `NikkiVeracruz/mlb-gamebook-dashboard`

Those branches preserve the original records for safe restoration. GitHub history also still contains prior versions. **This was a purge of active published data, not irreversible deletion from Git history.**

To restore historical backfill, first explicitly change or disable the forward-only filtering in each repository's `forward_only.py`; reconcile desired historical records from the backup branch; run the existing integrity and recovery rehearsals; then enable the repository variable `ENABLE_HISTORICAL_BACKFILL=true` and deliberately restore schedules as needed. Merely enabling the variable is not sufficient to restore history while forward-only filtering remains enabled.

## Known limitation

A completed game whose report is delayed beyond the live display window is **not retained as an incomplete archive game**. Existing recovery jobs are preserved, but some use the archive as their retry list. If reliable post-window catch-up is needed in the future, introduce a separate, bounded non-public pending-game retry queue; do not reintroduce unverified links into the published archive.
