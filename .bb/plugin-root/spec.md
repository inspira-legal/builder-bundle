---
status: in-progress
created: 2026-08-27
slug: plugin-root
---

# the plugin root, resolved where nobody expands it

`${CLAUDE_PLUGIN_ROOT}` reaches a skill two ways, and neither ends in a path a command can
open on this machine. A file read off disk arrives raw, because a `Read` is a file read and
nothing interpolates it, so `references/build-tasks-workflow.md` hands over
`$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js` verbatim, the variable is empty in the tool
call, and the command runs as `cat /workflows/build-tasks.js` and exits 1. A skill body
arrives with the variable already expanded, and that is the half that looks fixed and is not:
what it expands to is the per-session copy under `AppData\Roaming\Claude`, a directory that
MSYS tools list and native processes say does not exist.

```
python3 -c "...os.path.exists(r'C:\Users\PC\AppData\Roaming\Claude')"  → False
PowerShell  Test-Path 'C:\Users\PC\AppData\Roaming\Claude'             → False
ls -l  .../rpm/plugin_.../scripts/scan_specs.py                        → 5404 bytes
```

So `/bb:implement`'s step 1 is delivered as `python3 <per-session>/scripts/scan_specs.py` and
comes back `can't open file`. The build dispatch is where the raw half costs the most: the
same `build-tasks-workflow.md` that resolves the script through the variable also declares "a
`Bash` call that cannot read the file" to be the last step of the fallback chain. The
documented happy path fails, the failure reads as the fallback's own condition, and
`/bb:implement` builds in the main context with nobody having refused anything, which is the
degradation `.bb/build-via-workflow/spec.md` exists to prevent.

This spec gives the bundle one way to name its own root, `<plugin-root>`, resolved by a rule that
survives both failures, and rewrites every mention that ends in a command. Success:
`/bb:implement` dispatches on this machine without improvising a path, and `scan_specs.py`,
`resolve_checks.py`, `preflight.py`, `gather_context.py` and `fetch_comments.py` run on the
first try from the documents that call them.

## Where the literal stays, and where it goes

| the path is written in | how it arrives | verdict |
| --- | --- | --- |
| a reference `.md`, read on demand | raw, so the variable is empty | `<plugin-root>` |
| a `SKILL.md` body | expanded, to a directory scripts cannot open | `<plugin-root>` |
| `hooks/hooks.json` | expanded, into a hook's own environment | keep the literal |

The first two rows fail for different reasons and take the same fix. The third is a different
environment: a hook is not a tool call, this run has no evidence about what a hook's
`${CLAUDE_PLUGIN_ROOT}` opens, and `hooks/check_version.py` already carries its own guard,
reading the variable first "because it is what the platform states" and falling back to the
module's own `__file__` "when the variable does not reach the process". Untouched here.

## The three copies, and which one the rule takes

| copy | glob | line endings |
| --- | --- | --- |
| install cache | `$HOME/.claude/plugins/cache/*/bb/*` | CRLF, until this ships |
| repo | `./plugins/bb` | LF |
| per-session | `$APPDATA/Claude/local-agent-mode-sessions/*/*/rpm/plugin_*` | LF |

**The installed copy is the answer.** It is the version the session is running, it is where an
update lands, and it is readable by every process on the machine. Its directories are many and
the newest by modification time is not the newest release, so they are ordered by version. The
repo copy follows, so a checkout of the bundle itself resolves to the files being edited. The
per-session copy is last and, on this machine, unreachable, which is also why the announced
`Base directory for this skill` is not a step of the rule: it names the one copy a script
cannot open.

`$APPDATA` is the Windows spelling and `$HOME/Library/Application Support` the macOS one, so
`${APPDATA:-$HOME/Library/Application Support}` covers both.

Putting the cache first would make CRLF the normal path, and `Workflow` inlines a `scriptPath`
into the approval dialog as `script` and rejects the CR as a control character that would be
hidden there. That is a packaging bug with a packaging fix, one level up from any document:
the marketplace clone at `$HOME/.claude/plugins/marketplaces/inspira-legal` is configured
`core.autocrlf = true`, its checkout converts LF to CRLF, and the cache copy inherits it. This
repo ships no `.gitattributes`, so nothing overrides that. One does now, and `.gitattributes`
outranks `core.autocrlf`.

