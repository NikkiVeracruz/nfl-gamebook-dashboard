#!/usr/bin/env python3
"""Read-only source archive verification: inspect actual 2026 official documents.

Writes ONLY document-verification/2026.json in the central Mega Board repository.
No game archive, feed, or published report link is ever rewritten by this audit.
A successful run means the inspection completed, NOT that every document passed.
"""
import argparse
import hashlib
import io
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from pypdf import PdfReader

ROOT = "https://raw.githubusercontent.com/NikkiVeracruz/"
REPOS = {"NFL": ("nfl-gamebook-dashboard", ""),
         "NBA": ("nba-gamebook-dashboard", ""),
         "WNBA": ("nba-gamebook-dashboard", "wnba/"),
         "NHL": ("nhl-gamebook-dashboard", ""),
         "MLB": ("mlb-gamebook-dashboard", "")}
REPORT = Path("document-verification/2026.json")
HEADERS = {"User-Agent": "GamebookArchiveDocumentVerifier/1.0",
           "Accept": "application/pdf,text/html,application/json,*/*"}
MAX_BYTES = 12_000_000
CUTOFF_DAYS = 3
REFRESH_DAYS = 30
PDF_HOSTS = {"NFL": {"static.www.nfl.com", "www.nfl.com", "nfl.com"},
             "NBA": {"statsdmz.nba.com"}, "WNBA": {"statsdmz.nba.com"}}
GOOD = {"verified_match", "verified_report", "verified_official_stats"}


def now_utc():
    return datetime.now(timezone.utc)


def fetch_json(url):
    r = requests.get(url, timeout=(10, 35), headers=HEADERS)
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {url}")
    return payload


def gather(league):
    repo, prefix = REPOS[league]
    combined = {}
    for filename in ("archive.json", "gamebooks.json"):
        payload = fetch_json(ROOT + repo + "/main/" + prefix + filename)
        games = payload.get("games")
        if not isinstance(games, list):
            raise ValueError(f"{league}/{filename}: invalid games list")
        source_seen = set()
        for g in games:
            if not isinstance(g, dict) or not isinstance(g.get("date"), str):
                raise ValueError(f"{league}/{filename}: invalid game")
            key = str(g.get("slug") if league == "NFL" else g.get("id") or "")
            if not key or key == "None" or key in source_seen:
                raise ValueError(f"{league}/{filename}: missing or repeated game ID {key}")
            source_seen.add(key)
            if not g["date"].startswith("2026-"):
                continue
            old = combined.get(key)
            if old is None:
                combined[key] = g
            else:
                if old["date"] != g["date"]:
                    raise ValueError(f"{league}: conflicting dates for {key}")
                # Retain fields from both sources while honoring existing documents.
                combined[key] = {**old, **{k: v for k, v in g.items() if v}}
    return list(combined.values())


def archive_documents(league, games, today):
    linked, missing = [], []
    for g in games:
        gid = str(g.get("slug") if league == "NFL" else g["id"])
        if league == "NHL" and g.get("competition") == "international_hockey":
            continue  # Not a standard NHL club GS/ES document.
        d = date.fromisoformat(g["date"])
        status = str(g.get("status", "")).lower()
        is_final = "final" in status or status in {"off", "completed"}
        eligible = d <= today - timedelta(days=CUTOFF_DAYS) and (
            league == "NFL" or is_final or league == "NHL" and status == "final")
        if not eligible:
            continue
        keys = (("pdf_url", "PDF"),) if league in ("NFL", "NBA", "WNBA") else (
            (("gs_url", "GS"), ("es_url", "ES")) if league == "NHL" else
            (("box_url", "BOX"), ("plays_url", "PLAYS")))
        for attr, kind in keys:
            url = g.get(attr)
            identity = f"{league}:{gid}:{kind}"
            item = {"key": identity, "league": league, "id": gid, "kind": kind,
                    "date": g["date"], "label": g.get("label", "")}
            if isinstance(url, str) and url.startswith("https://"):
                linked.append({**item, "url": url})
            else:
                missing.append({**item, "reason": "not_linked"})
    return linked, missing


def bounded_get(url):
    # Full PDF is needed to parse and identify a game, unlike first-byte checks.
    with requests.get(url, timeout=(10, 25), stream=True, headers=HEADERS,
                      allow_redirects=True) as response:
        if response.status_code == 404:
            return None, "not_found"
        if response.status_code in (401, 403, 429) or response.status_code >= 500:
            return None, "source_unavailable_http_" + str(response.status_code)
        response.raise_for_status()
        raw = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                raw.extend(chunk)
            if len(raw) > MAX_BYTES:
                return None, "too_large_to_inspect"
        return bytes(raw), "downloaded"


def slugs_from_label(item):
    if item["league"] == "NFL":
        slug = item["id"]
        m = re.fullmatch(r"(.+)-at-(.+)-2026-(?:pre|reg|post)-\d+", slug)
        return (m.group(1).split("-")[-1], m.group(2).split("-")[-1]) if m else ()
    parts = item.get("label", "").split(" @ ")
    if len(parts) != 2:
        return ()
    return tuple(side.strip().split()[-1] for side in parts)


