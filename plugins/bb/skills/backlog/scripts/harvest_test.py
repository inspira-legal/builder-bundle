"""Tests for harvest.py, on a `.bb/` built in a temporary folder.

Usage:
    python3 harvest_test.py

The records are invented: a product called Orbit, with boards.
"""

import datetime as dt
import importlib.util
import pathlib
import sys
import tempfile

spec = importlib.util.spec_from_file_location("harvest", pathlib.Path(__file__).with_name("harvest.py"))
harvest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvest)

DISCOVERY = """---
slug: boards
created: 2026-09-01
phase: done
verdict: build-mvp
---

## Cuts

Cut:
- **Shared boards with guests**, `out-of-appetite`: one owner per board in the first cut.
  _revisit_ after the owners ask for it twice
- Board templates: low-confidence. Nobody asked yet.
Kept, in priority order:
1. **Board per client** (ICE 8, high impact, low effort)
2. Archive a board
"""

SPEC = """---
status: {status}
created: 2026-09-01
slug: boards
wave: PRJ-7
---

# Boards

## Decisions

- One owner per board.

## Tasks

- [x] **1. The board**: a board per client. · verify: reading
- [ ] **2. Archive**: archive a board. · verify: reading

## Out of scope

- Shared boards with guests. _revisit_ after the owners ask for it twice
- Exporting a board to a spreadsheet. _discarded_ because nobody exports a board.

## Open

- Nothing decided on the board's color.
"""

failures = []


def case(name, fn):
    try:
        fn()
        print(f"ok    {name}")
    except AssertionError as error:
        failures.append(name)
        print(f"FAIL  {name}: {error}")


def build(status="pending", backlog=None):
    root = pathlib.Path(tempfile.mkdtemp())
    (root / ".git").mkdir()
    folder = root / ".bb" / "boards"
    folder.mkdir(parents=True)
    (folder / "discovery.md").write_text(DISCOVERY, encoding="utf-8")
    (folder / "spec.md").write_text(SPEC.format(status=status), encoding="utf-8")
    if backlog is not None:
        (folder / "backlog.md").write_text(backlog, encoding="utf-8")
    return root


def run(root, **kwargs):
    kwargs.setdefault("today", dt.date(2026, 10, 27))
    result = harvest.harvest(str(root), **kwargs)
    return result["slugs"][0] if result["slugs"] else None


def by_kind(slug, kind):
    return [i for i in slug["items"] if i["kind"] == kind]


def cuts_carry_reason_and_trigger():
    cuts = by_kind(run(build()), "cut")
    assert [c["title"] for c in cuts] == ["Shared boards with guests", "Board templates"], cuts
    assert cuts[0]["reason"] == "out-of-appetite" and cuts[1]["reason"] == "low-confidence"
    assert cuts[0]["revisit"] and cuts[0]["trigger"] == "after the owners ask for it twice"
    assert not cuts[1]["revisit"] and cuts[1]["trigger"] is None


def kept_work_is_not_a_leftover():
    titles = [i["title"] for i in run(build())["items"]]
    assert not any("Board per client" in t or "Archive a board" in t for t in titles), titles


def live_spec_keeps_its_tasks():
    assert by_kind(run(build("pending")), "task") == []
    assert by_kind(run(build("in-progress")), "task") == []


def ended_spec_gives_up_its_unticked_tasks():
    for status in ("done", "blocked"):
        tasks = by_kind(run(build(status)), "task")
        assert [t["title"] for t in tasks] == ["2. Archive"], (status, tasks)


def out_of_scope_and_open_are_read():
    slug = run(build())
    assert len(by_kind(slug, "out_of_scope")) == 2
    source = by_kind(slug, "open")[0]["source"]
    assert source == "spec.md#open:26", source
    assert slug["spec"]["wave"] == "PRJ-7"
    assert [i["discarded"] for i in by_kind(slug, "out_of_scope")] == [False, True]


def the_same_idea_twice_is_flagged():
    slug = run(build())
    cut = by_kind(slug, "cut")[0]["id"]
    out = by_kind(slug, "out_of_scope")[0]["id"]
    assert {"kind": "near_duplicate", "ids": [cut, out]} in slug["alerts"], slug["alerts"]


def an_old_pending_spec_is_flagged():
    alerts = run(build("pending"))["alerts"]
    assert alerts[0] == {"kind": "stale_spec", "days": 56, "wave": "PRJ-7"}, alerts
    assert all(a["kind"] != "stale_spec" for a in run(build("pending"), stale_days=60)["alerts"])
    assert all(a["kind"] != "stale_spec" for a in run(build("done"))["alerts"])


