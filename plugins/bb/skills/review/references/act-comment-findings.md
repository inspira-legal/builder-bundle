# Action: leave the findings on the PR

For items the user chose to **comment instead of fix**. Available only when the
probe found an open PR for this branch (`fronts.md`); with no PR the items stay in
the report and the gate offers `/bb:ship` to open one.

## 1. Show the body, then post

A PR comment is outward-facing and carries the user's identity: print the exact body
of every comment first and post only on an explicit yes. On no, the items stay in the
report and nothing is sent.

## 2. Anchor only where an anchor holds

- **Location inside the diff** → one review comment per item, anchored to the line:
  `gh api repos/<owner>/<repo>/pulls/<n>/comments` with `path`, `line` and
  `commit_id` (the head sha).
- **Location outside the diff**: a correctness finding in an untouched line of a
  function the diff moved (`front-correctness.md` puts that in scope), a whole-file
  rule deviation, a candidate that grouped by `file` with no line. None of those
  has an anchor, so the API rejects it. Those go into the summary comment with `file:line` written into
  the text, and the re-report says which items landed as summary instead of inline.
- Items that are about the change as a whole (a contract gap, the rules checklist)
  are summary comments by nature: `gh pr comment <n> --body-file -`.

## 3. Additive: the whole conversation is the corpus

The corpus to match against is everything already said on this PR, not only what bb
said in an earlier round. It is step 0's intent read (`SKILL.md`, "The intent read"):
the `fetch_comments.py` payload, with the top-level comments, the review bodies and
the inline threads, each note carrying its `author { login }`. A point another
reviewer made counts exactly as much as one bb made, and the item that repeats it
carries that author's name. What decides is that the point was said, not who said it.

The match is by `file:line` plus substance, what the point is and not how it was
worded. Each point then lands exactly once:

- **already said** → nothing is posted. The item keeps its line in the report with
  the `[já dito: <link>]` mark step 4 gave it, and the re-report records it as
  `já dito (link)`.
- **partly said** → one comment carrying only the new part, opening with the note it
  builds on and its author ("@<author> already asked for the guard on `parse()`; what
  is still missing is the empty-list case").
- **not said yet** → under `new`, with the full shape from section 4.
- **already said and now fixed** → out of the body; it survives as a count in the
  opening line ("2 of the 3 earlier points resolved").

The mark's link is what `fetch_comments.py` does not carry: the payload has the author
and the body of every note, no per-note URL. So take the link from the two reads that
do carry one, `gh pr view <n> --json comments` (`url`) and
`gh api repos/<owner>/<repo>/pulls/<n>/comments` (`html_url`), and where the note that
said it has no link of its own, the mark carries its author and `file:line` instead.

**When every picked item was already said, nothing is posted at all.** Say it in one
line, with the count ("6 items, all 6 already in the conversation, nothing posted"),
and open no review to carry it. An empty comment costs the next comment its reader.

A comment that does go out is a new comment: the earlier one stays on the PR as
posted, so the thread reads as a history.

## 4. Keep the shape the report gave it

Each item carries over what it had: rule ID and quoted rule, WCAG criterion,
trigger, suggested fix, **and its verdict**, so the comment stands on its own for
whoever reads the PR without this transcript. A PLAUSIBLE posted as if it were
CONFIRMED is how the next comment stops being read.

Collect each comment's URL as it's created; the re-report links them
(`comentado (link)`).
