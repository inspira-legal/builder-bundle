# review-changes skill + script dedup + tidy-pr reframe

## what

Three interlocking changes to the `ofc` plugin, plus the convention amendment that
unblocks them:

1. **New `/ofc:review-changes` skill** — standalone correctness + quality review of
   the branch diff (Pass 1 + Pass 2), **report-only**, ending with a suggested next
   step. The missing door to ship's review engine without landing.
2. **Centralize shared scripts** to `plugins/ofc/scripts/` — `fetch_comments.py`
   (byte-identical in ship + address-comments), `reply_resolve_thread.py`, and a
   unified gather script (the near-clone `gather_branch_context.py` +
   `gather_pr_context.py`). Skills point at them via `${CLAUDE_PLUGIN_ROOT}/scripts/`.
3. **Reframe `address-comments` → `/ofc:tidy-pr`** — lightweight, curated PR hygiene:
   you pick which unresolved threads to handle, it replies + resolves (and can polish
   title/body), no CI watch / no quality pass / no merge. Distinct from ship's full
   automatic finalization.

## why

The review engine (ship's Pass 1 correctness fan-out) had no standalone entry — `tidy`
is quality-only by design, and the only way to get a correctness review was to invoke
ship, which heads toward landing. `review-changes` fills that gap. The script
duplication (`fetch_comments.py` identical across two skills; two near-clone gather
scripts) is silent-drift risk — the same anti-pattern the `quality-checklist`
unification just removed, but for executable code. `address-comments` as-is is a weaker
subset of ship's comment flow; reframing it as `tidy-pr` gives it a real identity (the
lightweight curated mode) and is what justifies keeping it over deleting it.

## decisions

- **No `ofc-` name prefix.** Skills are already namespaced `/ofc:<skill>`, so the
  built-in `/review` does not collide with `/ofc:review-changes`. Prefixing would
  produce `/ofc:ofc-<name>` — redundant. Just use a distinct name.
- **New skill name: `review-changes`** — verb-led (consistent with the repo),
  branch/PR-agnostic, dodges the built-in `review`.
- **`review-changes` is report-only.** It does not edit code. It reports findings
  (`file:line | what | evidence | suggested fix | confidence`) grouped by
  correctness / quality, then **suggests the next step** (clean → `/ofc:ship`; quality
  smells → `/ofc:tidy`; bugs → offer to fix or hand to ship). Mirrors
  `gather-branch-context`'s "offer next steps" ending.
- **Share the review engine as a doc, not a script.** Move
  `ship/references/review-checklist.md` → `plugins/ofc/references/review-checklist.md`
  (plugin root, like `quality-checklist.md`). Both `ship` and `review-changes` point at
  it. The fan-out (one read-only agent per checklist area: logic-edges, async-state,
  contracts-security, quality) is described thinly in each skill body and keyed off the
  shared checklist's areas — no orchestration prose duplicated beyond the one-line
  "fan out one agent per checklist area".
- **`review-changes` reads the diff inline** (`git diff <base>...HEAD` + uncommitted),
  like `tidy` — introduces no new script.
- **Centralize shared scripts + amend the convention.** Move scripts used by 2+ skills
  to `plugins/ofc/scripts/`; amend `.claude/CLAUDE.md` so skill bodies may use
  `${CLAUDE_PLUGIN_ROOT}/scripts/<x>.py` **for shared plugin-root scripts** (skill-owned
  scripts stay relative; the rule still bans `${CLAUDE_PLUGIN_ROOT}` for a skill's own
  scripts). Ship-only `inspect_pr_checks.py` stays in `ship/scripts/`.
- **Unify the two gather scripts** into one (branch/base/diff/uncommitted always;
  PR-template + upstream as optional output), consumed by `ship`,
  `gather-branch-context`, and available to `tidy-pr`.
- **Reframe `address-comments` → `tidy-pr`** (rename dir + frontmatter `name` + all
  cross-refs). Scope: operate on the **existing open PR** for the branch; fetch threads;
  present numbered unresolved threads; **user curates** which to handle; fix/answer +
  reply + resolve via the centralized scripts; optionally polish title/body to
  convention. No CI watch, no quality pass, no merge, no PR creation.

## design

Shared substrate at the plugin root (the established pattern):

```
plugins/ofc/
├── references/
│   ├── quality-checklist.md      # (exists) shared by tidy + ship Pass 2
│   └── review-checklist.md       # (MOVED here) shared by review-changes + ship
└── scripts/                      # (NEW) shared executables, refs via ${CLAUDE_PLUGIN_ROOT}/scripts/
    ├── fetch_comments.py         # shared: ship, tidy-pr
    ├── reply_resolve_thread.py   # shared: ship, tidy-pr
    └── gather_context.py         # unified: ship, gather-branch-context (+ tidy-pr)
```

Skill bodies:

- `review-changes/SKILL.md` — inline `git diff`; fan out per shared `review-checklist.md`;
  report-only; suggest next step. Points at `quality-checklist.md` for Pass 2 criteria.
