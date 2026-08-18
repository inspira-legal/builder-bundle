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

## 3. On a PR that already carries a review comment

Before posting, read what's already there (`gh pr view <n> --json comments` plus
`gh api repos/<owner>/<repo>/pulls/<n>/comments`), and match this round's items
against the findings already raised (by `file:line` + what the point is, not by
wording). Each point then lands exactly once:

- **already raised and still true** → one line under `ainda aberto`, referencing the
  point instead of re-explaining it. A reader who saw the first comment gets the
  status, not the essay again.
- **raised for the first time** → under `novo`, with the full shape from section 4.
- **already raised and now fixed** → out of the body; it survives as a count in the
  opening line ("2 dos 3 pontos anteriores resolvidos").

The new comment is a new comment: the earlier one stays on the PR as posted, so the
thread reads as a history.

## 4. Keep the shape the report gave it

Each item carries over what it had: rule ID and quoted rule, WCAG criterion,
trigger, suggested fix, **and its verdict**, so the comment stands on its own for
whoever reads the PR without this transcript. A PLAUSIBLE posted as if it were
CONFIRMED is how the next comment stops being read.

Collect each comment's URL as it's created; the re-report links them
(`comentado (link)`).
