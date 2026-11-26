# Mega Board — Master Project Register

**Status reviewed:** 2026-11-23 · **Canonical data:** [project/feature_registry.json](project/feature_registry.json)

> This page is generated from the canonical registry. Automatic checks must not accept, reject, or supersede user decisions.

## Purpose and scope

One fast, accurate place for customer service agents to find game/team/player reference data and official league reports.

**Leagues:** NFL, NBA, WNBA, NHL, MLB. **Board:** [Mega Board](https://nikkiveracruz.github.io/nfl-gamebook-dashboard/command-center/).

**Operating direction:** Forward-only collection from November 23, 2026: keep live scheduled and active game views, archive only completed games with all required official reports, and store new complete games going forward. Keep dormant historical infrastructure but do not backfill historical seasons.

**Authority rule:** Later explicit user decisions supersede older plans. Recommendations are not approved unless the user accepts them.

## Status overview

**56 tracked items:** 33 implemented · 7 paused · 3 removed · 0 proposed · 0 deferred · 9 not started · 4 open

| State | Meaning |
|---|---|
| Implemented | Evidenced in code or configuration, not an uptime guarantee. |
| Paused | Preserved but intentionally inactive/restricted. |
| Removed | Deliberately removed; do not reinstate without approval. |
| Proposed | An idea not yet approved to implement. |
| Not started | Work not deployed; decision may be accepted, declined, or undecided. |
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

### NCAA-POC-001 — Separate NCAA Stats contest-link proof of concept

**Decision:** accepted · **Status:** implemented · **Area:** research

A strictly isolated, read-only NCAA contest-ID link matching proof of concept has been implemented in a separate repository for FBS/FCS football and Division I men's/women's basketball. It discovers ESPN games and joins to published SportsDataverse NCAA contest IDs without scraping NCAA Stats/gamebooks, collecting player stats, backfilling, scheduling runs, publishing a board, or altering the five-league Mega Board. Source latency and destination-page verification remain unresolved; this is NOT an operational NCAA dashboard.

*Notes:* Approved 2026-11-23 and implemented as an isolated read-only feasibility tool in https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/1 (squash merge f438dd8ed6f6d638a82bff456c2dc7bb01201f7d). Latest applicable pre-merge safety workflow completed successfully: https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45285894447 ; ten offline unit tests passed plus live source trials for four one-day samples. Source-ID match observations: 2026-11-12 81 of 81 games; 2026-11-14 237 of 244; 2026-11-21 0 of 225; 2026-11-22 0 of 101. This is an apparent ID-crosswalk publication lag, NOT proof the latest games lack an NCAA box score. Generated NCAA Stats URLs are explicitly unverified and require human browser identity checks, as the site was inaccessible to this automated environment. Link coverage and delay must be tested over time before any dashboard approval; no production NCAA dashboard, historical import, scheduled feed, Pages deployment, NCAA gamebook scraping or player-statistics collection exists. The existing DEC-001 NCAA removal remains in force for the old NCAA boards, and all five original league repositories/pages, archive rules, and monitoring remain unchanged. The earlier local-only seven-test ZIP was superseded by the now-merged ten-test GitHub source; state=implemented describes the research proof ONLY, not a deployed board.

*Implementation evidence:* [ncaa_poc.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/ncaa_poc.py), [tests/test_poc.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/tests/test_poc.py), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/.github/workflows/pre-merge-safety.yml), [.github/workflows/probe.yml](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/.github/workflows/probe.yml), [README.md](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/README.md)

### NCAA-RESEARCH-002 — Isolated NCAA contest-ID reliability investigation

**Decision:** accepted · **Status:** implemented · **Area:** research

Completed isolated NCAA contest-ID feasibility research; timely verified game-specific links were not achievable. User superseded the link-discovery goal with official sport/division scoreboard navigation on Nov 23; preserve research evidence, do not continue individual link work without approval.