def ids_are_stable_and_the_backlog_is_remembered():
    first = run(build())["items"]
    again = run(build())["items"]
    assert [i["id"] for i in first] == [i["id"] for i in again]
    kept = first[0]["id"]
    slug = run(build(backlog=f"- **Shared boards with guests** <!-- id:{kept} -->\n"))
    assert slug["backlog_exists"]
    assert [i["in_backlog"] for i in slug["items"]][:2] == [True, False]


def merged_and_skipped_ids_are_remembered():
    items = run(build())["items"]
    cut, out, rest = items[0]["id"], items[2]["id"], [i["id"] for i in items[3:]]
    backlog = f"- **Shared boards with guests** <!-- id:{cut} id:{out} -->\n\n<!-- skipped id:{' id:'.join(rest)} -->\n"
    slug = run(build(backlog=backlog))
    assert [i["id"] for i in slug["items"] if not i["in_backlog"]] == [items[1]["id"]], slug["items"]
    assert all(a["kind"] != "near_duplicate" for a in slug["alerts"]), slug["alerts"]


def a_stray_byte_in_the_backlog_does_not_stop_the_harvest():
    root = build()
    kept = run(root)["items"][0]["id"]
    (root / ".bb" / "boards" / "backlog.md").write_bytes(b"- caf\xe9 <!-- id:" + kept.encode() + b" -->\n")
    assert run(root)["items"][0]["in_backlog"]


def items_that_differ_in_a_short_word_keep_their_own_ids():
    root = build("done")
    spec_path = root / ".bb" / "boards" / "spec.md"
    extra = "- Export a board as PDF.\n- Export a board as XLS.\n- SSO\n- iOS\n"
    spec_path.write_text(spec_path.read_text(encoding="utf-8").replace("## Open", extra + "\n## Open"), encoding="utf-8")
    slug = run(root)
    ids = [i["id"] for i in by_kind(slug, "out_of_scope")]
    assert len(ids) == len(set(ids)) == 6, ids
    assert all(len(set(a["ids"])) == 2 for a in slug["alerts"] if a["kind"] == "near_duplicate"), slug["alerts"]


def a_quoted_or_embedded_marker_is_not_a_marker():
    root = build("done")
    spec_path = root / ".bb" / "boards" / "spec.md"
    extra = (
        "- Drop the `needs_revisit_flag` column.\n"
        "- Explain `_discarded_` in the docs.\n"
        "- **Archive later.** __revisit__ next quarter\n"
    )
    spec_path.write_text(spec_path.read_text(encoding="utf-8").replace("## Open", extra + "\n## Open"), encoding="utf-8")
    out = by_kind(run(root), "out_of_scope")[2:]
    assert [(i["revisit"], i["discarded"]) for i in out] == [(False, False), (False, False), (True, False)], out


def the_walk_stops_at_the_repository():
    outer = pathlib.Path(tempfile.mkdtemp())
    (outer / ".bb" / "elsewhere").mkdir(parents=True)
    (outer / ".bb" / "elsewhere" / "spec.md").write_text(SPEC.format(status="done"), encoding="utf-8")
    inner = outer / "repo"
    (inner / ".git").mkdir(parents=True)
    assert harvest.harvest(str(inner))["slugs"] == []


case("a cut carries its reason and its revisit trigger", cuts_carry_reason_and_trigger)
case("the kept list is in scope, not a leftover", kept_work_is_not_a_leftover)
case("a live spec keeps its unticked tasks", live_spec_keeps_its_tasks)
case("a done or blocked spec gives up its unticked tasks", ended_spec_gives_up_its_unticked_tasks)
case("out of scope and open are read, with the wave key", out_of_scope_and_open_are_read)
case("the same idea in discovery and spec is flagged", the_same_idea_twice_is_flagged)
case("a pending spec past the window is flagged", an_old_pending_spec_is_flagged)
case("ids are stable and backlog.md marks what is kept", ids_are_stable_and_the_backlog_is_remembered)
case("a merged entry and the skipped line keep their ids", merged_and_skipped_ids_are_remembered)
case("a stray byte in backlog.md does not stop the harvest", a_stray_byte_in_the_backlog_does_not_stop_the_harvest)
case("items that differ in a short word keep their own ids", items_that_differ_in_a_short_word_keep_their_own_ids)
case("a marker in a code span or an identifier is not a marker", a_quoted_or_embedded_marker_is_not_a_marker)
case("the root walk stops at the repository", the_walk_stops_at_the_repository)

print()
print(f"{len(failures)} failure(s)" if failures else "every case behaved as expected")
sys.exit(1 if failures else 0)
