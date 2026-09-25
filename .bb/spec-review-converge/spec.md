---
status: done
created: 2026-09-25
slug: spec-review-converge
---

# The spec review converges: a diff after the first pass, three passes at most

`/bb:spec`'s step 6 runs the two `bb:bb-spec-reviewer` lenses on every pass that reaches
the gate, and each pass reads the whole spec. Nothing in the step ends the loop except
two clean verdicts. On a large spec that point never comes: every finding folded in adds
text, the new text carries new claims about the code, and the grounding lens, capped at 8
rows, fills its 8 again. `interface-t3code` ran 21 passes in 2h20 and closed with 8
grounding findings; `t3code-paridade` ran 18, with the grounding lens clean three passes
in a row before a coherence fold sent it back to 8. `acabamento-t3code`, at 578 lines,
closed clean in 6. The coherence lens takes 1–2 minutes a pass; the grounding lens takes
3–8, with 50–100 tool calls, so the pass waits on it.

This change keeps the rule that a change reaches a lens before the build, and stops paying
for rereading what did not change. After the first pass the grounding lens reads the diff
since the last text it read, the folding stops at three passes, and what is left reaches
the build and the gate by name. The lint warns when a spec is large enough that it should
have been two.

Success: the gate first opens after at most three passes, and says plainly whether the
last one was clean.

## How the passes run

```
pass 1        coherence: whole spec     grounding: whole spec + repo
pass 2, 3     coherence: whole spec     grounding: diff since the text it last read + repo
after pass 3  the findings are routed, not folded, and the gate opens
at the gate   each change the user makes runs one delta pass, routed, then the gate again
```

A pass runs only when the spec differs from the last text the grounding lens read. When
every finding of a pass was rejected on a stated ground, the spec did not change, and
the run goes to the gate. When the grounding lens died on a pass, it never read that
text, so the next pass runs even over an unchanged spec, and hands it every change since
the text it did read. When it has read no text yet, because it died on pass 1, the next
pass gives it the whole spec, the way pass 1 does. When the coherence lens dies, the run
dispatches it alone once more over the same text, with no `next` call and no pass
counted; a second death reaches the gate as a lens that did not run.

The coherence lens keeps reading the whole spec. It opens no files, so it is the cheap
lens, and a contradiction between a changed section and an unchanged one is exactly what
a diff would hide from it.

## The counter and the diff

`skills/spec/scripts/review_pass.py` keeps the pass count and the last text the grounding
lens read, so neither depends on the run's memory surviving a context compaction. It has
two subcommands:

```bash
python3 scripts/review_pass.py next .bb/<slug>/spec.md --state <dir>
python3 scripts/review_pass.py read .bb/<slug>/spec.md --state <dir>
```

- **`next`** runs before a pass and prints one JSON object: `run` (whether a pass runs),
  `pass` (the number it will be) and `diff` (the unified diff against the last text the
  grounding lens read, `null` when it has read none). `run` is true when the grounding
  lens has read nothing yet, or when the spec differs from the text it read; only then
  does `next` count the pass.
- **`read`** runs after the grounding lens returns a verdict, and saves the spec's current
  text as the text it read. A grounding lens that died never calls it.

The state holds, per slug, the count and that one text, so two specs in one session keep
separate counts. `<dir>` is the session's scratchpad directory, so the count belongs to
the run: a later session that reopens the spec starts at pass 1, with a full read. On a
host with no scratchpad, `--state` is left out and the script uses a fixed directory
under `tempfile.gettempdir()`, the way `scripts/normalize_workflow.py` does, so a
compaction cannot lose the path. There `next` treats a slug's state older than 12 hours
as a finished run and starts again at pass 1, so the reset depends on the clock and not on
the run remembering where it began.

The delta prompt gives the grounding lens the diff, the spec's path and the repo root.
Its scope is the claims inside the changed hunks, plus the unchanged claims those hunks
contradict or depend on: a task that names a file a changed decision now cuts, a decision
that relies on a signature a changed task rewrites. Claims the lens already grounded, and
that the diff does not touch, are out.

