#!/usr/bin/env python3
"""Cheap local pre-check for a LexFlow app manifest.

Covers only the stable subset that is worth checking outside the platform CLI:
that ``lexflow.toml`` parses, declares ``[app]``, and that every ``source`` it
references resolves to a real file. Everything deeper — slug format, duplicate
slugs, connection kinds, secret scope — is validated by ``lexflow deploy``
itself (``manifest.py``/``load_manifest``, which runs before any network call);
reimplementing it here would only drift from upstream.

The value this adds over the CLI: it runs in milliseconds, needs no network,
and works while logged out — so ship has something to gate on even when the
platform is unreachable.

With ``--changed``, it also maps changed files onto the deployments they affect.
A file can reach a deployment two ways: by being a declared ``source``, or by
being referenced from inside one (a .sql query pulled in by a workflow YAML).
The second is found by text search, so no YAML parser is needed. A changed file
that matches neither is reported as ``unmatched`` and ``affects_deploy`` becomes
``"unknown"``: absence of a text reference is weak evidence, so the call of
whether a deploy is warranted stays with the caller reading the YAMLs.

Every exit prints the same envelope — ``ok``, ``findings``, and the rest —
so the caller reads one shape whatever happened.
Exit codes: 0 clean, 1 findings in the app, 2 cannot check.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None


SECRET_PLACEHOLDER = "$secret"


def _collect_sources(raw: dict) -> list[dict]:
    """Return every declared source with its owner, in manifest order."""
    sources: list[dict] = []

    for item in raw.get("workflows", []) or []:
        if isinstance(item, dict) and item.get("source"):
            sources.append(
                {"kind": "workflow", "slug": item.get("slug"), "source": str(item["source"])}
            )

    for item in raw.get("deployments", []) or []:
        if not isinstance(item, dict):
            continue
        slug = item.get("slug")
        if item.get("source"):
            sources.append(
                {
                    "kind": "deployment",
                    "slug": slug,
                    "source": str(item["source"]),
                    "type": item.get("type"),
                }
            )
        for mw in item.get("middlewares", []) or []:
            if isinstance(mw, dict) and mw.get("source"):
                sources.append(
                    {
                        "kind": "middleware",
                        "slug": slug,
                        "source": str(mw["source"]),
                        "priority": mw.get("priority"),
                    }
                )

    return sources


def _declared_secrets(raw: dict) -> list[str]:
    """Env keys whose value is the deploy-time secret placeholder."""
    env = raw.get("env") or {}
    if not isinstance(env, dict):
        return []
    return [k for k, v in env.items() if isinstance(v, str) and v.strip() == SECRET_PLACEHOLDER]


def _match_changed(
    changed: list[str], sources: list[dict], app_dir: Path, manifest_path: Path
) -> tuple[list[dict], list[str]]:
    """Map changed files onto the sources they affect.

    Direct hits are path comparisons; indirect hits are found by searching each
    source file's text for the changed file's relative path or basename, which
    catches queries and fragments a workflow pulls in without a parser.
    """
    resolved_sources = [(s, (app_dir / s["source"]).resolve()) for s in sources]
    matches: list[dict] = []
    unmatched: list[str] = []

    for rel in changed:
        target = Path(rel).resolve()

        if target == manifest_path.resolve():
            matches.append({"file": rel, "how": "manifest", "kind": "manifest", "slug": None})
            continue

        direct = [s for s, path in resolved_sources if path == target]
        if direct:
            matches.extend(
                {"file": rel, "how": "source", "kind": s["kind"], "slug": s["slug"]}
                for s in direct
            )
            continue

        # Indirect: does any declared source mention this file?
        needles = {target.name}
        try:
            needles.add(target.relative_to(app_dir.resolve()).as_posix())
        except ValueError:
            pass

        referenced_by = []
        for s, path in resolved_sources:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(n in text for n in needles):
                referenced_by.append(s)

        if referenced_by:
            matches.extend(
                {"file": rel, "how": "referenced_by", "kind": s["kind"], "slug": s["slug"]}
                for s in referenced_by
            )
        else:
            unmatched.append(rel)

    return matches, unmatched


def _emit(payload: dict, code: int) -> int:
    payload.setdefault("findings", [])
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # -d mirrors the lexflow CLI's own flag. A flag rather than a positional because
    # `--changed` is variadic and would otherwise swallow a trailing directory.
    parser.add_argument("-d", "--dir", default=".", help="App dir holding lexflow.toml.")
    parser.add_argument(
        "--changed",
        nargs="*",
        default=[],
        metavar="FILE",
        # Paths resolve against the current directory, so run this from wherever
        # `git diff --name-only` was taken (the repo root).
        help="Changed files (repo-relative) to map onto affected deployments.",
    )
    args = parser.parse_args()

    if tomllib is None:
        return _emit(
            {"ok": False, "error": "tomllib requires Python 3.11+ — cannot pre-check locally."}, 2
        )

    app_dir = Path(args.dir)
    manifest_path = app_dir / "lexflow.toml"

    if not manifest_path.is_file():
        return _emit({"ok": False, "error": f"No lexflow.toml in {app_dir}."}, 2)

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:  # unreadable file is an environment problem, not a bad manifest
        return _emit({"ok": False, "error": f"Cannot read {manifest_path}: {exc}"}, 2)

    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return _emit(
            {
                "ok": False,
                "manifest": str(manifest_path),
                "findings": [f"lexflow.toml does not parse: {exc}"],
            },
            1,
        )

    findings: list[str] = []

    app = raw.get("app")
    if not isinstance(app, dict):
        findings.append("Missing required [app] section.")
        app = {}

    sources = _collect_sources(raw)
    for entry in sources:
        entry["exists"] = (app_dir / entry["source"]).is_file()
        if not entry["exists"]:
            findings.append(
                f"{entry['kind']} '{entry['slug']}': source '{entry['source']}' not found."
            )

    result: dict = {
        "ok": not findings,
        "manifest": str(manifest_path),
        "app": {k: app.get(k) for k in ("name", "slug", "team") if app.get(k)},
        "sources": sources,
        "findings": findings,
        "secrets_declared": _declared_secrets(raw),
        "has_datastores": bool(raw.get("datastores")),
    }

    if args.changed:
        matches, unmatched = _match_changed(args.changed, sources, app_dir, manifest_path)
        result["changed"] = {
            "matches": matches,
            "unmatched": unmatched,
            # Two states only: a match proves the deploy is affected, while no match
            # is weak evidence. The caller reads the YAMLs and settles "unknown".
            "affects_deploy": True if matches else "unknown",
            "affected_slugs": sorted({m["slug"] for m in matches if m["slug"]}),
        }

    return _emit(result, 1 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
