---
name: implement
description: Implement a validated `.ofc/tasks/<slug>/shape.md` brief in the working tree — build the slices, run the local gate, commit per slice, then offer to ship (or auto-chain when shipping is already authorized). The trio's executor — supervised at your desk, and the build step of an unattended routine under the `OFC_UNATTENDED` frame. Use when the user says "implement the brief", "build the shaped tasks", "build it", "implement this", or right after /ofc:shape. Do NOT use to shape an idea first (use /ofc:shape) or to open/green a PR on its own (use /ofc:ship).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.1.0
---

# Implement

Build the validated, shaped work in the working tree — taking `.ofc/tasks/<slug>/shape.md` from a brief to code that's ready to ship. The trio's executor: at your desk it builds the backlog then offers to ship; under the unattended frame (`OFC_UNATTENDED`) it builds the whole backlog and chains straight to a draft PR. To schedule that unattended run, see the routine guide (`references/routines.md` at the plugin root).

## Prerequisites

A validated `.ofc/tasks/<slug>/shape.md` (brief + a `## tasks` checklist). If there's no shaped brief for this work, stop and suggest `/ofc:shape` first — implementing without alignment is exactly what shaping prevents.

## Workflow

1. **Load the brief.** Read `.ofc/tasks/<slug>/shape.md` whole: what/why, the decisions made, the **reuse** notes, the `## design` block (components, data model, data flow — Large work; follow it), the `## behavior` map (happy path + edge→outcome — **build to this; it's the acceptance contract**), what's **out of scope** (a hard line — do not build it), and the `## tasks` slices.
2. **Reuse first.** Before writing anything, confirm the code/patterns named in the brief's reuse notes still exist, and prefer extending them over reinventing. If they've moved or changed, flag it and adjust rather than guessing.
3. **Implement every unchecked slice, in order.** Each slice is a thin end-to-end cut — build it as one. Stay inside scope; the out-of-scope bucket is a boundary, not a suggestion.
4. **Keep the gate green as you go.** Detect the project's checks in this order of authority: CLAUDE.md / docs → CI workflow files → `package.json` / `justfile` / `Makefile` / `pyproject.toml`. Run lint/format/typecheck/tests; fix before moving on. Run what CI runs, not a subset. **Unattended:** retry a failing gate at most **3 times and only on a known-flake signature** (a transient the same command clears); a real, unrecoverable failure stops the build — commit what's green, then chain to `/ofc:ship` to open the draft PR with the blocker written into its description, and exit (no further slices).
5. **Commit per slice, check the box.** Commit in logical units (conventional style; no AI attribution), and tick that slice's `- [ ]` → `- [x]` in the `## tasks` section as it lands — so progress is visible and a partial run is resumable. **Unattended:** put the commits on a `claude/<slug>` branch (create it before the first commit; the routine clones on the default branch) so ship opens the draft PR from it.
6. **Safety valve.** If a slice reveals the idea was underspecified — surprises pile up, scope wants to grow, a decision the brief skipped now bites — STOP and hand back to `/ofc:shape` to re-shape. Don't improvise past the brief; that's the signal alignment was incomplete.
7. **Hand off — offer to ship, or chain.** Summarize what landed against the task list (done / skipped / blocked). Then branch on how the run went:
   - **Clean and supervised** (every slice landed, gate green): if shipping was already authorized this session — the user picked "Build and ship" at the shape gate — skip the question and invoke `/ofc:ship` directly. Otherwise offer it via `AskUserQuestion`: lead **"Ship it now"** (invoke `/ofc:ship`) against **"Stop here"** (print the command and stop). Either path, ship loads this same brief as the intent.
   - **Clean and unattended:** no question to ask — invoke `/ofc:ship` directly. It opens the draft PR on the `claude/<slug>` branch and watches it to resolution.
   - **Not clean** (a slice blocked, or the safety valve fired): report done/skipped/blocked and point back to `/ofc:shape` to re-shape — **don't** offer ship. A partial build shouldn't become a PR that claims to satisfy the brief.
