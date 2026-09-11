#!/usr/bin/env python3
"""
One call for the probes a run does before it decides anything: the branch and its
diff range, whether `gh` is authenticated, the PR for this branch and its check
buckets, whether the repo has a `CODE_REVIEW_GUIDE.md`, which spec this branch
belongs to, whether this is a LexFlow app, and whether the diff's hunks contain UI.

Consumed by /bb:ship (Prerequisites and Step 0) and by /bb:review (the availability
probe in `skills/review/references/fronts.md`), which read this one payload instead
of probing again.

The diff range is `<merge_base>...HEAD`, resolved once here so every reader shares it.

Usage:
  python3 preflight.py
  python3 preflight.py --repo /path/to/repo --base develop
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from shutil import which

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gather_context import resolve_merge_base  # noqa: E402
from inspect_pr_checks import parse_available_fields  # noqa: E402
from scan_specs import scan  # noqa: E402

MAX_UI_EXAMPLES = 8

# The elements an accessibility review is actually about. Used to tell a tag from a
# prose placeholder: `<merge_base>` and `<div>` are the same shape, and a repo of
# documentation is full of the first kind, so a bare name only counts when it is one
# of these. A tag carrying an attribute, a slash or a capital needs no list.
A11Y_ELEMENTS = (
    "a|abbr|article|aside|audio|button|canvas|dialog|details|summary|div|fieldset|"
    "figure|figcaption|footer|form|h[1-6]|header|iframe|img|input|label|legend|li|"
    "main|nav|ol|optgroup|option|p|picture|progress|section|select|span|svg|table|"
    "tbody|td|textarea|tfoot|th|thead|tr|ul|video"
)

# What makes a hunk a UI change is what the hunk contains, never the file's extension:
# a `.tsx` whose diff only moves handler bodies leaves the markup as it was.
UI_MARKERS = (
    (
        "markup",
        re.compile(
            r"</[A-Za-z]"  # a closing tag
            r"|<[A-Za-z][\w.-]*(?:\s+[\w:@.-]+\s*=|\s*/>)"  # an attribute, or self-closing
            r"|<[A-Z][\w.]*[\s/>]"  # a JSX component
            rf"|<(?:{A11Y_ELEMENTS})[\s/>]"  # a semantic element, written bare
            r"|createElement|innerHTML|dangerouslySetInnerHTML"
        ),
    ),
    (
        # Server-side and non-JSX templates: the markup is HTML but the interpolation
        # is what identifies the file as a rendered surface. `${{ }}` is excluded
        # because that is a GitHub Actions expression, not a template.
        "template",
        re.compile(
            r"(?<!\$)\{\{[^}]*\}\}|\{%[^%]*%\}|<%=?|\{#(?:if|each|await)\b|"
            r"\bv-html\b|\bv-if\b|\*ngIf\b|th:(?:text|if)\b|@html\b"
        ),
    ),
    ("semantics", re.compile(r"\brole=|\baria-[\w-]+|\balt=|\blabel=|\btabIndex|\bautoFocus|\.focus\(")),
    ("interaction", re.compile(r"\bon(?:Click|KeyDown|KeyUp|KeyPress|Focus|Blur|Pointer\w+)\b")),
    ("style", re.compile(r"\boutline\s*:|:focus|\bcolor\s*:|\bbackground(?:-color)?\s*:|display\s*:\s*none")),
)


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    # The encoding is named because `text=True` decodes in the locale codec, which is
    # cp1252 on Windows: one accented character in a filename, a PR title or a hunk
    # would raise before this script prints anything at all.
    p = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    code, out, _ = run(cmd, cwd=cwd)
    return out if code == 0 else None


def load_json(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def probe_pr(cwd: str) -> dict | None:
    """The **open** PR for this branch, or None.

    `gh pr view` answers with the branch's most recent PR whatever its state, and a
    non-null `pr` is read downstream as the run's destination, so a merged or closed one
    would send the landing back to a PR nobody can push to. `state` is what filters it.
    """
    pr = load_json(
        run_ok(
            ["gh", "pr", "view", "--json", "number,url,title,baseRefName,state,isDraft,mergeable"],
            cwd=cwd,
        )
    )
    if not pr or (pr.get("state") or "").upper() != "OPEN":
        return None
    return pr


# The buckets this names one by one. Anything `gh` starts emitting outside the set lands
# in `other` rather than nowhere: a check the reader never sees is worse than one it
# cannot classify.
NAMED_BUCKETS = ("fail", "pending", "cancel", "pass", "skipping")

# Every key the available shape carries, so the unavailable one can carry them too.
EMPTY_CHECKS = {
    "total": 0,
    "failing": [],
    "pending": [],
    "cancelled": [],
    "passing": 0,
    "skipping": 0,
    "other": {},
}


CHECK_FIELDS = ("name", "state", "bucket", "link")


def probe_checks(cwd: str, number: int) -> dict:
    """Bucket the PR's checks. `gh pr checks` exits non-zero while any check is red."""
    code, out, err = run(
        ["gh", "pr", "checks", str(number), "--json", ",".join(CHECK_FIELDS)], cwd=cwd
    )
    rows = load_json(out)
    if rows is None:
        # A `gh` that does not offer one of those fields rejects the whole request and
        # names the ones it has, so asking again with the intersection is what keeps the
        # buckets from vanishing over a version skew. `inspect_pr_checks.py` reads the
        # same message, which is why its parser is imported instead of rewritten here.
        usable = [f for f in CHECK_FIELDS if f in parse_available_fields(f"{err}\n{out}")]
        if usable:
            code, out, err = run(
                ["gh", "pr", "checks", str(number), "--json", ",".join(usable)], cwd=cwd
            )
            rows = load_json(out)
    if rows is None:
        # Same keys as the available shape. A reader that goes straight for `failing`
        # gets an empty list instead of nothing at all, and `available` is still the
        # one field that says whether any of it was measured.
        return {"available": False, "exit_code": code, **EMPTY_CHECKS}

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
        # A cancelled check is not a pass and not a failure. It is named because a PR
        # whose one gate was cancelled reads as "nothing failing" otherwise.
        "cancelled": buckets.get("cancel", []),
        "passing": len(buckets.get("pass", [])),
        "skipping": len(buckets.get("skipping", [])),
        "other": {
            name: rows_ for name, rows_ in buckets.items() if name not in NAMED_BUCKETS
        },
    }


