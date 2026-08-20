---
status: in-progress
created: 2026-08-20
slug: self-update
---

# bb keeps itself current

The plugin installs a version and then stays on it. Claude Code has no notice for an
outdated plugin, and a marketplace clone is refetched only when someone runs
`claude plugin marketplace update` by hand, so an install from July still serves July's
skills today. With 16 skills that change by PR every week, that is people running a bb the
CHANGELOG no longer describes.

This change makes the SessionStart hook do the update. It is silent: nothing appears on
screen, nothing is asked, and there is no flag that turns it off. The only trace is one line
in the session context, so the model can say what happened when it matters.

Success: a person who never runs a plugin command is on the current bb within a day of a
release, and never sees a prompt about it.

## What the platform allows

`claude plugin update` prints "restart required to apply", and the SessionStart hook runs
after the session has already loaded its plugins from
`plugins/cache/inspira-legal/bb/2.16.0`. An update installed during a session reaches the
person on the next start, and the running session keeps the version it loaded. The hook
cannot change that.

That constraint sets the design. Since the effect lands next session either way, no part of
this has to finish before the session opens.

The install path carries the version, so anything written inside it is lost on the next
update. `CLAUDE_PLUGIN_DATA` points at `plugins/data/bb-inspira-legal`, outside the versioned
path, and that is where the stamp lives.

`claude plugin update bb@inspira-legal` was run with stdin closed and no TTY: it printed
`bb is already at the latest version (2.16.0)` and exited 0. The command needs no terminal,
which is what lets a hook call it.

## Nothing waits

The hook does no network and no install. It reads one small JSON file, the stamp, adds a line
to the session context when the last run installed something, and spawns a detached worker
when the stamp's date is not today. The session start pays one file read.

The worker does the slow half: `git fetch` in the marketplace clone, compare the versions,
and, when the remote is ahead, run the two commands a person would run,
`claude plugin marketplace update MARKETPLACE` and `claude plugin update bb@MARKETPLACE`. It
writes what it did back into the stamp, which is how the next session knows.

The worker calls the CLI instead of installing by hand. Copying the plugin into the cache and
rewriting `installed_plugins.json` would be this hook reimplementing the installer that owns
those files, and it would break the first time the platform changes their shape.

The worker's output goes to the null device. The hook's stdout is a JSON payload the runner
parses, and a child that inherits that stream corrupts the session start.

## The guard on a clone that is a working tree

`claude plugin update` installs what the marketplace clone holds in its working tree, not what
the default branch holds. Where that clone doubles as a checkout for developing bb, an
unattended update installs whatever branch is checked out, unmerged work included.

So the worker installs only when the clone sits on the remote default branch with a clean
tree. Any other state records a reason in the stamp and installs nothing. Checking the branch
out is never an option, because the clone is someone's working tree.

## What the release signal becomes

The comparison is the version in `plugin.json`, so a commit that lands on `main` without a
bump reaches nobody. The bump is the release, and it is the only thing that propagates.

The other half of that: with no opt-out and a daily check, a bump on top of a broken `main`
reaches every install within a day, and the way back is a fix forward with another bump.
`claude plugin update` moves forward only, and the older versions sitting in the cache are
not somewhere it can return to. Keeping `main` green is the gate this feature leans on.

## Decisions

- **The hook updates, it does not ask.** No line on screen, no question, and no flag in
  `bb.config.json`. `.bb/no-opt-out` already settled the shape of this: the value of the rule
  is having no branch.
- **A detached worker, and the hook never waits.** The hook spawns and returns; the worker
  owns the network, the guard, and the install.
- **The check is git, the install is the CLI.** The branch and dirty guard needs git anyway,
  so the version comparison comes free from the same `git fetch`.
- **One file, two entry points.** `hooks/check_version.py` carries both: a function
  `sync_instructions.py` calls in process, and a `__main__` the hook spawns with
  `sys.executable`, because `python3` is not on every PATH a detached child inherits.
- **The day is claimed before the spawn.** The stamp is written with today's date first, so a
  second session starting at the same moment spawns no second worker.
- **Never a downgrade.** The install runs only when the remote version is greater, compared as
  integer tuples, so `2.9.0` against `2.16.0` reads right.
- **The target is the running install.** The marketplace name comes from `CLAUDE_PLUGIN_ROOT`
  (`.../cache/MARKETPLACE/bb/VERSION`), the clone path from `installLocation` in
  `known_marketplaces.json`, and the scope from the `installed_plugins.json` entry whose
  `installPath` matches `CLAUDE_PLUGIN_ROOT`.
