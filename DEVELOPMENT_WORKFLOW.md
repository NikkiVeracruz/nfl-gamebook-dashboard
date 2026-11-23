# Mega Board — Pre-merge development and deployment policy

**Approved November 23, 2026.** Applies to the NFL / central Mega Board, NBA and WNBA, NHL, and MLB GitHub repositories.

## Purpose

Catch preventable code, archive-safety and interface integration mistakes **before** they reach the public Mega Board, while keeping official gamebook discovery, normal publishing, live monitoring, production regression tests, and genuine failure notifications at their existing frequency.

## Required sequence for future changes

1. **Identify scope and preserve decisions.** Check `PROJECT_REGISTER.md`, `project/feature_registry.json` and `project/STATUS.md` before making changes. Only implement approved features. Keep user-declined features disabled, and never silently reinstate historical backfilling.
2. **Branch from current `main`.** Use a unique task branch in each repository needing a change. Never publish incomplete work directly to `main`.
3. **Develop and check the branch.** Run local/safe targeted tests where available; prepare the complete changeset before opening a pull request so partially wired features do not send unnecessary workflow-failure notifications.
4. **Create a pull request to `main`.** Each repository runs its read-only **Pre-merge safety checks** workflow against the proposed merged code. Do not merge after failed, missing, queued or inconclusive required checks. Correct problems on the branch and rerun until successful.
5. **Review what will change.** Check the PR diff against the user's approved requirements, current documented scope, and production behavior. Validate current report verification rules, no NCAA, and forward-only archiving. For a multi-repository feature, coordinate the order of merging and confirm interface/producer compatibility.
6. **Merge after green checks.** Revalidate if new commits change the PR head; do not claim an old pass validates newer changes. Changes should reach `main` through the PR process.
7. **Verify production independently.** Check the resulting `main` workflows and latest GitHub Pages deployment. If production fails, report the incident and investigate; do not suppress error emails or lower monitoring frequency.
8. **Update project history in the same task.** Record requirements, decisions, approved/rejected suggestions, implementation state, evidence, and limitations in `project/feature_registry.json`. Let `.github/workflows/project-register.yml` regenerate the human-readable register and verify it. This is a mandatory completion step.

## What the staging checks cover

Each of four repositories now has `.github/workflows/pre-merge-safety.yml`, triggered by a pull request to `main`. It uses **read-only permissions**, compiles the production monitor modules, verifies the complete-report forward-only retention policy, and runs archive integrity regression tests.

Additional coverage by repository:

- **NFL + Mega Board**: all five-league city/team search regression tests and JavaScript syntax, active/archive integration assertions, project register schema and governance drift-monitor tests.
- **NBA and WNBA**: WNBA archive safety and three-day window tests.
- **NHL**: three-day window tests.
- **MLB**: three-day window tests.

These checks are a baseline, not proof every statistic or externally hosted link is correct. Run additional feature-specific tests and appropriate review when needed.

## What does not change

- Existing production schedules, league-source polling, current game monitoring, official report verification and archive writing.
- Daily project integrity monitoring, weekly project review, and the live safeguards already in place.
- GitHub Actions failure notifications and relevant error signals.
- The five-league scope and forward-only storage policy; no automatic historical backfill or NCAA restoration.

## Important limits

- **Pre-merge checks are not branch protection.** GitHub will run the PR workflow, but an authorized person may still be able to push straight to `main` unless repository rules are separately configured. The assistant must follow this documented policy regardless. To make passing checks mandatory for all collaborators, configure GitHub branch protection/rulesets requiring the `Pre-merge safety checks / verify` check once it exists on `main`.
- Staging tests can catch mistakes earlier but cannot rule out problems from live APIs, externally hosted documents, browser differences or production timing. Post-merge checks remain required.
- For urgent operational repairs, use the shortest safe branch-and-PR cycle that still protects the live site; any exceptional bypass must be explicit, documented and followed by validation.
