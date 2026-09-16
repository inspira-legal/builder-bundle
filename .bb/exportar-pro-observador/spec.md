---
status: pending
created: 2026-08-20
slug: exportar-pro-observador
---

# export the records to an observer

The durable records bb writes, the specs in `.bb/<slug>/` with their `status`, the
tasks with their checkboxes, the design briefs with their journey frontmatter, live in
each repo and are read by whoever opens the folder. Nobody watching the work from
outside sees them. The people who watch do it through observers: the roadmap Carol
Grimaldi assembles and presents to leadership, and the Estilário, which is built to
ingest records and answer over them. Work that is not in an observer does not exist at
review time, and today nothing bb writes reaches one.

The direction: bb's side is an **exporter**, not an integration. It renders the
records it already owns into a shape an observer ingests, one way, on demand. The
observer never writes back into `.bb/`, and bb never holds observer state, the same
asymmetry the spec-state contract already uses between members. `/bb:spec` already has
an export mode (`references/export-spec.md`), but it renders one spec for a human
audience into local files; this is the other rendering, the whole folder's status for a
machine audience.

For an MVP, the observer is simulated inside elephant-mem: the export lands in the
memory bundle as facts and open loops, which Estilário-shaped tooling already knows how
to read, and which costs no new infrastructure while the real Estilário settles its
ingestion format.

## Decisions

- One direction only: bb emits, the observer reads. No shared mutable file, no status
  written back into `.bb/`.
- The export is a rendering of the records as they stand, never a second place where
  state lives. `.bb/<slug>/` frontmatter stays the only source.
- The MVP observer is the elephant-mem bundle, standing in for the Estilário until its
  ingestion format is settled.
- Nothing in this spec is built in the PR that lands it. It frames the work; the build
  waits for the open questions below.

## Behavior

The MVP as currently imagined, to be confirmed when this spec is picked up:

| WHEN                                            | THEN                                                                |
| ----------------------------------------------- | ------------------------------------------------------------------- |
| the builder asks to export the records          | the specs under `.bb/` render into the observer's shape             |
| a spec changed status since the last export     | the export carries the transition, not just the current value       |
| the observer is the elephant-mem bundle         | the export lands as facts and open loops in the bundle's own format |
| a record carries nothing new since the last run | it is skipped, and the export says how many were                    |

## Tasks

- [ ] **1. The record shape**: what one exported record carries (slug, status, tasks
      done over total, dates, the one-line intent) → behavior 1 · dep: — · verify:
      reading
- [ ] **2. The elephant-mem writer**: render into the bundle's fact and loop formats
      → behaviors 3, 4 · dep: 1 · verify: run over this repo's own `.bb/`
- [ ] **3. The entry point**: where the ask lives (a skill, a mode of an existing
      skill, or a gate offer) → behavior 1 · dep: 1 · verify: reading
- [ ] **4. The Estilário target**: swap the simulated observer for the real ingestion
      once its format is public → behavior 3 · dep: 2 · verify: a record visible in
      the Estilário

## Out of scope

- Writing into Carol's roadmap directly. The roadmap is a document a person curates;
  the export can feed the person, never edit the document.
- Two-way sync with any issue tracker. The asymmetry is the point.
- Exporting the design briefs' content. Status and shape travel; the research record
  stays in the repo it describes.

## Open

- Which records travel: every spec under `.bb/`, or only the ones whose status moved
  since the last export?
- The entry point: a new skill, a mode of `/bb:ship` after landing, or a standing
  offer at the delegate gate?
- The Estilário's ingestion format, unknown until its beta settles; the elephant-mem
  simulation is the hedge, not the answer.
- Cadence: on demand only, or also offered when `/bb:delegate` closes a spec?