## What reaches the build after three passes

Pass 3's findings are routed, not folded: nothing in the prose is rewritten after the last
pass. A finding rejected on a stated ground still counts as dealt with, and adds to the
verdict's `rejected`. Each other finding goes to one of three places:

- **`## Open`**, which the gate blocks on, for a load-bearing gap: a grounding finding of
  the three kinds step 6 already promotes (it invalidates a `## Decisions` bullet, it
  names a file a task does not have, it points at something the repo already does), and
  a coherence finding of a missing decision, a behavior with no decided outcome, an
  unmapped row (a happy path step with no task, a task with no behavior), or a
  contradiction. Before pass 3 a coherence finding folds into the draft; routing it into
  `## Open` on pass 3 is a new rule in step 6.
- **The task it names**, for any other grounding finding, as a nested plain bullet under
  that task, indented two spaces so a formatter keeps it a list item, opening with
  `**Left for the build**:`. The task agent reads the whole spec
  before it builds, so the note reaches it; a plain bullet is not a checkbox, so
  `scan_specs.py` does not count it as a task.
- **The gate's leftover list**, for a grounding finding that names no task and for a
  coherence finding of surplus (a repeated fact, prose that recounts the conversation).
  Step 7 prints it after what is still open, marked as not blocking, and the user
  decides there whether any of it becomes a change.

The notes are written after the last pass, so no lens read them, and the verdict says
so. The user can still change the spec at the gate, resolving an `## Open` item or
anything else: each change runs one delta pass like pass 2 and 3, its findings are
routed the same way, and the gate opens again. The gate calls `next` only after a change
the user made, so a gate where the user changes nothing runs no pass, and the first
delta pass at the gate reads the notes pass 3 wrote along with the change.

## The verdict line

The gate renders one line: one part per lens, then the pass count. A lens's part counts
the whole run, not only its last pass, and is built from these pieces, in the words the
gate prints in the user's language:

| the lens over the run                | its part of the line                                  |
| ------------------------------------ | ----------------------------------------------------- |
| its last pass came back clean        | `clean`, plus `delta` for a grounding delta pass      |
| it had findings before its last pass | `3 resolved, 1 rejected` before `clean`               |
| its last pass rejected every finding | `1 rejected, clean`: the spec did not change          |
| its last pass routed findings        | `did not close: 1 in ## Open, 4 in tasks, 2 leftover` |
| it died on a pass                    | `did not run on pass 2`                               |

A count of zero is left out of the part. After the parts, the line says
`closed in 2 passes`; once a pass has run at the gate, `4 passes, 1 at the gate`; and
`notes no lens read` while notes some pass routed are still unread. When
`review_pass.py` failed, the line opens with `review_pass.py failed: full passes`. A
whole line reads `coherence: clean · grounding: 3 resolved, did not close: 1 in ## Open,
4 in tasks · 3 passes, notes no lens read`.

## Decisions

- **Pass 1 is unchanged**: both lenses read the whole spec, dispatched in one message.
- **Passes 2 and 3 split the lenses**: coherence reads the whole spec, grounding reads
  the diff since the last text it read, plus the claims that diff touches.
- **A pass runs when the spec differs from the last text the grounding lens read**, as
  `next` reports in `run`. One stored text answers both "did it change" and "what does
  grounding still owe".
- **Passes 1 and 2 fold, pass 3 routes, then the gate opens.** A run is one session of
  `/bb:spec` over one slug. After pass 3, a pass runs only for a change the user makes at the gate, one delta
  pass per change.
- **After pass 3 the findings are routed, not folded**, to `## Open`, to the task they
  name, or to the gate's leftover list, by the rule in "What reaches the build after
  three passes".
- **Step 6's "Unconditional" paragraph is rewritten, not dropped**: every change still
  reaches a lens before the build, and the one exception is the notes a routed pass
  writes (pass 3, or a pass at the gate), which the verdict names as read by no lens.