*Notes:* NCAA PR #2 merged after 14 offline tests and 12-day live-source baseline passed: https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45287965739 . Snapshot November 23: zero matched IDs for 743 discovered games November 18–23; November 12–17 had high coverage. Diagnostic implementation complete; reliability investigation remains open. User approved actively resolving the gap before production. Upstream raw schedule datasets identified as candidates; freshness, access/reuse and exact identity remain unverified. No NCAA deployment, historical backfill or five-league production changes. On November 23 user approved the ordered expanded research roadmap: repair raw schedule experiment; investigate advance IDs; test NCAA.com; evaluate university platforms; investigate authorized access (no outreach or purchase authorized); extended per-sport trials; only then build standalone board if reliability and permission gates met. NCAA Stats remains preferred; official NCAA.com and university links may be evaluated as potential fallbacks, not yet approved for publication independent of validation. PR #3 first experiment: 17 tests passed, but zero basketball usable keys and unsupported football schema, so no recovery demonstrated (https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45289961523). PR #3 remains open; repaired direct football ID/date matching, row-level date and ID diagnostics, older positive controls, conflict gate and future-date sampling committed on branch; latest CI pending. No existing production changes. User approved addressing all diagnostic recommendations after failed runs 45290896104 and 45290920539. Grouped commit 752ebaebd44c9b2d6b2159a916b25f7f53d0479f on NCAA PR #3 fixes actual date formats, uses same-season team reference files, rejects conflicting IDs, tests alternative master and release schedules, always runs safety invariant. Latest run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45291733912: 21 offline tests passed; 10,622/10,622 MBB and 9,465/9,465 WBB raw schedule dates parsed, team mappings 365 MBB/363 WBB, but 4 MBB contest rows (2 unique matched keys) and 0 WBB contest rows. Published MBB schedule latest Nov 18 (one ID that date), WBB latest Nov 17; master indexes have contest_id/season/captured but no date or team keys. Football 115 older known-ID agreements, latest contest Nov 17; no recent or advance candidates recovered. Basketball controls failed (exit 3), safety invariant passed, PR remains unmerged. No source failure notifications suppressed. NCAA.com manual scoreboard research initiated; production use and permitted automation not established. No league functionality changed. NCAA.com independent-source review on November 23: four public scoreboards exist; henrygd/ncaa-api README and scoreboard source expose contest IDs and game URLs, but recent date-specific coverage, NCAA Stats ID equivalence, and detailed report completeness are unverified. NCAA.com terms https://www.ncaa.com/tos section 8 require written permission for commercial links and restrict permissible sites to homepage links; NCAA.org https://www.ncaa.org/terms-of-service/ restricts commercial use and unauthorized automated collection. No automated NCAA.com requests, provider integration, or publishing authorized by this review. Recommended next decisions: seek explicit permission or a permitted lightweight identifier/link feed through NCAAstats@ncaa.org and operator contact, check employer-authorized data resources without public redistribution, and evaluate independently permitted university sources. No outreach sent, no paid services, no production changes. PR #22 merged after successful safety checks; PR #3 remains unmerged. Readable register renderer omitted accepted open research items; add targeted rendering fix and regression test so pending decisions remain visible. User approved continuing public link-only data research on the understanding that the board is independently operated, free, public and non-revenue-generating, and approved university/conference evaluation and NCAA inquiry preparation. This is a user scope decision, not legal authorization from providers; no circumvention or unsupported claim of permissions. Nov 23 manual public-source research located game-specific official American Conference (Tulane–North Texas and Navy–Memphis, Nov 21), Big Sky (Montana State–Montana and Northern Arizona–Northern Colorado, Nov 21), UAlbany (North Carolina A&T, Nov 21), Utah (Minnesota, Nov 22) and Texas (Ohio State, Nov 22) pages across FBS/FCS/MBB/WBB. Utah's schedule includes the exact game-center and detailed box-score URLs for Nov 22 and a game-center link for scheduled Dec 2 (advance university identifier, not NCAA Stats ID). Conference pages use opaque boxscore.aspx identifiers; do not synthesize them. SIDEARM and WMT offer common athletics website infrastructure; Presto supports NCAA schedule integration but not an established public contest-ID feed. Conference-first and school fallback discovery remain proposals requiring bounded automated feasibility tests and source-specific terms review. NCAA Stats contact NCAAstats@ncaa.org confirmed via https://www.ncaa.org/championships/media-center/; inquiry draft prepared for user review, not sent. No feed added, no new public board, no historical archive or five-league changes. Governance PR #23 merged after passing safety run 45292452699; readable register publication verification pending. Latest explicit user scope reaffirmation Nov 23: do not contact NCAA; inquiry/outreach declined. Proceed with public data research, link-only to the original stats.ncaa.org game-specific page, not substitute university or NCAA.com box scores. Standalone NCAA board to resemble existing boards: FBS/FCS and D-I MBB/WBB all conferences/independents, upcoming/live/recent completed, score and game time, forward-only archive of all completed games with missing link status and later enrichment (NCAA-only; professional complete-report rules unchanged), current-view rollover timing undecided. No gamebooks, player/detailed team statistics, or backfill. Use host school as priority authority to confirm game identity/results; actual host may differ at neutral sites. Research found official NCAA.org scoreboard links https://stats.ncaa.org/contests/scoreboards?division=11&sport_code=MFB (FBS), division=12&sport_code=MFB (FCS), division=1&sport_code=MBB and division=1&sport_code=WBB; all four returned HTTP 403 in the automated web environment. Documented season-division date scoreboard parser returns contest IDs, but cloud access remains unproven. Next proposed task (awaiting review approval): one ordinary-browser source validation, then bounded direct NCAA date-index link-only feasibility test where access permitted, cross-check ESPN and actual host school, no access circumvention. Retain proven discovery and diagnostics; keep failed PR #3 unmerged; no production changes. NCAA Stats is sole required destination. Prior university/conference fallback publication and outreach proposals superseded. User supplied browser screenshot and saved FBS scoreboard and BYU–Kansas box-score HTML from Nov 21; local reader extracted 58 unique contest links, all entries with two team IDs and scores, and verified saved contest 6601304 team IDs/date/score. User approved direct reader and bounded cloud test. NCAA PR #4 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/4 commit 4839cb33111040b46994b84bca998f4b94b4347b adds direct_ncaa.py, six synthetic test cases, pinned HTML parser, read-only direct FBS experiment on existing PR checks. Raw browser exports not committed; no scripts executed or session tokens reused. Run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45296488801: 20 offline tests passed, original comparison/baseline checks passed, direct retrieval failed with HTTP 302 redirect loop (urllib stopped), diagnostic artifact and isolation invariant passed. No additional denial retries or bypass, PR #4 not merged, no production/scheduled retrieval, archives, backfill, or professional board changes. FBS offline extraction proven, not cloud access or all-game destination validation. FCS/MBB/WBB HTML layouts and coverage untested. Recommend comparing independently available NCAA.com contest identifiers to the known NCAA Stats IDs as a possible discovery source only, not replacement destination; if not equivalent, pursue other permitted ID feeds or user-initiated HTML import as a temporary option, subject to approval. No NCAA outreach. PR #25 merged and readable register confirmed; prior production Pages deploy 45295275086 success. On November 23 user explicitly approved next research steps 1–3: NCAA.com ID equivalence, alternate public original Stats ID sources/advance IDs, and FCS/MBB/WBB saved scoreboard format validation; steps 4–7 (integration, full tracker, extended trial, deployment) remain unapproved proposals. Retrieved original browser HTML via Library text reads (raw materialization unavailable); independently extracted 58 unique Nov 21 FBS IDs with two teams and scores. NCAA PR #5 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/5 head ac3d0051dba68934bc5762cd6162e4a0bb68ed49 adds minimal reference JSON, read-only comparison of documented public henrygd NCAA.com demo route (one bounded GET, no redirects/retries, no Stats access), eight synthetic regression tests, original CI checks preserved, isolation check always runs. PR diff reviewed; validation run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45300907308 completed successfully: 22 offline tests passed, all prior comparison/baseline checks and isolation passed; live demo returned 70 games, 58 eligible Nov 21 finals, 12 other/unknown-date records. All 58 references uniquely matched on date, names and scores; all 58 NCAA.com IDs differed, zero equal, zero ambiguous/unmatched. Examples BYU–Kansas Stats 6601304 vs NCAA.com 6604064; Ohio State–Nebraska Stats 6617031 vs NCAA.com 6604337. No direct substitution; no reliable independent mapping established. PR #5 remains unmerged as evidence, not a viable integration; avoid adding a recurring dependency on the demo. A green comparison means successful research, not identifier equivalence. NCAA.com publicly visible scoreboards and Nov 21 schedule corroborate sample scores but retrieved text lacks numeric identifiers; web tool could not access demo JSON. API operator publicly documents demo use; underlying data reuse rights remain unresolved, no production permission claimed. Separate third-party PR https://github.com/henrygd/ncaa-api/pull/10 shows Stats team schedule/ID fetching is separate and unmerged, not evidence of equivalent IDs. Exact-ID and university link searches yielded no new validated independent feed. Public documentation indicates pregame LiveStats IDs exist for operators (https://www.daktronics.com/en-us/support/kb/000031050), but equivalence to Stats contest IDs and public availability are unproven; no credentialed access, scraping workaround or paid feed proposed. SportsDataverse remains delayed candidate only. FCS/MBB/WBB actual HTML layouts remain untested; request saved browser scoreboard source for same day all conferences for each, and optional advance date example, only for offline validation. No raw HTML/tokens committed, NCAA outreach, production data, professional board changes, backfill, or deployment. NCAA PRs #3 and #4 remain unmerged. Nov 23 user supplied four browser-saved HTML files; local BeautifulSoup read-only inspection of actual scoreboard tables (no script execution, network requests or publication) found consistent three outer rows per game across all four sports. FCS Nov 21: 62 games, 62 unique actual box-score anchors, both scores and both team IDs on every row. MBB selected Nov 23 (not Nov 21): 46 games (45 dated Nov 23, one Nov 24 midnight), 17 unique box-score links with both scores, 29 blank-score/no-link rows, five games with one plain-text opponent lacking team link (two of those have box-score links), 22 nonblank neutral/tournament fields. WBB selected Nov 23: 37 games, 16 unique box-score links with both scores, 20 blank-score/no-link rows, one both-scores/no-link row, one game with plain-text opponent, 14 nonblank neutral/tournament fields. FBS Nov 28: 53 scheduled rows, all with both team IDs, no scores, no box-score links or numeric contest paths anywhere in saved source; does not establish IDs are unassigned or absent from all other pages. Total 198 rows, 95 unique within-page box-score anchors across these four files; not independent destination verification or discovery coverage. 2026–27 selected season-division IDs FBS 18904, FCS 18905, MBB 18983, WBB 19003; sport-year control IDs football 17161, MBB 17240, WBB 17260. Existing PR #4 parser is FBS/date-specific and rejects these legitimate plain-text, blank-score and next-day rows; future parser should preserve missing team IDs and scores as null, distinguish selected scoreboard date from row timestamp, retain unresolved identity and not infer final status solely from a score or anchor. No raw HTML/session tokens copied to GitHub. No runtime changes or new production workflow. Recommended next bounded manual research: inspect one official upcoming host-team season schedule (e.g. Ohio State for Michigan Nov 28) for actual game-specific contest IDs; independently measure SportsDataverse catch-up when new snapshots exist; no repeated denied requests, no bypass, no outreach. No extra user approval implied for production or manual import. Follow-up Nov 23: user supplied Ohio State official Stats team page (team 622207). Local read-only BeautifulSoup analysis of the Schedule/Results table found 12 games, all 11 played rows have unique numeric box-score links, and Nov 28 Michigan (team 622188) has scheduled time 12:00 PM but blank result/attendance and no game-specific ID or link in row attributes or descendants. Only 11 numeric contest paths in entire saved document. Nov 21 Nebraska link 6617031 and result Ohio State L 28–31 match original FBS scoreboard control. No evidence of pregame contest IDs from either public scoreboard or this team schedule; does not establish unassigned IDs or universal absence. Team schedules may corroborate completed identities, not demonstrated timely automated source. PR #28 passed all safety checks and merged c4342c6204a2bdb7c000052c2951dd3e89d5ccd9. No raw files, tokens, backfill, deployment or runtime changes. Recommend stop speculative pregame searches, next bounded research phase (not yet approved): remeasure SportsDataverse lag against actual saved official references, assess safe forward-only tracking with pending links and explicit source/verification indicators, or discuss user-approved alternative link-only navigation fallback if necessary. No assumption of automated Stats access, no circumventing access restrictions. Full production and fallback implementation require approval. User explicitly approved next three research steps Nov 23: remeasure SportsDataverse catch-up, assess combined ESPN tracking/crosswalk link discovery with identity verification, evaluate customer-service timeliness. Not approval to deploy, relax identity verification, implement fallback, schedule recurring research, or alter existing professional boards. PR #29 safety run 45304639471 passed, merged 1eb680387e234c5c881007bed10b2ac8241f1209 and generated register confirmed. New isolated NCAA PR #6 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/6 head 4e81cf78b0a748325b8c6f77eacf3f6c3d4a2161 reuses 12-day Nov 12–23 baseline with cached releases, completed-game denominators and exact normalized ESPN source aliases/date/scores compared against 153 saved linked rows (149 distinct family+ID keys; 4 FBS/FCS crossovers). Eight new regression tests, no raw HTML, no live Stats requests, no archives, no changes to existing tracking. Diff reviewed; CI run 45304801979 completed successfully, all 22 offline tests and prior checks passed, no source errors. Retest at 2026-11-24 01:24 UTC (Nov 23 Mountain): all three crosswalk release SHA256 hashes identical to baseline run 45287965739; no catch-up. Nov 12–17 708/720 completed games had candidate IDs (98.3%; all-game count 708/727). Nov 18–23 0/694 completed games had candidates (all-game count 0/743), daily completed denominators 140,87,106,225,100,36. Saved reference comparison 124/153 rows uniquely identity-matched but no candidate ID (FBS 52, FCS 44, MBB 15, WBB 13); 29 unmatched under strict aliases/date/final scores (6,18,2,3 respectively); zero actual candidate IDs to verify for these dates, not evidence of perfect accuracy. No exact publication lag can be estimated, but missing Nov 18 games are several days old. Combined architecture feasible in principle for tracking, unacceptable timely link coverage in this sample; do not deploy as a complete solution. PR #6 remains unmerged research evidence. Next options for user decision: continue bounded observation of release updates (not a new watchdog), consider explicitly labeled official date-scoreboard navigation as fallback (not individual game link), or manual import only if expressly approved; no fallback implementation or production approved. Candidate ID coverage is not page verification. Recommended design: game discovery and link enrichment independent, stable sport+source game ID, preserve all completed games forward only including missing links, never promote a candidate without independent match of teams/date/sport/ID/scores and destination verification, quarantine ambiguous/conflicting IDs, no routine manual work assumed; require timeliness evidence before production. Prior target 95% verified links within 6 hours remains proposed evaluation target, not approved SLA. A single re-observation cannot estimate exact per-game publication time. Nov 23 user approved investigating all alternative sources (research only). Reviewed public provider documentation: CFBD ESPN game IDs (https://github.com/sportsdataverse/cfbfastR-cfb-data/blob/main/DATASETS.md); CBBD own IDs and ESPN source_id (https://github.com/sportsdataverse/hoopR/blob/main/vignettes/cbbd-college-basketball-data.Rmd), shared 1000 monthly free calls; BALLDONTLIE, Sportradar, SportsDataIO no documented stats.ncaa.org contest ID mapping found; no live credentialed calls, accounts or purchases. NCAA.com IDs previously disproven. ncaahoopR ESPN-based; bigballR directly retrieves Stats pages, not a fresh independent published source; commercial Parse Stats API claims contest IDs but limited credits and same source access/rights unresolved, not pursued; Apify NCAA.com scoreboard not verified as Stats ID source. SportsDataverse status https://www.sportsdataverse.org/status reports football linescore/team/player stats assets Nov 23, schedule Nov 19, NCAA hoops schedules/team boxes Nov 18; tag timestamps not game coverage. Documented linescore includes contest_id and espn_game_id (https://py.sportsdataverse.org/docs/cfb/reference/loaders/ncaa). Isolated NCAA PR #7 head 1ea86c6fdb490d42fc479509a929ff1d93ba2d93, read-only tests 5 published parquet assets: football linescore 2026, MBB/WBB schedules and team boxes 2027; compare date/ID intersections against saved 153 reference rows and exact ESPN ID candidate coverage with baseline. No raw HTML, direct Stats requests, production writes, backfill, or deployment. CI run 45307701729 pending final live result; offline tests passed, diff reviewed, no merge until validated. No independent free timely replacement confirmed. Central PR #30 merged e7a745383b5b6eea787a5be5cc38c08abb5ee9b4; prior observed dates Nov 16 65/65, Nov 17 108/117, Nov 18–23 zero candidates in run 45304801979. Daily scoreboard fallback remains proposed, not approved.  First live alternate assets run 45307701729: 15 tests passed; football linescore 11234 rows, exact ESPN mapping Nov14 FBS54/55 FCS61/62, no extra candidates vs schedule, Nov21 FBS0/58 FCS0/62. MBB schedule 954 rows and WBB 940 rows; date parser incorrectly assumed ISO, actual MM/DD/YYYY; cannot claim validated date/reference results from first run. Team boxes lack date field, first live probe failed schema assertion. Fixed parser to normalize MM/DD/YYYY and accept date-less team-box exact ESPN mapping without claiming date verification; added regression test. Latest NCAA PR7 head 0ffcf4f679382cb2a2764f9e8e96b0dc5d3aab95 validation pending, do not merge incomplete work. Final alternative-assets validation run 45307832843 successful (16 regression tests; safety checks passed); football linescore latest Nov17, MBB schedule latest Nov18 (one ID), WBB schedule latest Nov17; basketball team boxes provide no date, Nov14 exact ESPN candidates 67/68 MBB and 55/55 WBB, no Nov21 or Nov23 additions. No additional IDs over baseline. NCAA PR7 retained as research evidence, not merged. Central PR31 passed 45307847421 and merged 9bbc517cab53e9dc1a125f9e501e7237dd6d1dd5. User Nov23 explicitly redirected project: abandon game-specific data/link discovery and instead accurately display all games with official overall sport/division scoreboard links and instructions for locating the game. This supersedes prior individual contest-ID goal; no SportsDataverse requirement, no automated NCAA Stats scraping, no individual link enrichment. Prior research preserved; do not continue unless separately approved. Standalone preview only, no deployment or integration approved. See NCAA-NAV-003.

