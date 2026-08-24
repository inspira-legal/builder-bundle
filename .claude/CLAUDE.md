# Builder Bundle (bb)

A **Claude Code plugin** (`bb`) published through a one-plugin marketplace, the
unified skill set for Inspira builders. Install via
`claude plugin marketplace add inspira-legal/builder-bundle` then
`claude plugin install bb@inspira-legal`. Skills are invoked as `/bb:<skill>`
(e.g. `/bb:spec`). The plugin writes its operating context into
`~/.claude/BUILDER-BUNDLE.md` and imports it from `~/.claude/CLAUDE.md`, from the
first `/bb:profile` on.

## Structure

```
.claude-plugin/marketplace.json        # lists the single `bb` plugin
plugins/bb/
├── .claude-plugin/plugin.json
├── agents/                            # pipeline roles (auto-discovered, no plugin.json entry)
│   ├── bb-review-finder.md             # review fan-out: finds candidates, read-only by `tools:`
│   └── bb-review-verifier.md           # review fan-out: CONFIRMED / PLAUSIBLE / REFUTED
├── hooks/                             # session infra (auto-active, no skill)
│   ├── hooks.json                      # SessionStart: BUILDER-BUNDLE.md, and bb's own update
│   ├── enter_worktree.py               # worktree isolation for local autonomous runs
│   ├── scheduling-decision.md          # /loop vs Desktop task vs Channels decision table
│   ├── sync_instructions.py            # writes ~/.claude/BUILDER-BUNDLE.md + the CLAUDE.md import
│   ├── check_version.py                # the daily self-update: the stamp, and the detached worker
│   └── operating-context.md            # the operating frame it writes from (edit to tune)
├── references/                        # plugin-level docs (not skill-scoped)
│   ├── doc-style.md                    # the style rules for every sentence bb writes
│   ├── handoff-gate.md                 # the one convention for end-of-skill gates (+ AskUserQuestion rationale)
│   ├── confidence-and-steelman.md      # shared reasoning protocols (think, challenge)
│   ├── spec-state.md                   # the .bb/<slug>/ folder contract
│   ├── bb-config.md                    # ~/.claude/bb.config.json: the schema and who reads it
│   ├── consult-manifesto.md            # runtime stack decisions from inspira-legal/manifesto
│   └── build-tasks-workflow.md         # how the skills call workflows/build-tasks.js, and what it returns
├── scripts/                           # shared executables (2+ skills), ref via ${CLAUDE_PLUGIN_ROOT}/scripts/
│   ├── fetch_comments.py               # ship, review
│   ├── reply_resolve_thread.py         # ship, review
│   └── gather_context.py               # ship, review (resolves the diff range), gather-branch-context
├── skills/                            # all 16 skills flat; trilha grouping is a docs concept
│   ├── Pensar:        discover, challenge, think, legal-lens
│   ├── Desenhar:      spec
│   ├── Construir:     implement, ship, delegate, gather-branch-context
│   ├── Revisar:       review, maintain-repo, review-setup
│   ├── Design:        brisar
│   ├── Pesquisar/Doc: code-deep-research, write-readme
│   └── no trilha:     profile
└── workflows/                         # dispatched by a skill, not read by one
    └── build-tasks.js                  # one agent per task, run via Workflow's scriptPath
```

### Naming conventions

- Skills live in `plugins/bb/skills/<name>/SKILL.md`. Names are **verb-led** where
  possible, invoked as `/bb:<name>` (`/bb:ship`). No trilha prefix in the name;
  the trilha grouping (Pensar / Desenhar / Construir / Revisar / Design /
  Pesquisar-Doc) is a docs concept (README sections), not part of the name. Keep
  the dir name identical to the frontmatter `name`.
- Each skill is self-contained: `scripts/` and `references/*.md` relative to the
  skill dir.
- Agents live in `plugins/bb/agents/<name>.md`, auto-discovered (no `plugin.json`
  entry). What an agent buys is a **system prompt the harness delivers**: the
  invariant half of a role travels with it instead of being re-composed into every
  prompt by the context that fans out, which is the half a caller trims first.
  That single ownership is the reason to reach for an agent; the skill references
  defer to it rather than restating it. The `tools:` list narrows the surface on top
  of that (CI fails a bb agent that lists a write tool), but with `Bash` on the list
  it narrows the surface without closing it, so don't write it up as a guarantee. Name
  agents by **role in the pipeline**, not by front or phase: what varies between
  fronts is prompt content the caller already assembles. The `description` sits in
  context globally, so keep it narrow and name the skill that is the real entry
  point.
- The plugin ships hooks in `plugins/bb/hooks/hooks.json` (auto-activate when the
  plugin is enabled). Hook commands reference files via `${CLAUDE_PLUGIN_ROOT}/...`.

## Skills

Each skill is a folder with a `SKILL.md` containing YAML frontmatter (`name`,
`description`, `license`, `metadata`) followed by Markdown instructions. The
`description` field doubles as the trigger. It tells the agent when to invoke
the skill.

### Progressive disclosure (mandatory for fused skills)

A skill that fuses sources or has phases/modes keeps its `SKILL.md` lean, a
router: what the skill is, how it decides which phase/mode applies, and one line
per phase pointing at its reference. The per-phase material lives in the skill's
`references/` and is loaded **only when that phase runs**. A monolithic SKILL.md
that inlines every phase is a defect, not a style choice.

