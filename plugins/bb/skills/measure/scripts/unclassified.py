"""List the events that fired and carry no level in the company's classification.

Usage:
    python3 unclassified.py INVENTORY.out CLASSIFIED.txt

- INVENTORY.out: the output of db_read.py for an inventory query, with the columns `event_name`
  and `people`, separated by " | ".
- CLASSIFIED.txt: the events the classification already covers, one name per line. Blank lines
  and lines starting with `#` are skipped. A CSV works too: the first column is read.

An event outside the classification may be one the metric should count and does not. That is why
the output is sorted by people, largest first.
"""

import sys


def fail(message: str) -> None:
    """Stop with a message on stdout, where the caller reads it, and a non-zero exit."""
    print(message)
    sys.exit(1)


def inventory(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if not line.startswith("--")]
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


def classified(path: str) -> set:
    with open(path, encoding="utf-8-sig") as f:
        names = (line.split(",")[0].strip().strip('"') for line in f)
        return {n for n in names if n and not n.startswith("#")}


def main() -> None:
    if len(sys.argv) != 3:
        fail(__doc__)
    fired, known = inventory(sys.argv[1]), classified(sys.argv[2])
    missing = sorted(((p, e) for e, p in fired.items() if e not in known), reverse=True)
    print(f"{len(fired)} events fired; {len(missing)} outside the classification")
    for people, event in missing:
        print(f"{people:>6} people | {event}")


if __name__ == "__main__":
    main()
