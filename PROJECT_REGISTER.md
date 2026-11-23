# Mega Board — Master Project Register

**Status reviewed:** 2026-11-23 · **Canonical data:** [project/feature_registry.json](project/feature_registry.json)

> This page is generated from the canonical registry. Automatic checks must not accept, reject, or supersede user decisions.

## Purpose and scope

One fast, accurate place for customer service agents to find game/team/player reference data and official league reports.

**Leagues:** NFL, NBA, WNBA, NHL, MLB. **Board:** [Mega Board](https://nikkiveracruz.github.io/nfl-gamebook-dashboard/command-center/).

**Operating direction:** Forward-only collection from November 23, 2026: keep live scheduled and active game views, archive only completed games with all required official reports, and store new complete games going forward. Keep dormant historical infrastructure but do not backfill historical seasons.

**Authority rule:** Later explicit user decisions supersede older plans. Recommendations are not approved unless the user accepts them.

## Status overview

**49 tracked items:** 30 implemented · 4 paused · 3 removed · 0 proposed · 0 deferred · 9 not started · 3 open

| State | Meaning |
|---|---|
| Implemented | Evidenced in code or configuration, not an uptime guarantee. |
| Paused | Preserved but intentionally inactive/restricted. |
| Removed | Deliberately removed; do not reinstate without approval. |
| Proposed / not started | An idea or request, not approval to implement. |
| Deferred | Delayed, not necessarily rejected. |
| Open | Known risk or incomplete follow-up. |


## Accepted and implemented

Implemented requirements or work accepted by the user.

### PRJ-001 — Single reliable agent-facing reference board

**Decision:** required · **Status:** implemented · **Area:** mission

Centralize accurate, detailed official game, player and team reference material for quick customer-service agent lookup; distinguish linked source reports from the summarized cards.

*Notes:* The user explicitly said on 2026-11-23 that dedicated player-statistics features are not needed; exclude player-statistics search, tables, databases and analytics from future Mega Board recommendations. Existing league-provided gamebooks, reports and approved board behavior remain unchanged. IDEA-001 declined.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-002 — Five supported leagues

**Decision:** accepted · **Status:** implemented · **Area:** scope

NFL, NBA, WNBA, NHL and MLB feeds are combined on the Mega Board; WNBA lives in the basketball repository.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-003 — Independent league feeds and dashboards

**Decision:** accepted · **Status:** implemented · **Area:** architecture

Keep the four league repos and their source feeds; the Mega Board integrates them. Existing standalone board pages may remain without equal UI enhancement effort.

*Implementation evidence:* [monitor.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/monitor.py), [wnba_monitor.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/wnba_monitor.py), [monitor.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/monitor.py), [monitor.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/monitor.py), [monitor.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/monitor.py)

### PRJ-004 — Current-game vs archive search separation

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Current games and historical/retained archive have separate search and filters.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-005 — League sections and combined view

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Expandable/collapsed league sections with a combined all-leagues view.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-006 — Search by team, matchup, league, and game status

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Current-game search and team/league/status filters; archival league, team, year, status and matchup filtering.

*Notes:* Normalization for alternate team spellings and abbreviations remains separately proposed (IDEA-002).

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-007 — Rolling display periods

**Decision:** accepted · **Status:** implemented · **Area:** display

NFL uses a weekly window; NBA, WNBA, NHL and MLB display yesterday/today/tomorrow, rotating at 3 AM America/New_York.

*Implementation evidence:* [monitor.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/monitor.py), [three_day_window.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/three_day_window.py), [three_day_window.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/three_day_window.py), [three_day_window.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/three_day_window.py)

### PRJ-008 — Archive disclosure with 200-result cap

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Archive collapsed by default, shows up to the 200 most recent matching games and expands upon league+team selection.

*Notes:* Pagination beyond 200 was suggested but not approved.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-009 — Official report links by league

**Decision:** required · **Status:** implemented · **Area:** source integrity

NFL/NBA/WNBA official gamebook PDFs; NHL both GS and ES HTML reports; MLB official game-specific box score and play-by-play (not PDFs).

*Implementation evidence:* [monitor.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/monitor.py), [monitor.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/monitor.py), [wnba_monitor.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/wnba_monitor.py), [monitor.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/monitor.py), [mlb_policy.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/mlb_policy.py)

### PRJ-010 — Truthful game and report status

**Decision:** accepted · **Status:** implemented · **Area:** source integrity

Show scheduled, live, finished awaiting report and report-available states without treating a finished game or guessed URL as a published document.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [monitor.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/monitor.py)

### PRJ-011 — Automatic active-game monitoring

**Decision:** accepted · **Status:** implemented · **Area:** operations

Calendar-controlled adaptive/approximately five-minute game-time monitoring and reporting heartbeat; idle/offseason is not an error.

*Implementation evidence:* [.github/workflows/nfl-calendar.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/nfl-calendar.yml), [.github/workflows/update.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/update.yml), [adaptive_monitor.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/adaptive_monitor.py), [adaptive_monitor.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/adaptive_monitor.py), [adaptive_monitor.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/adaptive_monitor.py)

### PRJ-012 — Page refresh and clock updates

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Mega Board refreshes displayed data periodically; manual refresh is available; clocks are separately updated.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-013 — Right-side instructions and feedback

**Decision:** accepted · **Status:** implemented · **Area:** user experience

Published Help/How to Use area covering discovery, refresh, statuses, report latency, official sources and suggestions/feedback.

*Notes:* The current sidebar still uses some older 'historical archive' wording; it should match forward-only retention. Tracked as RISK-003.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### PRJ-014 — Protect archive on window rollover

**Decision:** accepted · **Status:** implemented · **Area:** source integrity

Archive eligible outgoing games before removing them from the rolling view; never overwrite a previously stored verified report just because a later poll is incomplete.

*Implementation evidence:* [three_day_window.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/three_day_window.py), [three_day_window.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/three_day_window.py), [three_day_window.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/three_day_window.py), [archive.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/archive.py)

### PRJ-015 — Archive integrity checks and safe publishing

**Decision:** accepted · **Status:** implemented · **Area:** source integrity

Fail on corrupt archive payloads/duplicate IDs; use atomic writes and regression gates. Forward-only retention is a scoped exception to original no-deletion behavior.

*Implementation evidence:* [tests/archive_integrity_gate.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/archive_integrity_gate.py), [archive.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/archive.py), [archive.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/archive.py), [archive.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/archive.py)

### PRJ-016 — Independent current schedule missing-game audit

**Decision:** accepted · **Status:** implemented · **Area:** quality

Read-only current schedule comparisons including exact NFL matchups; discrepancies fail the audit instead of showing false green.

*Notes:* Current scheduled game coverage continues; full historical coverage is intentionally paused.

*Implementation evidence:* [tests/missing_game_audit.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/missing_game_audit.py), [.github/workflows/missing-game-audit.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/missing-game-audit.yml)

### PRJ-017 — Forward-only current and future collection

**Decision:** accepted · **Status:** implemented · **Area:** retention

Active archives contain complete reports only for games in the current reporting windows and newly completed games going forward; current scheduled/live games still display.

*Notes:* Switched 2026-11-23; supersedes previous comprehensive historical archive plan.

*Implementation evidence:* [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md), [forward_only.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/forward_only.py)

### PRJ-018 — Archive complete-data-only rule

**Decision:** accepted · **Status:** implemented · **Area:** retention

NFL/NBA/WNBA archived PDFs; NHL both GS+ES reports; MLB both game-specific report links backed by verified official API data. Incomplete games are not retained as complete archives.

*Notes:* Important limitation: a report delayed beyond the current window may be missed (RISK-001).

*Implementation evidence:* [forward_only.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/forward_only.py), [forward_only.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/forward_only.py)

### PRJ-020 — Pre-cleanup branch backups

**Decision:** accepted · **Status:** implemented · **Area:** recovery

Retain backup/pre-forward-only-2026-11-23 in all four source repositories; original historical data remains accessible through Git history.

*Implementation evidence:* [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md)

### PRJ-021 — Forward-only five-league safety check

**Decision:** accepted · **Status:** implemented · **Area:** quality

Read-only daily audit checks all five active archives for complete reports and verifies that historical backfill is guarded.

*Implementation evidence:* [tests/forward_only_cross_league_audit.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/forward_only_cross_league_audit.py), [.github/workflows/forward-only-safety.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/forward-only-safety.yml)

### PRJ-022 — Document-level official source verification

**Decision:** accepted · **Status:** implemented · **Area:** quality

Incremental PDF/report/API validation, now scoped to current/new forward-only records, without rewriting the source archives.

*Notes:* Document verification means PDF/game identity or official report type/MLB API data; not a guarantee that every statistic was independently audited.

*Implementation evidence:* [tests/document_level_verification.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/document_level_verification.py), [.github/workflows/document-level-verification.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/document-level-verification.yml)

### PRJ-024 — Simple diagnostics and honest health labels

**Decision:** accepted · **Status:** implemented · **Area:** operations

Differentiate a legitimately idle league, monitor check, missing-game discrepancy and pending report; do not claim unavailable sources are verified.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [tests/production_health.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/production_health.py)

### PRJ-025 — Preserve independent recovery and monitoring machinery

**Decision:** accepted · **Status:** implemented · **Area:** architecture

Keep report recovery scripts, calendars, monitors, archive storage and tests so forward-only normal operation continues and historical recovery remains possible later.

*Implementation evidence:* [recover_reports.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/recover_reports.py), [recover_reports.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/recover_reports.py), [recover_reports.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/recover_reports.py)

### IDEA-002 — More forgiving team/date/abbreviation search

**Decision:** accepted · **Status:** implemented · **Area:** suggestion

Search across all five leagues by full team name, franchise nickname, city/market (including shared markets), common city abbreviations, official team abbreviations, minor spelling variations, and two-team matchup; applies to both current tracking and the forward-only archive.

*Notes:* User explicitly approved smarter search on 2026-11-23 and added city and common city-abbreviation coverage. Implemented together with missing MLB/WNBA dropdown fix. Nine search unit tests and page integration test passed: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45266196881 .

*Implementation evidence:* [command-center/search.js](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/search.js), [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [tests/test_mega_search.cjs](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_mega_search.cjs), [.github/workflows/mega-search-safety.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/mega-search-safety.yml)

### IDEA-008 — Clearer official report availability indicators

**Decision:** accepted · **Status:** implemented · **Area:** suggestion

Keep existing game cards and Scheduled/Live/Final status separate from document availability. Show Awaiting reports (or Awaiting official gamebook), Partially available with required-document checklist and counts, Verification pending for unconfirmed links, and All required reports verified only when league-source checks justify it. Show complete/partial/awaiting totals, report-status filters, and preserve the time-since-final display, monitoring schedule, current feeds and complete-only forward archive rules.

*Notes:* User explicitly approved implementation of the previous-chat proposal on 2026-11-23. Implemented in the Mega Board presentation only: separate game and report status; per-document NHL GS/ES and MLB box/play-by-play rows; verified/partial/pending/awaiting states; summary counters and filters; existing final-first-detected-in-browser clock retained. Non-MLB links are emitted only after validation by the individual verified-source monitors and must match official URL format; MLB requires link_verification=verified_api. These labels reflect source checks, not live revalidation of remote availability. No new polling, report fetching, historical backfill or archive policy changes. Validation evidence (2026-11-23): pre-merge safety job PASS (all applicable archive, search, report-status, register and governance tests), https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45275540930; post-merge five-league search safety PASS, https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45275817341; canonical register generation PASS, https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45275817339; latest GitHub Pages build/deployment PASS, https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45275848019. Browser HTTP smoke testing of deployed pages and live revalidation of every external report were not performed.

*Implementation evidence:* [command-center/report-status.js](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/report-status.js), [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [tests/test_report_status.cjs](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_report_status.cjs), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml)

### IDEA-010 — More independent, standardized end-to-end tests

**Decision:** accepted · **Status:** implemented · **Area:** suggestion

Broadened cross-league archive, workflow, coverage, and document regression checks; continue refining as actual failures appear.

*Implementation evidence:* [tests/test_forward_only.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_forward_only.py), [tests/test_forward_only.py](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/tests/test_forward_only.py), [tests/test_forward_only.py](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/tests/test_forward_only.py), [tests/test_forward_only.py](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/tests/test_forward_only.py)

### GOV-001 — Canonical project register and change history

**Decision:** accepted · **Status:** implemented · **Area:** governance

Maintain this register with user decisions, suggestions, actual implementation evidence, and an automated read-only drift monitor.

*Notes:* New approvals and rejections require explicit user instruction; the monitor reports drift but does not make product decisions.

*Implementation evidence:* [project/feature_registry.json](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/project/feature_registry.json), [PROJECT_REGISTER.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/PROJECT_REGISTER.md)

### GOV-002 — Update project register with every decision and project change

**Decision:** accepted · **Status:** implemented · **Area:** governance

The user explicitly requires the canonical GitHub project registry to be updated as part of every Mega Board decision or project modification performed with the assistant, including approvals, rejections, deferrals, source changes, evidence, and unresolved risks. The readable master register is regenerated from the structured registry, and the update is verified before a change is reported complete.

*Notes:* User confirmed required documentation on 2026-11-23. On 2026-11-23 the governance monitor's push trigger was changed to run after the generated PROJECT_REGISTER.md is committed, instead of directly on the JSON change; this prevents false failures while the two files are temporarily out of sync. Check run: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45266503282. Scheduled review detects external edits but cannot guarantee instantaneous awareness.

*Implementation evidence:* [project/feature_registry.json](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/project/feature_registry.json), [project/render_register.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/project/render_register.py), [.github/workflows/project-register.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/project-register.yml), [project/STATUS.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/project/STATUS.md), [.github/workflows/project-governance-monitor.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/project-governance-monitor.yml)

### PRJ-026 — Show complete team lists in active and archive selectors even without games

**Decision:** accepted · **Status:** implemented · **Area:** user experience

All five leagues' current 2026 franchise lists are available in both the active-tracking team filter and the archive team filter, independent of live fixture results or stored archive records. This corrects missing MLB/WNBA options during their offseason; MLB lists 30 teams and WNBA lists 15, including the 2026 expansion franchises Portland Fire and Toronto Tempo.

*Notes:* Approved and implemented alongside IDEA-002 on 2026-11-23. Selecting an offseason team may legitimately show no current games or archive records; the option stays available. Latest CI: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45266196881 .

*Implementation evidence:* [command-center/search.js](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/search.js), [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [tests/test_mega_search.cjs](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_mega_search.cjs)

### GOV-003 — Branch-first development, pre-merge tests and production verification

**Decision:** accepted · **Status:** implemented · **Area:** governance

For every future Mega Board code/configuration change, develop on a task-specific branch, run tests before opening the pull request where possible, obtain a green read-only pre-merge safety check in every affected repository, review the PR, merge to main only after validation, then verify production deployment and existing monitoring. Do not weaken report discovery, tests, or GitHub error notifications.

*Notes:* Explicit user approval November 23, 2026. CI workflows are read-only pull_request checks. Branch protection/rulesets cannot be assumed enabled; this is a mandatory documented working practice, not yet repository-enforced merge blocking. Staging checks complement, not replace, post-merge monitoring.

*Implementation evidence:* [DEVELOPMENT_WORKFLOW.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/DEVELOPMENT_WORKFLOW.md), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml)


## Explicitly declined, removed, or superseded

Never reintroduce these without a fresh explicit decision.

### DEC-001 — Remove all NCAA boards and automation

**Decision:** declined · **Status:** removed · **Area:** declined or removed

User explicitly requested complete removal of NCAA dashboards and associated pipelines, while preserving the five supported leagues.

*Notes:* Do not reintroduce NCAA without a new explicit user decision.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html)

### DEC-002 — Do not show a data-staleness monitor

**Decision:** declined · **Status:** removed · **Area:** declined or removed

Visible data-age/staleness display and its separate monitoring feature were intentionally removed as unnecessary.

*Notes:* Keep meaningful live monitoring and missing-game/report checks.

*Implementation evidence:* [.github/workflows/update.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/update.yml)

### DEC-003 — Do not run historical game backfills

**Decision:** declined · **Status:** paused · **Area:** declined or removed

No continuing historical restoration or full past-season rebuilding. Keep code/backups for possible later reactivation.

*Notes:* Supersedes the earlier 2025 and 2026 comprehensive coverage goals.

*Implementation evidence:* [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md)

### DEC-004 — Do not retain historical unverified links

**Decision:** declined · **Status:** removed · **Area:** declined or removed

Old or unverified historical game links and verification evidence were removed from active archives; do not reintroduce into active data.

*Notes:* The backup branches retain previous history; this is not erasure of Git history.

*Implementation evidence:* [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md), [tests/document_level_verification.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/document_level_verification.py)

### DEC-005 — No more 2025 season restoration

**Decision:** declined · **Status:** paused · **Area:** declined or removed

The user explicitly stopped extra 2025 restoration even before the broader forward-only decision.

*Implementation evidence:* [.github/workflows/restore-nfl-nov-2025.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/restore-nfl-nov-2025.yml)

### IDEA-001 — Dedicated player-level statistics search

**Decision:** declined · **Status:** not started · **Area:** suggestion

Search player names and game-by-game statistics directly rather than relying only on PDF/report reading.

*Notes:* High-value strategic opportunity, not implemented; availability/rights/API accuracy must be evaluated before committing. User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review. Dedicated player-statistics search, indexing, dashboards, tables and analysis are not a project need and must be excluded from future feature ideation; existing official report contents are unaffected.

### IDEA-003 — One-click comprehensive game reference

**Decision:** declined · **Status:** not started · **Area:** suggestion

Open one consolidated game view linking official reports, game context, and team/player data.

*Notes:* User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review. Its illustrative design included player stats; no game-reference detail view or associated player-statistics functionality should be proposed without explicit user request.

### IDEA-004 — Permanent deep links to games

**Decision:** declined · **Status:** not started · **Area:** suggestion

Share direct, stable links to a particular archived or current game.

*Notes:* User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.

### IDEA-005 — Favorites and recently viewed games

**Decision:** declined · **Status:** not started · **Area:** suggestion

Provide quick access to frequently used teams or previously opened games.

*Notes:* User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.

### IDEA-006 — Navigation by document type

**Decision:** declined · **Status:** not started · **Area:** suggestion

Filter or jump directly to PDF, NHL GS/ES, MLB box score or play-by-play by report type.

*Notes:* User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.

### IDEA-007 — Pagination or result navigation past 200

**Decision:** declined · **Status:** not started · **Area:** suggestion

Permit exploring more than the latest 200 matching archived games when historical archiving is reactivated.

*Notes:* Reduced priority in forward-only mode; current 200 cap is accepted. User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.

### IDEA-009 — Temporary pending-reports retry queue

**Decision:** declined · **Status:** not started · **Area:** suggestion

Allow report URLs delayed beyond the current window to be recovered later using a bounded private queue, without archiving an incomplete or unverified game.

*Notes:* Mitigates RISK-001; not approved or implemented. User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.

### IDEA-011 — Large-scale refactor / additional watchdogs

**Decision:** declined · **Status:** not started · **Area:** suggestion

Additional watchers and a broad architectural rewrite were explicitly deferred in review rather than made a new project priority.

*Notes:* Deferred is not a user rejection; reconsider only with a demonstrated need. User explicitly declined this suggested change on 2026-11-23. It was previously deferred and is now declined. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review.


## Paused infrastructure

Preserved for future reactivation only if requested.

### PRJ-019 — Historical backfill suspended but recoverable

**Decision:** accepted · **Status:** paused · **Area:** retention

Historical backfill workflows no longer run on a schedule. Manual jobs and code remain, guarded by an explicit ENABLE_HISTORICAL_BACKFILL opt-in.

*Notes:* Requires deliberate policy changes before any future historical restoration.

*Implementation evidence:* [.github/workflows/backfill.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/backfill.yml), [.github/workflows/backfill.yml](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/.github/workflows/backfill.yml), [.github/workflows/wnba-backfill.yml](https://github.com/NikkiVeracruz/nba-gamebook-dashboard/blob/main/.github/workflows/wnba-backfill.yml), [.github/workflows/backfill.yml](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard/blob/main/.github/workflows/backfill.yml), [.github/workflows/backfill.yml](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard/blob/main/.github/workflows/backfill.yml)

### PRJ-023 — Independent full 2026 schedule coverage checker

**Decision:** accepted · **Status:** paused · **Area:** quality

Full-season read-only schedule audit was built and passed before forward-only cleanup; its historical workflow is now gated and unscheduled.

*Implementation evidence:* [tests/archive_2026_schedule_audit.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/archive_2026_schedule_audit.py), [.github/workflows/archive-2026-completeness.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/archive-2026-completeness.yml)


## Suggested features / undecided requests

These are NOT automatically approved development tasks.

### REQ-001 — Remove name from public Mega Board URL

**Decision:** not decided · **Status:** not started · **Area:** request

User asked about changing the GitHub Pages URL to remove their name; no deployment/domain change was confirmed.

*Notes:* Treat as an open request for discussion, not a committed implementation.


## Deferred ideas

Deliberately postponed without claiming that the user rejected them.

No entries.


## Known risks and gaps

Report unresolved risks even when all routine workflows are green.

### RISK-001 — Late reports can fall out of current window

**Decision:** acknowledged · **Status:** open · **Area:** known risk

Strict complete-only forward retention may miss a final report if it appears after the game leaves the rolling period.

*Notes:* Do not silently backfill historical games. IDEA-009 is an unapproved possible mitigation.

*Implementation evidence:* [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md)

### RISK-002 — Green workflows do not prove every player statistic

**Decision:** acknowledged · **Status:** open · **Area:** known risk

Official-document and schedule checks verify coverage, source format, and identities, not independent correctness of every statistic.

*Implementation evidence:* [document-verification/README.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/document-verification/README.md)

### RISK-003 — Help text may still describe historical archive behavior

**Decision:** acknowledged · **Status:** open · **Area:** known risk

Mega Board help sidebar includes pre-cleanup historical-search wording. Should be updated to accurately describe forward-only retention without changing approved features.

*Implementation evidence:* [command-center/index.html](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/command-center/index.html), [FORWARD_ONLY_MODE.md](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/FORWARD_ONLY_MODE.md)


## Repository map

| Area | GitHub |
|---|---|
| Mega Board + NFL | [nfl-gamebook-dashboard](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard) |
| NBA + WNBA | [nba-gamebook-dashboard](https://github.com/NikkiVeracruz/nba-gamebook-dashboard) |
| NHL | [nhl-gamebook-dashboard](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard) |
| MLB | [mlb-gamebook-dashboard](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard) |

**Rollback:** Original pre-purge history is preserved on the backup/pre-forward-only-2026-11-23 branch of all four repositories. See [retention and restoration instructions](FORWARD_ONLY_MODE.md).

## How this record stays accurate

1. Add each new user request or assistant idea under a stable ID in project/feature_registry.json; mark not_decided until explicitly approved or declined.
2. When a feature is shipped, change the implementation state only after checking code/workflows/tests; add source evidence and date context.
3. Regenerate this document with python project/render_register.py --write. GitHub automation also regenerates it on registry changes.
4. A scheduled independent check verifies critical runtime/configuration invariants and can raise a GitHub issue for drift. It does not make product decisions, rewrite approvals or restore rejected features.
5. New assistant implementation work should include a corresponding register update, preserving the user-approved scope and reasons for refusals.

## Major decision history

- **Nov 21–22, 2026:** The five-league Mega Board, separate archive/current search, expandable sections, help sidebar, calendar monitoring and rollovers were added; standalone data feeds were retained.
- **Nov 22:** The user explicitly removed all NCAA dashboards.
- **Nov 23:** The user removed the unnecessary visible data-staleness monitor. Independent 2026 game coverage and document audits were implemented.
- **Nov 23, later:** The user superseded older season-restoration decisions, moved to complete-only current/new game archives, halted old backfills and removed old historical/unverified links from active data.

**Historical reconstruction limit:** This inventory was assembled from available conversations and code, not from a guaranteed exhaustive export of every earlier message. Anything without a substantiated approval stays not_decided. From this point onward, new decisions should be recorded here.
