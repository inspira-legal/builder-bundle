---
status: in-progress
created: 2026-10-26
slug: debug
---

# /bb:debug: investigate an error in a running environment, read only

Debugging a running service is the same work every time, and every session rebuilds it from
memory. Someone opens the cloud CLI, guesses the project, guesses the service, reads a log with no
window, and loses an hour on a filter that returned nothing because the project was the wrong one.
The method that worked across those sessions is consistent: start from an anchor, bound every
read, check the instance before the code, join the request log to the app log, and prove a cause
before calling it one. `/bb:debug` carries that method, so any builder runs it the same way, in a
development or a production environment, without writing anything to either.

The skill's main tool is the cloud CLI. The company's map (which projects exist, which services
and queues each feature uses, which log messages mark each stage, how to reach each database) is
the company's content, so it lives in the company's documentation base and the skill reads it at
run time, the way `/bb:measure` reads its definitions. What the skill learns goes back there: a
cause that got fixed becomes a postmortem, and every later investigation reads the postmortems
first, so the base grows into the company's record of what broke and why.

Success is a builder who names a symptom and gets back a report with a confirmed root cause, the
evidence behind it and what was ruled out, with no write made to any environment and no secret or
customer record left in the conversation or on disk.

## Where the company's map lives

The documentation base holds three roles for this skill, each found by its tag, under the
convention `plugins/bb/references/company-definitions.md` owns:

| tag                     | what the document holds                                                  | read when                    |
| ----------------------- | ------------------------------------------------------------------------ | ---------------------------- |
| `bb-debug:environments` | the projects and which are development, regions, services, log retention | every run                    |
| `bb-debug:access`       | the roles a person needs, how to log in, how to reach each database      | a credential or access fails |
| `bb-debug:service`      | one system or feature: its queues, log messages, ids, known failures     | the system the anchor points |

A role holds as many documents as it needs, and each stays small enough to be found by the base's
search, so one system becomes one document per feature. The `environments` document is also what
tells the guard which projects are development projects.

The postmortems are the fourth source, found by kind rather than by tag: a semantic search for the
symptom over every document of kind `postmortem`, the ones people wrote and the ones this skill
published.

## The method

The skill runs in one order, and each step has its own reference:

1. **The anchor.** What the person has: a business id, a trace, a time window, or only the
   symptom, and the environment. With no anchor, find one before any hypothesis: a 5xx in the
   request log, an error message in a bounded window, the last deploy before the symptom.
2. **The map.** The `environments` document, the `service` documents of the system the anchor
   points at, and the postmortems closest to the symptom.
3. **The hypotheses.** Listed from the anchor, the map and the postmortems. With two or more, one
   investigator agent per hypothesis runs in parallel; with one, the skill runs it itself.
4. **The sources**, cheapest first: the app log and the request log in the retention window, the
   instance signals (memory, restarts, revisions), the deployed image against the repository, the
   queue's configuration against the code and the infrastructure files, the long-term log sink in
   the warehouse past the retention window, and a development database last.
5. **Reproduce**, only when the cause needs proof: the production image locally with the cloud
   limits and a local or development configuration, a test that fails before the fix, a
   comparison against the default branch.
6. **The report**, then the gate.
7. **The postmortem**, once the fix is applied.

## The investigators

An investigator is a read-only agent on the smallest model, Haiku, and it explores one hypothesis
and runs that hypothesis's reads through the guard. The main session does the thinking around it:
it writes each investigator a brief scoped to its hypothesis alone (the anchor, the project, the
service, the window, the excerpt of the map it needs, and what would confirm or refute it), and it
reviews each verdict against the evidence the investigator returned before the report uses it. A
verdict whose evidence doesn't hold up is rerun or checked by the main session itself.

## The guard

Every call to the cloud CLI, the warehouse and a database goes through one script,
`skills/debug/scripts/gcloud_read.py`, standard library only. The skill never calls those tools
directly, and the investigators don't either.

- **Reads only.** The script runs read verbs. A write verb is refused, and the script prints the
  command for the person to run, with what it changes and whether it can be undone.
- **Bounded.** A log read needs a project, a resource, a time window and a row limit. A result as
  long as its limit is reported as truncated.
