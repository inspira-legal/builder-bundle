"""Tests for catalog_changes.py, with no network.

Usage:
    python3 catalog_changes_test.py

Each case writes two invented snapshots of a product called Orbit and checks what the script
prints about them.
"""

import contextlib
import importlib.util
import io
import pathlib
import sys
import tempfile

spec = importlib.util.spec_from_file_location("cc", pathlib.Path(__file__).with_name("catalog_changes.py"))
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

failures = []
folder = pathlib.Path(tempfile.mkdtemp())


def write(name, text):
    path = folder / name
    path.write_text(text.lstrip())
    return str(path)


def run(argv):
    out = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(out):
            cc.main(argv)
    except SystemExit as e:
        code = e.code
    return code, out.getvalue()


def case(name, argv, code, *expected, absent=()):
    got, printed = run(argv)
    problems = [f"exit {got}, expected {code}"] if got != code else []
    problems += [f"no {text!r}" for text in expected if text not in printed]
    problems += [f"printed {text!r}" for text in absent if text in printed]
    print(f"{'ok    ' if not problems else 'FAILED'} | {name} | {'; '.join(problems) or 'passed'}")
    if problems:
        failures.append(name)


previous = write(
    "previous.csv",
    """
event,activation,renamed_from
board_view_opened,,
board_sub_shared,yes,
board_clk_export,yes,
board_clk_copy,,
search_view_opened,,
board_list_done,yes,
""",
)
current = write(
    "current.csv",
    """
event,activation,renamed_from
board_view_opened,,
board_sub_shared,yes,
board_clk_copy,yes,
search_view_opened,no,
board_list_closed,yes,board_list_done
board_sub_archived,yes,
board_view_history,,
""",
)
fired = write(
    "inventory.out",
    """
-- would read 1.20 GB
event_name | people
board_view_opened | 400
board_sub_shared | 120
board_clk_export | 90
board_clk_copy | 75
board_list_done | 30
board_sub_archived | 12
legacy_board_open | 8
""",
)

case("counts the catalog", [current], 0, "catalog: 7 events, 4 activation events")
case("no previous snapshot says so", [current], 0, "nothing to compare with", absent=("new in the catalog",))
case("an event entered the activation list", [current, previous], 0, "entered the activation list: 1\n  board_clk_copy")
case("an activation event left the catalog", [current, previous], 0, "left the catalog: 1\n  board_clk_export (was an activation event)")
case(
    "new events carry their decision",
    [current, previous],
    0,
    "new in the catalog: 2",
    "board_sub_archived (activation)",
    "  board_view_history\n",
)
case(
    "a rename is one event, never new and removed",
    [current, previous],
    0,
    "renamed, counted as one event: 1\n  board_list_done -> board_list_closed",
    absent=("board_list_closed (activation)", "board_list_done (was"),
)
case("an empty cell and `no` read the same", [current, previous], 0, "left the activation list: 0")
case(
    "the inventory puts people first, most fired on top",
    [current, previous, "--inventory", fired],
    0,
    "    90 people | board_clk_export (was an activation event)",
    "     ? people | board_view_history",
)
case(
    "fired outside the catalog, a renamed name not among them",
    [current, previous, "--inventory", fired],
    0,
    "fired outside the catalog: 2 of 7 fired events",
    "     8 people | legacy_board_open",
    absent=("people | board_list_done\n",),
)
case(
    "the IN list carries the earlier names of a rename",
    [current, "--in-list"],
    0,
    "'board_list_closed',\n'board_list_done'",
    absent=("board_view_opened",),
)
case(
    "a snapshot without the activation column stops",
    [write("bad.csv", "event,level\nboard_view_opened,primary\n")],
    1,
    "needs the columns event and activation",
)
case(
    "an id that would break out of a quoted list stops",
    [write("quote.csv", "event,activation\nboard_x') OR TRUE --,yes\n"), "--in-list"],
    1,
    "is not an event id",
)
case("a missing snapshot stops cleanly", [str(folder / "nope.csv")], 1, "could not read")

print()
print(f"{len(failures)} failure(s)" if failures else "every change was reported as expected")
sys.exit(1 if failures else 0)
