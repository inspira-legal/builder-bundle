#!/usr/bin/env python3
"""Check the mechanical shape of a spec.

Judgment (is it too long, does it repeat itself, is it recounting the conversation)
belongs to the independent reviewer. This only catches what is decidable by reading
the bytes: the required sections, dead names, frontmatter, malformed tables, and the
Metric section's shape (provenance notes and event-row citations).

Usage: lint_spec.py <path>...
Output: `path:line CODE message` on stdout. Exit 1 when any E-code fired.
"""

import re
import sys

# The heading is matched lowercased, so `## decisions` and `## Decisions` are one name.
REQUIRED_SECTIONS = (
    ("Decisions", "decisions"),
    ("Open", "open"),
)
RECOMMENDED_SECTIONS = (
    ("Behavior", "behavior", "W001", "the behavior map is the acceptance contract"),
    ("Metric", "metric", "W005", "the measure the landing is judged by, or one `skipped: <reason>` line"),
    ("Tasks", "tasks", "W002", "with no tasks the build has nothing to consume"),
    ("Out of scope", "out of scope", "W004", "it is the boundary the build stays inside"),
)
# `{raw}` takes the heading as the file spells it, so the message quotes the string the
# author will search for.
MOVED_TO_DISCOVERY = (
    "`## {raw}` belongs to `.bb/<slug>/discovery.md`, written by `/bb:discover`. "
    "The spec reads it there by path; a copy here goes stale on the next round."
)
DEAD_SECTIONS = {
    "design": (
        "`## {raw}` is a dead name: in bb `design` is screen design (`/bb:brisar`). "
        "Architecture belongs in the free top half, under the name it has in this problem."
    ),
    "still open": "section `## {raw}`: the name is `## Open`.",
    "problem": MOVED_TO_DISCOVERY,
    "hypothesis": MOVED_TO_DISCOVERY,
    "fit": MOVED_TO_DISCOVERY,
    "cuts": MOVED_TO_DISCOVERY,
}
VALID_STATUS = ("pending", "in-progress", "done", "blocked")
MAX_CELL = 100

HEADING = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR_CELL = re.compile(r"^:?-{2,}:?$")
# A `|` escaped as `\|` is content, not a column boundary.
CELL_SPLIT = re.compile(r"(?<!\\)\|")
# The Metric section's mechanical shape (references/spec-format.md): the Baseline and
# Target bullets carry provenance as a parenthesized note or an honest per-value
# `skipped: <reason>`, a `skipped: <reason>` line alone replaces the whole section,
# and a numbered happy-path row is what an event row cites.
METRIC_VALUE = re.compile(r"^\s{0,3}[-*+]\s+\**(Baseline|Target)\**\s*:", re.IGNORECASE)
VALUE_SKIP = re.compile(r"skipped\s*:\s*\S", re.IGNORECASE)
# Anchored at column 0: an indented `skipped:` is a sub-note of some other bullet,
# not the section-level skip, and must not silence the checks below.
METRIC_SKIP = re.compile(r"^(?:[-*+]\s+)?skipped\s*:\s*\S", re.IGNORECASE)
PROVENANCE = re.compile(r"\([^)]+\)")
BEHAVIOR_ROW = re.compile(r"^\s{0,3}(\d+)[.)]\s")
NUMBERED_CELL = re.compile(r"^(\d+)[.)]?$")
# A new list item, an `okr:` or a `skipped:` line closes the bullet above it; anything
# else directly under an open bullet is a wrapped or lazy continuation of it.
NEW_ITEM = re.compile(r"^\s{0,3}(?:[-*+]\s|\d+[.)]\s|okr\s*:|skipped\s*:)", re.IGNORECASE)
# A citation cell is numbers, commas and ranges once parenthesized notes are stripped;
# anything else is prose naming an inline behavior, judged by the gate, not here.
PAREN_NOTE = re.compile(r"\([^)]*\)")
CITATION_CELL = re.compile(r"^[\d\s,;.–-]+$")
CITED_RANGE = re.compile(r"(\d+)\s*[–-]\s*(\d+)")
CITED_NUMBER = re.compile(r"\d+")


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


def cited_rows(cell):
    """Return the row numbers a behaviors cell cites, or None when the cell is prose."""
    cleaned = PAREN_NOTE.sub(" ", cell).strip()
    if not cleaned or not CITATION_CELL.match(cleaned):
        return None
    cited = set()

    def expand(match):
        cited.update(range(int(match.group(1)), int(match.group(2)) + 1))
        return " "

    rest = CITED_RANGE.sub(expand, cleaned)
    cited.update(int(n) for n in CITED_NUMBER.findall(rest))
    return cited


def check_citations(metric_tables, behavior_rows):
    """Yield W007 for event rows citing a numbered behavior row that does not exist."""
    for rows in metric_tables:
        if len(rows) < 2:
            continue
        header = rows[0][1]
        column = next((i for i, cell in enumerate(header) if "behavior" in cell.lower()), None)
        if column is None:
            continue
        is_separator = all(SEPARATOR_CELL.match(c) for c in rows[1][1])
        for line_no, cells in rows[2:] if is_separator else rows[1:]:
            if column >= len(cells):
                continue
            cited = cited_rows(cells[column])
            if cited is None:
                continue
            for n in sorted(cited):
                if n not in behavior_rows:
                    yield (
                        line_no,
                        "W007",
                        f"event row cites behavior {n}, and `## Behavior` has no row {n}",
                    )


