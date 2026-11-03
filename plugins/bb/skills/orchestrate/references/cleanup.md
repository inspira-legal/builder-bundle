# Cleaning up

The orchestrator tidies up itself. A side session asked to clean up after itself can
archive the wrong thing or stop mid-way, so these steps stay here.

## When a front ends

The orchestrator archives each front as soon as it ends, without asking the person:

- **A front with a PR** ends when the PR merges into `main`.
- **A front with no PR** (research, a report, a spec) ends when its report has arrived
  and the person has received what they needed from it. A report that leaves a question
  open or a decision pending has not ended its front.
- **A front whose PR is abandoned** ends when the PR closes with its comment.

When a spec front stopped at the spec (its scope ended there, or the person picked Stop
here at the gate), the build opens a new front with the same slug as its `name`. The spec
front ends with its report, so archive it first, and open the build front only once that archive
went through. While the archive waits on the person's approval, or after they declined it,
the build front waits too: say so, since a live spec front still holds the `name`.

## The steps

When a front ends, run these in order:

1. **Stop what the front left running**: dev servers, app instances, watchers. Check the
   ports and processes the front's brief named, and stop each one.
2. **Move a running app to `main`.** When the person is using an app that runs from the
   front's folder, restart it from `main` first; archiving removes the worktree it runs
   from.
3. **Close an abandoned PR with a comment** that says why it closed and where the work
   went, if anywhere.
4. **Make sure the front's work outlives its folder.** Archiving removes the worktree, so
   everything the front wrote is committed and pushed on its branch, or sits in the notes
   folder. When something is not, ask the front to commit and push it, and archive only
   once its answer confirms it.
5. **Archive the front** with `archive_session`, the `reason` naming the PR ("PR #42
   merged") or the report ("research report delivered").

Outside auto mode the app asks the person to approve each archive. Say which approvals
are waiting, so tidying up does not stall unnoticed. When the person declines an archive,
the front stays in the sidebar, and the orchestrator does not ask again for that front for
the rest of the run.

## A follow-up on an archived front

A follow-up on an archived front with no PR goes to that front again. First check that no
live front of the run holds its `name`; when one does, the follow-up goes to that live
front instead. Otherwise unarchive it with `unarchive_session`, then send the message.
Archiving removed the front's worktree, so the message says its folder may be gone and its
work lives on its branch or in the notes folder.

## Renaming

- **Rename a front only when its work changes**, with `set_session_title`, by the rule in
  `references/briefs.md`, "Naming a front".
