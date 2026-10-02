# Hypotheses and actions

Read this when the mode is "hypotheses": after a measurement, someone wants to know where to
evolve, what is already planned and what to do first. This mode needs a measurement. When there is
no reading of the feature yet, run "measure a feature" first, or at least the inventory and the
denominator: a hypothesis with no data is an opinion, and this mode exists to tie one to the
other.

## What goes in

- **The measurement:** the saved one (`.bb/<slug>/measure.md`) or this session's, with its
  numbers and the `.out` outputs.
- **The themes:** the concerns of whoever asked, in their words. Each theme becomes a front. A
  front the data raises that nobody brought can go in too; say the suggestion is yours.
- **The planned work:** the feature's spec, its tasks, the specs of neighboring features, and the
  project's tracker when the company has one. With no spec for the feature, the work items come
  from the neighbors and the tracker.

## Step 1: each theme becomes a question with a decision rule

For each theme, write three things:

1. **The question the data answers.** "Few people use the excerpt" becomes "do people who select
   text in the document pick any action?".
2. **The decision rule:** what each answer would mean. "If they never select, the actions never
   show: that is discovery. If they select and pick nothing, they saw the actions: that is
   preference." Check the rule against the real flow of the product before using it; a rule
   written backwards reads fine and only an audit catches it.
3. **Whether it can be measured today.** When the event does not exist, the gap is an action of
   its own, and it enters the final list.

## Step 2: one query that answers several fronts

Build one row per object (the conversation, the task, the document), with one flag per front.
Then aggregate in parts, with `UNION ALL` over the same `WITH`. One read answers every front:

```sql
WITH e AS (           -- the feature's events in the window, with the object's id
  SELECT person_id, event_name, event_time, JSON_VALUE(properties, '$.OBJECT_ID') AS object
  FROM `EVENTS_TABLE`
  WHERE event_time >= TIMESTAMP('START') AND event_time < TIMESTAMP('END')
    -- the filters of the data document
    AND event_name LIKE 'PREFIX%'
),
o AS (               -- one row per object, one flag per front
  SELECT object,
    LOGICAL_OR(event_name = 'SUCCESS_EVENT') AS success,
    LOGICAL_OR(event_name = 'FRONT_1_EVENT') AS front_1,
    LOGICAL_OR(event_name = 'FRONT_2_EVENT') AS front_2
  FROM e WHERE object IS NOT NULL GROUP BY object
)
SELECT 'A' AS part, IF(success, 'with success', 'without success') AS slice, COUNT(*) AS n,
       COUNTIF(front_1) AS front_1, COUNTIF(front_2) AS front_2
FROM o GROUP BY 2
-- UNION ALL one part per question, with the same columns
```

Compare groups instead of reading loose numbers. "Objects never exported are edited as often as
the exported ones (31% against 29%)" says more than "1,240 objects were not exported". Keep the
comparison inside what it shows: similar engagement weakens the idea of abandonment, it does not
prove use.

## Step 3: check in the code what the question assumes

Two checks, always in the code, on the default branch's remote tip:

- **Does the measurement exist?** Find the event in the event contract and where it fires. A
  tracker that only switches on in one surface leaves the other surfaces with no event at all.
- **Is the behavior the person assumes the real one?** Treat the premise of the request as one
  more hypothesis. When the code contradicts it, say so plainly, without softening.

## Step 4: what is already planned

Hand the reading of the planned work to a subagent: specs, tasks and decisions of the feature,
the neighbors and the tracker. For each front it returns the work items with:

- a title in plain words, that someone from outside understands in a meeting;
- one sentence of what the item does;
- its name in the project (slug, task number, tracker key);
- its state: done, in progress, in framing, pending, parked, or to create;
- how much it attacks the front: directly, in part, or lightly.

Ask it for the contradictions between the documents and the data too: the hypothesis that founded
the work, decisions that assumed the opposite, the order of the tasks. Then check at the source the
three or four claims the recommendation will lean on: a task marked done can point at code that
never reached the default branch. Never invent a work item: what does not exist shows as "to
create".

## Step 5: the tension

When the fronts point at a strategic choice the project has not made on purpose, name it. Show two
or three stances in a table, with what the product is in each and what weighs in the plan under
each. Include the stance of whoever asked, when they gave one. Do not decide for the person: show
how each stance reorders the work, and offer to stress the choice with `/bb:challenge`.

## Step 6: hypotheses and solutions, in order

Order by what makes sense to do first, by this rule:

1. What costs little and unlocks other decisions: measure what does not show today, ask the people
   who use it.
2. What improves behavior that already exists, where people already are.
3. The concrete fixes already planned.
4. The larger bets.
5. What has a small measured impact or already has a safety net.

Each item carries a title in plain words (the solution) and four lines: **Hypothesis**,
**Solution**, **Work item** (the plain title and its name in the project, or "to create") and
**Why in this position**. Make dependencies explicit ("depends on item 1: if people never select,
this item rises"). Be decisive. When the proposed order contradicts the plan's current order, say
so.

## Step 7: the shape of the delivery

- **When the measurement already has a document, the second part goes into it**, after its
  caveats, under the title "Where to evolve", with a link at its opening. One document that grows
  keeps everything in one place for whoever receives it.
- **Each front** has a title with its finding, then **The data** (a chart when there are five
  values or more), **The hypothesis**, the table of work items and one sentence of reading.
- **The table of work items** has the columns Item, What it does, In the project and State.
- **After the fronts** comes "The tension", when there is one, and last "Hypotheses and solutions,
  in order".
- **The same content is saved** beside the measurement, as `deliver.md` states.

**Audit before it circulates**, as `deliver.md` states, with three more checks: the work items
against the plan, the claims about code against the default branch, and the logic of each
decision rule. Tell the person what the audit changed the meaning of.

The gate of this mode leads with `/bb:discover` for the first large item, or `/bb:spec` when that
item is already a clear change, as the `SKILL.md` gate states.