*Implementation evidence:* [ncaa_poc.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/ncaa_poc.py), [README.md](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/README.md), [reliability_probe.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/reliability_probe.py), [tests/test_reliability.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/tests/test_reliability.py)

### PRJ-027 — Bounded retries for existing NFL backup watchdog

**Decision:** accepted · **Status:** implemented · **Area:** operations

User approved on November 24, 2026: retry transient HTTP server errors in the existing NFL backup watchdog at 5 and 15 seconds after unsuccessful attempts, with a maximum of three attempts; retain normal failure notification if exhausted. No cadence, dispatch guard, archive policy, or other monitoring changes.

*Notes:* Incident run45336913795 failed Nov23 22:57 MT with raw GitHub feed HTTP503 Backend.max_conn reached before any dispatch; regular update run45340804928 subsequently passed including archive-loss guard and publication. Watchdog run45345950698 retrieved healthy feed (41 minutes), run45357468731 reported idle; governance Nov24 12:13Z passed, 13 NFL archived games. Approved bounded retry implementation on task branch: retry HTTP 500/502/503/504 only, wait 5 then 15 seconds, preserve 25-second per-request timeout and 2MB cap, rethrow persistent errors and reject invalid feeds immediately; existing main failure handling and notifications remain. Seven new offline regression cases and pre-merge integration added. Validation, merge and production execution pending. Final pre-merge safety run https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45414858015 passed all seven offline retry tests and all existing checks; reviewed diff limited to watchdog fetch, tests, CI and registry. PR41 merged 5b66620952a127a16c03b77d6fe31c595408e290. Code implemented on main; first post-merge watchdog run not yet observed, real-world transient recovery not yet demonstrated. No scheduling or notification changes. Register regeneration and Pages runs started after merge.

*Implementation evidence:* [tests/nfl_update_watchdog.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/nfl_update_watchdog.py), [tests/test_nfl_watchdog_retry.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_nfl_watchdog_retry.py), [.github/workflows/pre-merge-safety.yml](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/.github/workflows/pre-merge-safety.yml)


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

