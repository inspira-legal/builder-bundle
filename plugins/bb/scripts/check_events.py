#!/usr/bin/env python3
"""Hold planned or emitted event names to a project's `EVENTS.md`.

The convention file's format is `plugins/bb/references/events-convention.md`: five
parts found by heading, each a table this script reads. The plan it checks is either a
spec's `## Metric` events table (`--spec`) or a list of emitted names (`--names`, a
file or `-` for stdin). Two skills call it: `/bb:spec` at step 6, beside
`lint_spec.py`, and `/bb:review`'s instrumentation front, once before the fan-out.

Usage:
  check_events.py --spec .bb/<slug>/spec.md [--convention path/to/EVENTS.md]
  check_events.py --names emitted.txt        [--convention path/to/EVENTS.md]
  ... | check_events.py --names -

Output: `path:line CODE message` per finding on stdout, or `checked N names, clean`
when nothing fired, so silence never reads as a pass. Exit 1 when an E-code fired, 0
otherwise, warnings included. The script reads and never writes, and every malformed
input is a coded line rather than a traceback.

Codes:
  C001 E  the convention file is malformed (a part missing or written twice, a table
          without header or a second table under a part, a prefix or field twice, a
          value outside its closed list)
  C002 E  a name starts with no registered prefix (an empty name included)
  C003 E  the type slot is not in the Grammar table
  C004 E  the element is not lowercase words joined by underscores
  C005 W  a payload field is not in the Dictionary
  C006 E  a payload field typed `text` has no Exceptions row
  C007 E  a name duplicates a catalog name or another planned name
  C008 W  an Exceptions row was used, named with its status
  C009 W  no source to check against: no file, no repository root, no `event` column
  C010 E  an input could not be read: the spec path, the names file, a bad encoding

The convention resolves before the plan is read, so a missing file is one C009 line
even for a plan of zero events. A finding with no path of its own anchors to the spec
path when one was given and to the working directory otherwise, at line 0.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONVENTION_NAME = "EVENTS.md"
FORMAT_REFERENCE = "plugins/bb/references/events-convention.md"
PAYLOAD_RULE = "the payload rule in `skills/spec/references/spec-format.md`, `### The events table`"

SEVERITY = {
    "C001": "E",
    "C002": "E",
    "C003": "E",
    "C004": "E",
    "C005": "W",
    "C006": "E",
    "C007": "E",
    "C008": "W",
    "C009": "W",
    "C010": "E",
}

# The five parts, by the exact heading text the format fixes, and the columns the checker
# reads in each. Every other column is documentary and stays free.
PARTS = ("Grammar", "Prefix registry", "Dictionary", "Exceptions", "Catalog")
READ_COLUMNS = {
    "Grammar": ("type",),
    "Prefix registry": ("prefix",),
    "Dictionary": ("field", "type"),
    "Exceptions": ("field", "status"),
    "Catalog": ("event", "status"),
}
PAYLOAD_TYPES = ("id", "enum", "number", "boolean", "text")
EXCEPTION_STATUSES = ("approved", "under-review")
LEGACY = "legacy"

HEADING = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
# GFM asks one or more dashes per delimiter cell; `|-|-|` is a table too.
SEPARATOR_CELL = re.compile(r"^:?-+:?$")
# A `|` escaped as `\|` is content, not a column boundary.
CELL_SPLIT = re.compile(r"(?<!\\)\|")
BACKTICKED = re.compile(r"`([^`]+)`")
# The element slot: lowercase words joined by single underscores. This is the checker's
# own shape; no pattern is ever built from project text, cells are compared as words.
ELEMENT = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


@dataclass
class Section:
    name: str
    line: int
    tables: list = field(default_factory=list)  # runs of (line_no, cells)


@dataclass
class Convention:
    path: str
    types: dict = field(default_factory=dict)  # type -> line
    prefixes: dict = field(default_factory=dict)  # prefix -> line
    fields: dict = field(default_factory=dict)  # field -> (type, line)
    exceptions: dict = field(default_factory=dict)  # field -> (status, line)
    catalog: list = field(default_factory=list)  # (name, is_legacy, line)
    catalog_lines: dict = field(default_factory=dict)  # name -> line

    def is_legacy(self, name):
        return any(legacy for n, legacy, _ in self.catalog if n == name)


@dataclass
class PlanRow:
    line: int
    name: str
    fields: list


# ---------------------------------------------------------------- reading markdown


def read_text(path):
    """Return (text, None) or (None, message) when the file cannot be read as UTF-8."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read(), None
    except OSError as err:
        return None, f"could not read `{path}`: {err.strerror or err}"
    except UnicodeDecodeError as err:
        return None, f"`{path}` is not valid UTF-8: {err}"


