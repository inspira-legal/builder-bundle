#!/usr/bin/env python3
"""Make a front's `name` for start_session from its slug or title.

start_session takes `[a-z0-9-]` and at most 24 characters, and derives a name
by cutting mid-word when none is passed. This makes the name deterministically:
fold to ASCII, kebab, and cut at the last hyphen that fits. The first word alone
passing 24 is the one case a word is cut. A name already held by a live session
of the run is flagged, never suffixed: the orchestrator picks another slug.

Output (one JSON object on stdout):
  {"slug": "orchestrate-session-naming", "name": "orchestrate-session",
   "cut": true, "collision": false}
  Exit 1 with {"error": ...} when nothing of the input survives the charset.

Usage:
  python3 front_name.py <slug-or-title> [--live NAME ...]
  python3 front_name.py "Fix sessão naming" --live session-naming,add-diagnose
"""

import argparse
import json
import re
import sys
import unicodedata

MAX_LEN = 24
# Letters NFKD does not decompose into an ASCII base would be dropped whole.
FOLD = str.maketrans(
    {"ß": "ss", "ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE",
     "ł": "l", "Ł": "L", "đ": "d", "Đ": "D", "þ": "th", "Þ": "TH"}
)


def kebab(text):
    """Fold accents to ASCII and reduce to lowercase `[a-z0-9-]`."""
    folded = unicodedata.normalize("NFKD", text.translate(FOLD))
    folded = folded.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-")


def cut(slug):
    if len(slug) <= MAX_LEN:
        return slug
    # A hyphen at index 24 still leaves a 24-char name before it.
    idx = slug.rfind("-", 0, MAX_LEN + 1)
    if idx <= 0:
        return slug[:MAX_LEN]
    return slug[:idx]


def live_names(values):
    names = []
    for value in values or []:
        names.extend(n.strip().lower() for n in value.split(",") if n.strip())
    return names


class JsonArgumentParser(argparse.ArgumentParser):
    # The caller parses stdout as JSON, so a usage error has to be JSON too.
    def error(self, message):
        print(json.dumps({"error": message}))
        sys.exit(2)


def main():
    parser = JsonArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="the front's slug or title")
    parser.add_argument(
        "--live",
        nargs="*",
        default=[],
        help="names of the run's live sessions (space or comma separated)",
    )
    args = parser.parse_args()

    slug = kebab(args.source)
    if not slug:
        print(json.dumps({"error": "no [a-z0-9] characters in the slug or title"}))
        return 1

    name = cut(slug)
    taken = name in live_names(args.live)
    print(
        json.dumps(
            {
                "slug": slug,
                "name": name,
                "cut": name != slug,
                "collision": taken,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