- **`review_pass.py` is skill local**, stdlib only, in `skills/spec/scripts/` beside
  `lint_spec.py`, with the subcommands `next` and `read` and the flag `--state`. Only
  `/bb:spec` runs it. The diff is `difflib.unified_diff` with three lines of context.
- **The state lives in the session's scratchpad**; without one, in a fixed directory
  under `tempfile.gettempdir()`, where a slug's state older than 12 hours starts a new
  run.
- **When `review_pass.py` fails**, the passes run full for both lenses, the run keeps the
  count in its own context, and the gate names the failure.
- **The delta prompt carries no "anything else"**: the lens checks the diff and what the
  diff touches. The agent's contract says so, so a caller cannot widen it back.
- **`bb-spec-reviewer.md` learns the delta pass**: its `description` and "What the caller
  gives you" stop promising every lens the spec's full text, and the grounding lens says
  what a delta pass gets and what its scope is. Its closing line says whether it worked a
  full pass or a delta one. The 8 row cap stays.
- **Lint `W005`** fires when a spec passes 800 lines, or 100 rows across the tables under
  its `## Behavior`, and says to split it along its `###` phases into sibling specs. It
  is a warning, so the exit code and the CI stay green.
- **`spec-format.md`'s paragraph after the lint table is rewritten**, the one that opens
  "Whether the document is too long" and says a line ceiling "just rebuilds the form":
  the ceiling `W005` sets measures the review surface, and its advice is to split, never
  to trim prose to fit. `CODE_REVIEW_GUIDE.md`'s code range becomes `W001` to `W005`.
- **`draft-first.md`'s line on step 6** names the delta pass after pass 1 and the three
  passes before the gate, and points at `SKILL.md` step 6 for the rest.
- **Version**: `plugin.json` `3.6.1` → `3.7.0`, `skills/spec/SKILL.md`'s
  `metadata.version` `2.6.0` → `2.7.0`, and a `3.7.0` entry in `CHANGELOG.md`.

## Behavior

Happy path (`/bb:spec`, step 6, a spec that needs two passes):

1. The adversarial pass closes and the lint runs over the draft.
2. `next` reports `run: true`, `pass: 1` and `diff: null`; both lenses read the whole
   spec, in one message.
3. The grounding lens returns, and `read` saves the text it read.
4. The findings fold back into step 3, and the spec changes.
5. `next` reports `run: true`, `pass: 2` and the diff; coherence reads the whole spec,
   grounding reads the diff, in one message.
6. Both come back clean, `read` saves the text, and the gate renders the verdict line
   with the pass count.

| WHEN                                                     | THEN                                                                 |
| -------------------------------------------------------- | -------------------------------------------------------------------- |
| pass 1 comes back clean                                  | the gate, `closed in 1 pass`                                         |
| every finding of a pass is rejected                      | `next` reports `run: false`, no pass is counted, the gate            |
| pass 3 returns findings                                  | routed, not folded; no pass 4; the verdict says it did not close     |
| a pass 3 finding is one the gate blocks on               | it goes into `## Open` and the gate blocks on it                     |
| a pass 3 grounding finding of another kind names a task  | a `**Left for the build**:` bullet under that task                   |
| a pass 3 grounding finding of another kind names no task | the gate's leftover list, not blocking                               |
| a pass 3 coherence finding of surplus                    | the gate's leftover list, not blocking                               |
| the user changes the spec at the gate                    | one delta pass, routed like pass 3, then the gate again              |
| the user changes nothing at the gate                     | no `next` call, no pass, the gate's pick goes on                     |
| the grounding lens dies on a pass                        | no `read`; the next pass runs and hands it every change it missed    |
| the grounding lens dies on pass 1                        | pass 2 gives it the whole spec, since it has read no text            |
| the grounding lens dies on pass 3                        | no pass 4; the gate names it as not run on pass 3                    |
| the coherence lens dies on a pass                        | it runs alone once more, uncounted; dies again, the gate names it    |
| the context compacts mid run                             | `next` reads the count and the text from the state directory         |
| a later session reopens the spec                         | pass 1, a full read; with no scratchpad, within 12 hours, it goes on |
| two specs are reviewed in one session                    | each slug keeps its own count and text                               |
| the host has no scratchpad directory                     | the fixed directory; state older than 12 hours starts at pass 1      |
| `review_pass.py` fails                                   | full passes for both lenses; the gate names the failure              |
| a changed hunk contradicts an unchanged task             | the grounding lens reports it: the task is a claim the diff touches  |
| a delta pass stumbles on a stale claim the diff misses   | out of scope; the closing line may name it, the table does not       |
| the spec passes 800 lines or 100 behavior rows           | `W005` names the measure and the split along `###`; exit code 0      |
| the CI lints the specs in `.bb/` of this repo            | no `W005`: the largest is 304 lines                                  |

