---
status: done
created: 2026-08-27
slug: plugin-root
---

# the plugin root, resolved where nobody expands it

`/bb:implement` stopped dispatching its build workflow, and two independent things were doing
it. Neither is in the workflow script.

The first is `${CLAUDE_PLUGIN_ROOT}` in a reference. A file read off disk arrives raw, because
a `Read` is a file read and nothing interpolates it, so `references/build-tasks-workflow.md`
hands over `$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js` verbatim, the variable is empty in
the tool call, and the command runs as `cat /workflows/build-tasks.js` and exits 1. That same
reference declares "a `Bash` call that cannot read the file" to be the last step of its
fallback chain, so the documented happy path fails, the failure reads as the fallback's own
condition, and the build runs in the main context with nobody having refused anything, which
is the degradation `.bb/build-via-workflow/spec.md` exists to prevent.

The second is line endings. The marketplace clone at
`$HOME/.claude/plugins/marketplaces/inspira-legal` is configured `core.autocrlf = true` and
this repo shipped no `.gitattributes`, so the install cache got a CRLF `build-tasks.js`.
`Workflow` inlines a `scriptPath` into the approval dialog as `script` and rejects the CR as a
control character that would be hidden there, which takes out the path dispatch and the inline
one together.

Success: `/bb:implement` dispatches on this machine without improvising a path.

## Where the literal stays

`${CLAUDE_PLUGIN_ROOT}` is left alone wherever the platform already expands it into something
a command can open: `hooks/hooks.json`, where it lands in the hook process's own environment,
and a `SKILL.md` body, which the platform composes. Only the reference that dispatches the
build resolves the root itself, because a reference is the one place the literal arrives raw.

## The copies, and which one the rule takes

| copy          | glob                                 | line endings           |
| ------------- | ------------------------------------ | ---------------------- |
| install cache | `$HOME/.claude/plugins/cache/*/bb/*` | CRLF, until this ships |
| repo checkout | `./plugins/bb`                       | LF                     |

**The installed copy is the answer.** It is where an update lands and every process on the
machine can open it. Its directories are many and the newest by modification time is not the
newest release, so they are ordered by version. The repo checkout follows, so someone editing
the bundle resolves to the files being edited.

Putting the cache first would make CRLF the normal path, which is a packaging bug with a
packaging fix one level up from any document. The timing works out on its own: an update
re-clones the marketplace before copying the new version into the cache, so the release that
carries `.gitattributes` is the first one checked out LF. Nothing in the dispatch strips
anything.

## Decisions

- **The rule lives in `references/build-tasks-workflow.md`**, the one file that needs it, and
  nothing else in the bundle gains a copy. A second definition is a second thing to drift.
- **The rule is two steps, first hit wins**: `$CLAUDE_PLUGIN_ROOT` when it is non-empty, then
  the search over the copies table in its order, by version inside the cache. A directory
  counts as the root only when `workflows/build-tasks.js` is readable under it, which is what
  keeps step 1 from winning with a path nothing can open.
- **The search is the rule's body, not its fallback.** A task agent inside the build workflow
  has no skill body and no variable, and it resolves the root the same way.
- **The CR is fixed once, in `.gitattributes`, not on every dispatch.** A guard in the
  documented `Bash` call would run forever against a checkout setting, so the setting is what
  changes.
- **The CR refusal keeps no fallback of its own.** Both dispatch steps read the same file, so
  stripping the CR in one place would leave the other broken. If it ever recurs, it recurs as
  the chain's own last step, which is a build in the main context and a named reason.
- **The fallback chain's last step stops meaning "the interpolated path did not exist".** The
  in-context build is reached when the whole resolution rule comes back empty, when there is no
  `Workflow` tool, or when both dispatch attempts were refused. A first path that does not
  resolve is a step of the rule, not a step of the chain.
- **A session rule that forbids workflows is named, not silently absorbed.** It is not a step
  of the chain: the build runs in the main context and the report says the session's own rules
  vetoed the dispatch, so the reason is visible instead of reading as a missing file.
