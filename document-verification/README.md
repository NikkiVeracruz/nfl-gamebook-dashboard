# 2026 official document verification

This is a **read-only inspection of published 2026 game documents**, separate from the game-record completeness audit. It does not create, delete, replace, or repair archived game records. Results live in [2026.json](./2026.json).

## What is checked

- **NFL, NBA, WNBA:** Download the entire official PDF (12 MB safety limit), confirm PDF structure using pypdf, and extract text from the first three pages. A **verified_match** requires readable PDF pages, **both teams** and the **game date** in the document text. **readable_identity_unconfirmed** means a valid, readable PDF could not yet be matched to both teams *and* date; do not call that fully verified.
- **NHL:** Download the game-ID-specific NHL Game Summary (GS) and Event Summary (ES) HTML reports. Require the canonical NHL report URL plus the correct HTML report heading/type. **verified_report** confirms the official report endpoint and report type; it does **not** independently compare every statistic or both team rosters.
- **MLB:** Fetch the *official* game-specific MLB Stats API v1.1 live feed, require the returned gamePk to match the archived game ID, and check that the box-score or play-by-play section exists. MLB links are Gameday pages, **not PDFs**.

'not_found' means an inspected link returned HTTP 404. 'source_unavailable', 'source_unavailable_http_*', 'inspection_error', or 'too_large_to_inspect' mean verification was inconclusive; the document must not be called missing. 'invalid_url', 'invalid_format', 'unreadable_document', 'invalid_report_content', and 'mismatched_game_id' require investigation. A file can still be online when it is unverified.

'no_link' counts *eligible completed games* without a stored document link. Missing links can reflect All-Star/exhibition games where no standard official report is published. These are **not automatically broken links**, and are kept separate from link verification failures.

## Scope and cadence

- Only games dated **2026**, at least **three calendar days old**, with eligible final/completed status are checked. NFL relies on the date after three days; future/in-progress games are not considered missing documents.
- The hourly current-game monitor and weekly independent full-season game-record audit remain separate.
- A successful GitHub Actions run means the audit executed. It is **not evidence that all reports passed**.
- The first workflow push runs a sample of **60** across all five leagues. Scheduled and manual runs inspect up to **450 due links per day**, allocated fairly between leagues.
- Previously successful links are rechecked every **30 days**, and unsuccessful/inconclusive checks can retry the following day. Never invent a document link.
- Results are recorded separately in JSON. No archive data or original gamebook URLs are modified.
- NHL international hockey is excluded from NHL club GS/ES report requirements, but the games remain archived.
- A document-level confirmation does not prove that every individual player/statistic inside the report is correct. It checks the official document's identity, format, or data structure to the extent documented above.

## Run manually

Open [2026 official document verification workflow](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard/actions/workflows/document-level-verification.yml), choose **Run workflow** on main, and inspect the run log and [2026.json](./2026.json). A workflow error or an inconclusive document must not be silently labeled verified.

## Safety

The workflow only stages the report at document-verification/2026.json; it never writes original archive files or changes the Mega Board user interface. Daily checks are spread out to reduce the risk of official sites rate-limiting or rejecting large bursts of requests.
