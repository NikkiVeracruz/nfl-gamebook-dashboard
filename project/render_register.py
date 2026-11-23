#!/usr/bin/env python3
"""Render PROJECT_REGISTER.md from canonical project/feature_registry.json.

Only the JSON registry is edited by people; this script cannot approve,
decline, or modify project decisions. It only formats the recorded facts.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project" / "feature_registry.json"
DEST = ROOT / "PROJECT_REGISTER.md"


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported register version")
    proj = data.get("project", {})
    if not proj.get("name") or not proj.get("governance_policy"):
        raise ValueError("Missing project name or governance rules")
    entries = data.get("features")
    if not isinstance(entries, list) or len(entries) < 20:
        raise ValueError("Feature register missing or unexpectedly incomplete")
    seen = set()
    enums = proj.get("status_semantics", {})
    for item in entries:
        for key in ("id", "title", "area", "decision", "state",
                    "summary", "evidence", "notes"):
            if key not in item:
                raise ValueError(f"Missing {key} in feature {item.get('id')}")
        if item["id"] in seen or not item["id"]:
            raise ValueError("Duplicate or missing register ID")
        seen.add(item["id"])
        if item["decision"] not in enums.get("decision", []):
            raise ValueError(f"Invalid decision on {item['id']}")
        if item["state"] not in enums.get("state", []):
            raise ValueError(f"Invalid implementation on {item['id']}")
        if not isinstance(item["evidence"], list):
            raise ValueError(f"Invalid evidence array for {item['id']}")
        for ev in item["evidence"]:
            if not isinstance(ev, dict) or not ev.get("repo") or not ev.get("path"):
                raise ValueError(f"Missing evidence source for {item['id']}")
    return entries


def section(lines, heading, items, introduction):
    lines.extend(["", "## " + heading, "", introduction, ""])
    if not items:
        lines.extend(["No entries.", ""])
        return
    for item in items:
        lines.extend(["### " + item["id"] + " — " + item["title"], "",
                      "**Decision:** " + item["decision"].replace("_", " ") +
                      " · **Status:** " + item["state"].replace("_", " ") +
                      " · **Area:** " + item["area"].replace("_", " "), "",
                      item["summary"], ""])
        if item["notes"]:
            lines.extend(["*Notes:* " + item["notes"], ""])
        if item["evidence"]:
            links = [
                "[" + x["path"] + "](https://github.com/" + x["repo"] +
                "/blob/main/" + x["path"] + ")"
                for x in item["evidence"][:5]
            ]
            if len(item["evidence"]) > 5:
                links.append("+" + str(len(item["evidence"]) - 5) + " additional in JSON")
            lines.extend(["*Implementation evidence:* " + ", ".join(links), ""])


def render(data):
    entries = validate(data)
    proj = data["project"]
    counts = Counter(e["state"] for e in entries)
    lines = [
        "# Mega Board — Master Project Register", "",
        "**Status reviewed:** " + proj["review_date"] +
        " · **Canonical data:** [project/feature_registry.json](project/feature_registry.json)", "",
        "> This page is generated from the canonical registry. Automatic checks "
        "must not accept, reject, or supersede user decisions.", "",
        "## Purpose and scope", "",
        proj["mission"], "",
        "**Leagues:** NFL, NBA, WNBA, NHL, MLB. "
        "**Board:** [Mega Board](https://nikkiveracruz.github.io/nfl-gamebook-dashboard/command-center/).", "",
        "**Operating direction:** Forward-only collection from November 23, 2026: "
        "keep live scheduled and active game views, archive only completed games "
        "with all required official reports, and store new complete games going forward. "
        "Keep dormant historical infrastructure but do not backfill historical seasons.", "",
        "**Authority rule:** Later explicit user decisions supersede older plans. "
        "Recommendations are not approved unless the user accepts them.", "",
        "## Status overview", "",
        "**" + str(len(entries)) + " tracked items:** " +
        " · ".join(str(counts.get(s, 0)) + " " + s.replace("_", " ")
                   for s in ("implemented", "paused", "removed", "proposed",
                             "deferred", "not_started", "open")), "",
        "| State | Meaning |", "|---|---|",
        "| Implemented | Evidenced in code or configuration, not an uptime guarantee. |",
        "| Paused | Preserved but intentionally inactive/restricted. |",
        "| Removed | Deliberately removed; do not reinstate without approval. |",
        "| Proposed | An idea not yet approved to implement. |",
        "| Not started | Work not deployed; decision may be accepted, declined, or undecided. |",
        "| Deferred | Delayed, not necessarily rejected. |",
        "| Open | Known risk or incomplete follow-up. |", "",
    ]
    section(lines, "Accepted and implemented",
            [e for e in entries if e["state"] == "implemented"],
            "Implemented requirements or work accepted by the user.")
    section(lines, "Explicitly declined, removed, or superseded",
            [e for e in entries if e["decision"] == "declined"],
            "Never reintroduce these without a fresh explicit decision.")
    section(lines, "Paused infrastructure",
            [e for e in entries if e["state"] == "paused"
             and e["decision"] != "declined"],
            "Preserved for future reactivation only if requested.")
    section(lines, "Approved work awaiting implementation",
            [e for e in entries if e["decision"] in ("accepted", "required")
             and e["state"] in ("not_started", "proposed")],
            "Explicitly authorized but not implemented or deployed; status and evidence remain pending.")
    section(lines, "Suggested features / undecided requests",
            [e for e in entries if e["decision"] == "not_decided"],
            "These are NOT automatically approved development tasks.")
    section(lines, "Deferred ideas",
            [e for e in entries if e["decision"] == "deferred"],
            "Deliberately postponed without claiming that the user rejected them.")
    section(lines, "Known risks and gaps",
            [e for e in entries if e["area"] == "known_risk"],
            "Report unresolved risks even when all routine workflows are green.")
    lines.extend([
        "", "## Repository map", "",
        "| Area | GitHub |", "|---|---|",
        "| Mega Board + NFL | [nfl-gamebook-dashboard](https://github.com/NikkiVeracruz/nfl-gamebook-dashboard) |",
        "| NBA + WNBA | [nba-gamebook-dashboard](https://github.com/NikkiVeracruz/nba-gamebook-dashboard) |",
        "| NHL | [nhl-gamebook-dashboard](https://github.com/NikkiVeracruz/nhl-gamebook-dashboard) |",
        "| MLB | [mlb-gamebook-dashboard](https://github.com/NikkiVeracruz/mlb-gamebook-dashboard) |", "",
        "**Rollback:** Original pre-purge history is preserved on the "
        "backup/pre-forward-only-2026-11-23 branch of all four repositories. "
        "See [retention and restoration instructions](FORWARD_ONLY_MODE.md).", "",
        "## How this record stays accurate", "",
        "1. Add each new user request or assistant idea under a stable ID in "
        "project/feature_registry.json; mark not_decided until explicitly approved or declined.",
        "2. When a feature is shipped, change the implementation state only after "
        "checking code/workflows/tests; add source evidence and date context.",
        "3. Regenerate this document with python project/render_register.py --write. "
        "GitHub automation also regenerates it on registry changes.",
        "4. A scheduled independent check verifies critical runtime/configuration "
        "invariants and can raise a GitHub issue for drift. It does not make "
        "product decisions, rewrite approvals or restore rejected features.",
        "5. New assistant implementation work should include a corresponding "
        "register update, preserving the user-approved scope and reasons for refusals.", "",
        "## Major decision history", "",
        "- **Nov 21–22, 2026:** The five-league Mega Board, separate archive/current "
        "search, expandable sections, help sidebar, calendar monitoring and rollovers "
        "were added; standalone data feeds were retained.",
        "- **Nov 22:** The user explicitly removed all NCAA dashboards.",
        "- **Nov 23:** The user removed the unnecessary visible data-staleness monitor. "
        "Independent 2026 game coverage and document audits were implemented.",
        "- **Nov 23, later:** The user superseded older season-restoration decisions, "
        "moved to complete-only current/new game archives, halted old backfills and "
        "removed old historical/unverified links from active data.", "",
        "**Historical reconstruction limit:** This inventory was assembled from "
        "available conversations and code, not from a guaranteed exhaustive export "
        "of every earlier message. Anything without a substantiated approval stays "
        "not_decided. From this point onward, new decisions should be recorded here.", "",
    ])
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    result = render(json.loads(SOURCE.read_text(encoding="utf-8")))
    if args.write:
        DEST.write_text(result, encoding="utf-8")
        print("Generated PROJECT_REGISTER.md")
    elif args.check:
        if not DEST.is_file() or DEST.read_text(encoding="utf-8") != result:
            raise SystemExit("Stale or missing PROJECT_REGISTER.md; use --write")
        print("PASS canonical register rendered accurately")
    else:
        print(result)


if __name__ == "__main__":
    main()
