#!/usr/bin/env python3
"""Monitor code-vs-decisions drift without modifying source archives or decisions.

This produces observed health evidence. It never changes feature approvals,
historical retention, source games, PDFs, or the human decision register.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from render_register import SOURCE, DEST, render, validate

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "project" / "monitor_status.json"
OUTPUT_MD = ROOT / "project" / "STATUS.md"
RAW = "https://raw.githubusercontent.com/"
REPO = {
    "NFL": ("nfl-gamebook-dashboard", "archive.json", "gamebooks.json", ".github/workflows/backfill.yml"),
    "NBA": ("nba-gamebook-dashboard", "archive.json", "gamebooks.json", ".github/workflows/backfill.yml"),
    "WNBA": ("nba-gamebook-dashboard", "wnba/archive.json", "wnba/gamebooks.json", ".github/workflows/wnba-backfill.yml"),
    "NHL": ("nhl-gamebook-dashboard", "archive.json", "gamebooks.json", ".github/workflows/backfill.yml"),
    "MLB": ("mlb-gamebook-dashboard", "archive.json", "gamebooks.json", ".github/workflows/backfill.yml"),
}
LEGACY_WORKFLOWS = [
    ("nfl-gamebook-dashboard", ".github/workflows/restore-nfl-2026-season.yml"),
    ("nfl-gamebook-dashboard", ".github/workflows/restore-nfl-nov-2025.yml"),
    ("nba-gamebook-dashboard", ".github/workflows/reconcile-basketball-special-2026.yml"),
    ("nba-gamebook-dashboard", ".github/workflows/repair-wnba-2026.yml"),
    ("nhl-gamebook-dashboard", ".github/workflows/classify-nhl-2026.yml"),
    ("mlb-gamebook-dashboard", ".github/workflows/reconcile-mlb-special-2026.yml"),
]


def remote_text(repo, path, ref="main"):
    # Return explicit errors as CHECK FAILED, never assume an unavailable
    # official/source endpoint means the feature has been removed.
    url = RAW + "NikkiVeracruz/" + repo + "/" + ref + "/" + path
    error = None
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "MegaBoardGovernanceMonitor/1.0",
                "Cache-Control": "no-cache",
            })
            with urllib.request.urlopen(req, timeout=22) as response:
                raw = response.read(12_000_001)
            if len(raw) > 12_000_000:
                raise ValueError("Response exceeded 12 MB")
            return raw.decode("utf-8")
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            error = exc
            if attempt == 0:
                time.sleep(0.5)
    raise RuntimeError(f"{repo}/{path}: source inaccessible or malformed: {error}")


def valid_archived_game(game, league, minimum):
    if not isinstance(game, dict):
        return "malformed game"
    if not isinstance(game.get("date"), str) or game["date"] < minimum:
        return "historical date retained"
    status = str(game.get("status", "")).lower()
    if league == "NFL":
        complete = bool(game.get("pdf_url")) and (not status or "final" in status or status == "completed")
    elif league in ("NBA", "WNBA"):
        complete = "final" in status and bool(game.get("pdf_url"))
    elif league == "NHL":
        complete = status in ("off", "final") and bool(game.get("gs_url") and game.get("es_url"))
    elif league == "MLB":
        complete = ("final" in status and game.get("link_verification") == "verified_api"
                    and bool(game.get("box_url") and game.get("plays_url")))
    else:
        raise ValueError("Unsupported league")
    return None if complete else "incomplete or unverified report data"


def audit_archive(league, payload, minimum):
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError(f"{league}: malformed archive feed")
    seen = set()
    for g in payload["games"]:
        ident = g.get("slug") if league == "NFL" else g.get("id")
        if not ident or str(ident) in seen:
            raise ValueError(f"{league}: missing/duplicate identity {ident}")
        seen.add(str(ident))
        error = valid_archived_game(g, league, minimum)
        if error:
            raise ValueError(f"{league} {ident}: {error}")
    return len(seen)


def audit_backfill(workflow, variable):
    if variable not in workflow:
        raise ValueError("Historical workflow no longer requires explicit opt-in")
    # A user must explicitly restore schedules as well as enable the variable.
    if "\n  schedule:" in workflow or "\n    - cron:" in workflow:
        raise ValueError("Historical backfill schedule was reactivated")
    if "workflow_dispatch:" not in workflow:
        raise ValueError("Historical recovery workflow entrypoint disappeared")


def audit_workflow_job_conditions(source, label):
    """Reject duplicate job-level if keys, which GitHub rejects at parsing time."""
    current_job = None
    checks = {}
    in_jobs = False
    for number, line in enumerate(source.splitlines(), start=1):
        if line == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        if line and not line.startswith(" "):
            in_jobs = False
            current_job = None
            continue
        if line.startswith("  ") and not line.startswith("   ") and line.endswith(":"):
            current_job = line.strip()[:-1]
            checks[current_job] = 0
        elif current_job and line.startswith("    if:"):
            checks[current_job] += 1
            if checks[current_job] > 1:
                raise ValueError(
                    f"{label}: duplicate if condition for job {current_job}, line {number}"
                )
    return len(checks)


def audit_registry(data):
    rows = validate(data)
    decisions = {x["id"]: x for x in rows}
    must_decline = ("DEC-001", "DEC-002", "DEC-003", "DEC-004", "DEC-005")
    for key in must_decline:
        if decisions.get(key, {}).get("decision") != "declined":
            raise ValueError(f"Explicit user veto lost: {key}")
    for f in rows:
        if f["decision"] == "not_decided" and f["state"] == "implemented":
            raise ValueError(f"Unapproved proposal marked implemented: {f['id']}")
    return rows


def inspect(data, read=remote_text):
    checked = []
    failures = []
    policies = data["project"]["operating_policy"]
    def record(name, action):
        try:
            result = action()
            checked.append({"check": name, "status": "pass", "detail": str(result)})
        except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
            checked.append({"check": name, "status": "drift_or_inconclusive", "detail": str(exc)[:550]})
            failures.append(name + ": " + str(exc)[:260])

    record("Canonical user decisions", lambda: str(len(audit_registry(data))) + " tracked decisions/requirements")
    record("Readable register matches JSON", lambda: (
        "Generated Markdown matches" if DEST.is_file() and DEST.read_text(encoding="utf-8") == render(data)
        else (_ for _ in ()).throw(ValueError("PROJECT_REGISTER.md is stale or missing"))
    ))
    record("Exactly five supported leagues", lambda: (
        "NFL NBA WNBA NHL MLB" if data["project"]["supported_leagues"] == list(REPO)
        else (_ for _ in ()).throw(ValueError("Unexpected league scope"))
    ))
    for league, (repo, archive, feed, backfill) in REPO.items():
        def league_check(league=league, repo=repo, archive=archive, feed=feed, backfill=backfill):
            baseline = policies["archive_start_date_by_league"][league]
            archive_data = json.loads(read(repo, archive))
            count = audit_archive(league, archive_data, baseline)
            live_data = json.loads(read(repo, feed))
            if not isinstance(live_data, dict) or not isinstance(live_data.get("games"), list):
                raise ValueError("Current live feed is invalid; schedule may be broken")
            forward = read(repo, "forward_only.py")
            if baseline not in forward or "filter_archive" not in forward or "complete" not in forward:
                raise ValueError("Forward-only retention implementation changed")
            audit_backfill(read(repo, backfill), policies["historical_backfill_opt_in_variable"])
            # Explicit backup must still exist so historical infrastructure is reversible.
            backup = read(repo, archive, ref="backup/pre-forward-only-2026-11-23") if read is remote_text else ""
            if backup and not isinstance(json.loads(backup).get("games"), list):
                raise ValueError("Historical backup archive invalid")
            return f"{count} complete retained games; live feed valid; backfill gated; backup present"
        record(f"{league} forward-only archive, current feed and backup", league_check)

    def central_check():
        board = read("nfl-gamebook-dashboard", "command-center/index.html")
        required = ("NFL", "NBA", "WNBA", "NHL", "MLB", "history-disclosure",
                    "How to Use This Dashboard", "leagueFilter", "statusFilter")
        absent = [x for x in required if x not in board]
        if absent:
            raise ValueError("Mega Board missing required UI features: " + ", ".join(absent))
        if "NCAA" in board:
            raise ValueError("NCAA was reintroduced to the Mega Board")
        return "Five league filters, archive/current separation and help are present; NCAA absent"
    record("Central Mega Board basic functionality", central_check)

    def review_mode():
        wf = read("nfl-gamebook-dashboard", ".github/workflows/archive-2026-completeness.yml")
        if "ENABLE_HISTORICAL_BACKFILL" not in wf or "\n  schedule:" in wf:
            raise ValueError("Historical full-season audit activated without approval")
        for repo, path in LEGACY_WORKFLOWS:
            source = read(repo, path)
            audit_workflow_job_conditions(source, f"{repo}/{path}")
            if "ENABLE_HISTORICAL_BACKFILL" not in source:
                raise ValueError(f"Ungated legacy restoration workflow: {repo}/{path}")
        if "schedule:" not in read("nfl-gamebook-dashboard", ".github/workflows/missing-game-audit.yml"):
            raise ValueError("Current missing-game audit schedule disappeared")
        if "schedule:" not in read("nfl-gamebook-dashboard", ".github/workflows/document-level-verification.yml"):
            raise ValueError("Official document verification schedule disappeared")
        return "Historical restoration disabled, current-game completeness and document checks present"
    record("Approvals and auditing workflow modes", review_mode)

    # Validate code-evidence files exist (deduplicated). Failed fetches are
    # unverified evidence, not proof that the feature is absent.
    paths = {(ev["repo"].split("/")[-1], ev["path"])
             for f in data["features"] if f["state"] in ("implemented", "paused")
             for ev in f["evidence"]}
    evidence_errors = []
    if paths:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(read, repo, path): (repo, path) for repo, path in paths}
            for future in as_completed(futures):
                repo, path = futures[future]
                try:
                    content = future.result()
                    if not content.strip():
                        raise ValueError("Empty code evidence")
                except (OSError, ValueError, RuntimeError) as exc:
                    evidence_errors.append(f"{repo}/{path}: {exc}")
    if evidence_errors:
        checked.append({"check": "Implementation evidence files still present",
                        "status": "drift_or_inconclusive",
                        "detail": " | ".join(evidence_errors[:8])})
        failures.append(f"{len(evidence_errors)} cited implementation files unavailable")
    else:
        checked.append({"check": "Implementation evidence files still present",
                        "status": "pass", "detail": f"{len(paths)} cited files checked"})

    return {
        "scope": "live implementation drift; no user decisions modified",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "drift_or_inconclusive" if failures else "pass",
        "checks": checked,
        "failure_count": len(failures),
        "failures": failures,
    }


def markdown(result):
    lines = [
        "# Mega Board — Project Governance Monitor", "",
        f"**Latest observation:** {result['checked_at']}",
        "",
        "**Outcome:** " + ("PASS" if result["status"] == "pass"
                         else "DRIFT OR INCONCLUSIVE — manual investigation needed"),
        "",
        "This monitor never changes game data, archive contents, feature approvals, "
        "or user preferences. An unreachable source is not counted as a pass.", "",
        "| Check | Result | Detail |", "|---|---|---|",
    ]
    for ch in result["checks"]:
        detail = str(ch["detail"]).replace("|", "/").replace("\n", " ")
        lines.append(f"| {ch['check']} | {ch['status']} | {detail[:350]} |")
    lines.extend(["", f"**Findings requiring attention:** {result['failure_count']}.",
                  "", "[Open the master register](../PROJECT_REGISTER.md) "
                  "or [the canonical JSON](feature_registry.json).", ""])
    return "\n".join(lines)


def run(write=True):
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = inspect(data)
    if write:
        OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        OUTPUT_MD.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "checked_at": result["checked_at"],
                      "checks": len(result["checks"]), "failures": result["failures"]},
                     indent=2), flush=True)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    sys.exit(run(write=not args.no_write))