- **Only bb is updated**, at the scope it is installed at, with `-y` for the absent TTY.
- **The stamp is the only channel**, holding `date`, `outcome`, `from`, `to`, and `reason`.
- **Every failure stays silent.** The hook's existing contract, exit 0 and print nothing,
  covers the new path too.

## Behavior

Happy path:

1. SessionStart: `sync_instructions.py` calls `check_version.report()`, which reads the stamp.
2. The stamp records an install from the last run, so its line joins the JSON payload's
   `additionalContext`.
3. The stamp's date is not today, so the hook writes today into it and spawns the detached
   worker, then returns.
4. The worker resolves the marketplace name, the clone path, and the install scope.
5. The worker runs `git fetch` and reads the version from
   `plugins/bb/.claude-plugin/plugin.json` on the remote default branch.
6. The remote is ahead, the clone is on the default branch, and the tree is clean, so the
   worker runs `claude plugin marketplace update` and then `claude plugin update`.
7. The worker writes `installed` with the two versions and exits. The next session carries
   the line, and that session runs the new version.

| #   | when                                              | then                                                            |
| --- | ------------------------------------------------- | --------------------------------------------------------------- |
| 8   | the stamp's date is today                         | no worker, no network, no output                                |
| 9   | two sessions start at the same moment             | the claimed date leaves only the first spawning a worker        |
| 10  | the clone is not on the remote default branch     | nothing installs; the branch name goes to `reason`              |
| 11  | the clone's tree is dirty                         | nothing installs; `reason` says so                              |
| 12  | the remote version equals or trails the installed | nothing installs, and no downgrade is attempted                 |
| 13  | `git` or `claude` is not resolvable               | the worker exits after writing `reason`                         |
| 14  | the marketplace has no git clone                  | the worker exits after writing `reason`                         |
| 15  | the fetch or either command fails or times out    | `outcome` is `failed`, and the next day retries                 |
| 16  | the worker writes to stdout or stderr             | both are the null device, so the hook's JSON stays parsable     |
| 17  | bb is installed at project scope                  | the update runs with that scope, from that project directory    |
| 18  | `CLAUDE_PLUGIN_DATA` is unset                     | the stamp falls back under `~/.claude/plugins/data`             |
| 19  | the stamp is missing or malformed                 | it reads as a first run: no line, and the worker spawns         |
| 20  | anything raises anywhere in the hook              | the session opens with no output and exit 0                     |
| 21  | an install lands                                  | the loaded version stays; the line says the new one starts next |

## Tasks

- [x] **1. Resolution and stamp**: `hooks/check_version.py` resolves the marketplace, clone,
      scope, and stamp path, and reads and writes the stamp. No network, no spawn.
      → behaviors 4, 18, 19 · dep: — · verify: run the module on this machine, read the stamp
- [ ] **2. The worker**: the `__main__` path with the fetch, the version compare, the branch
      and dirty guard, the two CLI calls, and the outcome recording.
      → behaviors 5, 6, 7, 10, 11, 12, 13, 14, 15, 17 · dep: 1 · verify: run it by hand with
      the clone on `main` and again on a feature branch
- [ ] **3. The wiring**: `sync_instructions.py` calls `report()` and the spawn on both of its
      paths, merging one JSON payload, with the child's streams closed.
      → behaviors 1, 2, 3, 8, 9, 16, 20, 21 · dep: 1, 2 · verify: run the hook, read its JSON
- [ ] **4. The record**: a `README.md` line saying bb keeps itself current, and the CHANGELOG
      entry with the version bump in `plugin.json`.
      → behaviors 7, 21 · dep: 3 · verify: CI (`validate.yml`) green

## Out of scope

- Pruning the old versions the cache keeps side by side. Each release leaves about 1.1 MB
  behind, and those directories belong to the platform.
- Updating any plugin other than bb, and updating the CLI itself.
- Telling the person on screen. _Revisit_ if a silent install ever ships a broken release,
  because that is the day the silence costs something.
- Deleting the local prototype, `~/.claude/hooks/bb-update-check.ps1` and its `SessionStart`
  entry in `~/.claude/settings.json`. It lives outside this repo and goes by hand when this
  lands, so the two do not both fire.

## Open

Nothing.