- **Rows projected.** A log read, a warehouse row and a development database row print named
  fields (time, severity, service, message, the business and trace ids, stage, error type), never
  a whole entry or document. A field beyond those is asked for by name.
- **Checked output.** Everything the guard prints passes a personal data check first: a value
  shaped like an email, a personal document number or a long free text is redacted, and the
  output says how many were.
- **Masked.** A service description never prints environment values or headers: names, and
  whether each is a secret reference. A scheduler job and a queued task are printed through a
  field list that leaves their headers out.
- **Databases in development only.** The script opens a database path only to a project the
  `environments` document lists as development, and reads that list itself. A project missing
  from the list, or a documentation base it can't reach, closes every database path. A SQL session
  opens read only. A document database runs only the queries the script builds: find, count, and
  an aggregation with no stage that writes.
- **The warehouse past retention.** A dry run first, a byte ceiling on the real run, and only
  aggregate counts or rows filtered by one business id.
- **Temporary files.** Each run saves into its own temporary directory, named by the run, and
  deletes it when the run closes, together with any image the reproduce phase pulled. A directory
  an interrupted run left behind is deleted at a later start once it is a day old.

## The report

The report goes to chat: the root cause and how sure it is, the evidence (each query, run through
the guard, and what it returned), the postmortems it drew on, what was ruled out, and what is
still open. Only aggregates and ids reach it, never a customer record. When a name in a `service`
document didn't match what the skill found, the report lists the correction with the corrected
text ready.

## The postmortem

"Fix now" is the gate's option for a cause small enough to fix in the same session: the session
changes the code on the current branch with a test that fails before the fix and passes after, and
the fix is applied once it is committed. Then the skill writes the postmortem: the symptom, the
cause, the evidence (the queries and the counts), the fix with its commit, and the services
affected. Its approval is a confirmation inside the "fix now" path, not a second gate, and the run
ends after it. A fix that is abandoned, or whose test doesn't pass, gets no postmortem; the report
stands.

A fix that goes through `/bb:spec` instead gets its postmortem with the fix marked pending. A later
`/bb:debug` run that finds it by search, once the person says the fix landed and names its commit
or PR, offers to complete it.

A postmortem carries technical ids only (trace, task, revision, commit). It never carries a
workspace, user or customer id, a name, or a document's content, and its text passes the same
personal data check as the report before it is shown. The skill shows the whole text and publishes
it as a document of kind `postmortem`, tagged with the system, only after the person approves that
text.

## Decisions

- The skill is `/bb:debug`, in the Revisar trilha.
- Nothing from any one company enters bb: no project, service, queue, log message or document key.
  Examples and tests use an invented product.
- The company's map is read at run time from the documentation base by role tag, and only the
  roles the run needs are read. The postmortems are read by a semantic search on the symptom.
- Without the documentation base, or without a document for the system, the skill says so in one
  line and investigates from the repository's code. Every database path stays closed.
- The skill never runs a write in any environment. It prints the command for the person.
- The skill never opens a database in a project the `environments` document doesn't list as
  development.
- Past the log retention window, the skill reads the warehouse sink with aggregates or rows
  filtered by one business id, and never lists customer messages.
- Every investigation starts from an anchor, and from a named environment.
- With two or more hypotheses the investigators run in parallel, one per hypothesis, on Haiku. The
  main session briefs each one and reviews each verdict before the report uses it.
- Reproducing locally is an optional phase, run when the cause needs proof, and never with a
  production configuration or credential.
- The skill writes to the documentation base only text the person approved, shown whole: a new
  postmortem, the completion of one it published, or a correction to a `service` document.
- A cause becomes a postmortem once its fix is applied, and every investigation reads the closest
  postmortems before listing hypotheses.
- Anything a run saves is deleted when the run closes.
- The build writes the company's documents as local drafts, outside the repository, from the
  research already done. The person reviews and publishes them. The drafts absorb what the private
  log skill for the document pipeline still gets right, corrected against the code, and that
  skill is retired by the person once the drafts are published.
- The first drafts cover two backends: the AI platform service (chat, agent, document collection,
  table analysis) and the main product API.

## Behavior

Happy path:

1. A person runs `/bb:debug` with a symptom, the environment, and an id or a time window when they
   have one.