def check_body(lines):
    """Yield problems with sections, tables, and the Metric section's shape."""
    seen = set()
    fence_marker = None  # the marker (``` or ~~~) that opened the current fence
    section = None  # the current `##` heading, lowercased
    table = []  # (line_no, cells) of the current run of table rows
    behavior_marks = []  # numbered-list markers under `## Behavior`, in file order
    table_rows = set()  # numbered rows collected from a `## Behavior` table
    metric_line = None  # the `## Metric` heading's line, anchors section-level warnings
    metric_values = []  # [line_no, key, text] of the Baseline and Target bullets
    metric_tables = []  # the Metric section's table runs, kept for the citation check
    metric_skipped = False
    open_value = None  # index into metric_values of the bullet still accumulating

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

    def end_table():
        # Called before the run is flushed, while `section` still names the heading
        # the table sits under.
        if section == "metric":
            metric_tables.append(list(table))
        elif section == "behavior":
            # A behavior map written as a table still numbers its rows in the first
            # cell; those numbers are citable the same as a list's.
            for _, cells in table:
                numbered = cells and NUMBERED_CELL.match(cells[0])
                if numbered:
                    table_rows.add(int(numbered.group(1)))

    for i, line in enumerate(lines, start=1):
        # A fence ends the current run of rows; two tables around a code block are
        # two tables, not one with a mismatched header. Only the marker that opened
        # a fence closes it: a ``` line inside a ~~~ block is content.
        fence = FENCE.match(line)
        if fence_marker is not None:
            if fence and fence.group(1) == fence_marker:
                fence_marker = None
            continue
        if fence:
            fence_marker = fence.group(1)
            open_value = None
            if table:
                end_table()
                yield from flush(table)
                table = []
            continue

        if line.strip().startswith("|"):
            open_value = None
            table.append((i, split_row(line)))
            continue
        if table:
            end_table()
            yield from flush(table)
            table = []

        match = HEADING.match(line)
        if match:
            open_value = None
            raw = match.group(1).strip()
            name = raw.lower()
            seen.add(name)
            section = name
            if name == "metric":
                metric_line = i
            if name in DEAD_SECTIONS:
                yield i, "E003", DEAD_SECTIONS[name].format(raw=raw)
            continue

        if section == "behavior":
            row = BEHAVIOR_ROW.match(line)
            if row:
                behavior_marks.append(int(row.group(1)))
        elif section == "metric":
            if METRIC_SKIP.match(line):
                metric_skipped = True
            value = METRIC_VALUE.match(line)
            if value:
                metric_values.append([i, value.group(1), line])
                open_value = len(metric_values) - 1
            elif open_value is not None and line.strip() and not NEW_ITEM.match(line):
                # A wrapped bullet, indented or a CommonMark lazy continuation: the
                # provenance note may close on this line.
                metric_values[open_value][2] += " " + line.strip()
            else:
                open_value = None

    if table:
        end_table()
        yield from flush(table)

    for name, spelling in REQUIRED_SECTIONS:
        if spelling not in seen:
            yield 1, "E002", f"no `## {name}`: the format requires it"

    for name, spelling, code, why in RECOMMENDED_SECTIONS:
        if spelling not in seen:
            yield 1, code, f"no `## {name}`: {why}"

    # An explicit skip is the whole section, so nothing below applies to it.
    if "metric" in seen and not metric_skipped:
        # A heading alone does not satisfy the mandate: the block carries both
        # bullets, or the section is the one skip line.
        present = {key.lower() for _, key, _ in metric_values}
        for key in ("Baseline", "Target"):
            if key.lower() not in present:
                yield (
                    metric_line or 1,
                    "W006",
                    f"no `{key}:` bullet: the metric block carries baseline and target, "
                    "or the section is one `skipped: <reason>` line",
                )
        for line_no, key, text in metric_values:
            rest = text[METRIC_VALUE.match(text).end() :].strip()
            if VALUE_SKIP.match(rest):
                # An honest per-value skip (`Baseline: skipped: not-instrumented`)
                # needs no provenance; it flags the instrumentation as first work.
                continue
            if not PROVENANCE.search(text):
                yield (
                    line_no,
                    "W006",
                    f"`{key}:` without provenance: name the source in a parenthesized "
                    "note on the same bullet (a query, a log, a named person's estimate)",
                )
        # Markers all spelling `1.` are a CommonMark auto-numbered list that renders
        # 1, 2, 3…; the citable numbers are what the reader sees, not the literals.
        if len(behavior_marks) > 1 and len(set(behavior_marks)) == 1:
            rows = set(range(behavior_marks[0], behavior_marks[0] + len(behavior_marks)))
        else:
            rows = set(behavior_marks)
        rows |= table_rows
        # A `## Behavior` in prose, or a table with no numbered rows, leaves nothing
        # to cite; the gate judges the trace there, the same as a Medium spec.
        if rows:
            yield from check_citations(metric_tables, rows)


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