### Handoff gates

Every skill with a natural next step ends with a single `AskUserQuestion` gate, whose
format and journey map live in `plugins/bb/references/handoff-gate.md`. Gates suggest,
never auto-invoke (exceptions documented there). Skills without a natural next
step just report and stop.

### Scripting principle

Skills are folders. They can contain scripts alongside the SKILL.md. **Prefer
Python scripts for deterministic operations** (parsing, formatting, data
transformation, file manipulation, JSON processing) over having the LLM do it
inline. Reserve LLM reasoning for judgment calls, synthesis, and creative
decisions.

The **`workflows/` exception is JavaScript**: a file under `plugins/bb/workflows/` is
`.js` because the `Workflow` tool takes a JavaScript script and nothing else. It gets
no shell and no filesystem, so it only coordinates agents and reads their structured
returns; the deterministic work Python would do belongs in a script an agent calls. The
repo's own tooling under `.github/scripts/` follows the repo instead, which is bun and
TypeScript.

### Writing guidelines

- The prose of this repo, and every document a skill generates, follows
  `plugins/bb/references/doc-style.md`, which states every rule it asks for instead of
  pointing at a guide on the web. The rules name no language: they govern how a
  sentence is built, in whatever language the reader arrived in.
- Keep SKILL.md focused on the workflow and decision-making logic
- Keep guidance positive and lean by default; enforce irreversible hazards with
  capability scoping, not prose. Don't write catalogs of anti-patterns / "DO NOT"
  lists; a single sharp caution is allowed where negation is genuinely the
  clearest signal.
- Use `references/` for static context the LLM needs (per-phase material,
  checklists, formats)
- Trigger descriptions should be specific; list exact phrases the user might say
- Skill workflows reference their **own** scripts relatively (e.g.
  `scripts/foo.py`). Scripts shared by 2+ skills live at the plugin root in
  `plugins/bb/scripts/` and are referenced with
  `${CLAUDE_PLUGIN_ROOT}/scripts/<x>.py` (hooks use it for their own files too). A
  skill's own, non-shared script stays relative.
- **Borrowing another skill's reference** is allowed when one skill owns a method
  two entry points must share, and duplicating it would mean two definitions that
  drift. Path it via `${CLAUDE_PLUGIN_ROOT}/skills/<owner>/references/<x>.md` and
  say in both skills who owns it. Reading a reference is not invoking a skill;
  the borrower still orchestrates its own run, which is why borrowing beats
  invoking when the owner's router would ask questions the borrower answers by
  policy. Today nothing is borrowed. The review engine (the fronts, the verify pass, the
  apply guard and the `{review,quality}-checklist.md` criteria they point at) is
  `/bb:review`'s alone and lives under `skills/review/references/`; `/bb:ship`
  stopped reading it when it stopped reviewing. The one guard it still needs (one
  change at a time, untested code left flagged) is two lines in its own Step 2,
  which beats a cross-skill read for a principle that short.

## Scripts

- Python scripts use `gh api graphql` for GitHub data (not the REST API directly)
- Scripts are invoked via `Bash` tool from within skill workflows
- Scripts write to stdout (JSON or plain text) for the LLM to consume
- New scripts should use Python, stdlib only (no third-party imports), with the two
  exceptions the scripting principle names: `plugins/bb/workflows/*.js` and the repo's
  own `.github/scripts/*.ts`

## Spec state

The on-disk contract is `plugins/bb/references/spec-state.md`: `.bb/<slug>/` holds
three documents and a prototype, and **every skill writes its own document, with
`spec.md` having exactly one writer**. `/bb:discover` writes `discovery.md` (the
framing), `/bb:brisar` writes `design.md` (the journey) plus `prototype/` (the clickable
artifact), and `/bb:spec` writes `spec.md` (the contract, with its
`status`/`created`/`slug` frontmatter and the status lifecycle owned by `/bb:delegate`).
The spec reads the two records by path and never copies their prose; where a record and
the spec disagree the spec wins, and the record's own writer registers the reversal on
its next round. Members are independent, and a folder can carry any one of them alone.
Skills reference that file instead of restating the contract.

The spec's **form** belongs to `plugins/bb/skills/spec/references/spec-format.md`:
a free top half (opening plus whatever sections the problem asks for) over a fixed
set (`Decisions`, `Behavior`, `Tasks`, `Out of scope`, `Open`), fixed because each
member has a reader. `skills/spec/scripts/lint_spec.py` enforces the
mechanical half of that and runs in CI over every `.bb/*/spec.md`.

## Commits

- No AI attribution in commits, PRs, or code comments
- Conventional commit style: `<type>(<scope>): <description>`
- Scope is the skill name (`spec`, `maintain-repo`, …), `hooks` for the hook
  layer, or `repo` for repo-wide changes
- **The commit body carries the rationale.** Why a decision changed, what a
  closer read of the source corrected, which alternative lost and on what
  grounds. That belongs here, not in the file being changed. A spec in
  `.bb/` describes what to build as it stands now; the history of how it
  got there is what `git log` is for, and duplicating it into the document is
  what makes specs unreadable.
