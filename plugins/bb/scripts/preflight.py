#!/usr/bin/env python3
"""
One call for the probes a run does before it decides anything: the branch and its
diff range, whether `gh` is authenticated, the PR for this branch and its check
buckets, whether the repo has a `CODE_REVIEW_GUIDE.md`, which spec this branch
belongs to, whether this is a LexFlow app, and whether the diff's hunks contain UI.

Consumed by /bb:ship (Prerequisites and Step 0) and by /bb:review (the availability
probe in `skills/review/references/fronts.md`). Both used to spend five to seven
prose-decided calls on exactly this, one round trip each.

The diff range is `<merge_base>...HEAD`, resolved once here so every reader shares it.

Usage:
  python3 preflight.py
  python3 preflight.py --repo /path/to/repo --base develop
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_specs import scan  # noqa: E402

MAX_UI_EXAMPLES = 8

# What makes a hunk a UI change is what the hunk contains, never the file's extension:
# a `.tsx` whose diff only moves handler bodies leaves the markup as it was.
UI_MARKERS = (
    ("markup", re.compile(r"<[A-Za-z][\w.-]*[\s/>]|createElement|innerHTML|dangerouslySetInnerHTML")),
    ("semantics", re.compile(r"\brole=|\baria-[\w-]+|\balt=|\blabel=|\btabIndex|\bautoFocus|\.focus\(")),
    ("interaction", re.compile(r"\bon(?:Click|KeyDown|KeyUp|KeyPress|Focus|Blur|Pointer\w+)\b")),
    ("style", re.compile(r"\boutline\s*:|:focus|\bcolor\s*:|\bbackground(?:-color)?\s*:|display\s*:\s*none")),
)


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    code, out = run(cmd, cwd=cwd)
    return out if code == 0 else None


def load_json(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def resolve_range(base: str, cwd: str) -> tuple[str | None, str | None]:
    run(["git", "fetch", "origin", base], cwd=cwd)  # best-effort; offline is fine
    for ref in (f"origin/{base}", base):
        merge_base = run_ok(["git", "merge-base", ref, "HEAD"], cwd=cwd)
        if merge_base:
            return merge_base, ref
    return None, None


def probe_pr(cwd: str) -> dict | None:
    return load_json(
        run_ok(
            ["gh", "pr", "view", "--json", "number,url,title,baseRefName,state,isDraft,mergeable"],
            cwd=cwd,
        )
    )


def probe_checks(cwd: str, number: int) -> dict | None:
    """Bucket the PR's checks. `gh pr checks` exits non-zero while any check is red."""
    code, out = run(
        ["gh", "pr", "checks", str(number), "--json", "name,state,bucket,link"], cwd=cwd
    )
    rows = load_json(out)
    if rows is None:
        return {"available": False, "exit_code": code}

    buckets: dict[str, list[dict]] = {}
    for row in rows:
        buckets.setdefault(row.get("bucket") or "unknown", []).append(
            {"name": row.get("name"), "state": row.get("state"), "link": row.get("link")}
        )
    return {
        "available": True,
        "exit_code": code,
        "total": len(rows),
        "failing": buckets.get("fail", []),
        "pending": buckets.get("pending", []),
        "passing": len(buckets.get("pass", [])),
        "skipping": len(buckets.get("skipping", [])),
    }


def probe_ui(cwd: str, diff_range: str) -> dict:
    diff = run_ok(["git", "diff", diff_range, "-U0"], cwd=cwd) or ""
    hits: dict[str, list[str]] = {}
    current = "?"
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
            continue
        if line.startswith(("+++", "---", "@@", "diff ", "index ")):
            continue
        if not line.startswith(("+", "-")):
            continue
        body = line[1:]
        for name, pattern in UI_MARKERS:
            if pattern.search(body):
                examples = hits.setdefault(name, [])
                if len(examples) < MAX_UI_EXAMPLES:
                    examples.append(f"{current}: {body.strip()[:120]}")
    return {"hit": bool(hits), "markers": sorted(hits), "examples": hits}


def branch_spec(specs: list[dict], branch: str | None) -> dict | None:
    """The spec this branch belongs to, when its name carries the slug."""
    if not branch:
        return None
    for spec in specs:
        if spec["dir"] and spec["dir"] in branch:
            return spec
    return None


def parse_args(argv: list[str]) -> tuple[str, str | None]:
    repo, base = ".", None
    args = argv[:]
    while args:
        if args[0] == "--repo" and len(args) > 1:
            repo, args = args[1], args[2:]
        elif args[0] == "--base" and len(args) > 1:
            base, args = args[1], args[2:]
        else:
            args = args[1:]
    return repo, base


def main() -> None:
    repo, base_override = parse_args(sys.argv[1:])

    git_root = run_ok(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if not git_root:
        print(json.dumps({"error": "Not inside a git repository"}))
        sys.exit(1)

    cwd = git_root
    root = Path(cwd)
    gh_ok = run(["gh", "auth", "status"], cwd=cwd)[0] == 0

    base = base_override
    if not base and gh_ok:
        base = run_ok(
            ["gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
            cwd=cwd,
        )
    base = base or "main"
    merge_base, base_ref = resolve_range(base, cwd)
    diff_range = f"{merge_base}...HEAD" if merge_base else None

    pr = probe_pr(cwd) if gh_ok else None
    specs = scan(cwd)
    branch = run_ok(["git", "branch", "--show-current"], cwd=cwd)

    result = {
        "git_root": cwd,
        "branch": branch,
        "upstream": run_ok(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=cwd
        ),
        "base_branch": base,
        "base_ref": base_ref,
        "merge_base": merge_base,
        "diff_range": diff_range,
        "diff_stat": run_ok(["git", "diff", diff_range, "--stat"], cwd=cwd) if diff_range else "",
        "files_changed": (
            run_ok(["git", "diff", diff_range, "--name-status"], cwd=cwd) if diff_range else ""
        ),
        "uncommitted_changes": run_ok(["git", "status", "--short"], cwd=cwd) or "",
        "gh_authenticated": gh_ok,
        "pr": pr,
        "checks": probe_checks(cwd, pr["number"]) if pr and pr.get("number") else None,
        "code_review_guide": (root / "CODE_REVIEW_GUIDE.md").is_file(),
        "project_kind": "lexflow" if (root / "lexflow.toml").is_file() else "git",
        "bb_root": specs["bb_root"],
        "has_bb_dir": specs["has_bb_dir"],
        "branch_spec": branch_spec(specs["specs"], branch),
        "selected_spec": specs["selected"],
        "pending_slugs": specs["pending_slugs"],
        "ui": probe_ui(cwd, diff_range) if diff_range else {"hit": False, "markers": [], "examples": {}},
    }

    if not merge_base:
        result["warning"] = f"Could not find merge base between {base} and HEAD"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