*Notes:* High-value strategic opportunity, not implemented; availability/rights/API accuracy must be evaluated before committing. User explicitly declined this suggested change on 2026-11-23. It was proposed but never approved. Do not implement or proactively suggest it again; reconsider only if the user explicitly requests a review. Dedicated player-statistics search, indexing, dashboards, tables and analysis are not a project need and must be excluded from future feature ideation; existing official report contents are unaffected. Batch decision documentation and validation: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/pull/15 ; read-only pre-merge safety checks passed (report-status, search, archive retention, register and drift safeguards): https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45278116856 ; generated master register succeeded: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45278203040 ; post-merge GitHub Pages succeeded: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45278265857 . An early governance run failed only because it checked while the generated Markdown was still outdated: https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/runs/45278203204 ; logs established the mismatch, which has since been resolved by generator output; an independent post-generation governance audit remains pending. No source feeds, official reports, archive or user-interface behavior were changed; other declined proposals share this PR and evidence. Governance regression checks were adjusted to distinguish never-started rejections from removed/paused features without weakening safeguards.

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

### NCAA-NAV-003 — Standalone NCAA game tracker with official scoreboard navigation

**Decision:** accepted · **Status:** paused · **Area:** research

User chose accurate scheduled/live/completed game display for FBS, FCS and Division I men's/women's basketball, with links to official NCAA sport/division scoreboards and instructions to locate matchup and Box Score. No individual contest links or statistics collection; no dependency on SportsDataverse. Forward-only completed game archive, no historical backfill. Separate NCAA repository; no professional board changes or integration approved.

*Notes:* User decision Nov 23 2026: abandon game-specific data, display games accurately, provide specific overall sport/league tracker links with navigation instructions. Interactive illustrative chat mockup based on Nov21 observed 225 unique completed ESPN games, categories 58 FBS/62 FCS/57 MBB/52 WBB; only examples BYU-Kansas and Ohio State-Nebraska shown. Four known sport-level URLs https://stats.ncaa.org/contests/scoreboards?division=11&sport_code=MFB (FBS), division=12&sport_code=MFB (FCS), division=1&sport_code=MBB and division=1&sport_code=WBB. User-browser access and date-specific selection across four categories still require validation; do not imply a box score has been published. Proposed next approved-stage work subject to user design approval: independently validate daily discovery identities, completeness, scores and status against official saved scoreboards across dates; test date/time boundaries, cross-division dedup, neutral sites, non-DI opponents, outages, cancellation/postponement, team aliases; agree rollover/refresh and archive start date; implement branch-first standalone tracker only. No direct Stats access attempts, no individual-link work, no new paid service, no historical backfill, no deployed changes. Existing five pro leagues preserved. User approved Nov 23 exploration of official university game-specific box-score links as a new alternative (not resuming NCAA Stats ID discovery); NCAA scoreboard navigation remains fallback. See NCAA-UNI-004. Nov23 user approved initial standalone tracker implementation with school schedule/homepage shortcuts and official NCAA scoreboard navigation, optional reviewed direct box-score links. Completed games archive regardless of report availability in NCAA only; not a change to five pro leagues. See NCAA-TRACK-005.
November 25, 2026: User explicitly paused all standalone NCAA development and tracking, without deletion, to reconsider strategy. No resumption, expansion or historical catch-up without explicit new approval.

*Implementation evidence:* [ncaa_poc.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/ncaa_poc.py), [README.md](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/README.md)

### NCAA-UNI-004 — Official university game report link feasibility

**Decision:** accepted · **Status:** paused · **Area:** research

Approved isolated research for official school-hosted individual game links: home/hosting school preferred, visiting school or neutral host fallback, official NCAA sport/division scoreboard fallback. Track games independently; verify sport/date/teams/final score and report type; assess football participation and basketball minutes/DNP visibility. No stats extraction/storage, no SportsDataverse requirement, no backfill, no production or integration approval.

*Notes:* Nov 23 2026 approved start of six proposed university-link research steps. Central prior direction PR32 passed run45308381824, merged 0c505c16e39d54f1e51108bbb0e9bbb61b19cd45. Pinned ncaapyscraper 0.2.0 source commit ecbe9a9518e0fbad42c516a428dffd37405448fe schools.csv MIT license retained; 977 rows, 356 DI: 157 SIDEARM,167 legacy,29 WMT,3 WordPress; 136 FBS and 122 FCS labels, 98 other DI; unvalidated against current membership and sport sponsorship. Public separate 1359-school directory found, not adopted pending licensing. Package inspected LICENSE, pyproject and __init__; own box-score function targets NCAA.com, not university reports; no package installed/executed. Latest data release Nov16, not current. SIDEARM terms noncommercial language https://sidearmsports.com/sports/2022/12/7/terms-of-service and Nebraska WMT terms https://www.iubenda.com/terms-and-conditions/73394775 reviewed preliminarily; code license not access/reuse authorization; business-use applicability and each school/robots/interface review remain open. No school bulk automated requests or bypass. Independently web-inspected four Nov21 official report controls: Nebraska Ohio State 31–28 https://huskers.com/boxscore/21833 (schedule corroborates result, participation not confirmed); Montana State Montana 42–16 https://msubobcats.com/sports/football/stats/2026/montana/boxscore/6242 (participation tab); Wofford Winthrop 91–86 https://winthropeagles.com/boxscore.aspx?id=24088&path=mbball (away report, minutes); Duke Columbia 71–47 https://gocolumbialions.com/sports/womens-basketball/stats/2026-27/duke/boxscore/15598 (minutes). Not automated discovery or proof of DNP completeness. NCAA PR8 head 9f2630fa4fee263700b1674931cc52c3ca068a07 read-only one-date directory matching against ESPN and four control identity/domain checks, 4 targeted regression tests, no school requests or publication. Validation pending. Next: quantify directory mapping, verify official school domains, review permitted schedule retrieval (or published link-only datasets), measure full 225-game link coverage and latency with independent controls; no deployment approval. Initial live pilot run 45309394832: 18 regression tests passed, all safety steps succeeded, 225 unique completed ESPN IDs, 229 category entries including crossovers; FBS 58 completed/45 home directory candidates/53 either school/40 both; FCS 62/57/61/47; MBB 57/43/51/30; WBB 52/40/51/33. Total category entries 185 home candidates and 216 either-school candidates; not deduplicated coverage, not verified domains or automatic report discovery. All 4 independently reviewed control URLs matched game sport/date/team/final-score identity and directory host, no source errors. Actual ncaapyscraper api.py confirms get_boxscore takes NCAA.com game ID; SIDEARM/WMT platform source inspection shows no boxscore link extraction. No third-party package executed. PR8 kept as isolated research evidence (not deployed); further research required to map missing aliases/domains and discover published report links across all games via permitted sources, then evaluate actual publication latency and report completeness. Nov23 user approved continuation of next research steps. Prior central PR33 validated run45309518001, merged 1699aca248a13863abfd3be70d78aec343ca5338, generated register verified. NCAA PR8 validated run45309394832 and merged 08ac02491f8aadca17ae812c395e76de8833b5d3 (research only). Downloaded own diagnostic artifact 14882402204; 13 category entries with neither school resolved. Added exact team aliases, independently evidenced missing Colgate directory entry, 13 new manually public-web-reviewed official report references covering each formerly unresolved entry (5 FBS,1 FCS,6 MBB,1 WBB). All 13 pages found with matching final scores/date/sport; total 17 controls (6 FBS,2 FCS,7 MBB,2 WBB). Added participating-school requirement, exact alias conflict regression, unique ID denominator. NCAA PR9 head e455fc8e4791434a4b21701c7408bf15e0692b34 safety run45310368858 completed success, 19 tests passed, no source errors, 225/225 unique ESPN games with at least one directory candidate; category home/either/both: FBS58/58/56 of58; FCS60/62/58 of62; MBB55/57/48 of57; WBB50/52/48 of52. 17/17 reviewed links matched. Candidate directory resolution is not verified domain completeness or automatic individual link coverage. Public browser schedule navigation confirmed SIDEARM Sam Houston https://gobearkats.com/sports/football/schedule -> https://gobearkats.com/sports/football/stats/2026/middle-tennessee/boxscore/15549 and WMT UTSA https://goutsa.com/sports/mens-basketball/schedule -> https://goutsa.com/boxscore/8943, actual published links not guessed. Football App State/Nevada/NCA&T reports contain participation sections; NCA&T home starter tables blank so completeness cannot be inferred. Sam Houston/UAB/UNLV individual participation tabs and starter lists present; no DNP completeness claim. No automated school-site retrieval, no player data collection, no historical backfill, no deployment, $0. Remaining: establish permitted link retrieval method, test full-day report coverage and report latency, verify basketball and football participation completeness; no production changes. Nov23 user approved proceeding to automatic report discovery. Prior register PR34 validated run45310509804 and merged 5179e454fb0b7673432b6c522bf20e0e414d794d. Four official public page navigation observations: Sam Houston football schedule -> boxscore/15549 confirmed Middle Tennessee 31–28 final, individual participation; Montana State football schedule still showed Nov21 Montana as upcoming in retrieved page, visiting Montana recap https://gogriz.com/news/2026/11/21/football-second-half-surge-leads-cats-over-griz -> https://gogriz.com/sports/football/stats/2026/montana-state/boxscore/5262 confirmed Montana State 42–16 and participation; UTSA MBB schedule -> https://goutsa.com/boxscore/8943 shows correct matchup in page title but destination requires JavaScript, no independent final-score verification; Columbia WBB schedule -> boxscore/15598 verified Duke71–47 and minutes. Public web observations only, not automated retrieval. Reviewed SIDEARM terms https://sidearmsports.com/sports/2022/12/7/terms-of-service (school footer links; noncommercial language), WMT UTSA footer lacks clear general terms in retrieved page; authorized business-use automated retrieval remains unresolved. Investigated Pushbuild https://pushbuild.com/apis/college-sports-data.html explicitly offers school boxscore link field but weekly refresh, key required, $1 monthly credit/4166 rows then $0.24 per 1000; no purchase or credentials, not suitable timely free source. NCAA PR10 head 3ec6c07ed44df78958d4e76db20f51cffcb32cb8 adds normalized independent public source observations (not raw HTML), replay selection against live ESPN identities, home-first/away fallback, HTTPS exact school host, explicit box-score label, final destination identity, ambiguity suppression; 10 new targeted tests. No school HTTP requests, no live discovery claim, no deployment/backfill. CI pending. Remaining gate is a permitted current automated source acquisition method; no bypass, no paid service. Full 225-game automated retrieval and latency not tested. Final NCAA run45310934633 completed success, 29 offline tests passed, all prior and safety checks succeeded; live ESPN replay selected reviewed FBS Sam Houston home ID401871081, FCS Montana away ID401868117, WBB Columbia home ID401915910; MBB UTSA ID401911337 candidate withheld due unavailable independently reviewed destination. 3/4 reviewed destination matches; 4/4 link observations; neither measures automated retrieval coverage. PR10 merged as research only; no school acquisition implementation or deployment. Recommend evaluating public authorized school syndication/link feed or explicitly approved schedule-link-only fallback; no assurance such feed includes box scores. User has not approved paid service, new recurring automation, or school-site bypass. Nov23 user clarified automation need not reach 100%; human agents already know alternate methods. Stop treating complete automated individual report discovery, participation analysis, or publication latency measurement as launch prerequisites. Optional direct links only when legitimately sourced and reviewed; school schedule shortcuts immediately useful. Retain research; no further acquisition experiments required for initial tracker. Prior register PR35 validated run45311030011, merged c072bc4ea167c5a3060762e35792e854ad1529be.
November 25, 2026: User explicitly paused all standalone NCAA development and tracking, without deletion, to reconsider strategy. No resumption, expansion or historical catch-up without explicit new approval.

