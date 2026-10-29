#!/usr/bin/env python3
"""
Read every `.bb/<slug>/` and list what the work left out, for /bb:backlog to give it a place.

It reads the parts of the records that are decidable from the bytes: the `## Cuts` of
`discovery.md`, the `## Out of scope` and `## Open` of `spec.md`, the unticked tasks of a spec
that ended (`done` or `blocked`) or of a discovery that shelved the idea, and the ids already
written to `backlog.md`. Which item is worth keeping, and where it goes, is the skill's
judgment (`references/destination.md`). This script writes nothing.

Usage:
  python3 harvest.py
  python3 harvest.py --repo /path/to/repo --slug my-feature
  python3 harvest.py --stale-days 14 --today 2026-10-27
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

# The contract's root walk and frontmatter parser live in the plugin's shared scan_specs.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from scan_specs import find_bb_root, parse_frontmatter  # noqa: E402

CUT_REASONS = ("no-market", "out-of-appetite", "depends-on-other", "low-confidence")
ENDED = ("done", "blocked")
# The emphasized marker only: inside a snake_case identifier or a `code span` it is not one.
REVISIT = re.compile(r"(?<![\w`])[_*]{1,2}revisit[_*]{1,2}(?![\w`])", re.IGNORECASE)
DISCARDED = re.compile(r"(?<![\w`])[_*]{1,2}discarded[_*]{1,2}(?![\w`])", re.IGNORECASE)
ICE = re.compile(r"\bICE\s*(\d+(?:[.,]\d+)?)", re.IGNORECASE)
BACKLOG_ID = re.compile(r"id:([0-9a-f]{8})")
UNTICKED = re.compile(r"^\s*-\s+\[ \]\s+(.*)$")
# Two items sharing this much of their content words are worth a second look, not a merge.
DUPLICATE_OVERLAP = 0.5


def section(lines: list[str], name: str) -> tuple[int, list[str]] | None:
    """The body of `## name`, with the line number of its first body line (1-based)."""
    head = re.compile(rf"^##\s+{re.escape(name)}\s*$", re.IGNORECASE)
    for i, line in enumerate(lines):
        if head.match(line):
            end = next((j for j in range(i + 1, len(lines)) if re.match(r"^##\s", lines[j])), len(lines))
            return i + 2, lines[i + 1 : end]
    return None


def bullets(start: int, body: list[str], stop: re.Pattern | None = None) -> list[tuple[int, str]]:
    """Top-level `- ` bullets with their indented continuation lines folded in."""
    found: list[tuple[int, str]] = []
    for offset, line in enumerate(body):
        if stop and stop.match(line):
            break
        if re.match(r"^- ", line) and not UNTICKED.match(line):
            found.append((start + offset, line[2:].strip()))
        elif found and line.startswith((" ", "\t")) and line.strip():
            found[-1] = (found[-1][0], f"{found[-1][1]} {line.strip()}")
    return found


def title_of(text: str) -> str:
    # A leading bold run is the item's name; bold further in is emphasis.
    bold = re.match(r"\*\*(.+?)\*\*", text)
    first = bold.group(1) if bold else re.split(r"(?<=[.;])\s", text, maxsplit=1)[0]
    for reason in CUT_REASONS:
        first = re.sub(rf"[,:]?\s*`?{reason}`?.*$", "", first)
    return first.replace("**", "").strip(" .;:,")[:120]


def trigger_of(text: str) -> str | None:
    marker = REVISIT.search(text)
    if not marker:
        return None
    after = text[marker.end() :].strip(" .,;:()")
    return after or None


def tokens(text: str) -> list[str]:
    plain = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", plain)


def words(text: str) -> set[str]:
    # Only the duplicate check drops short words; the id keeps them, or "PDF" and "XLS" collide.
    return {w for w in tokens(text) if len(w) >= 4}


def item(slug: str, kind: str, file: str, sec: str, line: int, text: str, **extra) -> dict:
    normalized = " ".join(tokens(text))
    digest = hashlib.sha1(f"{slug}#{file}#{sec}#{normalized}".encode()).hexdigest()[:8]
    ice = ICE.search(text)
    return {
        "id": digest,
        "kind": kind,
        "title": title_of(text),
        "text": text,
        "revisit": bool(REVISIT.search(text)),
        "trigger": trigger_of(text),
        "discarded": bool(DISCARDED.search(text)),
        "ice": ice.group(1).replace(",", ".") if ice else None,
        "source": f"{file}#{sec.lower().replace(' ', '-')}:{line}",
        **extra,
    }


def read_discovery(slug: str, path: Path) -> tuple[dict | None, list[dict]]:
    if not path.is_file():
        return None, []
    text = path.read_text(encoding="utf-8", errors="replace")
    block = parse_frontmatter(text)
    record = {"verdict": block.get("verdict") or None, "phase": block.get("phase") or None}
    cuts = section(text.splitlines(), "Cuts")
    found = []
    if cuts:
        start, body = cuts
        # The `Cut:` list ends where the `Kept` list starts: kept work is in scope.
        for line, raw in bullets(start, body, stop=re.compile(r"^\s*Kept\b", re.IGNORECASE)):
            reason = next((r for r in CUT_REASONS if r in raw), None)
            found.append(item(slug, "cut", "discovery.md", "Cuts", line, raw, reason=reason))
    return record, found


def read_spec(slug: str, path: Path, verdict: str | None) -> tuple[dict | None, list[dict]]:
    if not path.is_file():
        return None, []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    block = parse_frontmatter(text)
    status = block.get("status") or "pending"
    record = {"status": status, "created": block.get("created") or None, "wave": block.get("wave") or None}
    found = []
    for name, kind in (("Out of scope", "out_of_scope"), ("Open", "open")):
        sec = section(lines, name)
        if sec:
            for line, raw in bullets(*sec):
                found.append(item(slug, kind, "spec.md", name, line, raw, reason=None))
    # A task left unticked is a leftover only once the work stopped; in a live spec it is
    # still the plan.
    tasks = section(lines, "Tasks")
    if tasks and (status in ENDED or verdict == "shelve"):
        start, body = tasks
        for offset, raw in enumerate(body):
            match = UNTICKED.match(raw)
            if match:
                found.append(item(slug, "task", "spec.md", "Tasks", start + offset, match.group(1), reason=None))
    return record, found


def duplicates(items: list[dict]) -> list[dict]:
    pairs = []
    for i, a in enumerate(items):
        for b in items[i + 1 :]:
            wa, wb = words(a["text"]), words(b["text"])
            if wa and wb and len(wa & wb) / min(len(wa), len(wb)) >= DUPLICATE_OVERLAP:
                pairs.append({"kind": "near_duplicate", "ids": [a["id"], b["id"]]})
    return pairs


def harvest_slug(slug_dir: Path, today: dt.date, stale_days: int) -> dict:
    slug = slug_dir.name
    discovery, cut_items = read_discovery(slug, slug_dir / "discovery.md")
    spec, spec_items = read_spec(slug, slug_dir / "spec.md", (discovery or {}).get("verdict"))
    items = cut_items + spec_items
    backlog = slug_dir / "backlog.md"
    # Ids are hex ASCII, so a stray byte pasted into the file costs nothing here.
    text = backlog.read_text(encoding="utf-8", errors="replace") if backlog.is_file() else ""
    known = set(BACKLOG_ID.findall(text))
    for entry in items:
        entry["in_backlog"] = entry["id"] in known
    alerts = duplicates([i for i in items if not i["in_backlog"]])
    if spec and spec["status"] == "pending" and spec["created"]:
        try:
            age = (today - dt.date.fromisoformat(spec["created"])).days
        except ValueError:
            age = None
        if age is not None and age > stale_days:
            alerts.insert(0, {"kind": "stale_spec", "days": age, "wave": spec["wave"]})
    return {
        "slug": slug,
        "spec": spec,
        "discovery": discovery,
        "backlog_exists": backlog.is_file(),
        "items": items,
        "alerts": alerts,
    }


def harvest(repo: str = ".", slug: str | None = None, stale_days: int = 14, today: dt.date | None = None) -> dict:
    bb_root = find_bb_root(Path(repo).resolve())
    folder = bb_root / ".bb"
    dirs = sorted(d for d in folder.glob("*") if d.is_dir()) if folder.is_dir() else []
    if slug:
        dirs = [d for d in dirs if d.name == slug]
    today = today or dt.date.today()
    slugs = [harvest_slug(d, today, stale_days) for d in dirs]
    return {"bb_root": str(bb_root), "today": today.isoformat(), "slugs": [s for s in slugs if s["items"] or s["alerts"]]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--slug")
    parser.add_argument("--stale-days", type=int, default=14)
    parser.add_argument("--today", type=dt.date.fromisoformat)
    args = parser.parse_args()
    result = harvest(args.repo, args.slug, args.stale_days, args.today)
    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
