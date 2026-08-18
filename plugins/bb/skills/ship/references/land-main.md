# Land it → Push to main (or another protected branch)

Reached from ship's Step 1 when the destination is a protected branch. Everything is
committed and the project's checks are green. Ship stops here and hands off, because good practice (and
branch protection, typically) reserves protected-branch landing for a human.

1. Show the summary: commits, files, check results.
2. Hand off the exact command, e.g. `git push origin HEAD:main` (or
   `git -C <repo> push origin <branch>`).
3. Note that CI will run on push.

Ship never runs the protected-branch push, and never merges or force-pushes.
