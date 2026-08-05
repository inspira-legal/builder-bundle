#!/usr/bin/env python3
"""Canonicalize finder candidate paths and group them by location.

Deterministic half of verify.md step 1: finders return the same file as an
absolute path, a repo-relative one, or with backslashes, and an un-canonicalized
path splits one location into several groups — which is what the grouping exists
to prevent. Reads one JSON object on stdin, writes one on stdout.

Input:
  {"scope_files": ["src/a.ts", ...],
   "candidates": [{"file": "...", "line": 42, ...}, ...]}

Anything else on a candidate is carried through untouched.

Output:
  {"groups": [{"key": "src/a.ts:42", "file": "src/a.ts", "line": 42,
               "candidates": [{..., "index": 0}]}],
   "unmatched": ["path/not/in/scope.ts"],
   "stats": {"candidates": N, "groups": M, "rewritten": K, "unmatched": U}}

Usage: python group_candidates.py < candidates.json
"""

import json
import sys


def normalize(path):
    """Backslashes to forward, drop a leading ./, collapse repeats."""
    p = str(path or "").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    while "//" in p:
        p = p.replace("//", "/")
    return p.strip().lstrip("/")


def canonicalize(path, scope):
    """Match by path segment suffix against the scope list; longest match wins.

    Returns (canonical_path, matched). Segment-aware so `b/a.ts` never matches
    `lib/aaa.ts`.
    """
    norm = normalize(path)
    if not norm:
        return norm, False
    segments = norm.split("/")
    best = None
    for candidate in scope:
        c_segments = candidate.split("/")
        n = len(c_segments)
        if n <= len(segments) and segments[-n:] == c_segments:
            if best is None or n > len(best.split("/")):
                best = candidate
        elif len(segments) <= n and c_segments[-len(segments) :] == segments:
            if best is None or n > len(best.split("/")):
                best = candidate
    if best is not None:
        return best, True
    return norm, False


def parse_line(value):
    """A line number, or None for a whole-file / cross-file claim."""
    if value is None or value == "":
        return None
    try:
        n = int(str(value).split("-")[0].split(":")[0].strip())
    except (ValueError, TypeError):
        return None
    return n if n > 0 else None


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        json.dump({"error": f"stdin nao e JSON valido: {exc}"}, sys.stdout)
        sys.stdout.write("\n")
        return 1

    scope = [normalize(f) for f in payload.get("scope_files") or []]
    scope = [f for f in scope if f]
    candidates = payload.get("candidates") or []

    groups = {}
    order = []
    unmatched = []
    rewritten = 0
    index = 0

    for raw in candidates:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        original = item.get("file")
        canonical, matched = canonicalize(original, scope)
        if not matched and canonical and canonical not in unmatched:
            unmatched.append(canonical)
        if canonical != normalize(original):
            rewritten += 1
        item["file"] = canonical
        line = parse_line(item.get("line"))
        item["line"] = line
        item["index"] = index
        index += 1

        key = canonical if line is None else f"{canonical}:{line}"
        if key not in groups:
            groups[key] = {"key": key, "file": canonical, "line": line, "candidates": []}
            order.append(key)
        groups[key]["candidates"].append(item)

    # Re-index within each group: verifiers address candidates as [0], [1], ...
    for key in order:
        for local, item in enumerate(groups[key]["candidates"]):
            item["local_index"] = local

    result = {
        "groups": [groups[k] for k in order],
        "unmatched": unmatched,
        "stats": {
            "candidates": index,
            "groups": len(order),
            "rewritten": rewritten,
            "unmatched": len(unmatched),
        },
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