*Implementation evidence:* [university_probe.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/university_probe.py), [research/UNIVERSITY_RESEARCH.md](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/research/UNIVERSITY_RESEARCH.md), [research/university_controls.json](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/research/university_controls.json), [tests/test_university_probe.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/tests/test_university_probe.py)

### NCAA-TRACK-005 — Practical standalone NCAA tracker and official navigation shortcuts

**Decision:** accepted · **Status:** paused · **Area:** dashboard

Approved standalone game tracker for FBS/FCS and DI men's/women's basketball. Prioritize useful accurate navigation for trained agents over exhaustive automation. ESPN current games, optional reviewed direct box-score links, school sport schedule shortcuts/homepages and NCAA scoreboard fallback, forward-only completed game archive independent of links. No player statistics collection, no SportsDataverse runtime, no paid sources, no historical backfill, no professional Mega Board changes.

*Notes:* User approved start making change Nov23 2026 and clarified tool is a convenience for trained agents who retain their usual verification methods; full automation is not a requirement. Apply this practical design principle to future feature decisions without weakening factual accuracy, existing pro safeguards, or requiring routine manual maintenance. NCAA PR11 head f39f05d7a29e15bbd7852afe0c7b9eecd487fe0b staged ESPN-only current game collector, stable family+ID dedup, live/scheduled/final distinctions, current today/yesterday ET, explicit first-run cutoff today, atomic feed with completed archive and no historical imports, school directory schedule shortcuts labeled unverified, home and away athletics websites, NCAA division scoreboard navigation, optional empty reviewed_reports.json, search/filter and collapsed groups, archive hidden until team/date search, instructions, refresh preview data every minute. No school HTTP requests or deployment, no pro board code changes. Existing pre-merge research safety checks retained, 12 targeted tracker unit tests added plus live disposable preview artifact and JS syntax check; validation pending. Preview browser refresh is not a scheduled producer; production activation and final rollover policy remain outstanding. No claim of all-game completeness or verified schedule URL coverage. No personal employment details recorded. Final NCAA validation run45312022945 completed success: 41 offline tests, all prior research checks, Python compile, Node syntax check, disposable real-data preview and safety invariant passed. Preview generated Nov23 ET, 184 current-window games, 182 with at least one schedule shortcut, 62 completed archive records from initial date, zero reviewed direct reports. No actual production archive seeded. NCAA PR11 merged 275693493a4933f85efd5c0c6798747125d5ca8c; staging code implemented, deployment and scheduled refresh not yet enabled. Known preview limitations: schedule shortcuts based on common site paths are not individually verified, refresh rerenders collapsed groups, pending older games need reconciliation in production. No pro board changes. Next: preview review and production activation with persistent forward-only feed, safe polling and deployment checks. Nov23 user requested tiered optional postgame discovery: every 5 minutes first hour, every 15 minutes next three hours, hourly thereafter until 24 hours total after completion (not an additional 24 hours). Stop each link type when found; retain verified links and completed archive independent of report availability. This is the requested design cadence, not an implemented or scheduled workflow. GitHub supports minimum five-minute scheduled cadence but delays/dropped runs possible; batch only due eligible checks, respect permitted access, no repeated requests to blocked hosts, no school retrieval permission assumed. Completion observation timestamp if exact time unknown, persist timestamps and expiry; no historical retry. Proposed (not approved) display rollover: FBS/FCS Thursday 3am ET current football week through Wednesday, retain unresolved live games; basketball yesterday/today/tomorrow, 3am ET daily rollover; upcoming games as soon as discovered, archive all finals forward only. Final display window and implementation await approval. Prior PR36 latest head 5475bb75b57961d002020a3c06176b531448f9f9 passed run45312152682 but reported nonmergeable, so its approved changes are reconciled here against current main. No NCAA production changes. Nov23 user explicitly approved all recommended settings and requested an explanation inside each NCAA dropdown, including goal, label meanings and PDF navigation. NCAA PR12 head de77cac9ea7ba4da8624d7035a70d184a860d857 implements weekly Thu 3AM ET FBS/FCS, daily 3AM ET MBB/WBB yesterday/today/tomorrow; date range batching, unresolved games reconciliation, persistent final_seen_at and 5/15/60 minute eligibility through 24h, separate archived enrichment, home/away reviewed Game Center, HTML and PDF links with exact identity checks; guide in each sport including PDF instructions and participation cautions. Reviewed Michigan/Ohio State Game Center https://ohiostatebuckeyes.com/game-center/22225 independently reverified. No authorized automatic university-source acquisition established, so actual remote enrichment remains unavailable; timing engine processes local reviewed observations only, not actual remote checks. Standalone Pages update workflow prepared, serialized state on ncaa-data branch, initial manual run plus NCAA_TRACKER_ENABLED=true activation flag; no Pages configuration/dispatch tool available, production not verified. Pre-merge validation run45314226412 pending. User approval applies to standalone NCAA only; existing five-league production, archive requirements and monitoring unchanged. Prior PR37 run45313574836 passed and merged f22c86cc906bff969c9a714d782c2bed70c7d68b; generated register verified. Preserve no paid services, no historical backfill, and no bypass. Final validation: initial run45314226412 failed HTTP400 on ESPN date-range queries (offline tests passed); corrected to supported single-day queries. Run45314393894 revealed missing scheduled team identity; fixed placeholder handling, require full live/final identities. Final NCAA PR12 head 9317b7438df954026d6886cd9eccb758019cb0c4 run45314498583 passed all 50 offline tests, prior checks, compile, live preview and safety checks. Preview 460 current-window games, 454 with school schedule shortcuts, 65 completed test archive records, one reviewed Game Center (Vanderbilt at Ohio State Nov24); Michigan Nov28 enters football window Thursday. No real archive written during PR. Merged 021d9032ba814eda327c0bc2550234538d89522e. Public repo metadata confirms has_pages=false; connector cannot enable Pages/configure variables/dispatch arbitrary workflow. Production activation pending user UI: Settings > Pages > GitHub Actions; run NCAA tracker update and publish manually on main, verify actual deployment and durable ncaa-data feed, then set NCAA_TRACKER_ENABLED=true to enable five-minute schedule. Link cadence applies to reviewed observations only; automatic university source retrieval not implemented. Final professional board untouched. $0 additional services. First standalone deployment Nov23 ET verified: manual workflow run45315385305 at main 021d9032ba814eda327c0bc2550234538d89522e completed success; update job138180873500 persisted ncaa-data/feed.json, deploy job138180977937 succeeded; public repository has_pages=true. Durable feed updated 2026-11-24T02:51:30.278290+00:00, cutoff 2026-11-23, 460 current records, 66 completed archive records, one reviewed Game Center (Vanderbilt at Ohio State). User reported green check. Production Pages deployment succeeded; independent live browser page inspection not performed. Recurring schedule activation still requires user to set NCAA_TRACKER_ENABLED=true in repository Actions variables; verify first scheduled run. Optional remote university retrieval remains outstanding, only reviewed observations are processed. Professional Mega Board unchanged. Register PR38 merged 2340891a113e9d66eabc444bd4930d33969fa53a, generated register verified. User confirmed NCAA_TRACKER_ENABLED=true added in Actions repository variables. As of verification after confirmation, run45315385305 remains the newest run; no scheduled run yet observed. Recurring activation user-confirmed, execution pending independent verification. Do not claim automated university discovery. No other changes. Follow-up Nov24 morning: first scheduled execution https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45321263075 started 03:41:36Z (Nov23 20:41 MT); both update and deploy succeeded. Ten scheduled runs through https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45404511720 all completed successfully; last update/deploy jobs138481467169 and138481586527 passed. Feed at ncaa-data commit cbfc7779597baf76bb5aae0ff49b03cd13b87904 updated 2026-11-24T13:32:45.714031+00:00, 477 current and 83 unique complete archived games, cutoff Nov23. Exact key/score comparison with initial feed commit 8cf3b270bec46e1b7be35fd5a8228e3da79f9fb3 confirms all 66 initial archive records preserved, no score differences, 17 additions and no invalid/pre-cutoff archive entries. Actual scheduled intervals approximately 54–86 minutes, not requested five minutes, despite unchanged cron */5; activation proven, cadence not reliable, investigate scheduler latency before changing configuration; no change authorized. Prior PR40 documenting pre-activation observation remains unmerged; this supersedes pending schedule observation. Source-level interface checks done earlier; browser interaction, real rollover, automatic university source acquisition, offseason detection and integration remain outstanding. No professional board changes for NCAA. Nov24 user approved automatic university report discovery and scheduler mitigation. NCAA PR13 merged 963370a770867dd2d7c9577b5d3fa9cea4be3c06 after green run45415677819: offset cron to 2-57/5 * * * * (same 12 slots/hour). First post-merge scheduled run45416317201 succeeded update and deploy, feed updated 14:38:23Z with 477 current, 83 archive and Nov23 cutoff; prior 13:32Z update implies ~66-minute actual gap, so cadence remains unproven. NCAA PR14 merged 26781a095041fd147b49668cf1b5606aacfb04e6: limited automatic Vanderbilt women's basketball final PDF pilot. Source review: Vanderbilt public schedule and published wrapper lead to school CDN; check robots rules, exact opponent/date/score and season, no guessed URLs, bounded size/time and one eligible game per run, persist slot and source block on access denial/rate limit, no repeated blocked requests; no blanket permission claimed for other schools. Live probe run45415937035 found exact box-score and PDF wrapper links for Vanderbilt 93 Arizona 62 Nov23; run45416406897 verified actual PDF identity. Early pre-merge failures were regex and missing pdftotext; corrected, no production failure. Final reconciled branch head79eb47e9b6e69a7ded22c7c9c5d21627386d11ba passed run45417434806, all 68 offline tests and all existing live checks, disposable preview, safety invariant, and actual production-path read-only control wbb:401913059 automatically verified direct PDF https://storage.googleapis.com/vucommodores-prod/2026/11/24/U8pWzpCE9GyayoOkoGnWAJ5AMANMtwHbeqMLQGzC.pdf in both current and archive. Review diff performed. No PDF rehosting, player stats, historical backfill, paid services, professional board changes or weakening monitoring. Pilot uses existing 24-hour eligibility and does not modify archive membership/scores or overwrite existing reports. Optional dependency/source errors logged; game tracking continues. Other school/sport sources and automated online box score/Game Center discovery remain outstanding. Production pilot run and Pages publication not yet observed after merge; do not equate live pre-merge control with production delivery. Scheduler remains best effort. Nov24 first production pilot verified: user manually triggered NCAA tracker run45419033993 at 14:52:53Z on merged head26781a095041fd147b49668cf1b5606aacfb04e6; update job138533151052 and Pages deploy job138533455077 completed success, all eligibility/dependency/enrichment/persistence steps green. Actual production log at 14:53:18Z OPTIONAL UNIVERSITY PDF VERIFIED for wbb:401913059, direct Vanderbilt CDN PDF https://storage.googleapis.com/vucommodores-prod/2026/11/24/U8pWzpCE9GyayoOkoGnWAJ5AMANMtwHbeqMLQGzC.pdf. Durable ncaa-data feed blob13081f5ea8b8856562de73e3d695e4eb6c76029e updated 14:53:02Z, last_attempt verified_pdf at 14:53:15Z, both current and archive entries contain same automatic_final_pdf_identity report with official schedule and wrapper provenance. 477 current, 83 unique completed archives, exactly one archived direct PDF, zero missing prior archive keys, changed scores or invalid entries, cutoff Nov23 preserved. No independently interactive browser test; Pages deploy succeeded. First production acquisition verified, recurrence and other schools/report types not yet proven; no further feature implementation authorized in this verification turn. Nov24 user explicitly approved expanding automatic university PDF discovery after verified Vanderbilt production run. Directory labels 29 schools WMT, 11 additional archived games with these schools; labels are candidate research only. Official Iowa–Utah 75–66 and Miami–Michigan 58–79 Nov23 reports identified via school schedules, as was Virginia Tech–UT Martin 85–41. NCAA PR15 first head b5e78026ec5189309ebe0e5f7a3cf23330d12d23 run45420182827: 74 offline tests and Vanderbilt control passed; actual Iowa direct PDF and Miami Gamebook wrapper verified, Virginia Tech no verified PDF (not an access-denial result), live expansion gate failed. Virginia Tech explicitly excluded from production; parser test retained, no weakening of identity verification. Final head26de78f1f086f47edf7884993791ead65035c9f9 pending final run45420481794. Proposed active sources Vanderbilt, Iowa, Miami (FL) WBB only; exact school domains, explicitly observed CDN prefixes, first-page final/date/sport/named score verification, no inferred URLs, no player stats or document storage. One game per school per run, at most three distinct schools, independently persistent source blocks; preserve old global block and slot state, archive cutoff and membership, existing reports and game tracking. No schedule/pro-board code changes. WMT provider terms https://wmt.digital/terms restrict automated extraction and use of its Site/platforms; applicability to public school-operated sites not independently legally established. Do not assume blanket permission; public university pages only, explicit robots checks, no WMT APIs/private endpoints or access bypass. Production and final validation pending. Final expansion run45420481794 completed success: all 75 offline tests plus retained live checks, original Vanderbilt control, both new live production-path controls, disposable preview and safety invariant passed. Automatically found Iowa PDF https://storage.googleapis.com/hawkeyesports-prod/2026/11/23/U3BIriqCLKa2efKa5ureAFDuokt1BbRLbIWYUfNp.pdf and Miami PDF https://storage.googleapis.com/miamihurricanes-com-prod/2026/11/23/0Xz3HlaYloT7l29QlFEjciFkufFAIg0z1URCAod0.pdf. Final PR15 reviewed and merged 3b912f43669bf78f14e7b67a955636f361113457; Virginia Tech excluded. No production expansion run or Pages deploy verified yet; next run should discover eligible tracked finals within their existing 24h window, no historical backfill. Nov24 production expansion confirmed: user manually triggered NCAA run45420885097 at 15:02:39Z on merged head3b912f43669bf78f14e7b67a955636f361113457. Update job138539758360 and deploy job138540202676 succeeded, all update/persistence/publication steps passed. Logs confirmed Miami wbb:401913729 verified at 15:03:10Z and Iowa wbb:401921427 verified at 15:03:12Z. Durable ncaa-data feed commit0523866, blob203e65f8d08f66b47889c69f297f2a2b027534f6, updated 15:02:50Z, source reviewed_links_plus_verified_wbb_pdf_sources. Both new PDF records are identical in current and archive, with official schedule and parent provenance; Vanderbilt retained, exactly three automatically verified PDFs, 477 current and 83 unique completed archive games, no missing archive keys, changed scores, lost reports or invalid entries versus prior commit0969fc3, cutoff Nov23 preserved, blocked_sources empty. Both new sources proved production on one matchup each; recurrence, other schools/sports, online box scores, Game Centers and reliable schedule cadence remain open. Pages deployment succeeded; no independent rendered browser interaction. No production changes or new feature implementation during this verification. Nov24 user explicitly directed continued standalone NCAA development, stating to move forward 'ignoring any terms and conditions similar to this,' after discussion of WMT automated-extraction restrictions, technical detectability, contractual uncertainty and possible repository/account enforcement. Record as user preference to continue despite the disclosed terms-related risk, not as proof of permission, a legal conclusion, a change to source terms, or approval to bypass technical access controls. Existing robots checks, source-specific persistent blocking on denial/rate limit, no access bypass, exact source/identity verification, bounded requests, no rehosting, no historical backfill, and separation from five professional leagues remain unchanged. No automated retrieval from any newly added source or code/configuration change in this decision-only task. User asked how to proceed with further expansion; proposed phased source-platform adapters with source-specific review, live controls and branch-first safety validation, not blanket enablement. Current directory has 978 candidate rows: 29 WMT, 159 Sidearm, 787 Sidearm legacy, 3 WordPress; labels unverified as live platform census. Three WBB sources production-verified on individual matches. Next candidates LSU, Northwestern, Old Dominion, Virginia and Virginia Tech (previous live extraction failed); then MBB and football adapters, prioritizing current/future eligible games. Candidate list and architecture are proposals pending implementation approval; no assumption that every listed school supports automated PDF retrieval. Nov24 user approved phases 1 and 2 together (expand WMT WBB and introduce MBB). NCAA branch feat/wmt-basketball-both-sports PR16 head78bb7176e9c48f5e279b0ce4d5dc05fd6b06b60b stages LSU WBB, Virginia Tech WBB retest, and San Jose State MBB as explicit school/sport combinations; Vanderbilt/Iowa/Miami WBB retained. Real public controls Nov23: LSU 103 Belmont 45 (official 29-page PDF https://storage.googleapis.com/lsusports-net-prod/2026/11/24/WFKj1QsgFcWrRelGo35HOckluyYx0SKdvFTmJwcI.pdf), San Jose State 88 UC San Diego 79 (22-page PDF https://storage.googleapis.com/san-jose-state-prod/2026/11/24/jUB41teze6HrSZznBQbESArN5s9og0JujEZyKfha.pdf), Virginia Tech 85 UT Martin 41 (published wrapper https://hokiesports.com/documents/31dde63f-805e-4c75-b493-cdcddb358b46.pdf and PDF https://storage.googleapis.com/virginiatech-prod/2026/11/23/X3i34GguWJ1poOoqAUpcTs7RyCUb3Txyok0yyQnZ.pdf). Schedule formatting adapters require correct sport/season, exact opponent, date, score, explicit link and PDF identity; same-day repeated dates for LSU, compact dates for SJSU, short result for VT. No change to three-school cap, source-specific access safeguards, 24h window, existing report retention or professional boards. Other candidates: Northwestern–Oakland, ODU–Memphis, BYU–Washington, Seattle–Loyola schedule rows have HTML box scores but no directly labeled final PDF; Virginia has a separate static.virginiasports.com PDF host requiring distinct review/adapter; Clemson's published linked gamebook exceeds existing 8MB cap, do not weaken bound. All remain unconfigured in this stage. Full live controls and final check required before merging, production not yet verified. Prior decision PR47 merged4f48ded5105ec010b9f01ca066208c21d1ce6200, register generation45422359643 and Pages45422392282 passed. No permission claimed from user acceptance of terms risk; existing technical guardrails retained. Combined expansion initial run45422877110: 81 offline tests and all three existing live controls passed; LSU WBB and San Jose State MBB live controls verified the actual PDFs; Virginia Tech again returned no verified PDF and was explicitly excluded. Revised head81a97a81ffa97da9699438aef4275218ffda5b6a run45423199174 failed in existing Miami live control: UTF-8 decoding error invalid start byte 0x8b at position 1 (consistent with compressed response, not confirmed without response headers); all 81 offline tests, Vanderbilt and Iowa controls and safety invariant passed, new LSU/SJSU controls skipped. PR16 remains open/unmerged. No regression to deployed source code established; production feed still 477 current, 83 archive, three verified PDFs, blocked_sources empty, last update15:02:50Z on prior successful manual run45420885097. Proposed next fix: inspect response Content-Encoding, test bounded standards-compliant gzip decoding with strict size/host/access checks and rerun complete safety suite, then merge and verify production only if green. No production code edits in status review. Schedule cadence unresolved; no newer scheduled run visible in recent run list. Nov24 user approved steps 1–3 together: repair pending expansion response handling; structured university source registry; scalable fair queue. PR48 merged ba299d84cd6451971a6d7bfa6fcaf3d68840ea75 following green45423484237; generated register confirmed contains prior failure. NCAA PR16 head8612ea0339a4323e5b2bdf5ed7d70564c27bc1a9 implements bounded identity/gzip response handling (header or exact gzip magic, corrupt/unknown encoding rejected; both wire and decompressed limits unchanged; strict UTF-8), validated university_sources.json schema with per-school host/platform/CDN prefix and per-sport path/format/live evidence, strict premerge registry validation and fail-closed optional source loading. Retains three existing WBB sources and previously live-tested LSU WBB/San Jose State MBB; Virginia Tech remains excluded. Queue increases cap from 3 to 5 distinct schools per run, one game per school, 120-second budget to start new attempts, in-flight bounded request may finish after budget. Durable least-recent school and game attempt state, unattempted first, newer final times break ties, deferred slots remain unconsumed, legacy slot/access blocks preserved, no backfill or schedule change. O(n) duplicate identity count replaces per-game full archive scan. Existing 5/15/60 slot windows and 24h expiration unchanged, no additional costs/services or changes to professional league boards. Initial final safety run45424162173 pending; merge and production not yet confirmed. Final run45424162173 completed success: 94 offline tests, strict registry validation, all retained data/identity checks, five live school PDF controls (Vanderbilt, Miami, Iowa, San Jose State and LSU), disposable preview and safety invariant passed. Miami response handling passed live regression after bounded gzip fix; actual prior response headers unavailable, so exact original encoding not independently established. PR16 diff reviewed and merged93dcc5a613b7ac1aa3013637a18e75615d5fd2c4. Queue tests demonstrated five-school capacity, rotation under two-school limit, deferred slots not consumed, recent-completion tiebreak, retained blocked source and unchanged archive/current. Capacity is maximum, not guaranteed; no scheduler improvement claimed. New school sources and queue not yet verified in live production, first post-merge update/Pages run pending; existing three PDF records remain last observed production state. Source registry and queue implementation complete on main; production verification still outstanding. Nov24 production verification: user manually ran NCAA workflow45424534312 on merged93dcc5a613b7ac1aa3013637a18e75615d5fd2c4 at15:21:19Z; update job138552785676 and deploy job138553554476 both succeeded, all steps passed. Actual logs verified San Jose State MBB wbb-independent key mbb:401921664 at15:22:18Z and LSU WBB wbb:401912970 at15:22:20Z. Queue logged eligible_games=2, attempted_schools=2, deferred_games=0, persisted per-school and per-game attempts and slots, blocked_sources empty. Durable ncaa-data commit c7e553e, blob615b612d3076219b8b840935573b0730da523ab7, updated15:21:38Z, source reviewed_links_plus_verified_basketball_pdf_sources. Five verified PDFs (four WBB, one MBB), both new URLs identical in current/archive; all previous three retained. Compared to prior0523866: 477 current, 83 unique completed archive games, zero missing keys, changed scores, lost report links or invalid records, cutoff Nov23 preserved. Production registry loading and normal queue execution confirmed; five-school capacity and fairness under contention verified offline only, and actual compressed response path not independently observed on this production run. No independent rendered-browser test; Pages deployment succeeded. No new production edits. Documentation PR49 passed45424445206 and merged2fe69fa01877691ef4b9c2239996073856c9d0c6. Broader school/sport coverage and reliable schedule cadence remain open. Nov24 user approved implementing and testing all 24 remaining directory-labeled WMT schools together. Scope interpreted as both basketball sports (48 school/sport cases), football-specific verification remains future work. Baseline five production-verified sources retained; prior production documentation PR50 passed45425045671, merged9b8f04711224395f615739462730b110659d841b, generated register45425364632 and central Pages45425396336 passed. NCAA research PR17 branch research/wmt-24-school-batch head38cade7978debbefd6f1d2c44b09a41939f3201b freezes exact candidate list and tests both sports using up to three recent unambiguous completed controls per combination (Nov18–23 read-only, no historical import), one school robots fetch, one schedule and at most one PDF candidate per sport, at most three concurrent schools. Published URL and exact opponent/date/score/sport/final PDF identity remain mandatory. No redirects or access-denial retries, no stored PDFs, no automatic registry promotion, no production source/schedule changes. Directory paths are candidate navigation, with observed special paths for Georgia Tech, Notre Dame, New Mexico and Virginia. All 48 outcomes required; successful candidates need reviewed exact school/sport config and a separate passing production-path live control before activation. First batch run45425898284 pending.
Nov24 continuation: batch research run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45425898284 succeeded (100 offline tests, five existing live controls, all 48 cases). Verified seven combinations across six schools: Auburn MBB, Cincinnati WBB, Missouri MBB, Purdue MBB/WBB, San Diego State WBB and Stanford WBB. Remaining 41: 23 no matching PDF link, seven PDF identity not verified, five no unambiguous recent final, four unsupported heading, two unavailable/stopped (Clemson 404). Activation PR18 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/18 passed run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45427093280 on exact head d5beed610bd5663be179822f3afd209128b074f4: 103 offline tests, five existing live controls, seven real production-path live controls, compilation, preview, and safety invariant. Diff reviewed; merged 04c1a83172f7579d29e56952193dfb52a38132ae. Main registry confirmed 11 universities / 12 combinations (8 WBB, 4 MBB). Activation merged; production update/Pages verification pending. Historical controls are read-only, no backfill; existing queue, timing, archive rules, five professional boards and monitoring unchanged. No blanket source permission inferred; school-specific access restrictions remain relevant. Failed/unverified combinations remain disabled. Next recommendation (not yet approved): diagnose identity failures and unsupported headings before broader expansion.
November 25, 2026: User explicitly paused all standalone NCAA development and tracking, without deletion, to reconsider strategy. No resumption, expansion or historical catch-up without explicit new approval.
Prior activation: production run45428060642 and scheduled run45428777687 on merged 04c1a83172f7579d29e56952193dfb52a38132ae succeeded; latest durable feed Nov24 15:43:28 UTC held 477 current, 83 archive, five automatic PDF links, cutoff Nov23. All 21 later consecutive scheduled failures (45441515217 through 45636210014) were reviewed by job logs: game-identity guard in tracker.py before enrichment/persistence, nine MBB IDs 401928859,401924267,401911535,401909763,401920414,401911253,401921707,401921666,401921030; all prior scheduled neutral-site games without reports. Full read-only replay on proposed repair PR19 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/19 head f61c380206199594f857dac2aa841de1c5466390, run45643597074, passed 104 offline tests and confirmed five exact neutral-site designation reversals, but encountered separate non-neutral identity conflict mbb:401921223 (saved Navy/Penn State Berks). Both repair runs45643550036 and45643597074 failed; repair remains unmerged, do not resume investigation without approval. User pause isolated into PR20 https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/pull/20, head ff518ce6c0cf57de45ffdefba92e4e952dfef8a6, safety run45643846269 passed, diff reviewed, merged fa6a206ec95557dfab3d1505d3ed01a2430959cc. Removed production cron, hard-disabled production update and manual research probe, preserved code and ncaa-data branch; static pause notice only deploys on relevant main push or manual dispatch. Production pause deployment run https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/actions/runs/45643933494 verified on merged head fa6a206ec95557dfab3d1505d3ed01a2430959cc: update job139309701270 skipped, static-only artifact job139309697724 succeeded, Pages deployment job139309801892 succeeded. Durable ncaa-data feed unchanged: blob917fb71309e533c4a449ca66322f09efd5031a1c, updated Nov24 15:43:28 UTC, 477 current / 83 archived / five automatically verified PDF links. No direct rendered browser test. Professional league scope and monitoring unchanged. No alert suppression, data deletion, new paid service or archive backfill. Resume only on user approval via reviewed PR, resolve incident and decide pause-gap handling. Prior verification PR54 remains unmerged; production evidence incorporated here.

