# Builder Bundle (bb)

A **Claude Code plugin** (`bb`) published through a one-plugin marketplace — the
unified skill set for Inspira builders. Install via
`claude plugin marketplace add inspira-legal/builder-bundle` then
`claude plugin install bb@inspira-legal`. Skills are invoked as `/bb:<skill>`
(e.g. `/bb:spec`). The plugin ships a `SessionStart` operating-context hook,
auto-active when the plugin is enabled. Never-merge for the unattended path is
enforced by cloud capability scoping (see the routine setup docs), not a local hook.

## Structure

```
.claude-plugin/marketplace.json        # lists the single `bb` plugin
plugins/bb/
├── .claude-plugin/plugin.json
├── agents/                            # pipeline roles (auto-discovered, no plugin.json entry)
│   ├── bb-finder.md                    # review fan-out: finds candidates, read-only by `tools:`
│   └── bb-verifier.md                  # review fan-out: CONFIRMED / PLAUSIBLE / REFUTED
├── hooks/                             # session infra (auto-active, no skill)
│   ├── hooks.json                      # SessionStart context injection
│   ├── enter_worktree.py               # worktree isolation for local autonomous runs
│   ├── scheduling-decision.md          # /loop vs Desktop task vs Cloud Routine decision table
│   ├── inject_operating_context.py     # SessionStart hook script
│   ├── operating-context.md            # the injected operating frame (edit to tune)
│   └── unattended-context.md           # addendum appended when BB_UNATTENDED is truthy
├── references/                        # plugin-level docs (not skill-scoped)
│   ├── handoff-gate.md                 # the one convention for end-of-skill gates (+ AskUserQuestion rationale)
│   ├── confidence-and-steelman.md      # shared reasoning protocols (think, challenge)
│   ├── task-state.md                   # the .bb/tasks/<slug>/spec.md contract
│   ├── consult-manifesto.md            # runtime stack decisions from inspira-legal/manifesto
│   ├── quality-checklist.md            # canonical quality criteria — the six lenses (review engine)
│   ├── review-checklist.md             # canonical correctness criteria — Pass 1 rows (review engine)
│   ├── routines.md                     # Cloud Routine guide — the unattended path
│   └── scripts/scaffold_routine.py     # emit a routine prompt + setup for a brief slug
├── scripts/                           # shared executables (2+ skills) — ref via ${CLAUDE_PLUGIN_ROOT}/scripts/
│   ├── fetch_comments.py               # ship, review
│   ├── reply_resolve_thread.py         # ship, review
│   └── gather_context.py               # ship, review (resolves the diff range), gather-branch-context
└── skills/                            # all 15 skills flat; trilha grouping is a docs concept
    ├── Pensar:        discover, challenge, think, legal-lens
    ├── Desenhar:      spec
    ├── Construir:     implement, ship, delegate, gather-branch-context
    ├── Revisar:       review, maintain-repo, review-setup
    ├── Design:        brisar
    └── Pesquisar/Doc: code-deep-research, write-readme
```

### Naming Conventions

- Skills live in `plugins/bb/skills/<name>/SKILL.md`. Names are **verb-led** where
  possible — invoked as `/bb:<name>` (`/bb:ship`). No trilha prefix in the name;
  the trilha grouping (Pensar / Desenhar / Construir / Revisar / Design /
  Pesquisar-Doc) is a docs concept (README sections), not part of the name. Keep
  the dir name identical to the frontmatter `name`.
- Each skill is self-contained: `scripts/` and `references/*.md` relative to the
  skill dir.
- Agents live in `plugins/bb/agents/<name>.md`, auto-discovered (no `plugin.json`
  entry). They exist to make a hazard structural: the `tools:` list is what keeps
  the review fan-out from writing, which is why CI fails a bb agent that lists a
  write tool. Name them by **role in the pipeline**, not by front or phase — what
  varies between fronts is prompt content the caller already assembles. The system
  prompt owns that role's invariant contract as its single owner, and the skill
  references defer to it; the `description` is PT-BR and sits in context globally,
  so keep it narrow and name the skill that is the real entry point.