def read_stdin():
    try:
        return sys.stdin.buffer.read().decode("utf-8"), None
    except (OSError, UnicodeDecodeError) as err:
        return None, f"could not read the names from stdin: {err}"


def split_lines(data):
    # Markdown's line breaks are `\n` and `\r\n`; splitlines() also splits on \v, \f
    # and U+2028/29, which would shift every reported line number after one.
    return data.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def split_row(line):
    """Return a table row's cells, dropping the empty edges around the outer pipes."""
    parts = CELL_SPLIT.split(line.strip())
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.strip() for p in parts]


def word(cell):
    """A cell compared as a word: the backticks the format wraps values in come off."""
    return cell.strip().strip("`").strip()


def sections(lines):
    """Return the `##` sections in order, each carrying its runs of table rows.

    Content inside a fence is skipped, so a fenced example of a table is not a table.
    Only the marker that opened a fence closes it.
    """
    result = []
    current = Section(name="", line=0)
    table = []
    fence_marker = None

    def close_table():
        if table:
            current.tables.append(list(table))
            table.clear()

    for i, line in enumerate(lines, start=1):
        fence = FENCE.match(line)
        if fence_marker is not None:
            if fence and fence.group(1) == fence_marker:
                fence_marker = None
            continue
        if fence:
            fence_marker = fence.group(1)
            close_table()
            continue
        if line.strip().startswith("|"):
            table.append((i, split_row(line)))
            continue
        close_table()
        match = HEADING.match(line)
        if match:
            result.append(current)
            current = Section(name=match.group(1).strip(), line=i)
    close_table()
    result.append(current)
    return result


def header_of(rows):
    """Return (header cells lowercased, body rows), or None when the run has no header.

    A GFM table is a header row over a delimiter row; a run of pipe lines without the
    delimiter is a paragraph, and its first line is no header.
    """
    if len(rows) < 2 or not all(SEPARATOR_CELL.match(c) for c in rows[1][1]):
        return None
    header = [word(c).lower() for c in rows[0][1]]
    return header, rows[2:]


def cell_at(cells, index):
    return cells[index] if index is not None and index < len(cells) else ""


# ----------------------------------------------------------- the convention file


def find_root(start):
    """The repository root: the nearest directory holding `.git`, a dir or a worktree's file."""
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def resolve_convention(explicit, cwd, anchor):
    """Return (display path, None) or (None, one C009 finding)."""
    if explicit is not None:
        if Path(explicit).is_file():
            return explicit, None
        return None, (anchor, 0, "C009", f"no convention file at `{explicit}`: nothing checked")
    root = find_root(cwd)
    if root is None:
        return None, (
            anchor,
            0,
            "C009",
            f"no repository root: no `.git` above `{cwd}`, so `{CONVENTION_NAME}` cannot "
            "resolve; pass the file with `--convention`",
        )
    path = root / CONVENTION_NAME
    if not path.is_file():
        return None, (
            anchor,
            0,
            "C009",
            f"no `{CONVENTION_NAME}` at `{root}`: the project has no event convention, "
            f"nothing checked (the format is {FORMAT_REFERENCE})",
        )
    try:
        display = os.path.relpath(path, cwd)
    except ValueError:
        display = str(path)
    return display, None


