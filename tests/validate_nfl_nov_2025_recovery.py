#!/usr/bin/env python3
"""One-time November 2025 NFL archive restoration guard.

Refuse a write unless the proposed archive only adds the exactly reviewed
November 2025 batch; original records and original backfill cursor must
remain unchanged. Used in a read-only staging rehearsal before publication.
"""
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

START = "2025-11-02"
END = "2025-11-30"  # exclusive
EXPECTED_NEW = 60
OFFICIAL_HOSTS = {"static.www.nfl.com", "www.nfl.com", "nfl.com"}


def inspect_batch(old, proposed):
    previous = validate_games(old, "Existing production NFL archive")
    candidate = validate_games(proposed, "Proposed NFL historical recovery")
    verify_change(old, proposed, "November 2025 restoration")
    for key, item in previous.items():
        if candidate[key] != item:
            newer = candidate[key]
            changes = {
                field: {"before": item.get(field), "after": newer.get(field)}
                for field in sorted(set(item) | set(newer))
                if item.get(field) != newer.get(field)
            }
            raise ArchiveIntegrityError(
                f"Refusing to change previously archived game {key}; "
                f"changed fields: {changes}"
            )
    additions = [g for key, g in candidate.items() if key not in previous]
    if len(additions) != EXPECTED_NEW:
        raise ArchiveIntegrityError(
            f"Expected exactly {EXPECTED_NEW} new November games; found {len(additions)}"
        )
    urls = set()
    for g in additions:
        if not (START <= g["date"] < END):
            raise ArchiveIntegrityError(f"New game outside recovery window: {g['date']}")
        url = g.get("pdf_url")
        if not isinstance(url, str) or not url:
            raise ArchiveIntegrityError("Proposed game missing a verified NFL PDF")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
            raise ArchiveIntegrityError(f"Nonofficial proposed NFL PDF URL: {url}")
        if ".pdf" not in parsed.path.lower():
            raise ArchiveIntegrityError(f"Proposed report URL is not a PDF path: {url}")
        if url in urls:
            raise ArchiveIntegrityError(f"Duplicate gamebook PDF URL: {url}")
        urls.add(url)
    return additions, len(previous), len(candidate)


def read_git_blob(ref, path):
    return subprocess.check_output(
        ["git", "show", f"{ref}:{path}"],
        stderr=subprocess.PIPE,
    )


def main(ref="FETCH_HEAD"):
    old = json.loads(read_git_blob(ref, "archive.json"))
    proposed = json.loads(Path("archive.json").read_bytes())
    cursor = read_git_blob(ref, "archive-progress.json")
    if Path("archive-progress.json").read_bytes() != cursor:
        raise ArchiveIntegrityError("Production backfill cursor must not change")
    additions, before, after = inspect_batch(old, proposed)
    dates = sorted({g["date"] for g in additions})
    message = (
        f"SAFE ONE-TIME NFL RECOVERY: {len(additions)} new November 2025 games, "
        f"{len(additions)} unique official PDF links; archive {before} -> {after}; "
        f"original records and progress cursor unchanged. "
        f"Dates {dates[0]} through {dates[-1]}."
    )
    print(message)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("### One-time November 2025 publication gate\n\n"
                         + message + "\n")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) == 2 else "FETCH_HEAD")
    except (ArchiveIntegrityError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"ONE-TIME RESTORATION BLOCKED: {exc}")
