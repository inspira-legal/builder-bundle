# Capture: what the conversation leaves for later

Over a task, ideas come up that do not fit the current version: a technical improvement, a
user's feedback, a feature someone liked and pushed back. Capture keeps the ones worth keeping
and lets the rest go. A backlog that keeps everything is read by nobody.

## The two doors

An item gets in through one of two doors, and only through them:

1. **Interest.** The person asked to keep it ("park this", "note it for the next version",
   "anota pra depois"), or accepted the idea and put it off.
2. **Value to the user, with evidence.** A lawyer's or a customer's feedback with its source
   (the meeting, the ticket, the message), or a technical problem the end user feels: an
   error, a slow screen, lost data.

Your own suggestion that nobody took up stays out, and so does an internal refactor with no
effect a user would notice, unless the person asked for it. So does an idea the person turned
down, one already in the tracker, and a detail that belongs in a PR comment.

When you are not sure an item passes a door, leave it out of the file and ask once, at the
end: "These 2 ideas came up and were left open: keep them?"

## Where it is written

Write to `.bb/<slug>/backlog.md` of the work in progress: the slug of the spec this session
is building, or the one the person names. With no slug in sight, ask for it in the same
question as above.

Place the item under `references/destination.md`: `## Next version` when the person said when
it comes back, `## No trigger yet` when not. The line carries its door, `interest` or
`value: <source>`, and `<!-- captured <YYYY-MM-DD> -->` in place of an id.
