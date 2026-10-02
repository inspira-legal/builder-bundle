---
name: measure
description: Product analysis over the company's own usage data, through a read-only guard. Answers "did the feature hit the target its spec wrote?" from the spec's Metric section, and any usage question about a live product, in four modes (explore an open question, measure a live feature, the official metric of a company or a team, hypotheses and actions after a measurement). Starts with the inventory of what actually fires, reads the number as product, and closes with what changes for the product. Use when the user says "did it hit the target", "measure this feature", "how many people use X", "are people using Y", "what is the retention this week", "pull the numbers", "what are the hypotheses", "what do we do first", or asks anything whose answer is a usage number. Don't use it to read what a person wrote (it refuses and offers the aggregate), to write to the database, for numbers outside the product's events such as revenue, to frame a new problem (use /bb:discover) or to write a spec (use /bb:spec).
license: MIT
metadata:
  author: Matheus Morais - github.com/matheusmorais-ux
  version: 1.0.0
---

# Measure

Answer a usage question with a number that holds up, and say what it means for the product. The
cycle already writes the measure down: every spec carries `## Metric`, with a baseline, a target
and the events its behaviors emit. This skill reads that section after the landing and measures
it, and answers any other usage question the same way.

Everything that belongs to the company (which database, which tables, the filters every query
carries, what counts as usage, the official metrics) is fetched at run time by role tag, the way
the plugin-level `references/company-definitions.md` states. Nothing of it is written here.

## The guard, before any query

The locks live in `scripts/db_read.py`, not in this text. The skill only never works around them.

- **Every query goes through the script**, with `--database` and `--project` taken from the
  company's `data` document. Never another client, never the database's own CLI or API, never a
  token fetched outside the script.
- **A refusal for cost is answered by rewriting the query**, never by raising the ceiling: fewer
  columns, one table, aggregate before joining.
- **Only aggregate numbers.** A person is `COUNT(DISTINCT <person id>)`. When an event carries
  text a person typed, count the occurrences and never read the field.
- **A request about content is refused**: what a person wrote or received in a conversation, a
  search, a document or a cell. Say the skill does not read content, and offer the aggregate that
  answers the same question (how many requests carry an instruction, which action was picked).
- **Each person uses their own credential.** Never a key found in a repository's `.env`. When the
  credential fails, stop, read the `access` document and give the person its renewal step.
- **Sources beyond the database follow the `data` document**, and only the ones it names.

## Step 1: the request and the mode

List the questions the request asks, in the person's own words, because the answer takes them in
that order. Then pick the mode, and when two fit, take the likelier one and name it in one line.

| mode                  | when                                                        | read before                       |
| --------------------- | ----------------------------------------------------------- | --------------------------------- |
| **Explore**           | an open question about behavior                             | `references/method.md`            |
| **Measure a feature** | adoption, entry point, funnel, plan split of a live feature | `references/measure-a-feature.md` |
| **Official metric**   | a company or team metric for a closed week                  | `references/official-metric.md`   |
| **Hypotheses**        | after a measurement: where to evolve, what to do first      | `references/hypotheses.md`        |

**Against the spec.** When the request names a feature with a spec, or asks whether it hit its
target, read `references/against-the-spec.md` too, whatever the mode: the spec's `## Metric` is
the starting point. The hypotheses mode needs a measurement; with none, measure first.

`references/method.md` is the core every mode runs on (the inventory, the query discipline, the
reading as product). Read it on every run.

## Step 2: the context

- **Always:** the `data` and `usage` documents, by tag. Read them whole, every run.
- **Against a target, or a spec with an `okr:` line:** the `metrics` document.
- **A team's official metric:** that team's `team` document.
- **A feature:** its spec, when there is one, and the code where its events are born, on the
  default branch's remote tip, since a local checkout is often behind. The comment beside an
  event says what it measures and what it does not.
- **The baseline:** `.bb/<slug>/measure.md`, the previous measurement of this feature, when it
  exists. The answer compares with it.

## Steps 3 to 5: inventory, query, read

`references/method.md`: the inventory always comes first, one file per query with its output
saved beside it, and every answer leads with its number, its denominator and its window, and
closes with what changes for the product.

## Step 6: deliver by intent

`references/deliver.md`: chat by default, `.bb/<slug>/measure.md` when the result becomes
context, a shareable document when someone else will read it, and an audit by a fresh agent
before anything circulates.

## Handoff gate

A chat answer offers the next level in one line and has no gate. A saved file or a document
closes with one `AskUserQuestion` per the plugin-level `references/handoff-gate.md`:

```
question: "Measurement saved at <where>. Where do we go?"
options:
  - "Map hypotheses (Recommended)". I run the hypotheses mode over this measurement: each front with its data, the actions in order.
  - "Frame the first item". I run /bb:discover on the largest open question the measurement raised.
  - "Spec the fix". I run /bb:spec on the change the measurement points at.
  - "Stop here". The measurement stays at <where>; pick it back up with /bb:measure.
```

Lead with the pick the result supports: a feature measurement that raised questions leads with
the hypotheses mode; a hypotheses run leads with `/bb:discover` for its first large item, or
`/bb:spec` when that item is already a clear change. The hypotheses mode never frames a new
problem itself: that is `/bb:discover`'s.

## Edge cases

| WHEN                                                 | THEN                                                           |
| ---------------------------------------------------- | -------------------------------------------------------------- |
| a tag the request needs returns no document          | stop and name the missing tag                                  |
| the `wave` CLI is missing or logged out              | stop and say the documentation base was the source that failed |
| the credential fails                                 | stop, read the `access` document and give its renewal step     |
| the `data` document names a database with no adapter | the script refuses by name; stop and say so                    |
| the request has no spec                              | measure anyway, in the modes that need no target               |
| the spec's baseline is `skipped`                     | measure the baseline first and say it is the first reading     |
| the week asked for has not closed                    | say the number is partial, or use the last closed week         |
| the request asks for what a person wrote             | refuse and offer the aggregate                                 |
| the premise of the request contradicts the code      | say so plainly, and treat the premise as one more hypothesis   |
| the script prints `showing N of M rows`              | the output is not aggregated enough; aggregate further         |