def pdf_date_match(text, iso):
    d = date.fromisoformat(iso)
    names = ("January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December")
    yy = d.year % 100
    patterns = (rf"\b{d.month:02d}/{d.day:02d}/{d.year}\b",
                rf"\b{d.month}/{d.day}/{d.year}\b",
                rf"\b0?{d.month}[/\-]0?{d.day}[/\-]{yy:02d}\b",
                rf"\b{d.month:02d}-{d.day:02d}-{d.year}\b",
                rf"\b{names[d.month - 1]}\s+0?{d.day},?\s+{d.year}\b",
                rf"\b{names[d.month - 1][:3]}\w*\.?\s+0?{d.day},?\s+{d.year}\b",
                rf"\b{d.year}-{d.month:02d}-{d.day:02d}\b")
    return any(re.search(p, text, flags=re.I) for p in patterns)


def inspect_pdf(item, raw):
    if not raw.startswith(b"%PDF-"):
        return "invalid_format", "Response is not a PDF"
    try:
        reader = PdfReader(io.BytesIO(raw), strict=False)
        pages = len(reader.pages)
        if pages < 1:
            return "invalid_format", "PDF has no readable pages"
        # NFL report cover/title dates can appear after the opening summary
        # pages; check more pages without requiring full-text extraction of a
        # potentially very long NBA/WNBA gamebook.
        max_pages = 8 if item["league"] == "NFL" else 3
        text = "\n".join((page.extract_text() or "") for page in list(reader.pages)[:max_pages])
    except Exception as exc:
        return "unreadable_document", str(exc)[:150]
    terms = slugs_from_label(item)
    norm = re.sub(r"[^a-z0-9]", "", text.lower())
    matches = bool(len(terms) == 2 and all(
        re.sub(r"[^a-z0-9]", "", term.lower()) in norm for term in terms))
    # Content-level match demands both distinct teams AND a date in the PDF.
    if matches and pdf_date_match(text, item["date"]):
        return "verified_match", f"{pages} pages; team names and date matched text"
    return "readable_identity_unconfirmed", (
        f"{pages} pages; teams_in_text={matches}; date_in_text={pdf_date_match(text, item['date'])}"
    )


def valid_url(item):
    url = item["url"]
    p = urlparse(url)
    if p.scheme != "https" or p.username or p.password or p.port:
        return False
    if item["kind"] == "PDF":
        return p.hostname in PDF_HOSTS[item["league"]] and p.path.lower().endswith(".pdf")
    if item["league"] == "NHL":
        gid = item["id"]
        if not re.fullmatch(r"\d{10}", gid):
            return False
        season = int(gid[:4])
        expected = (f"/scores/htmlreports/{season}{season + 1}/"
                    f"{item['kind']}{gid[4:]}.HTM")
        return p.hostname == "www.nhl.com" and p.path == expected
    if item["league"] == "MLB":
        expected = "box-score" if item["kind"] == "BOX" else "play-by-play"
        return (p.hostname == "www.mlb.com"
                and p.path.rstrip("/") == f"/gameday/{item['id']}/{expected}")
    return False


def inspect_nhl(item, raw):
    html = raw.decode("utf-8", errors="replace").lower()
    expected = "game summary" if item["kind"] == "GS" else "event summary"
    if "<html" not in html or expected not in html:
        return "invalid_report_content", "NHL report HTML/type not found"
    # Official report path already encodes exact NHL game ID and report type.
    return "verified_report", f"Official {item['kind']} HTML contains expected report heading"


def inspect_mlb(item):
    gid = item["id"]
    if not gid.isdigit():
        return "invalid_game_id", "Non-numeric MLB game ID"
    # Validate the actual game's identity AND both official stats sections.
    # The underlying Gameday webpage URL by itself is not evidence that the
    # score or play-by-play exists for this game.
    try:
        url = f"https://statsapi.mlb.com/api/v1.1/game/{gid}/feed/live"
        payload = fetch_json(url)
        game_data = payload.get("gameData") or {}
        official_id = str((game_data.get("game") or {}).get("pk")
                          or payload.get("gamePk") or "")
        if official_id != gid:
            return "mismatched_game_id", f"Official API gamePk {official_id!r}, expected {gid}"
        live = payload.get("liveData") or {}
        if item["kind"] == "BOX":
            teams = (live.get("boxscore") or {}).get("teams")
            ok = isinstance(teams, dict) and all(x in teams for x in ("home", "away"))
        else:
            plays = (live.get("plays") or {}).get("allPlays")
            ok = isinstance(plays, list) and bool(plays)
        if not ok:
            return "invalid_report_content", "Official feed lacks required statistics structure"
        return "verified_official_stats", (
            f"Official game ID {gid} and {'box-score' if item['kind'] == 'BOX' else 'play-by-play'} data verified"
        )
    except requests.HTTPError as exc:
        n = getattr(exc.response, "status_code", "unknown")
        return "source_unavailable", f"Official stats API HTTP {n}"
    except (requests.RequestException, ValueError) as exc:
        return "source_unavailable", str(exc)[:180]