The timing works out on its own: an update re-clones the marketplace before copying the new
version into the cache, so the release that carries these documents is the first one checked
out LF. Nothing in the dispatch strips anything.

## `<plugin-root>`

The notation every document uses from here on: a path with a resolution rule behind it, where
`${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py` is a path that looks runnable and is not. The
literal goes rather than gaining a warning beside it, because a document that writes the
failing command and then says not to use it has still written the failing command.

The rule as the reference will carry it:

```bash
plugin_root() {
  for d in "$CLAUDE_PLUGIN_ROOT" \
           $(ls -d "$HOME"/.claude/plugins/cache/*/bb/* 2>/dev/null | sort -Vr) \
           ./plugins/bb \
           $(ls -dt "${APPDATA:-$HOME/Library/Application Support}"/Claude/local-agent-mode-sessions/*/*/rpm/plugin_* 2>/dev/null); do
    [ -n "$d" ] && [ -f "$d/workflows/build-tasks.js" ] && { printf '%s\n' "${d%/}"; return 0; }
  done; return 1; }
```

## Decisions

- **One new plugin-level reference, `references/plugin-root.md`**, owns the raw-versus-expanded
  split, the resolution rule and the `<plugin-root>` notation. Every other document points at it
  and carries no copy of the rule.
- **The rule is two steps, first hit wins**: `$CLAUDE_PLUGIN_ROOT` when it is non-empty, then
  the search over the copies table in its order, by version inside the cache. A directory
  counts as the root only when `workflows/build-tasks.js` is readable under it, which is what
  keeps step 1 from winning with a path nothing can open.
- **The search is the rule's body, not its fallback.** A task agent inside the build workflow
  has no skill body and no variable, and it resolves the root the same way every other reader
  does.
- **`<plugin-root>` replaces the literal wherever a document is read by the model**, in runnable
  commands and in file citations alike, so one directory has one name. `hooks/hooks.json`,
  `check_version.py` and `plugin-root.md` itself keep the literal, the last because it has to
  write it to explain it.
- **A rewritten file gains one pointer to `references/plugin-root.md`**, at its first
  `<plugin-root>`, and no repetition after.
- **The CR is fixed once, in `.gitattributes`, not on every dispatch.** A guard in the
  documented `Bash` call would run forever against a checkout setting, so the setting is what
  changes. The dispatch call resolves the root and proves `build-tasks.js` is readable, and
  what it prints is what `scriptPath` takes.
- **The CR refusal keeps no fallback of its own.** Both dispatch steps read the same file, so a
  CR that survived would take out `scriptPath` and the inline `script` together, and stripping
  it in one place would leave the other broken anyway. If it ever recurs, it recurs as the
  chain's own last step, which is a build in the main context and a named reason.
- **The fallback chain's last step stops meaning "the interpolated path did not exist".** The
  in-context build is reached when the whole resolution rule comes back empty, when there is no
  `Workflow` tool, or when both dispatch attempts were refused. A first path that does not
  resolve is a step of the rule, not a step of the chain.
- **A session rule that forbids workflows is named, not silently absorbed.** It is not a step
  of the chain: the build runs in the main context and the report says the session's own rules
  vetoed the dispatch, so the reason is visible instead of reading as a missing file.
- **The sweep is text only.** No script gains a resolver, and `scripts/*.py` keep taking their
  paths as arguments.

## Behavior

The happy path, one build dispatch on Desktop:

1. `/bb:implement <slug>` reaches step 6 and reads `references/build-tasks-workflow.md`.
2. The documented `Bash` call resolves `<plugin-root>`: the variable is empty, so the search
   answers with the newest cache directory.
3. The call reads `<plugin-root>/workflows/build-tasks.js`, confirms it is readable, and prints
   its path.
4. `Workflow({scriptPath: <printed path>, args})` dispatches. The permission dialog shows the
   script, the user approves, and one agent per task runs.