- The plugin ships hooks in `plugins/bb/hooks/hooks.json` (auto-activate when the
  plugin is enabled). Hook commands reference files via `${CLAUDE_PLUGIN_ROOT}/...`.
  Irreversible hazards on the unattended path are kept out by capability scoping
  in the cloud routine, not by a local hook.

## Skills

Each skill is a folder with a `SKILL.md` containing YAML frontmatter (`name`,
`description`, `license`, `metadata`) followed by Markdown instructions. The
`description` field doubles as the trigger — it tells the agent when to invoke
the skill.

### Language (hybrid)

Instruction bodies are written in **English** (the method); everything the user
sees is **PT-BR**: frontmatter `description`/triggers, handoff-gate questions and
option labels, report templates, error messages addressed to the user.

### Progressive disclosure (mandatory for fused skills)

A skill that fuses sources or has phases/modes keeps its `SKILL.md` lean — a
router: what the skill is, how it decides which phase/mode applies, and one line
per phase pointing at its reference. The per-phase material lives in the skill's
`references/` and is loaded **only when that phase runs**. A monolithic SKILL.md
that inlines every phase is a defect, not a style choice.

### Handoff gates

Every skill with a natural next step ends with a single `AskUserQuestion` gate —
format and journey map in `plugins/bb/references/handoff-gate.md`. Gates suggest,
never auto-invoke (exceptions documented there). Skills without a natural next
step just report and stop.

### Scripting Principle

Skills are folders — they can contain scripts alongside the SKILL.md. **Prefer
Python scripts for deterministic operations** (parsing, formatting, data
transformation, file manipulation, JSON processing) over having the LLM do it
inline. Reserve LLM reasoning for judgment calls, synthesis, and creative
decisions.

### Writing Guidelines

- Keep SKILL.md focused on the workflow and decision-making logic
- Keep guidance positive and lean by default — enforce irreversible hazards with
  capability scoping, not prose. Don't write catalogs of anti-patterns / "DO NOT"
  lists; a single sharp caution is allowed where negation is genuinely the
  clearest signal.
- Use `references/` for static context the LLM needs (per-phase material,
  checklists, formats)
- Trigger descriptions should be specific — list exact phrases the user might say
  (in PT-BR)
- Skill workflows reference their **own** scripts relatively (e.g.
  `scripts/foo.py`). Scripts shared by 2+ skills live at the plugin root in
  `plugins/bb/scripts/` and are referenced with
  `${CLAUDE_PLUGIN_ROOT}/scripts/<x>.py` (hooks use it for their own files too). A
  skill's own, non-shared script stays relative.
- **Borrowing another skill's reference** is allowed when one skill owns a method
  two entry points must share, and duplicating it would mean two definitions that
  drift. Path it via `${CLAUDE_PLUGIN_ROOT}/skills/<owner>/references/<x>.md` and
  say in both skills who owns it. Reading a reference is not invoking a skill —
  the borrower still orchestrates its own run, which is why borrowing beats
  invoking when the owner's router would ask questions the borrower answers by
  policy. Today: `/bb:ship` reads
  `skills/review/references/{fronts,verify,front-*,act-apply-fixes}.md`, and
  `skills/review` reads the plugin-root `references/{review,quality}-checklist.md`
  as the criteria its fronts point at.

## Scripts

- Python scripts use `gh api graphql` for GitHub data (not the REST API directly)
- Scripts are invoked via `Bash` tool from within skill workflows
- Scripts write to stdout (JSON or plain text) for the LLM to consume
- New scripts should use Python, stdlib only (no third-party imports)

## Task briefs

The on-disk contract for shaped work is `plugins/bb/references/task-state.md` —
canonical location `.bb/tasks/<slug>/spec.md`, frontmatter schema
(`status`/`created`/`slug`) and the status lifecycle owned by `/bb:delegate`. Skills
reference that file instead of restating the contract.

## Commits

- No AI attribution in commits, PRs, or code comments
- Conventional commit style: `<type>(<scope>): <description>`
- Scope is the skill name (`spec`, `maintain-repo`, …), `hooks` for the hook
  layer, or `repo` for repo-wide changes