- **The change is text only.** No script gains a resolver, and `scripts/*.py` keep taking their
  paths as arguments.

## Behavior

The happy path, one build dispatch on Desktop:

1. `/bb:implement <slug>` reaches step 6 and reads `references/build-tasks-workflow.md`.
2. The documented `Bash` call resolves the root: the variable is empty, so the search answers
   with the newest cache directory.
3. The call reads `workflows/build-tasks.js` under it, confirms it is readable, and prints the
   path.
4. `Workflow({scriptPath: <printed path>, args})` dispatches. The permission dialog shows the
   script, the user approves, and one agent per task runs.
5. The run returns, and implement reports it as a dispatched build.

| WHEN                                                                    | THEN                                                                              |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `$CLAUDE_PLUGIN_ROOT` is non-empty and its `build-tasks.js` is readable | it is the root, and nothing is searched                                           |
| it is non-empty and that file is not readable                           | it is not a match: the search runs                                                |
| the search runs                                                         | the cache answers first, newest version, then the repo checkout                   |
| no location matches                                                     | the resolution failed: say so, and the build takes the chain's last step          |
| the marketplace clone converts line endings                             | `.gitattributes` pins LF, and the installed copy is LF from this release on       |
| the resolved `build-tasks.js` carries CR anyway                         | both dispatch steps are refused, and the chain's last step names CR as the reason |
| the dispatch is refused for its path                                    | step 2 runs: a refusal at step 1 ends the attempt, not the chain                  |
| the user denies the permission dialog                                   | report the denial and ask what they want, outside the chain                       |
| the session's own rules forbid `Workflow`                               | build in the main context and name the veto as the reason                         |
| a task agent runs with no skill body in context                         | the search alone resolves the root                                                |
| the documents change and `plugin.json` does not                         | every install stays on the old copy and no session sees the fix                   |

## Tasks

- [x] **1. `.gitattributes`**: `* text=auto eol=lf` at the repo root, so a clone configured
      `core.autocrlf = true` still checks the bundle out LF → behavior 5 · dep: — · verify:
      `git check-attr text eol -- plugins/bb/workflows/build-tasks.js` reports `eol: lf`
- [x] **2. The dispatch resolves the root before it proves the file**:
      `references/build-tasks-workflow.md` gets the `plugin_root` call, the corrected last step
      of the chain, CR as a reason that chain can name, and the session veto as a named
      non-step → behaviors 1, 2, 3, 4, 6, 7, 8, 9, 10 · dep: — · verify: run the documented
      call in `Bash` and confirm it prints an existing `build-tasks.js`
- [x] **3. The release**: `plugin.json` from 3.1.0 to 3.2.0 and the `CHANGELOG.md` entry naming
      both failures and what fixes each → behavior 11 · dep: 1, 2 · verify: reading

## Out of scope

- **Rewriting `${CLAUDE_PLUGIN_ROOT}` across the other twenty-two documents.** The same latent
  hazard is real there, a variable that looks runnable and expands to empty inside a reference,
  but none of those mentions was on the path that broke and none of them changes behavior in
  this release. It is a sweep, it is its own change, and bundling it here would have put five
  hundred lines of renaming around fifteen lines of fix (_revisit_).
- `hooks/hooks.json` and `hooks/check_version.py`. A hook's environment is not a tool call's,
  this run produced no evidence about what the variable opens there, and `check_version.py`
  already falls back to its own `__file__`.
- Anything that would make `CLAUDE_PLUGIN_ROOT` reach a tool call, or make
  `AppData\Roaming\Claude` visible to native processes. Both are the platform's, and the rule
  here is what a document can do without them.
- The account level preference that vetoes `Workflow` without an explicit request. It lives in
  no file in this repo, and bb's side of it is naming the veto when it fires.
- `hooks/sync_instructions.py` failing against a per-session directory from an older session.
  Real, separate, and not a root resolution bug (_revisit_).

## Open

Nothing.