## Tasks

### Teach the pass

- [x] **1. The pass counter**: `skills/spec/scripts/review_pass.py`, stdlib only, `next`
      and `read`, `--state`, the count and one text per slug, the 12 hour reset of the
      fixed directory → behaviors 2, 3, 5, 6 and the rejected, nothing changed at the
      gate, the four lens dies, compaction, two specs and no scratchpad rows · dep: —
      · verify: run `next`, `read`, edit, `next` on a copy of a spec and read the JSON
  - **Left for the build**: the "nothing changed at the gate" row is step 6's, which skips the `next` call; the script gets no gate path of its own.
  - **Left for the build**: the coherence lens's rerun is step 6's too, with no `next` call; the script gets no retry path of its own.
- [x] **2. The agent learns the delta pass**: `agents/bb-spec-reviewer.md`, its
      `description` and "What the caller gives you", the delta pass under the grounding
      lens, and the closing line naming the pass kind → behavior 5 and the contradiction
      and stale claim rows · dep: — · verify: reading
- [x] **3. Step 6 and the gate**: `skills/spec/SKILL.md` step 6 (the "Unconditional"
      paragraph rewritten, the script and when to call `read`, the split of lenses on
      passes 2 and 3, the delta prompt it sends the grounding lens, the `run` condition,
      the three passes, the routing of pass 3 findings with coherence's new route to
      `## Open`, one delta pass per change at the gate and `next` only after one, the
      script failing), step 7 (the verdict line from its pieces, the leftover
      list after what is still open), and the `metadata.version` bump → behaviors 1–6 and
      the pass 1, pass 3, the four routing, the two gate change, the four lens dies,
      compaction, reopen, no scratchpad and script fails rows · dep: 1, 2 · verify: reading
  - **Left for the build**: step 6's paragraph on a lens dying (it reads "the survivor's findings still fold into step 3") is rewritten too, for the coherence lens's rerun.

### Warn on size

- [x] **4. The size warning**: `W005` in `lint_spec.py` and its docstring, the row and the
      rewritten paragraph in `references/spec-format.md`, the code range in
      `CODE_REVIEW_GUIDE.md` → the two `W005` rows · dep: — · verify: `lint_spec.py`
      over a generated spec of 801 lines prints `W005` and exits 0, and the Validate's
      spec lint step stays green
  - **Left for the build**: the generated spec needs the frontmatter block and the `## Decisions` and `## Open` sections, or `E001` and `E002` exit 1 before `W005` is the one under test.
- [x] **5. Docs and version**: `references/draft-first.md`'s line on step 6,
      `plugin.json` `3.7.0`, the `CHANGELOG.md` entry → no behavior of its own
      · dep: 1–4 · verify: CI

Suggested PR: `feat(spec): a revisão da spec converge em três passes`.

## Out of scope

- **The grounding lens's model.** It inherits the session's model by the decision in
  `.bb/spec-reviewer/spec.md`; the delta pass cuts its cost without reopening that.
  _revisit_ if a delta pass still takes minutes.
- **A delta coherence lens.** It is the cheap one and the one that sees a changed section
  against the rest.
- **Splitting the specs that are large today** in `inspira-desktop`: `W005` names them
  the next time they are linted, and splitting them is that repo's work.
- **A threshold that blocks.** `W005` stays a warning: a large spec is a judgment the
  user makes at the gate.

## Open

Nothing.
