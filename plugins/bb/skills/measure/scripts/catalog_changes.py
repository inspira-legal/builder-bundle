"""Say what changed in the event catalog since the previous measurement.

Usage:
    python3 catalog_changes.py CURRENT.csv [PREVIOUS.csv] [--inventory INVENTORY.out]
    python3 catalog_changes.py CURRENT.csv --in-list

- CURRENT.csv: the catalog as read today, one event per row, saved beside the measurement as
  its snapshot. The header is `event,activation,renamed_from`. `activation` is `yes` for an
  activation event and empty (or `no`) for the rest. `renamed_from` holds the earlier names of
  an event the catalog declares as renamed, separated by spaces, and is empty otherwise.
- PREVIOUS.csv: the snapshot the previous measurement saved. Without it there is nothing to
  compare with, and the script says so instead of guessing.
- INVENTORY.out: the output of db_read.py for an inventory query, with the columns
  `event_name` and `people`, separated by " | ". With it, each event carries the people who
  fired it in the window, and the events that fired outside the catalog are listed.
- --in-list: print the activation events for a query's `IN (...)`, each earlier name of a
  renamed event included, so a rename counts as one event across the whole history.

The activation list applies to the whole history, so an event that enters or leaves it moves
every week a measurement shows. That is why the output names those events first.
"""

import csv
import re
import sys

NAME = re.compile(r"^[A-Za-z0-9_.:-]+$")  # an event id, safe to quote into a query


def fail(message: str) -> None:
    """Stop with a message on stdout, where the caller reads it, and a non-zero exit."""
    print(message)
    sys.exit(1)


def catalog(path: str) -> dict:
    """Return {event: (is activation, [earlier names])} from a snapshot."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as error:
        fail(f"could not read {path}: {error.strerror}")
    if rows and not {"event", "activation"} <= set(rows[0]):
        fail(f"{path} needs the columns event and activation; it has: {', '.join(rows[0])}")
    out = {}
    for row in rows:
        event = (row.get("event") or "").strip()
        if not event:
            continue
        earlier = (row.get("renamed_from") or "").split()
        for name in [event] + earlier:
            if not NAME.match(name):
                fail(f"{path}: '{name}' is not an event id")
        out[event] = ((row.get("activation") or "").strip().lower() in ("yes", "true"), earlier)
    return out


def inventory(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f if not line.startswith("--")]
    except OSError as error:
        fail(f"could not read {path}: {error.strerror}")
    if not lines:
        fail(f"{path} is empty")
    header = [c.strip() for c in lines[0].split(" | ")]
    try:
        i_event, i_people = header.index("event_name"), header.index("people")
    except ValueError:
        fail(f"{path} needs the columns event_name and people; it has: {', '.join(header)}")
    out = {}
    for line in lines[1:]:
        cells = [c.strip() for c in line.split(" | ")]
        if len(cells) == len(header) and cells[i_event]:
            out[cells[i_event]] = int(cells[i_people] or 0)
    return out


def in_list(current: dict) -> str:
    names = []
    for event, (active, earlier) in sorted(current.items()):
        if active:
            names += [event] + earlier
    return ",\n".join(f"'{name}'" for name in names)


def changes(current: dict, previous: dict) -> dict:
    """Compare two snapshots. A rename the current one declares is one event, not two."""
    renamed = {old: new for new, (_, earlier) in current.items() for old in earlier if old in previous}
    before = {renamed.get(event, event): active for event, (active, _) in previous.items()}
    now = {event: active for event, (active, _) in current.items()}
    return {
        "entered the activation list": [e for e in now if e in before and now[e] and not before[e]],
        "left the activation list": [e for e in now if e in before and before[e] and not now[e]],
        "left the catalog": [e for e in before if e not in now],
        "new in the catalog": [e for e in now if e not in before],
        "renamed": sorted(renamed.items()),
        "was activation": {e for e, active in before.items() if active},
    }


def show(events, fired: dict, note=lambda event: "") -> None:
    """One line per event, the most fired first; with an inventory, its people lead the line."""
    for event in sorted(events, key=lambda e: (-fired.get(e, -1), e)):
        people = (f"{fired[event]:>6}" if event in fired else "     ?") + " people | " if fired else ""
        print(f"  {people}{event}{note(event)}")


def main(argv=None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    want_list = "--in-list" in args
    if want_list:
        args.remove("--in-list")
    fired_path = None
    if "--inventory" in args:
        i = args.index("--inventory")
        if i + 1 >= len(args):
            fail(__doc__)
        fired_path = args.pop(i + 1)
        args.pop(i)
    if len(args) not in (1, 2) or (want_list and (len(args) != 1 or fired_path)):
        fail(__doc__)

    current = catalog(args[0])
    if want_list:
        print(in_list(current))
        return
    fired = inventory(fired_path) if fired_path else {}
    active = sum(1 for is_active, _ in current.values() if is_active)
    print(f"catalog: {len(current)} events, {active} activation events")

    if len(args) == 1:
        print("no previous snapshot: nothing to compare with, so no change is reported")
    else:
        found = changes(current, catalog(args[1]))
        notes = {
            "left the catalog": lambda e: " (was an activation event)" if e in found["was activation"] else "",
            "new in the catalog": lambda e: " (activation)" if current[e][0] else "",
        }
        for title in ("entered the activation list", "left the activation list", "left the catalog", "new in the catalog"):
            print(f"{title}: {len(found[title])}")
            show(found[title], fired, notes.get(title, lambda e: ""))
        print(f"renamed, counted as one event: {len(found['renamed'])}")
        for old, new in found["renamed"]:
            print(f"  {old} -> {new}")

    if fired:
        known = set(current) | {old for _, earlier in current.values() for old in earlier}
        outside = [e for e in fired if e not in known]
        print(f"fired outside the catalog: {len(outside)} of {len(fired)} fired events")
        show(outside, fired)


if __name__ == "__main__":
    main()
