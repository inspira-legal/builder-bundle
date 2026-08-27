#!/usr/bin/env python3
"""
Scan `.bb/*/spec.md` and apply the selection rule of the spec-state contract
(`plugins/bb/references/spec-state.md`): keep `pending` and `in-progress`, pick the
smallest `created`, tie-break on the slug, sort a spec with no frontmatter last, and
report a `blocked` one with the line its `## Open` carries instead of dropping it.

Consumed by /bb:implement (its step 1) and by /bb:review's availability probe through
`preflight.py`, which imports `scan()` from here.

Usage:
  python3 scan_specs.py
  python3 scan_specs.py --repo /path/to/repo
  python3 scan_specs.py --slug my-feature
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# A spec with no `created` sorts after every dated one, which is the contract's
# "unknown created (sorted last)".
UNDATED = "9999-12-31"

SELECTABLE = ("pending", "in-progress")

# A BOM and leading blank lines are invisible in an editor, and both push the opening
# `---` off the start of the file.
LEADING_NOISE = "\ufeff \t\r\n"


def find_bb_root(start: Path) -> Path:
    """Nearest ancestor of `start` that already has a `.bb/`, else `start` itself.

    The walk stops at the repository, the directory holding `.git`, and that boundary is
    the point: past it the next `.bb/` up belongs to another project, or to the home
    directory, and a run standing in a repo with no `.bb/` would adopt it.
    """
    for candidate in (start, *start.parents):
        if (candidate / ".bb").is_dir():
            return candidate
        if (candidate / ".git").exists():
            break
    return start


def parse_frontmatter(text: str) -> dict[str, str]:
    # A BOM or a blank line before the opening `---` is invisible in an editor and would
    # otherwise yield no block at all, which reads as `status: pending` and puts a spec
    # already `done` back in the selection.
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text.lstrip(LEADING_NOISE), re.DOTALL)
    if not match:
        return {}
    block = {}
    for line in match.group(1).splitlines():
        pair = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line.strip())
        if pair:
            value = pair.group(2).split("#")[0].strip().strip("\"'")
            block[pair.group(1)] = value
    return block


def first_open_line(text: str) -> str | None:
    """The one line a blocked spec's `## Open` carries, for the report."""
    match = re.search(r"^##\s+Open\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    for line in match.group(1).splitlines():
        stripped = line.strip().lstrip("-*").strip()
        if stripped:
            return stripped[:400]
    return None


def read_spec(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    block = parse_frontmatter(text)
    status = block.get("status") or "pending"
    entry = {
        "slug": block.get("slug") or path.parent.name,
        "dir": path.parent.name,
        "path": str(path),
        "status": status,
        "created": block.get("created") or None,
        "has_frontmatter": bool(block),
        "has_tasks": bool(re.search(r"^##\s+Tasks\s*$", text, re.MULTILINE)),
        "unticked_tasks": len(re.findall(r"^\s*-\s+\[ \]", text, re.MULTILINE)),
    }
    if status == "blocked":
        entry["open_note"] = first_open_line(text)
    return entry


def sort_key(entry: dict) -> tuple[str, str]:
    return (entry["created"] or UNDATED, entry["dir"])


def scan(repo: str = ".") -> dict:
    bb_root = find_bb_root(Path(repo).resolve())
    specs = sorted((read_spec(p) for p in (bb_root / ".bb").glob("*/spec.md")), key=sort_key)
    selectable = [s for s in specs if s["status"] in SELECTABLE]
    return {
        "bb_root": str(bb_root),
        "has_bb_dir": (bb_root / ".bb").is_dir(),
        "specs": specs,
        "selected": selectable[0] if selectable else None,
        "blocked": [s for s in specs if s["status"] == "blocked"],
        "pending_slugs": [s["dir"] for s in selectable],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan `.bb/*/spec.md` and apply the spec-state selection rule, as JSON."
    )
    parser.add_argument("--repo", default=".", help="Path inside the target repository.")
    parser.add_argument(
        "--slug", default=None, help="Target this spec by dir or slug instead of selecting one."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = scan(args.repo)

    # `is not None` and not truthiness: `--slug ""` named a target and missed it, which is
    # `found: false` and a reported error, not a silent fall-through to the selection rule.
    # The caller stops on `found: false`, so the key travels whenever a name was given.
    if args.slug is not None:
        # A named target replaces the selection rule; the scan still travels, because the
        # caller reports the available slugs when the name misses.
        named = next(
            (s for s in result["specs"] if args.slug in (s["dir"], s["slug"])),
            None,
        )
        result["selected"] = named
        result["named"] = args.slug
        result["found"] = named is not None

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
