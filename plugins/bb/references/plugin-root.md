# `<plugin-root>`: where the plugin's own files are

`<plugin-root>` is the directory this plugin was installed into, and the name every bb document
uses for it. It is a rule rather than a path: what it resolves to depends on which copy of
the bundle the machine has, and a reader resolves it before running anything under it.

## Why the literal does not travel

`${CLAUDE_PLUGIN_ROOT}` is expanded where the platform composes the text itself, and read as
plain text everywhere else. A skill gets it in two places, per the
[string substitutions reference](https://code.claude.com/docs/en/skills#available-string-substitutions):
the skill's markdown content, and the `Bash` rules in its `allowed-tools` frontmatter. Hook,
MCP and LSP subprocesses get it a different way, as a real environment variable.

| the path is written in            | how it arrives                                            |
| --------------------------------- | --------------------------------------------------------- |
| `hooks/hooks.json`                | expanded, into the hook process's own environment         |
| a `SKILL.md` body                 | expanded, to the per-session copy of the plugin           |
| a reference `.md`, read on demand | raw: a `Read` is a file read, and nothing interpolates it |

The third row is empty in a tool call, so `cat "$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js"`
runs as `cat /workflows/build-tasks.js` and exits 1. The second row is the one that looks
fine and is not: on Windows the per-session copy lives under `AppData\Roaming\Claude`, a
directory MSYS tools list and native processes report as non-existent, so a `python3` call
against that path comes back `can't open file`. Only the first row is a path a command can
open, which is why `hooks/hooks.json` keeps the literal and every document a model reads
carries `<plugin-root>` instead.

The documented pattern is to write the same string in the body and in `allowed-tools`, so the
rule matches the command and the script runs without a prompt. It buys nothing here: the row
that would use it is the row whose expansion does not open, and no bb skill declares
`allowed-tools`. `${CLAUDE_SKILL_DIR}` is not the way around it either. It resolves to the
skill's own subdirectory rather than the plugin root, and on Windows it lands inside the same
per-session copy.

## The rule

Two steps, first hit wins. A directory counts as the root only when
`workflows/build-tasks.js` is readable under it, which is what keeps step 1 from winning
with a path nothing can open.

1. `$CLAUDE_PLUGIN_ROOT`, when it is non-empty.
2. The search, in this order:

| copy          | glob                                                           |
| ------------- | -------------------------------------------------------------- |
| install cache | `<config>/plugins/cache/*/bb/*`, highest version first         |
| repo checkout | `./plugins/bb`                                                 |
| per-session   | `<app-data>/Claude/local-agent-mode-sessions/*/*/rpm/plugin_*` |

The installed copy answers first: it is where an update lands, and every process on the
machine can open it, which is exactly what the per-session copy fails at. It is not
necessarily the version this session is running, because a session delivered inline carries
its own copy; what the order buys is a path that opens. Order those directories by version
and not by modification time, which is a different order. The repo checkout follows, so
someone editing the bundle resolves to the files they are editing, which the cache outranks
wherever an install exists: set `CLAUDE_PLUGIN_ROOT` to the checkout when it has to win. The
per-session copy is last, for the machine where it is the only one.

`<config>` is `$HOME/.claude` unless `CLAUDE_CONFIG_DIR` moves it, which a multi-account setup
does, and it moves every path under it. `<app-data>` is where the three systems disagree:
`$APPDATA` on Windows, `$HOME/Library/Application Support` on macOS,
`${XDG_CONFIG_HOME:-$HOME/.config}` on Linux. Glob all three rather than branching on the
system, since the two that do not exist expand to nothing.

The search is the rule's body and not its fallback. A task agent inside a build workflow has
no skill body and no variable, and it resolves the root exactly this way.

As one shell function:

```bash
plugin_root() {
  cc="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
  for d in "$CLAUDE_PLUGIN_ROOT" \
           $(ls -d "$cc"/plugins/cache/*/bb/*/ 2>/dev/null | sed 's:/*$::' \
             | awk -F/ '{split($NF,v,"."); printf "%05d.%05d.%05d\t%s\n", v[1],v[2],v[3], $0}' \
             | sort -r | cut -f2-) \
           ./plugins/bb \
           $(ls -dt "$APPDATA"/Claude/local-agent-mode-sessions/*/*/rpm/plugin_* \
                    "$HOME"/Library/Application\ Support/Claude/local-agent-mode-sessions/*/*/rpm/plugin_* \
                    "${XDG_CONFIG_HOME:-$HOME/.config}"/Claude/local-agent-mode-sessions/*/*/rpm/plugin_* 2>/dev/null); do
    [ -n "$d" ] && [ -f "$d/workflows/build-tasks.js" ] && { printf '%s\n' "${d%/}"; return 0; }
  done
  return 1
}
```

Then `python3 "$(plugin_root)/scripts/scan_specs.py" ...`, and a non-zero exit from `plugin_root` is
the resolution failing, which is worth saying out loud instead of running a command against
an empty string.

Two things in that block are load-bearing and read as noise. The version order is spelled out
by hand because `sort -V` is a GNU extension: BSD sort, which is the macOS one, answers
`invalid option -- V` and takes the whole cache step down with it. Zero-padding each component
into a fixed width makes plain `sort -r` order versions correctly, `10.0.1` over `3.2.0`
included. And the `sed` is there because `ls -d` on a `*/` glob can return a trailing slash
twice over, which leaves the last path component empty and silently orders by name instead.
The guard is what keeps any of this from being dangerous: a step that resolves to the wrong
directory does not win, it fails `[ -f "$d/workflows/build-tasks.js" ]` and the next one
answers.

## Two notations, and which one runs

A document writes `<plugin-root>` and a shell writes `$(plugin_root)`. The first is a
placeholder: it names the directory in prose and in a path citation, and a reader resolves it
into a real path before opening anything. It is never text to paste into a shell, where `<`
and `>` are redirection operators and the command would not run at all.

`$(plugin_root)` is the runnable form, and it carries one requirement: **every `Bash` call is
a fresh shell**, so the function has to be defined in the same call that uses it. Paste the
block above at the top of that call, or resolve the root once and reuse the path it printed
in the calls that follow.

## Line endings

`.gitattributes` pins the repo to `eol=lf`. The marketplace clone at
`$HOME/.claude/plugins/marketplaces/<owner>` is configured `core.autocrlf = true`, and its
checkout would otherwise hand the install cache a CRLF copy. That reaches one caller in
particular: `Workflow` inlines a `scriptPath` into the approval dialog as `script` and
refuses the CR as a control character that would be hidden there, so a CRLF
`build-tasks.js` dispatches neither by path nor inline. The fix belongs to the checkout, and
nothing downstream strips anything.