def parse_convention(path, lines):
    """Return (Convention, C001 findings). Any finding means the file is not a source."""
    conv = Convention(path=path)
    problems = []
    by_name = {}

    def problem(line, message):
        problems.append((path, line, "C001", message))

    for section in sections(lines):
        if section.name in by_name:
            if section.name in PARTS:
                problem(
                    section.line,
                    f"`## {section.name}` appears twice (first at line {by_name[section.name].line}); "
                    "each part is one heading, so a second one is never read in silence",
                )
            continue
        by_name[section.name] = section

    def table_for(part):
        section = by_name.get(part)
        if section is None:
            problem(1, f"no `## {part}` section: the five parts are {', '.join(PARTS)}")
            return None
        if not section.tables:
            problem(section.line, f"`## {part}` has no table")
            return None
        if len(section.tables) > 1:
            problem(
                section.tables[1][0][0],
                f"`## {part}` carries a second table (the first starts at line {section.tables[0][0][0]}); "
                "each part is one table, so rows split across two are merged into one",
            )
            return None
        rows = section.tables[0]
        parsed = header_of(rows)
        if parsed is None:
            problem(
                rows[0][0],
                f"`## {part}`: the table has no header (no `| --- |` delimiter row under its first line)",
            )
            return None
        header, body = parsed
        columns = {}
        for name in READ_COLUMNS[part]:
            if name not in header:
                problem(rows[0][0], f"`## {part}` table header has no `{name}` column")
                return None
            columns[name] = header.index(name)
        return body, columns

    def keyed_rows(part, key):
        """Yield (line, key value, cells, columns) per body row, catching empty and repeated keys."""
        table = table_for(part)
        if table is None:
            return
        body, columns = table
        seen = {}
        for line, cells in body:
            value = word(cell_at(cells, columns[key]))
            if not value:
                problem(line, f"`## {part}`: a row with an empty `{key}` cell")
                continue
            if value in seen:
                problem(line, f"`## {part}`: `{value}` appears twice (first at line {seen[value]})")
                continue
            seen[value] = line
            yield line, value, cells, columns

    for line, value, _, _ in keyed_rows("Grammar", "type"):
        conv.types[value] = line
    for line, value, _, _ in keyed_rows("Prefix registry", "prefix"):
        conv.prefixes[value] = line
    for line, value, cells, columns in keyed_rows("Dictionary", "field"):
        kind = word(cell_at(cells, columns["type"])).lower()
        if kind not in PAYLOAD_TYPES:
            problem(
                line,
                f"`## Dictionary`: `{value}` has type `{kind}`; the closed list is {', '.join(PAYLOAD_TYPES)}",
            )
            continue
        conv.fields[value] = (kind, line)
    statuses = " or ".join("`" + s + "`" for s in EXCEPTION_STATUSES)
    for line, value, cells, columns in keyed_rows("Exceptions", "field"):
        status = word(cell_at(cells, columns["status"])).lower()
        if status not in EXCEPTION_STATUSES:
            problem(line, f"`## Exceptions`: `{value}` has status `{status}`; it is one of {statuses}")
            continue
        conv.exceptions[value] = (status, line)
    for line, value, cells, columns in keyed_rows("Catalog", "event"):
        legacy = word(cell_at(cells, columns["status"])).lower() == LEGACY
        conv.catalog.append((value, legacy, line))
        conv.catalog_lines[value] = line

    problems.sort(key=lambda p: (p[1], p[3]))
    return conv, problems


# ------------------------------------------------------------------- the plan


def plan_from_spec(path, lines):
    """Return (rows, None) from the spec's `## Metric` events table, or ([], C009).

    No table under `## Metric` (`Events: none`, a `skipped:` line, no section at all) is
    a plan of zero events, not a missing source.
    """
    metric = next((s for s in sections(lines) if s.name.lower() == "metric"), None)
    if metric is None or not metric.tables:
        return [], None
    for rows in metric.tables:
        parsed = header_of(rows)
        if parsed is None:
            continue
        header, body = parsed
        if "event" not in header:
            continue
        event_column = header.index("event")
        payload_column = header.index("payload") if "payload" in header else None
        plan = []
        for line, cells in body:
            event_cell = cell_at(cells, event_column)
            # The cell is the name, backticked or bare; a note beside a backticked name
            # is left alone. The payload fields are the backticked tokens, nothing else.
            ticked = BACKTICKED.findall(event_cell)
            name = ticked[0].strip() if ticked else event_cell.strip()
            fields = [f.strip() for f in BACKTICKED.findall(cell_at(cells, payload_column))]
            plan.append(PlanRow(line=line, name=name, fields=fields))
        return plan, None
    first_line, first_cells = metric.tables[0][0]
    shown = " | ".join(first_cells)
    return [], (path, first_line, "C009", f"the events table header (`{shown}`) has no `event` column")


def plan_from_names(text, numbered):
    """One name per line, blanks skipped. Unnumbered (stdin) rows sit at line 0."""
    plan = []
    for i, raw in enumerate(split_lines(text), start=1):
        name = raw.strip().strip("`'\"").strip()
        if name:
            plan.append(PlanRow(line=i if numbered else 0, name=name, fields=[]))
    return plan


# ----------------------------------------------------------------- the checks


def longest_prefix(name, prefixes):
    """The longest registered prefix the name starts with, at an underscore boundary."""
    return max((p for p in prefixes if name.startswith(p + "_")), key=len, default=None)


def grammar_finding(name, conv):
    """Return (code, message) when the name is off `{prefix}_{type}_{element}`, else None."""
    if not name:
        return "C002", "the event cell is empty: a name fills `{prefix}_{type}_{element}`"
    prefix = longest_prefix(name, conv.prefixes)
    if prefix is None:
        registered = ", ".join(sorted(conv.prefixes)) or "none registered"
        return (
            "C002",
            f"`{name}` starts with no registered prefix (registry: {registered}); a new prefix "
            f"is a task adding its row to `## Prefix registry` of `{CONVENTION_NAME}`, and the "
            "name waits on it",
        )
    kind, _, element = name[len(prefix) + 1 :].partition("_")
    if kind not in conv.types:
        return (
            "C003",
            f"`{name}`: type slot `{kind}` is not in `## Grammar` "
            f"(the closed list: {', '.join(conv.types) or 'empty'})",
        )
    if not element:
        return "C004", f"`{name}` has no element after the type `{kind}`"
    if not ELEMENT.match(element):
        return "C004", f"`{name}`: element `{element}` is not lowercase words joined by underscores"
    return None