2. The skill checks the cloud login through the guard, and reads the `environments` document.
3. It finds the anchor: with an id, the logs for that id in the right project and service, in a
   bounded window; without one, the first error in the request log or app log of that window.
4. It reads the `service` documents for the system the anchor points at and the closest
   postmortems, and lists the hypotheses.
5. With two or more hypotheses, it briefs one investigator per hypothesis, and each returns a
   verdict with its evidence. With one, it runs it itself.
6. It reviews each verdict against its evidence, confronts them, and runs the reproduce phase when
   the cause needs proof.
7. It writes the report, deletes the run's temporary directory and closes at the gate.
8. When the person picks "fix now", the session fixes the code with a test that failed before,
   and once the fix is committed the skill shows the postmortem and publishes it on approval.

| WHEN                                                              | THEN                                                                       |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------- |
| the person names no environment                                   | the skill asks which one, from the `environments` document, before a read  |
| the id is found in no project of that environment                 | the report says so and lists every project and service checked             |
| the id shows up in more than one project or service               | the skill follows each one and keeps them apart in the report              |
| the cloud login expired                                           | the skill stops and asks the person to log in; it can't log in for them    |
| a read targets a project that answers empty or denied             | the guard says so plainly, never as "no traffic", and names the project    |
| a log read has no window or no limit                              | the guard refuses before anything runs                                     |
| a result is exactly as long as its limit                          | the report calls it truncated, and the skill narrows the window            |
| a step needs a write (rerun a task, fire a job, change a flag)    | the guard refuses and prints the command, what it changes, and its undo    |
| the anchor points at a database in a non-development project      | the guard refuses; the skill uses logs, the warehouse sink or the API      |
| the documentation base is unreachable                             | one line says so, the code is the map, and every database path stays shut  |
| no `service` document exists for the system                       | one line says so, and the skill reads the system from the repository       |
| no postmortem is close to the symptom                             | the skill goes on, and the report says none was found                      |
| a log message or queue from a document returns nothing on traffic | the skill checks the default branch, goes on, and the report lists the fix |
| the symptom is older than the log retention window                | the skill reads the warehouse sink: dry run, ceiling, aggregate or one id  |
| a warehouse query would list rows not filtered by one id          | the guard refuses and the skill rewrites it as an aggregate                |
| a document database query holds a stage that writes               | the guard refuses it                                                       |
| a service description would print environment values or headers   | the guard prints names only, and whether each is a secret reference        |
| a permission is denied in production                              | the skill reads the infrastructure files or request logs, and says which   |
| an investigator's evidence doesn't support its verdict            | the main session reruns that hypothesis or checks it itself                |
| two verdicts contradict each other                                | the report shows both with their evidence and calls the cause unconfirmed  |
| the reproduce phase would load a production configuration         | the skill refuses and runs with a local or development configuration       |
| a postmortem draft holds a business id, a name or document text   | the check flags it and the text is fixed before the person sees it         |
| the person rejects the postmortem text                            | nothing is published, and the draft is shown for the person to edit        |
| the fix goes through `/bb:spec` instead of "fix now"              | the postmortem is published on approval with the fix marked pending        |
| the "fix now" fix is abandoned or its test doesn't pass           | no postmortem is written, and the report stands as the record              |
| the run is interrupted                                            | its directory is deleted at a later start once it is a day old             |
| no anchor exists and no error shows in the window                 | the report says no evidence was found, and what was checked                |

## Metric

- Metric: `/bb:debug` investigations whose report closed on a confirmed root cause, counted by
  hand over the dogfood window.
- Baseline: skipped: not-instrumented
- Target: 5 of the first 8 investigations, within 6 weeks of this landing (Enzo Figueiredo's
  estimate)
- Events: none; internal tooling, and the report itself is the reading.

## Attention points

- An agent with `Bash` can call the cloud CLI directly and skip the guard; the agent's `tools:`
  list narrows the surface without closing it.
- `company-definitions.md` says a document can't widen what a skill may do, and the `environments`
  document does: a production project listed there as development opens its database.
- If the development list reaches the guard as an argument, the caller can widen it; the fail
  closed rule only holds when the guard reads the document itself.
- The masking relies on the cloud CLI's field paths and default views, which a CLI update can
  change; whether a queued task's default view omits headers is not verified.
