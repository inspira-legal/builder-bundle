#!/usr/bin/env python3
"""Check the mechanical shape of a spec.

Judgment (is it too long, does it repeat itself, is it recounting the conversation)
belongs to the independent reviewer. This only catches what is decidable by reading
the bytes: the required sections, dead names, frontmatter, and malformed tables.

Usage: lint_spec.py <path>...
Output: `path:line CODE message` on stdout. Exit 1 when any E-code fired.
"""

import re
import sys

# (name to write, the spellings that resolve): a spec written before the rename still
# parses, and the message cites the English name.
REQUIRED_SECTIONS = (
    ("Decisions", ("decisions", "decisões")),
    ("Open", ("open", "em aberto")),
)
RECOMMENDED_SECTIONS = (
    (
        "Behavior",
        ("behavior", "comportamento"),
        "W001",
        "the behavior map is the acceptance contract",
    ),
    ("Tasks", ("tasks", "tarefas"), "W002", "with no tasks the build has nothing to consume"),
    (
        "Out of scope",
        ("out of scope", "fora de escopo"),
        "W004",
        "it is the boundary the build stays inside",
    ),
)
# A Portuguese section still parses; W003 carries the English name to write instead.
TRANSLATED_SECTIONS = {
    "decisões": "Decisions",
    "comportamento": "Behavior",
    "tarefas": "Tasks",
    "fora de escopo": "Out of scope",
    "em aberto": "Open",
    "problema": "Problem",
    "hipótese": "Hypothesis",
    "encaixe": "Fit",
    "cortes": "Cuts",
    "jurídico": "Legal",
}
# `{raw}` takes the heading as the file spells it, so the message quotes the string the
# author will search for.
DEAD_SECTIONS = {
    "design": (
        "`## {raw}` is a dead name: in bb `design` is screen design (`/bb:brisar`). "
        "Architecture belongs in the free top half, under the name it has in this problem."
    ),
    "still open": "section `## {raw}`: the name is `## Open`.",
}
VALID_STATUS = ("pending", "in-progress", "done", "blocked")
MAX_CELL = 100

HEADING = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR_CELL = re.compile(r"^:?-{2,}:?$")
# A `|` escaped as `\|` is content, not a column boundary.
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def split_row(line):
    """Return a table row's cells, dropping the empty edges around the outer pipes."""
    parts = CELL_SPLIT.split(line.strip())
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.strip() for p in parts]


def check_frontmatter(lines):
    """Yield problems with the `---` block the spec-state contract requires."""
    if not lines or lines[0].strip() != "---":
        yield 1, "E001", "no frontmatter: the `---` block with status/created/slug opens the file"
        return

    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        yield 1, "E001", "frontmatter never closed with `---`"
        return

    fields = {}
    for i in range(1, end):
        key, sep, value = lines[i].partition(":")
        if sep:
            fields[key.strip()] = (i + 1, value.strip())

    for key in ("status", "created", "slug"):
        if key not in fields:
            yield 1, "E001", f"frontmatter without `{key}`"

    if "status" in fields:
        line_no, value = fields["status"]
        if value not in VALID_STATUS:
            yield line_no, "E001", f"status `{value}` is invalid: use {', '.join(VALID_STATUS)}"

    if "created" in fields:
        line_no, value = fields["created"]
        if not DATE.match(value):
            yield line_no, "E001", f"created `{value}` is not in YYYY-MM-DD format"


def check_body(lines):
    """Yield problems with sections and tables, ignoring fenced blocks."""
    seen = set()
    in_fence = False
    table = []  # (line_no, cells) of the current run of table rows

    def flush(rows):
        if len(rows) < 2:
            return
        header_no, header = rows[0]
        width = len(header)
        is_separator = all(SEPARATOR_CELL.match(c) for c in rows[1][1])
        body = rows[2:] if is_separator else rows[1:]
        # The delimiter row is width-checked like any other: GFM needs it to match the
        # header, and a short one turns the whole table back into a paragraph of pipes.
        for line_no, cells in rows:
            if len(cells) != width:
                remedy = (
                    "the delimiter row needs the same cells as the header, or GFM stops "
                    "reading it as a table"
                    if is_separator and line_no == rows[1][0]
                    else "a literal `|` has to become `\\|`"
                )
                yield (
                    line_no,
                    "E005",
                    f"row with {len(cells)} cells against the header's {width}: {remedy}",
                )
        for line_no, cells in [rows[0]] + body:
            for cell in cells:
                if len(cell) > MAX_CELL:
                    yield (
                        line_no,
                        "E004",
                        f"cell of {len(cell)} characters (ceiling {MAX_CELL}): "
                        "content that long is prose or a bullet, not a table",
                    )

    for i, line in enumerate(lines, start=1):
        # A fence ends the current run of rows; two tables around a code block are
        # two tables, not one with a mismatched header.
        if FENCE.match(line) or in_fence:
            if table:
                yield from flush(table)
                table = []
            if FENCE.match(line):
                in_fence = not in_fence
            continue

        if line.strip().startswith("|"):
            table.append((i, split_row(line)))
            continue
        if table:
            yield from flush(table)
            table = []

        match = HEADING.match(line)
        if match:
            raw = match.group(1).strip()
            name = raw.lower()
            seen.add(name)
            if name in DEAD_SECTIONS:
                yield i, "E003", DEAD_SECTIONS[name].format(raw=raw)
            elif name in TRANSLATED_SECTIONS:
                yield i, "W003", (
                    f"`## {raw}` is Portuguese: the name to write is "
                    f"`## {TRANSLATED_SECTIONS[name]}`; the file stays valid"
                )

    if table:
        yield from flush(table)

    for name, spellings in REQUIRED_SECTIONS:
        if not any(spelling in seen for spelling in spellings):
            yield 1, "E002", f"no `## {name}`: the format requires it"

    for name, spellings, code, why in RECOMMENDED_SECTIONS:
        if not any(spelling in seen for spelling in spellings):
            yield 1, code, f"no `## {name}`: {why}"


def lint(path):
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as err:
        return [(1, "E001", f"could not read the file: {err}")]
    return sorted([*check_frontmatter(lines), *check_body(lines)], key=lambda p: (p[0], p[1]))


def main(argv):
    if not argv:
        print("usage: lint_spec.py <path>...", file=sys.stderr)
        return 2

    failed = False
    for path in argv:
        for line_no, code, message in lint(path):
            print(f"{path}:{line_no} {code} {message}")
            failed |= code.startswith("E")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
