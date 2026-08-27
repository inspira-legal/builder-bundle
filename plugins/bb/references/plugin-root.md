# `<plugin-root>`: where the plugin's own files are

`<plugin-root>` is the directory this plugin was installed into, and the name every bb document
uses for it. It is a rule rather than a path: what it resolves to depends on which copy of
the bundle the machine has, and a reader resolves it before running anything under it.

## Why the literal does not travel

`${CLAUDE_PLUGIN_ROOT}` is expanded by the platform in two places and read as plain text
everywhere else.

| the path is written in | how it arrives |
| --- | --- |
| `hooks/hooks.json` | expanded, into the hook process's own environment |
| a `SKILL.md` body | expanded, to the per-session copy of the plugin |
| a reference `.md`, read on demand | raw: a `Read` is a file read, and nothing interpolates it |

The third row is empty in a tool call, so `cat "$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js"`
runs as `cat /workflows/build-tasks.js` and exits 1. The second row is the one that looks
fine and is not: on Windows the per-session copy lives under `AppData\Roaming\Claude`, a
directory MSYS tools list and native processes report as non-existent, so a `python3` call
against that path comes back `can't open file`. Only the first row is a path a command can
open, which is why `hooks/hooks.json` keeps the literal and every document a model reads
carries `<plugin-root>` instead.

## The rule

Two steps, first hit wins. A directory counts as the root only when
`workflows/build-tasks.js` is readable under it, which is what keeps step 1 from winning
with a path nothing can open.

1. `$CLAUDE_PLUGIN_ROOT`, when it is non-empty.
2. The search, in this order:

| copy | glob |
| --- | --- |
| install cache | `$HOME/.claude/plugins/cache/*/bb/*`, highest version first |
| repo checkout | `./plugins/bb` |
| per-session | `$APPDATA/Claude/local-agent-mode-sessions/*/*/rpm/plugin_*` |

The installed copy answers first: it is the version the session is running, it is where an
update lands, and every process on the machine can read it. Order those directories by
version and not by modification time, which is a different order. The repo checkout follows,
so someone editing the bundle resolves to the files they are editing. The per-session copy is
last, for the machine where it is the only one. `$APPDATA` is the Windows spelling and
`$HOME/Library/Application Support` the macOS one.

The search is the rule's body and not its fallback. A task agent inside a build workflow has
no skill body and no variable, and it resolves the root exactly this way.

As one shell function:

```bash
plugin_root() {
  for d in "$CLAUDE_PLUGIN_ROOT" \
           $(ls -d "$HOME"/.claude/plugins/cache/*/bb/* 2>/dev/null | sort -Vr) \
           ./plugins/bb \
           $(ls -dt "${APPDATA:-$HOME/Library/Application Support}"/Claude/local-agent-mode-sessions/*/*/rpm/plugin_* 2>/dev/null); do
    [ -n "$d" ] && [ -f "$d/workflows/build-tasks.js" ] && { printf '%s\n' "${d%/}"; return 0; }
  done
  return 1
}
```

Then `python3 "$(plugin_root)/scripts/scan_specs.py" ...`, and a non-zero exit from `plugin_root` is
the resolution failing, which is worth saying out loud instead of running a command against
an empty string.

## Line endings

`.gitattributes` pins the repo to `eol=lf`. The marketplace clone at
`$HOME/.claude/plugins/marketplaces/<owner>` is configured `core.autocrlf = true`, and its
checkout would otherwise hand the install cache a CRLF copy. That reaches one caller in
particular: `Workflow` inlines a `scriptPath` into the approval dialog as `script` and
refuses the CR as a control character that would be hidden there, so a CRLF
`build-tasks.js` dispatches neither by path nor inline. The fix belongs to the checkout, and
nothing downstream strips anything.
