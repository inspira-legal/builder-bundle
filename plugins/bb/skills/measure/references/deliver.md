# Deliver by intent

The delivery follows what the request is for, read from its own words.

| intent                 | the signal in the request                                         | the delivery                         |
| ---------------------- | ----------------------------------------------------------------- | ------------------------------------ |
| a quick answer         | a direct question: "how many", "are they using it", "the rate"    | chat, and a one line offer to save   |
| context for later      | "save it", it feeds a spec or a decision, it belongs to a feature | `.bb/<slug>/measure.md`              |
| someone else will read | "to show", "for the team", a meeting, a presentation              | the shareable document, and the file |

When the intent is unclear, answer in chat and offer, in one line, to save it or to build the
document.

## The chat answer

The answer to each question in one sentence with its number, a small table when it helps, and the
caveat. Then one line offering the next level.

## The saved file: `.bb/<slug>/measure.md`

The feature's measurement record, beside its spec. `/bb:measure` is its only writer, under the
folder contract in the plugin-level `references/spec-state.md`. When the feature has no spec
folder, ask where to save, with the folder of the closest spec as the lead option.

It opens with its own frontmatter:

```yaml
---
slug: <slug> # matches the dir name
last_measured: 2026-10-05 # the date of the newest reading below
---
```

Each measurement is a dated section, the newest on top, so the next reading compares with the one
right under it:

```markdown
## 2026-10-05: did board sharing hit its target?

- mode: against the spec, measure a feature
- window: 2026-09-07 to 2026-10-04 (the landing to the last closed week)
- sources: the company documents read, by key and title
- queries: `measure-sql/2026-10-05/`

<the answer, one sentence per question, the tables, what changes for the product, the caveats>
```

The queries and their outputs go to `.bb/<slug>/measure-sql/<date>/`, one `NN-name.sql` beside its
`NN-name.out`. The outputs hold aggregate numbers only, because the guard lets nothing else out.

## The shareable document

Build it with the document tool the session offers, and prefer a claude.ai artifact: people can
share it, edit it, comment on it and see its versions, which is what an analysis that circulates
needs. With another document tool, use that one. With none, the saved file is the document, and
say so in one line.

It has two parts:

1. **The answer.** A title with the theme and the cut, a byline with the date and who asked, an
   opening with the answer and its number, and a pointer to the second part. Then one section per
   question of the request: a chart when there are five values or more over time or across items,
   a table for the rest, a table by plan when there is a plan split. "What changes for the
   product" and "Caveats before it circulates" close the part.
2. **How the analysis was built.** The window, the filters, and a table of each step with the
   event that measures it. The measurement gaps. What stayed out and why. The list of queries,
   with the main one in SQL and the path of the folder.

In the hypotheses mode, the second part of the answer is "Where to evolve", after the caveats
(`hypotheses.md`).

## Audit before it circulates

When the delivery goes to another person, hand the saved file and the `.out` outputs to a fresh
subagent before anything leaves. It recomputes every number from the outputs, checks the window of
each one, and points at every sentence that says more than the data shows. Fix the file and the
document before delivering, and tell the person what the audit changed the meaning of. An audit
that finds nothing is reported in one line too.
