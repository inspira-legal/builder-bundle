# Cleaning up

The orchestrator tidies up itself. A side session asked to clean up after itself can
archive the wrong thing or stop mid-way, so these steps stay here:

- **Archive a side session once its PR lands**, with `archive_session` and the PR in the
  `reason`.
- **Stop what a front left running**: dev servers, app instances, watchers. Check the
  ports and processes the front's brief named, and stop each one.
- **Close an abandoned PR with a comment** that says why it closed and where the work
  went, if anywhere.
- **Rename a side session when its scope changes**, with `set_session_title`, so the
  sidebar says what each one does now.
- **Move a running app to `main` before archiving its session.** When the person is using
  an app that runs from a side session's folder, restart it from `main` first; archiving
  removes the worktree it runs from.

Outside auto mode the app asks the person to approve each archive. Say which approvals
are waiting, so tidying up does not stall unnoticed.
