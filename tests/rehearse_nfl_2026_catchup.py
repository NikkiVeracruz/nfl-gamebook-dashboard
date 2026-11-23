#!/usr/bin/env python3
"""Reconstruct the 2026 NFL season only in a disposable Actions checkout."""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive import ArchiveIntegrityError, atomic_write_json, validate_games
from nfl_2026_coverage import END
from archive_integrity_gate import verify_change

ARCHIVE = Path("archive.json")
CURSOR = Path("archive-progress.json")
START = "2026-08-01"


def baseline_blob(path):
    return subprocess.check_output(
        ["git", "show", f"FETCH_HEAD:{path}"], stderr=subprocess.PIPE
    )


def rehearse():
    before_arch = baseline_blob("archive.json")
    before_cursor = baseline_blob("archive-progress.json")
    original = json.loads(before_arch)
    old = validate_games(original, "Actual production archive")
    ARCHIVE.write_bytes(before_arch)
    CURSOR.write_bytes(before_cursor)
    cursor = json.loads(before_cursor)
    cursor.update(next_date=START, complete=False)
    atomic_write_json(CURSOR, cursor)

    n = 0
    while True:
        progress = json.loads(CURSOR.read_text())
        if progress["next_date"] >= END.isoformat():
            break
        if n >= 7:
            raise ArchiveIntegrityError("2026 catch-up exceeded seven backfill batches")
        print(f"Scratch NFL 2026 batch {n+1}: starting {progress['next_date']}", flush=True)
        subprocess.run([sys.executable, "backfill.py"], check=True, timeout=600)
        newer = json.loads(CURSOR.read_text())
        if newer["next_date"] <= progress["next_date"]:
            raise ArchiveIntegrityError("Backfill cursor did not advance")
        n += 1

    proposed = json.loads(ARCHIVE.read_text())
    candidate = validate_games(proposed, "Scratch 2026 season recovery")
    # The existing archive is authoritative. Backfill metadata may legitimately
    # update a live game's label, but the one-time import must never do so.
    index = {str(g.get("id") or g.get("slug") or
                 (g["date"] + "|" + g.get("label", ""))): i
             for i, g in enumerate(proposed["games"])}
    for identity, item in old.items():
        if identity not in candidate:
            raise ArchiveIntegrityError(f"Backfill dropped archived game {identity}")
        proposed["games"][index[identity]] = item
    validate_games(proposed, "Merged 2026 archive with preserved original records")
    verify_change(original, proposed, "2026 catch-up")
    added = [g for g in proposed["games"]
             if str(g.get("id") or g.get("slug") or
                    (g["date"] + "|" + g.get("label", ""))) not in old]
    if any(not ("2026-08-01" <= g["date"] < END.isoformat()) for g in added):
        raise ArchiveIntegrityError("New record outside 2026 season recovery window")
    if any(not str(g.get("slug", "")).endswith(
            tuple(f"-2026-{kind}-{week}" for kind in ("pre", "reg", "post")
                  for week in range(0, 23))) for g in added):
        raise ArchiveIntegrityError("New record has invalid 2026 NFL season identifier")
    if not added:
        raise ArchiveIntegrityError("Catch-up found no new 2026 games")
    atomic_write_json(ARCHIVE, proposed)
    CURSOR.write_bytes(before_cursor)
    if CURSOR.read_bytes() != before_cursor:
        raise ArchiveIntegrityError("Failed to preserve historical backfill cursor")
    counts = dict(sorted(Counter(g["date"][:7] for g in added).items()))
    report = (
        f"Scratch catch-up: {n} batches, {len(old)} previously archived games, "
        f"{len(added)} new 2026 records, {len(proposed['games'])} total; "
        f"months added: {counts}; old records and historical cursor unchanged."
    )
    print(report, flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### NFL 2026 catch-up (read-only)\n\n" + report + "\n")
    return proposed


if __name__ == "__main__":
    try:
        rehearse()
    except (ArchiveIntegrityError, ValueError, OSError,
            subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        sys.exit(f"NFL 2026 SCRATCH CATCH-UP FAILED: {exc}")
