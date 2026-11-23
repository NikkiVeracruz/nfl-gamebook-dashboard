#!/usr/bin/env python3
"""Strict prepublication validation for the one-time 2026 NFL catch-up."""
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive import ArchiveIntegrityError, validate_games
from archive_integrity_gate import verify_change
from nfl_2026_coverage import START, END

PDF_HOSTS = {"static.www.nfl.com", "www.nfl.com", "nfl.com"}


def validate_candidate(before, candidate, before_cursor, candidate_cursor):
    if before_cursor != candidate_cursor:
        raise ArchiveIntegrityError("Refusing to publish changed historical progress cursor")
    old = validate_games(before, "Existing production NFL archive")
    proposed = validate_games(candidate, "Proposed 2026 NFL catch-up")
    verify_change(before, candidate, "2026 NFL restoration")
    for key, previous in old.items():
        if proposed[key] != previous:
            raise ArchiveIntegrityError(
                f"Refusing to change previously archived NFL game: {key}"
            )
    additions = [game for key, game in proposed.items() if key not in old]
    if not additions:
        raise ArchiveIntegrityError("No new 2026 NFL games; refusing duplicate restoration")
    for game in additions:
        if not (START.isoformat() <= game["date"] < END.isoformat()):
            raise ArchiveIntegrityError(
                f"New game outside reviewed 2026 window: {game['date']}"
            )
        slug = str(game.get("slug", ""))
        if f"-2026-" not in slug:
            raise ArchiveIntegrityError(
                f"New game has wrong season identity: {slug}"
            )
        url = game.get("pdf_url")
        if url:
            p = urlparse(url)
            if p.scheme != "https" or p.hostname not in PDF_HOSTS or ".pdf" not in p.path.lower():
                raise ArchiveIntegrityError(
                    f"New game has nonofficial PDF URL: {slug}"
                )
    return len(old), len(additions), len(proposed)


def git_blob(ref, filename):
    return subprocess.check_output(
        ["git", "show", f"{ref}:{filename}"], stderr=subprocess.PIPE
    )


def main(ref="FETCH_HEAD"):
    old = json.loads(git_blob(ref, "archive.json"))
    current = json.loads(Path("archive.json").read_bytes())
    baseline_cursor = git_blob(ref, "archive-progress.json")
    current_cursor = Path("archive-progress.json").read_bytes()
    old_count, added, total = validate_candidate(
        old, current, baseline_cursor, current_cursor
    )
    msg = (
        f"SAFE NFL 2026 CATCH-UP: {old_count} original games unchanged; "
        f"{added} new 2026 games; {total} total archived records; "
        "historical progress cursor unchanged"
    )
    print(msg)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("### NFL 2026 prepublication safety gate\n\n" + msg + "\n")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) == 2 else "FETCH_HEAD")
    except (OSError, ValueError, ArchiveIntegrityError, subprocess.CalledProcessError) as exc:
        sys.exit(f"NFL 2026 PUBLICATION BLOCKED: {exc}")