- The document database query filter and the warehouse "one id or aggregate" check are nets, not
  guarantees: free SQL and aggregation stages have more shapes than one rule catches.
- `/bb:measure`'s `db_read.py` already guards warehouse reads; a second guard for the same
  warehouse can drift from it.
- The personal data check on the report and the postmortem is a net: an id shaped like a business
  id but named otherwise passes it.
- A Haiku investigator can report a verdict its own evidence doesn't support; only the main
  session's review catches it.
- The guard's tests only protect the read-only promise if CI runs them; `validate.yml` runs
  `/bb:measure`'s tests by name.
- The research behind the drafts names real projects, services and queues; any example, test or
  fixture copied from it into the plugin leaks them into a public repository.
- The drafts are written from session digests and a dump of repository variables, which held
  credentials before redaction; the `access` draft is where one would land, and a published draft
  reaches the whole company.
- The reproduce phase pulls a production image, and its layers can carry configuration.
- Long log and warehouse reads pass the tool's 120 s timeout and need to run in the background.
- The documentation base CLI's JSON shape is owned outside this repo, and the installed CLI is
  behind the published one.
- A document above about 6000 characters is only partly found by the base's search, and a
  published postmortem enters the base's conflict check for every new task.
- A table cell above 100 characters breaks `fmt:check`, and the method's tables carry long cells.

## Tasks

### Foundation

- [x] **1. The company definitions gain the debug roles**: `plugins/bb/references/company-definitions.md`
      states the three `bb-debug:*` roles, the postmortems read by kind, `/bb:debug` as a reader
      that goes on without them, the one exception to "a document can't widen what a skill may
      do" (the `environments` document declares the development projects), and the one write a
      skill makes to the base: text the person approved, shown whole. · verify: reading

### The guard and the agent

- [x] **2. The read-only guard**: `skills/debug/scripts/gcloud_read.py` and its tests, covering
      every rule in "The guard" and the personal data check, with the development list read by
      the script from the documentation base, invented data in every case, and the tests run by
      `validate.yml`. · verify: the test script passes with no network, and CI runs it
- [x] **3. The investigator agent**: `plugins/bb/agents/bb-debug-investigator.md` on Haiku, read
      only by its `tools:`, one hypothesis per brief, every read through the guard, a verdict with
      the evidence that supports it. · verify: `bun run validate`

### The skill and the drafts

- [x] **4. /bb:debug**: the `SKILL.md` as a router over one reference per step of "The method",
      the investigator brief and its review, the report, the closing gate (fix now, `/bb:spec`,
      update a stale `service` document, stop), and the postmortem inside the "fix now" path. ·
      verify: reading
- [ ] **5. The company drafts**: under `~/.cache/bb-debug-research/wave-drafts/` (outside git),
      the `environments`, `access` and `service` drafts in Portuguese, from the research in
      `~/.cache/bb-debug-research/` (`SYNTHESIS.md`, `DECISIONS.md`, `findings/`),
      each under 6000 characters, every name checked against the systems' default branches, and a
      list of the `wave doc new` commands with their tags. · verify: a size check per draft, the
      names it cites found in the code, and a scan of the drafts for credentials comes back empty

### Close

- [ ] **6. What the person installing sees**: the README's Revisar table, the skill count in the
      README, the plugin description and `.claude/CLAUDE.md`, the structure tree with the new
      agent and skill, the version, the `CHANGELOG.md` entry and the handoff journey map. ·
      verify: `bun run validate`, `bun run fmt:check`, and a search of the diff for a real
      company's projects, services and queues comes back empty

## Out of scope

- Publishing the drafts in the documentation base, and retiring the private log skill: the
  person's steps.
- Any database in a production project, and any write in any environment.
- Fixing the development document database's tunnel (firewall and key): infrastructure work.
- Drafts for the front end, the workers and the search service; _revisit_ once the first two
  backends are in use.
- Choosing the main session's model or effort: the person's session setting.
- Backfilling postmortems for incidents investigated before this skill.

## Open

- Task 5 (The company drafts): red, it returned green with no commit to land; the drafts under `~/.cache/bb-debug-research/wave-drafts/` are outside git, so the task is unverified.