- `tidy-pr/SKILL.md` (was `address-comments`) — `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py`
  - `reply_resolve_thread.py`; curate → handle → reply/resolve; optional title/body polish.
- `ship/SKILL.md` — point Pass 1/2 at plugin-root `review-checklist.md`; point shared
  script refs at `${CLAUDE_PLUGIN_ROOT}/scripts/`; keep `inspect_pr_checks.py` local.
- `gather-branch-context/SKILL.md` — point at unified `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py`.

Verb/use grouping in README: `review-changes` joins **shape & ship**; `tidy-pr` replaces
`address-comments` in that group.

## behavior

### review-changes (report-only)

Happy path: invoked on a branch → resolve default base → `git diff <base>...HEAD` +
uncommitted → fan out one read-only agent per `review-checklist.md` area (small diff →
inline) → dedupe findings → print grouped report (correctness / quality), **no edits** →
suggest next step from the findings.

| WHEN                                | THEN                                             |
| ----------------------------------- | ------------------------------------------------ |
| diff vs base is empty               | report "no changes to review", stop              |
| no findings                         | report "clean", suggest `/ofc:ship`              |
| only quality smells                 | report them, suggest `/ofc:tidy`                 |
| correctness bugs found              | report them, offer to fix or hand to `/ofc:ship` |
| uncommitted changes present         | include in scope, flag them separately           |
| not a git repo / no base resolvable | report the error, stop                           |

### tidy-pr (curated, lightweight)

Happy path: `gh` authed + open PR for branch → fetch threads → present numbered
unresolved threads with one-line summaries → **user picks** which → for each: apply
fix (code) or compose answer, then reply + resolve → optionally offer title/body polish
→ report what was handled. No CI watch, no quality pass, no merge.

| WHEN                        | THEN                                                             |
| --------------------------- | ---------------------------------------------------------------- |
| no open PR for the branch   | tell user, suggest `/ofc:ship` to create one, stop               |
| `gh` not authenticated      | prompt `gh auth login`, stop                                     |
| no unresolved threads       | report "nothing to address", offer title/body polish             |
| user selects no threads     | do nothing, stop                                                 |
| fix-thread code change made | reply with what changed + commit sha, resolve; push to PR branch |
| answer-thread               | reply, do NOT resolve (reviewer closes)                          |

### scripts / convention

| WHEN                                    | THEN                                                                       |
| --------------------------------------- | -------------------------------------------------------------------------- |
| skill body needs a shared script        | references `${CLAUDE_PLUGIN_ROOT}/scripts/<x>.py` (per amended convention) |
| skill needs its own (non-shared) script | stays relative `scripts/<x>.py` (rule unchanged)                           |
| gather script called without PR context | returns branch/base/diff/uncommitted; PR-template fields empty/omitted     |

## tasks

- [ ] **Amend the script-reference convention** in `.claude/CLAUDE.md` — allow
      `${CLAUDE_PLUGIN_ROOT}/scripts/` in skill bodies for shared plugin-root scripts; keep
      the relative rule for skill-owned scripts. (delivers: scripts/convention behavior)
- [ ] **Centralize shared scripts** → `plugins/ofc/scripts/`: move `fetch_comments.py` +
      `reply_resolve_thread.py`; unify the two gather scripts into `gather_context.py`;
      repoint `ship` + `gather-branch-context`; keep `inspect_pr_checks.py` in ship.
      (delivers: gather-without-PR behavior, dedup)
- [ ] **Move `review-checklist.md`** → `plugins/ofc/references/`; repoint ship's Pass 1/2.
      (delivers: shared review engine)
- [ ] **Create `/ofc:review-changes`** — report-only correctness + quality review,
      inline diff, fan-out per shared checklist, suggest next step. (delivers: all
      review-changes behaviors)
- [ ] **Reframe `address-comments` → `/ofc:tidy-pr`** — rename dir/name/cross-refs;
      curated threads + reply/resolve via centralized scripts; optional title/body polish.
      (delivers: all tidy-pr behaviors)
- [ ] **Docs + release** — README (add `review-changes`, rename `address-comments`→
      `tidy-pr`, refresh descriptions), `.claude/CLAUDE.md` structure tree, bump
      `plugin.json` 1.14.0 → 1.15.0, run `bun run fmt` + `fmt:check` + `validate`.
      (delivers: discoverability, release)

## out of scope

- Deleting `address-comments` (chose reframe over delete).
- `ofc-` name prefixing of any skill (namespace already prevents collision).
- `review-changes` editing code (report-only by decision) — _revisit_ if an
  apply-fixes mode is wanted later.
- Touching `tidy` or the `quality-checklist` unification (already shipped this session).
- A separate `tidy-up-code`/`tidy-up-pr` symmetric family (rejected as false symmetry).

## still open

- None load-bearing. Minor build-time call: exact unified-gather output schema (superset
  of the two current scripts) — decide while implementing.
