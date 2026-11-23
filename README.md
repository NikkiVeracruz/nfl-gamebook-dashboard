# Five-League Official Gamebook Mega Board

A unified game and official-report reference board for customer-service agents, combining **NFL, NBA, WNBA, NHL, and MLB** data.

**[Open the Mega Board](https://nikkiveracruz.github.io/nfl-gamebook-dashboard/command-center/)**

## Project source of truth

- **[Master Project Register](PROJECT_REGISTER.md)** — the project mission, accepted requirements, implemented work, explicitly declined features, paused infrastructure, unapproved suggestions, unresolved requests, and known risks.
- **[Canonical machine-readable decision register](project/feature_registry.json)** — the data behind the readable master record. Future decisions and implementation changes should be captured here.
- **[Current governance monitoring status](project/STATUS.md)** — latest daily drift check across all five leagues, including completeness rules and backup/schedule safeguards.
- **[Governance monitor workflow](.github/workflows/project-governance-monitor.yml)** — daily scheduled monitoring that opens/updates a GitHub issue on detected drift or inconclusive source verification. Never changes approvals or source game archives.
- **[Forward-only policy and restoration procedure](FORWARD_ONLY_MODE.md)** — explains the user's latest direction, current/new complete-only archival, retired historical backfills, and backup branches.
- **[Independent document verification](document-verification/README.md)** — verification evidence and limitations.

## Change-control rules

**Explicit user decisions control the scope.** Do not interpret an assistant suggestion as approval. Once a user accepts, declines, defers or supersedes a proposal, update the canonical feature register with an ID and description. Change a feature's implementation state only when there is evidence in code, workflow runs or tests. The readable master document is generated automatically from JSON, so they cannot quietly disagree.

GitHub Actions detects drift and alerts via workflow failure and GitHub Issues, but it does **not** autonomously make product decisions or re-enable rejected features. A review by the assistant or a maintainer is required to reconcile the register to actual implemented changes.

The project is currently **forward-only**: current games remain visible, and only new/current completed games with the required official reports are saved in the active archive. Historical recovery scripts are retained but paused.