def inspect(item):
    if not valid_url(item):
        status, detail = "invalid_url", "Link is not the expected official document URL"
    elif item["league"] == "MLB":
        status, detail = inspect_mlb(item)
    else:
        try:
            raw, status = bounded_get(item["url"])
            if raw is None:
                detail = "Official host did not return an inspectable document: " + status
            elif item["kind"] == "PDF":
                status, detail = inspect_pdf(item, raw)
            else:
                status, detail = inspect_nhl(item, raw)
        except (requests.RequestException, OSError, ValueError) as exc:
            status, detail = "source_unavailable", str(exc)[:180]
    return {
        "url": item["url"], "league": item["league"], "id": item["id"],
        "kind": item["kind"], "date": item["date"],
        "status": status, "detail": detail, "checked_at": now_utc().isoformat(),
    }


def fresh(record, item, now):
    if not isinstance(record, dict) or record.get("url") != item["url"]:
        return False
    try:
        stamp = datetime.fromisoformat(record["checked_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            return False
        age = now - stamp
        days = REFRESH_DAYS if record.get("status") in GOOD else 1
        return timedelta(0) <= age < timedelta(days=days)
    except (KeyError, ValueError, TypeError):
        return False


def make_report(links, missing, previous, checked, now):
    existing = previous.get("results", {}) if isinstance(previous, dict) else {}
    # Preserve old verification evidence but count only currently linked documents.
    merged = dict(existing)
    merged.update(checked)
    current = {it["key"]: it for it in links}
    statuses = Counter()
    for key, item in current.items():
        prior = merged.get(key)
        if not prior or prior.get("url") != item["url"]:
            statuses["not_yet_checked"] += 1
        else:
            statuses[prior["status"]] += 1
    by_league = {}
    for league in REPOS:
        these = [it for it in links if it["league"] == league]
        inspected = [it for it in these if it["key"] in merged and
                     merged[it["key"]].get("url") == it["url"]]
        by_league[league] = {
            "linked": len(these),
            "inspected": len(inspected),
            "uninspected": len(these) - len(inspected),
            "no_link": sum(it["league"] == league for it in missing),
            "statuses": dict(sorted(Counter(merged[it["key"]]["status"]
                                    for it in inspected).items())),
        }
    return {
        "scope": "2026", "updated_at": now.isoformat(),
        "meaning": "A successful workflow does not mean every document has passed.",
        "summary": {"linked": len(links), "inspected": len(links) -
                    statuses["not_yet_checked"], "no_link": len(missing),
                    "statuses": dict(sorted(statuses.items()))},
        "leagues": by_league,
        "no_link_samples": missing[:75],
        "results": dict(sorted(merged.items())),
    }


def run(limit=150, workers=6, today=None, output=REPORT):
    now = now_utc()
    today = today or now.date()
    old = json.loads(output.read_text()) if output.exists() else {}
    links, missing = [], []
    for league in REPOS:
        games = gather(league)
        x, y = archive_documents(league, games, today)
        links.extend(x)
        missing.extend(y)
        print(f"SOURCE {league}: {len(games)} 2026 games; {len(x)} linked documents, "
              f"{len(y)} eligible reports not linked", flush=True)
    old_results = old.get("results", {})
    pending = [it for it in links if not fresh(old_results.get(it["key"]), it, now)]
    # Prioritize never checked docs rather than retrying the same unavailable host.
    pending.sort(key=lambda x: (x["key"] in old_results, x["date"], x["key"]))
    # Fair selection across leagues; prevent large MLB/NHL archives from
    # monopolizing the verification budget.
    buckets = {league: [it for it in pending if it["league"] == league]
               for league in REPOS}
    chosen = []
    while len(chosen) < limit and any(buckets.values()):
        for league in REPOS:
            if buckets[league] and len(chosen) < limit:
                chosen.append(buckets[league].pop(0))
    print(f"VERIFYING {len(chosen)} of {len(pending)} eligible due documents", flush=True)
    checked = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_map = {pool.submit(inspect, item): item for item in chosen}
        for future in as_completed(future_map):
            item = future_map[future]
            try:
                checked[item["key"]] = future.result()
            except Exception as exc:
                checked[item["key"]] = {
                    "url": item["url"], "league": item["league"], "id": item["id"],
                    "kind": item["kind"], "date": item["date"],
                    "status": "inspection_error", "detail": str(exc)[:180],
                    "checked_at": now_utc().isoformat(),
                }
    report = make_report(links, missing, old, checked, now)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("DOCUMENT VERIFICATION RESULTS (workflow success != full document coverage)")
    print(json.dumps(report["leagues"], indent=2))
    print("SUMMARY " + json.dumps(report["summary"], sort_keys=True))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=150)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    run(limit=max(1, min(args.limit, 800)), workers=max(1, min(args.workers, 8)))


if __name__ == "__main__":
    main()
