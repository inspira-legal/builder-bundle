---
name: write-readme
description: Generates or rewrites a repository's README in a minimal centered header style. Inspects the repo to derive the name, the badges and the install and usage commands. Use when the user says "write a readme", "generate a readme", "update the readme", "document this repo", or asks for a README for any project.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.1.0
---

# README generator

Write READMEs that respect the reader: a centered identity block, then copy-paste commands. Prose only where a command can't speak for itself.

## Typography

A README is prose this plugin writes outward, so the plugin-level `references/doc-style.md` governs it: voice, the dash rule, code font, lists and tables. One house rule sits on top and wins where the two meet:

- **All lowercase**: headings, lead-ins, taglines, badge labels, table text. Verbatim tokens (commands, filenames, flags) and acronyms (PR, CI, CLI) keep their casing.

## Style contract

Every README is exactly these blocks, top to bottom:

1. **Centered header**: wrap in `<div align="center">`:
   - `# <repo-name>`, lowercase
   - One line of [shields.io](https://shields.io) badges: `style=flat-square`, base color `111111`. One badge per fact that is _true_ of the repo (license file → license badge; published package → registry badge; public repo → github badge). A repo with zero verifiable facts gets zero badges.
   - Preview image (`width="1000"`) if a screenshot/preview asset exists in the repo
   - `_<tagline>_`, one italic sentence that says what this is; wit is welcome, vagueness is not
   - close `</div>`
2. **Action blocks**: 2–4 of them. Each is a terse imperative lead-in ("run instantly:", "install globally:", "develop from source:") followed by a fenced `bash` block. The first block is the fastest path to value.
3. **One compact section** (optional): a single table or short list for content that can't be a command: a skills/recipes catalog, a structure map, a recovery procedure. One section, not several.
4. **`<sub>` footer** (optional): one line of attribution/credits.

That's the whole README. If a section doesn't fit one of these four slots, it doesn't go in.

## Reference

The shape to reproduce (adapted from [t1code](https://github.com/maria-rcks/t1code)):

````markdown
<div align="center">

# t1code

[![license](https://img.shields.io/badge/license-MIT-111111?style=flat-square)](./LICENSE)
[![npm](https://img.shields.io/npm/v/%40maria__rcks%2Ft1code?color=111111&label=npm&style=flat-square)](https://www.npmjs.com/package/@maria_rcks/t1code)
[![github](https://img.shields.io/badge/github-maria--rcks%2Ft1code-111111?style=flat-square&logo=github)](https://github.com/maria-rcks/t1code)

<img src="./assets/repo/t1code-preview.webp" alt="t1code terminal UI screenshot" width="1000" />

_T3Code, but in your terminal._

</div>

run instantly:

```bash
bunx @maria_rcks/t1code
```

install globally:

```bash
bun add -g @maria_rcks/t1code
```

develop from source:

```bash
git clone https://github.com/maria-rcks/t1code.git
cd t1code
bun install
bun dev:tui
```

<sub>based on T3 Code by [@t3dotgg](https://github.com/t3dotgg) and [@juliusmarminge](https://github.com/juliusmarminge).</sub>
````

## Workflow

### 1. Inspect

Gather only what the README will assert:

```bash
basename "$(git rev-parse --show-toplevel)"   # repo name
git remote get-url origin                      # github badge + clone URLs
ls LICENSE* 2>/dev/null                        # license badge
cat package.json 2>/dev/null                   # registry badge, run scripts
ls justfile Makefile *.toml 2>/dev/null        # task runner → action blocks
ls assets/ docs/ 2>/dev/null                   # preview image
```

Read the repo enough to know what it _does_: the tagline and the first action block come from purpose, not file listings. If a README already exists, mine it for facts (catalog tables, attribution), then rewrite it into the contract above.

### 2. Derive the action blocks

Pick by repo type:

| Repo type        | Blocks                                                              |
| ---------------- | ------------------------------------------------------------------- |
| Published CLI    | run instantly (`npx`/`bunx`/`uvx`) → install globally → from source |
| Dotfiles/config  | bootstrap (clone + sync) → daily driver command → upgrade           |
| Skill/plugin set | install one-liner → what's inside (catalog table)                   |
| Private/personal | primary daily commands → recovery/bootstrap procedure               |

Every command must work as pasted: verify binaries and script names against the repo before writing them.

### 3. Write

Write `README.md` at the repo root. Tagline in the repo's language; commands verbatim. Leave committing to the user unless asked.