5. The run returns, and implement reports it as a dispatched build.

| WHEN | THEN |
| --- | --- |
| a document read by the model writes the literal | the sweep is incomplete, and `grep` is the check |
| `$CLAUDE_PLUGIN_ROOT` is non-empty and its `build-tasks.js` is readable | it is the root, and nothing is searched |
| it is non-empty and that file is not readable | it is not a match: the search runs |
| the search runs | the cache answers first, newest version, then the repo, then the per-session copy |
| more than one location matches | the first one wins, and the run names which copy it took |
| no location matches | the resolution failed: say so, and the build takes the chain's last step |
| the marketplace clone converts line endings | `.gitattributes` pins LF, and the installed copy is LF from this release on |
| the resolved `build-tasks.js` carries CR anyway | both dispatch steps are refused, and the chain's last step names CR as the reason |
| the dispatch is refused for its path | step 2 runs: a refusal at step 1 ends the attempt, not the chain |
| the user denies the permission dialog | report the denial and ask what they want, outside the chain |
| the session's own rules forbid `Workflow` | build in the main context and name the veto as the reason |
| a skill step calls a `scripts/*.py` | it resolves `<plugin-root>` first, so the call is not made against the per-session copy |
| a task agent runs with no skill body in context | the search alone resolves the root |
| the documents change and `plugin.json` does not | every install stays on the old copy and no session sees the fix |

## Tasks

- [x] **1. `references/plugin-root.md`**: the raw-versus-expanded split, the two step rule with
      the `plugin_root` shape and the `<plugin-root>` notation → behaviors 2, 3, 4, 5, 6, 13 · dep: — ·
      verify: reading
- [x] **2. `.gitattributes`**: `* text=auto eol=lf` at the repo root, so a clone configured
      `core.autocrlf = true` still checks the bundle out LF → behavior 7 · dep: — · verify:
      `git check-attr text eol -- plugins/bb/workflows/build-tasks.js` reports `eol: lf`
- [x] **3. The dispatch reads the new rule**: `references/build-tasks-workflow.md` gets the
      resolve-and-prove `Bash` call, the corrected last step of the chain, CR as a reason that
      chain can name, and the session veto as a named non-step → behaviors 6, 8, 9, 10, 11 ·
      dep: 1 · verify: run the documented call in `Bash` and confirm it prints an existing
      `build-tasks.js`
- [x] **4. The `review` and `ship` references**: `fronts.md`, `front-ci.md`, `front-threads.md`,
      `front-correctness.md`, `intent-read.md`, `act-apply-fixes.md`, `ship-pr.md`,
      `ship-lexflow.md` → behavior 1 · dep: 1 · verify: `grep -rn CLAUDE_PLUGIN_ROOT` over those
      eight files returns nothing
- [x] **5. The `brisar` and `spec` references**: `phase-develop.md`, `develop-modes.md`,
      `deliver-modes.md`, `phase-3-scaffold.md`, `references/spec-state.md`,
      `skills/spec/references/spec-format.md` → behavior 1 · dep: 1 · verify: `grep -rn
      CLAUDE_PLUGIN_ROOT` over those six files returns nothing
- [x] **6. The skill bodies**: `implement/SKILL.md`, `review/SKILL.md`, `ship/SKILL.md`,
      `review-setup/SKILL.md`, `gather-branch-context/SKILL.md`, twenty-one mentions, every one
      of them a `scripts/*.py` call → behaviors 1, 12 · dep: 1 · verify: `grep -rn
      CLAUDE_PLUGIN_ROOT --include=*.md plugins/bb` returns only `plugin-root.md`
- [x] **7. The release**: `plugin.json` from 3.1.0 to 3.2.0 and the `CHANGELOG.md` entry that
      says which copy the rule takes, why, and what `.gitattributes` fixes → behavior 14 · dep:
      2, 3, 4, 5, 6 · verify: reading

## Out of scope

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
- Teaching `scripts/*.py` to resolve the root themselves. Only `check_version.py` needs it, and
  it already does.

## Open

Nothing.
