# Land it → Push to a feature branch

Reached from ship's Step 1 when the destination is a non-protected branch. The
quality pass is already done and the gate is green; this is only the landing.

1. Confirm the target branch — the current one, or a new name the user gave.
2. Push: `git push -u origin <branch>`.
3. Report what landed (commits, files, gate result). No PR is opened — if they want
   one later, ship again with the PR destination.

Pushing a feature branch is reversible, so ship runs it. Merge, approve, and
force-push stay yours.