*Implementation evidence:* [tracker.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/tracker.py), [site/index.html](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/site/index.html), [site/app.js](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/site/app.js), [tests/test_tracker.py](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/tests/test_tracker.py), [TRACKER.md](https://github.com/NikkiVeracruz/ncaa-stats-link-dashboard/blob/main/TRACKER.md), +20 additional in JSON


## Approved work awaiting implementation

Explicitly authorized but not implemented or deployed; status and evidence remain pending.

No entries.


## Suggested features / undecided requests

These are NOT automatically approved development tasks.

### REQ-001 — Remove name from public Mega Board URL

**Decision:** not decided · **Status:** not started · **Area:** request

User asked about changing the GitHub Pages URL to remove their name; no deployment/domain change was confirmed.

*Notes:* Treat as an open request for discussion, not a committed implementation.


## Deferred ideas

Deliberately postponed without claiming that the user rejected them.

No entries.


## Approved research and open follow-ups

Approved investigations and incomplete follow-ups; not deployed features.

### PRJ-028 — NFL exact-date discovery, official club gamebooks and post-rollover recovery

**Decision:** accepted · **Status:** open · **Area:** operations

User approved all four incident recommendations: unusual-day discovery, official PDF fallback, existing watchdog report awareness, and pending-game rollover protection.

*Notes:* Nov25/26 Rams incident: last known game in a1ca3c084c70b6a201f1d72f79a07abc06c810a7; schedule warning run45752215327, watchdog healthy run45756996772; forward-only purge prevents incomplete archive-based retries. Rollover already occurred. Official Packers game center https://www.packers.com/game-day/2026/reg-week12/packers-at-rams/ links https://static.clubs.nfl.com/image/upload/packers/k39qtefpy28qk4wyi6lt; independently inspected first page, November 25 2026 Packers 13 Rams 26. Proposed exact independent scoreboard reconciliation only for observed official NFL URLs, narrow verified Packers club fallback with full PDF identity, operational pending queue seeded solely with already tracked Rams game, calendar and existing watchdog integration, document/UI verification compatibility. No new watchdog, schedule reduction, historical backfill, NCAA or other league changes. Branch tests, read-only live proof, merge and production verification outstanding. Initial pre-merge run45760154417 passed targeted offline tests and verified the newly available central NFL gamebook https://static.www.nfl.com/image/upload/v1795667766/gamecenter/abbf28ed-4feb-11f1-abca-2c54536568a9.pdf for exact Rams game. Added separate live club fallback proof and regression coverage for ambiguous independent events, preserved final observations and document/UI link markers; final validation pending.

*Implementation evidence:* [nfl_pending.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/nfl_pending.py), [monitor.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/monitor.py), [tests/test_nfl_pending.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/test_nfl_pending.py), [tests/live_rams_gamebook.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/live_rams_gamebook.py), [tests/nfl_update_watchdog.py](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/blob/main/tests/nfl_update_watchdog.py), +1 additional in JSON


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