def probe_ui(cwd: str, diff_range: str) -> dict:
    # `.bb/` is bb's own bookkeeping, and a spec is prose about a UI, never the UI. Left
    # in, a spec that quotes markup offers the a11y front over a diff that has none.
    diff = (
        run_ok(["git", "diff", diff_range, "-U0", "--", ".", ":(exclude).bb/"], cwd=cwd) or ""
    )
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
    """The spec this branch belongs to, when one of the branch's segments is its slug.

    A whole segment and not a substring: `perf/deterministic-probes` contains the slug
    `probes` without belonging to it, and the list arrives sorted by `created`, so the
    oldest accidental match would be the one that won.
    """
    if not branch:
        return None
    segments = {branch, *branch.split("/")}
    for spec in specs:
        if {name for name in (spec["dir"], spec["slug"]) if name} & segments:
            return spec
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe the ground a run stands on: branch, diff range, PR, checks, spec, UI."
    )
    parser.add_argument("--repo", default=".", help="Path inside the target git repository.")
    parser.add_argument(
        "--base", default=None, help="Base branch, overriding the PR's own and the repo default."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo, base_override = args.repo, args.base

    git_root = run_ok(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if not git_root:
        print(json.dumps({"error": "Not inside a git repository"}))
        sys.exit(1)

    cwd = git_root
    root = Path(cwd)
    # `which` first: `subprocess.run` raises FileNotFoundError for a missing executable
    # instead of exiting non-zero, and a traceback here would take down the whole probe
    # on the very machines whose payload is supposed to say `gh_authenticated: false`.
    gh_ok = which("gh") is not None and run(["gh", "auth", "status"], cwd=cwd)[0] == 0

    pr = probe_pr(cwd) if gh_ok else None

    # The PR's own base outranks the repo default, and is resolved before the range: a
    # stacked PR, or one opened against `develop`, otherwise gets the parent branch's
    # commits in every diff below and in the range each front reads as authoritative.
    base = base_override or (pr or {}).get("baseRefName")
    if not base and gh_ok:
        base = run_ok(
            ["gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
            cwd=cwd,
        )
    base = base or "main"
    merge_base, _ = resolve_merge_base(base, cwd)
    diff_range = f"{merge_base}...HEAD" if merge_base else None

    # `scan` walks up from where it is pointed, and the contract is the nearest ancestor
    # of the cwd, not of the git root: a monorepo package with its own `.bb/` is the one
    # the run is standing in. Every git call above is rooted, which is a different question.
    specs = scan(repo)
    branch = run_ok(["git", "branch", "--show-current"], cwd=cwd)

    result = {
        "git_root": cwd,
        "branch": branch,
        "upstream": run_ok(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=cwd
        ),
        "base_branch": base,
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
        # The one thing this probe wants out of the spec scan. Selecting a spec is
        # `/bb:implement`'s, off `scan_specs.py`'s own stdout, so the rest of that
        # payload has no reader here and is not copied into this one.
        "branch_spec": branch_spec(specs["specs"], branch),
        "ui": probe_ui(cwd, diff_range) if diff_range else {"hit": False, "markers": [], "examples": {}},
    }

    if not merge_base:
        result["warning"] = f"Could not find merge base between {base} and HEAD"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
