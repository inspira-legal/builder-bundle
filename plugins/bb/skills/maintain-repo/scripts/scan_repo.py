#!/usr/bin/env python3
"""
Read-only maintenance scan for a GitHub repo. Enumerates open PRs, Dependabot
security alerts, and (best-effort) outdated dependencies, then computes a
deterministic priority, an eligibility verdict, and a fail-closed mergeability
verdict for each PR. Emits ONE schema-versioned JSON object to stdout.

This script is strictly READ-ONLY: it only calls `gh api` GETs / `gh pr checks`
and (optionally) `bun outdated`. It never runs `bun install`, never executes a
package lifecycle script, never writes, and NEVER merges. It carries no merge
field at all; merge is a human action.

Usage:
  python scan_repo.py                       # current repo (resolved via gh)
  python scan_repo.py --repo owner/name     # explicit slug
  python scan_repo.py --repo .              # repo at a local path
  python scan_repo.py --max-prs 50 --json
  python scan_repo.py --self-test           # run built-in fixtures, exit non-zero on mismatch

Design notes:
  - Dependabot is detected via the REST `user.login == "dependabot[bot]"`, NOT
    the GraphQL author object (which is null for bot PRs). Unknown author ->
    human_only (fail closed).
  - `mergeable` is computed asynchronously by GitHub; a first read is often
    null/UNKNOWN. We poll-retry briefly and map a persistent UNKNOWN to
    needs-human, never to "mergeable" or "blocked".
  - All attacker-influenceable free text (PR title/body) is stored verbatim in
    `untrusted_*` fields and drives NO logic. Only structured GitHub facts
    (semver components parsed from the canonical title, file paths, enums) feed
    decisions, and even the semver parse falls back to needs-human on any miss.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from shutil import which
from typing import Any

SCHEMA_VERSION = 1

# Files a clean Dependabot PR is allowed to touch. Anything else -> human_only.
LOCKFILE_ALLOWLIST = {
    "package.json",
    "bun.lock",
    "bun.lockb",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

# Changed paths under these prefixes are high-leverage and always human_only.
CI_SENSITIVE_PREFIXES = (
    ".github/workflows/",
    ".github/scripts/",
    "lefthook.yml",
    "lefthook.yaml",
)

BOT_LOGINS = {"dependabot[bot]", "renovate[bot]"}

# REST mergeable_state values that are SAFE on the merge-state clause.
SAFE_MERGE_STATES = {"clean", "unstable"}
# Values that are async / not-yet-computed -> needs-human (never "safe").
PENDING_MERGE_STATES = {"unknown", ""}

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

DEPENDABOT_TITLE = re.compile(
    r"^bump\s+(?P<pkg>\S+)\s+from\s+(?P<frm>\S+)\s+to\s+(?P<to>\S+)",
    re.IGNORECASE,
)
GROUPED_TITLE = re.compile(r"^bump\s+the\s+.+\s+group", re.IGNORECASE)

MAX_UNTRUSTED = 2000


# --------------------------------------------------------------------------- #
# gh plumbing
# --------------------------------------------------------------------------- #
def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def gh_json(args: list[str], cwd: str | None = None) -> Any:
    code, out, err = run(["gh", *args], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {(err or out).strip()}")
    try:
        return json.loads(out or "null")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"could not parse JSON from gh {' '.join(args)}: {e}") from e


def ensure_gh(cwd: str | None) -> None:
    if which("gh") is None:
        raise RuntimeError("gh is not installed or not on PATH")
    code, _, err = run(["gh", "auth", "status"], cwd=cwd)
    if code != 0:
        raise RuntimeError(err.strip() or "gh not authenticated; run `gh auth login`")


def resolve_slug(repo_arg: str, cwd: str | None) -> str:
    if "/" in repo_arg and not repo_arg.startswith(".") and "\\" not in repo_arg:
        return repo_arg
    data = gh_json(["repo", "view", "--json", "nameWithOwner"], cwd=cwd)
    slug = (data or {}).get("nameWithOwner")
    if not slug:
        raise RuntimeError("could not resolve repository slug")
    return str(slug)


# --------------------------------------------------------------------------- #
# semver
# --------------------------------------------------------------------------- #
def parse_semver(version: str) -> tuple[int, int, int] | None:
    core = version.strip().lstrip("vV").split("+", 1)[0].split("-", 1)[0]
    parts = core.split(".")
    if len(parts) < 1:
        return None
    nums: list[int] = []
    for part in (parts + ["0", "0", "0"])[:3]:
        if not part.isdigit():
            return None
        nums.append(int(part))
    return nums[0], nums[1], nums[2]


def semver_class(frm: str, to: str) -> str:
    a = parse_semver(frm)
    b = parse_semver(to)
    if a is None or b is None:
        return "unknown"
    if b[0] != a[0]:
        return "major"
    if b[1] != a[1]:
        return "minor"
    if b[2] != a[2]:
        return "patch"
    return "patch"


def classify_title(title: str) -> dict[str, Any]:
    if GROUPED_TITLE.search(title):
        return {"package": None, "from": None, "to": None, "class": "unknown", "grouped": True}
    m = DEPENDABOT_TITLE.search(title)
    if not m:
        return {"package": None, "from": None, "to": None, "class": "unknown", "grouped": False}
    frm, to = m.group("frm"), m.group("to")
    return {
        "package": m.group("pkg"),
        "from": frm,
        "to": to,
        "class": semver_class(frm, to),
        "grouped": False,
    }


# --------------------------------------------------------------------------- #
# data collection (read-only)
# --------------------------------------------------------------------------- #
def list_open_prs(slug: str, cwd: str | None, max_prs: int) -> list[dict[str, Any]]:
    # REST list: user.login is reliable for bots here (unlike GraphQL author).
    prs = gh_json(
        ["api", "--paginate", f"/repos/{slug}/pulls?state=open&per_page=100"],
        cwd=cwd,
    )
    if not isinstance(prs, list):
        return []
    return prs[:max_prs]


def get_pr_detail(slug: str, number: int, cwd: str | None, retries: int = 3) -> dict[str, Any]:
    # Single-PR GET returns mergeable/mergeable_state; both are computed async,
    # so poll briefly when unknown.
    last: dict[str, Any] = {}
    for attempt in range(retries):
        last = gh_json(["api", f"/repos/{slug}/pulls/{number}"], cwd=cwd) or {}
        if last.get("mergeable") is not None:
            return last
        if attempt < retries - 1:
            time.sleep(1.5)
    return last


def get_ci_state(slug: str, number: int, cwd: str | None) -> dict[str, Any]:
    code, out, _ = run(
        ["gh", "pr", "checks", str(number), "--repo", slug, "--json", "name,state,bucket"],
        cwd=cwd,
    )
    # gh pr checks exits non-zero when checks are failing/pending; stdout is still valid.
    try:
        checks = json.loads(out or "[]")
    except json.JSONDecodeError:
        checks = []
    if not isinstance(checks, list) or not checks:
        return {"state": "none", "failing": []}
    failing = [
        c.get("name", "?")
        for c in checks
        if str(c.get("bucket") or c.get("state") or "").lower() in {"fail", "failure", "error", "cancel"}
    ]
    pending = any(
        str(c.get("bucket") or c.get("state") or "").lower() in {"pending", "queued", "in_progress", "waiting"}
        for c in checks
    )
    if failing:
        return {"state": "failure", "failing": failing}
    if pending:
        return {"state": "pending", "failing": []}
    return {"state": "success", "failing": []}


def get_review_decision(slug: str, number: int, cwd: str | None) -> str | None:
    # reviewDecision is a clean enum and is safe to read from GraphQL.
    query = (
        "query($owner:String!,$repo:String!,$n:Int!){repository(owner:$owner,name:$repo)"
        "{pullRequest(number:$n){reviewDecision}}}"
    )
    owner, name = slug.split("/", 1)
    code, out, _ = run(
        [
            "gh", "api", "graphql",
            "-F", "query=@-",
            "-F", f"owner={owner}",
            "-F", f"repo={name}",
            "-F", f"n={number}",
        ],
        cwd=cwd,
    )
    if code != 0:
        return None
    try:
        data = json.loads(out)
        return data["data"]["repository"]["pullRequest"].get("reviewDecision")
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def list_dependabot_alerts(slug: str, cwd: str | None) -> list[dict[str, Any]]:
    code, out, _ = run(
        ["gh", "api", "--paginate", f"/repos/{slug}/dependabot/alerts?state=open&per_page=100"],
        cwd=cwd,
    )
    if code != 0:
        return []  # alerts may be disabled / not permitted; not fatal
    try:
        alerts = json.loads(out or "[]")
    except json.JSONDecodeError:
        return []
    out_alerts: list[dict[str, Any]] = []
    for a in alerts if isinstance(alerts, list) else []:
        vuln = a.get("security_vulnerability") or {}
        pkg = (vuln.get("package") or {}).get("name")
        first_patched = (vuln.get("first_patched_version") or {}).get("identifier")
        out_alerts.append(
            {
                "number": a.get("number"),
                "severity": str(vuln.get("severity") or "").lower(),
                "package": pkg,
                "ecosystem": (vuln.get("package") or {}).get("ecosystem"),
                "first_patched_version": first_patched,
                "html_url": a.get("html_url"),
                "untrusted_summary": (a.get("security_advisory") or {}).get("summary", "")[:MAX_UNTRUSTED],
            }
        )
    return out_alerts


def get_bun_outdated(cwd: str | None) -> dict[str, Any]:
    if which("bun") is None:
        return {"available": False, "raw": "", "note": "bun not on PATH; skipped"}
    code, out, err = run(["bun", "outdated"], cwd=cwd)
    raw = (out or err or "").strip()
    # Display-only: do not parse the table into logic (formatting is unstable).
    return {"available": True, "raw": raw[:MAX_UNTRUSTED]}


# --------------------------------------------------------------------------- #
# scoring / eligibility / verdict (pure, deterministic, no untrusted text)
# --------------------------------------------------------------------------- #
def eligibility(pr: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not pr["is_dependabot"]:
        reasons.append("REASON_NON_BOT_AUTHOR")
    if pr["semver"]["class"] == "major":
        reasons.append("REASON_MAJOR_BUMP")
    if pr["semver"].get("grouped") or pr["semver"]["class"] == "unknown":
        reasons.append("REASON_MULTI_PACKAGE_OR_UNPARSED")
    touched = pr["changed_files"]
    if any(p.startswith(CI_SENSITIVE_PREFIXES) for p in touched):
        reasons.append("REASON_TOUCHES_CI")
    if any(p.split("/")[-1] not in LOCKFILE_ALLOWLIST for p in touched) and touched:
        reasons.append("REASON_NOT_LOCKFILE_SCOPED")
    return ("human_only" if reasons else "auto_candidate"), reasons


def mergeability_verdict(pr: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    risk: list[str] = []

    # Start fail-closed.
    state = pr["merge_state"]
    mergeable = pr["mergeable"]
    ci = pr["ci"]["state"]
    cls = pr["semver"]["class"]

    # Hard NO conditions (definitely not safe).
    if ci == "failure":
        return {"merge_safe": "no", "reasons": ["ci-failing"], "risk_notes": pr["ci"]["failing"]}
    if state in {"dirty", "conflicting"}:
        return {"merge_safe": "no", "reasons": ["merge-conflict"], "risk_notes": []}
    if cls == "major":
        return {
            "merge_safe": "needs-human",
            "reasons": ["major-version-bump"],
            "risk_notes": ["breaking; needs local sandboxed test before merge, not auto-tested"],
        }

    # Async / unknown -> needs-human (never collapse to safe/blocked).
    if mergeable is None or state in PENDING_MERGE_STATES:
        reasons.append("mergeability-still-computing")
    if ci in {"pending", "none"}:
        reasons.append("ci-not-settled")
    if pr["review_decision"] == "CHANGES_REQUESTED":
        return {"merge_safe": "no", "reasons": ["changes-requested"], "risk_notes": []}
    if pr["eligibility"] != "auto_candidate":
        reasons.extend(pr["reason_codes"])
    if state in {"behind", "blocked", "draft", "has_hooks"}:
        reasons.append(f"merge-state-{state}")

    if reasons:
        return {"merge_safe": "needs-human", "reasons": reasons, "risk_notes": risk}

    # Only reach here when every check explicitly passed.
    if (
        ci == "success"
        and mergeable is True
        and state in SAFE_MERGE_STATES
        and cls in {"patch", "minor"}
        and pr["eligibility"] == "auto_candidate"
    ):
        note = "ci green (observed); lockfile-scoped; not auto-executed"
        return {"merge_safe": "yes", "reasons": ["ci-green", "lockfile-scoped", cls], "risk_notes": [note]}

    return {"merge_safe": "needs-human", "reasons": ["did-not-meet-all-criteria"], "risk_notes": []}


def correlate_alert(pr: dict[str, Any], alerts: list[dict[str, Any]]) -> dict[str, Any] | None:
    pkg = pr["semver"].get("package")
    if not pkg:
        return None
    for a in alerts:
        if a["package"] and a["package"].lower() == pkg.lower():
            # CLAIM: package name match only. Severity drives ordering, never the merge verdict.
            return {**a, "confidence": "claim", "fixes_alert": "unconfirmed"}
    return None


def priority(pr: dict[str, Any]) -> tuple[int, str]:
    alert = pr.get("linked_alert")
    if alert:
        rank = SEVERITY_RANK.get(alert.get("severity", ""), 4)
        return rank, f"security-{alert.get('severity') or 'unknown'}"
    cls = pr["semver"]["class"]
    if not pr["is_dependabot"]:
        return 40, "human"
    return {"patch": 10, "minor": 20, "major": 30, "unknown": 35}.get(cls, 35), cls


def build_pr_record(slug: str, raw: dict[str, Any], cwd: str | None) -> dict[str, Any]:
    number = int(raw["number"])
    user = (raw.get("user") or {}).get("login") or ""
    is_bot = user in BOT_LOGINS or (raw.get("user") or {}).get("type") == "Bot"
    is_dependabot = user == "dependabot[bot]"
    title = raw.get("title") or ""
    labels = [lab.get("name") for lab in (raw.get("labels") or []) if lab.get("name")]
    changed_files: list[str] = []
    try:
        files = gh_json(["api", "--paginate", f"/repos/{slug}/pulls/{number}/files?per_page=100"], cwd=cwd)
        changed_files = [f.get("filename") for f in files if f.get("filename")]
    except RuntimeError:
        changed_files = []

    detail = get_pr_detail(slug, number, cwd)

    pr: dict[str, Any] = {
        "number": number,
        "url": raw.get("html_url"),
        "author_login": user,
        "is_bot": is_bot,
        "is_dependabot": is_dependabot,
        "draft": bool(raw.get("draft")),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "head_sha": (raw.get("head") or {}).get("sha"),
        "base_ref": (raw.get("base") or {}).get("ref"),
        "labels": labels,
        "changed_files": changed_files,
        "mergeable": detail.get("mergeable"),
        "merge_state": str(detail.get("mergeable_state") or "").lower(),
        "review_decision": get_review_decision(slug, number, cwd),
        "ci": get_ci_state(slug, number, cwd),
        "semver": classify_title(title),
        # Untrusted: verbatim, display-only, drives no logic.
        "untrusted_title": title[:MAX_UNTRUSTED],
        "untrusted_body": (raw.get("body") or "")[:MAX_UNTRUSTED],
    }
    elig, reasons = eligibility(pr)
    pr["eligibility"] = elig
    pr["reason_codes"] = reasons
    return pr


# --------------------------------------------------------------------------- #
# self-test
# --------------------------------------------------------------------------- #
def _fixture(**over: Any) -> dict[str, Any]:
    base = {
        "number": 1, "is_dependabot": True, "changed_files": ["bun.lock", "package.json"],
        "mergeable": True, "merge_state": "clean", "review_decision": None,
        "ci": {"state": "success", "failing": []},
        "semver": {"package": "zod", "from": "3.1.0", "to": "3.1.1", "class": "patch", "grouped": False},
        "linked_alert": None,
    }
    base.update(over)
    elig, reasons = eligibility(base)
    base["eligibility"] = elig
    base["reason_codes"] = reasons
    return base


def self_test() -> int:
    cases = [
        ("clean patch -> yes", _fixture(), "yes"),
        ("ci red -> no", _fixture(ci={"state": "failure", "failing": ["test"]}), "no"),
        ("major -> needs-human", _fixture(semver={"package": "vite", "from": "5.0.0", "to": "6.0.0", "class": "major", "grouped": False}), "needs-human"),
        ("conflict -> no", _fixture(merge_state="dirty"), "no"),
        ("mergeable unknown -> needs-human", _fixture(mergeable=None, merge_state="unknown"), "needs-human"),
        ("changes requested -> no", _fixture(review_decision="CHANGES_REQUESTED"), "no"),
        ("human author -> needs-human", _fixture(is_dependabot=False), "needs-human"),
        ("touches workflow -> needs-human", _fixture(changed_files=[".github/workflows/ci.yml", "bun.lock"]), "needs-human"),
        ("ci pending -> needs-human", _fixture(ci={"state": "pending", "failing": []}), "needs-human"),
    ]
    failures = 0
    for label, pr, expected in cases:
        got = mergeability_verdict(pr)["merge_safe"]
        ok = got == expected
        print(f"[{'PASS' if ok else 'FAIL'}] {label}: expected={expected} got={got}", file=sys.stderr)
        if not ok:
            failures += 1
    print(f"--- self-test: {len(cases) - failures}/{len(cases)} passed", file=sys.stderr)
    return 1 if failures else 0


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Read-only maintenance scan: PRs, Dependabot alerts, outdated deps -> JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--repo", default=".", help="Repo slug (owner/name) or a local path.")
    p.add_argument("--max-prs", type=int, default=100, help="Cap PRs scanned per run.")
    p.add_argument("--json", action="store_true", help="(default) emit JSON to stdout.")
    p.add_argument("--self-test", action="store_true", help="Run built-in verdict fixtures and exit.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()

    cwd = args.repo if ("/" not in args.repo or "\\" in args.repo or args.repo == ".") else None
    ensure_gh(cwd)
    slug = resolve_slug(args.repo, cwd)

    alerts = list_dependabot_alerts(slug, cwd)
    prs_raw = list_open_prs(slug, cwd, args.max_prs)

    records: list[dict[str, Any]] = []
    for raw in prs_raw:
        try:
            pr = build_pr_record(slug, raw, cwd)
        except RuntimeError as e:
            records.append({"number": raw.get("number"), "error": str(e), "merge_safe": "needs-human"})
            continue
        pr["linked_alert"] = correlate_alert(pr, alerts)
        pr["verdict"] = mergeability_verdict(pr)
        rank, label = priority(pr)
        pr["priority_rank"] = rank
        pr["priority_label"] = label
        records.append(pr)

    records.sort(key=lambda r: (r.get("priority_rank", 99), r.get("updated_at") or ""))

    result = {
        "schema_version": SCHEMA_VERSION,
        "repo": slug,
        "open_pr_count": len(prs_raw),
        "dependabot_alert_count": len(alerts),
        "dependabot_alerts": alerts,
        "outdated": get_bun_outdated(cwd),
        "prs": records,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