def check_catalog(conv):
    """The file is held to its own grammar: every catalog row not marked `legacy`."""
    for name, legacy, line in conv.catalog:
        if legacy:
            continue
        found = grammar_finding(name, conv)
        if found:
            code, message = found
            yield conv.path, line, code, f"catalog row: {message}"


def check_plan(plan, conv, path):
    planned = {}
    for row in plan:
        name = row.name
        if name and name in conv.catalog_lines:
            marked = ", marked `legacy`" if conv.is_legacy(name) else ""
            yield (
                path,
                row.line,
                "C007",
                f"`{name}` is already in the catalog ({conv.path}:{conv.catalog_lines[name]}{marked})",
            )
        elif name and name in planned:
            yield path, row.line, "C007", f"`{name}` is planned twice (first at line {planned[name]})"
        else:
            found = grammar_finding(name, conv)
            if found:
                code, message = found
                yield path, row.line, code, message
        planned.setdefault(name, row.line)

        for fld in row.fields:
            if fld not in conv.fields:
                yield (
                    path,
                    row.line,
                    "C005",
                    f"`{fld}` is not in `## Dictionary`; the draft proposes the entry as a task on "
                    f"`{CONVENTION_NAME}`, and the row stands",
                )
                continue
            kind, _ = conv.fields[fld]
            if kind != "text":
                continue
            if fld not in conv.exceptions:
                yield (
                    path,
                    row.line,
                    "C006",
                    f"`{fld}` is typed `text` with no row in `## Exceptions`: free text needs an "
                    f"exception with status, justification and retention, per {PAYLOAD_RULE}",
                )
                continue
            status, line = conv.exceptions[fld]
            verdict = ": the legal-lens round decides the field" if status == "under-review" else ""
            yield (
                path,
                row.line,
                "C008",
                f"`{fld}` is free text under an `{status}` exception ({conv.path}:{line}){verdict}",
            )


# ----------------------------------------------------------------------- main


def run(args, cwd):
    """Return (findings, names checked). Every path in here ends in a list, never a raise."""
    anchor = args.spec if args.spec is not None else str(cwd)
    conv_path, missing = resolve_convention(args.convention, cwd, anchor)
    if missing:
        return [missing], 0
    text, error = read_text(conv_path)
    if error:
        return [(conv_path, 0, "C010", error)], 0
    conv, problems = parse_convention(conv_path, split_lines(text))
    if problems:
        return problems, 0

    if args.spec is not None:
        text, error = read_text(args.spec)
        if error:
            return [(args.spec, 0, "C010", error)], 0
        plan, unreadable = plan_from_spec(args.spec, split_lines(text))
        if unreadable:
            return [unreadable], 0
        plan_path = args.spec
    elif args.names == "-":
        text, error = read_stdin()
        if error:
            return [(anchor, 0, "C010", error)], 0
        plan = plan_from_names(text, numbered=False)
        plan_path = anchor
    else:
        text, error = read_text(args.names)
        if error:
            return [(args.names, 0, "C010", error)], 0
        plan = plan_from_names(text, numbered=True)
        plan_path = args.names

    findings = list(check_catalog(conv))
    findings.extend(check_plan(plan, conv, plan_path))
    return findings, len(plan)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Hold a spec's events table, or a list of emitted names, to the project's EVENTS.md."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--spec", help="a spec whose `## Metric` events table is the plan")
    source.add_argument("--names", help="a file with one event name per line, or `-` for stdin")
    parser.add_argument(
        "--convention",
        default=None,
        help=f"the convention file; default: `{CONVENTION_NAME}` at the repository root",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    cwd = Path.cwd()
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        findings, count = run(args, cwd)
    except Exception as err:  # the last resort: unexpected content is a coded line, never a trace
        anchor = args.spec if args.spec is not None else str(cwd)
        findings = [(anchor, 0, "C010", f"the checker could not process the input ({type(err).__name__}: {err})")]
        count = 0

    if not findings:
        print(f"checked {count} name{'s' if count != 1 else ''}, clean")
        return 0
    failed = False
    for path, line, code, message in findings:
        print(f"{path}:{line} {code} {message}")
        failed |= SEVERITY.get(code) == "E"
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
