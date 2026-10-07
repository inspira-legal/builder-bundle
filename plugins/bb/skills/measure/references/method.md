# The method: inventory, query, read

Every mode runs on these three steps. The mode's own reference adds what that kind of question
needs on top of them.

## The inventory comes first

Every analysis starts with the inventory of what fires: each event the question needs, with its
first and last day and how many people fired it. The `data` document carries the company's
inventory query; when it does not, the shape is this, with the document's filters in place of the
comment:

```sql
SELECT event_name,
       MIN(DATE(event_time)) AS first_day,
       MAX(DATE(event_time)) AS last_day,
       COUNT(DISTINCT person_id) AS people
FROM `EVENTS_TABLE`
WHERE event_time >= TIMESTAMP('START')
  -- the filters of the data document
  AND event_name LIKE 'PREFIX%'
GROUP BY 1 ORDER BY 1
```

A declared event is not a fired event, and the real start of a feature often differs from the date
in its documents. Read the inventory before building any funnel, and answer three questions:

1. **Do the events the question needs fire?** An event that never fired is a caveat, never a zero.
2. **Since when?** A feature behind a flag starts the day the flag opened to customers, not the
   day the code shipped. `measure-a-feature.md` has the cut that finds that day.
3. **Which properties actually arrive?** A property born in the middle of the window only counts
   from its deploy on.

## The query discipline

- **One file per query**, numbered (`NN-name.sql`), with a comment on top saying the question, the
  window and the filters. **Always save the output beside it**
  (`... --run | tee NN-name.out`): the audit reads the outputs, not the chat. When the delivery is
  only in chat, the folder lives in the session's scratch space; when the analysis is saved later,
  the whole folder goes with it.
- **The filters of the `data` document go in every query of professional usage**, which is the
  default. They come out only when the question is about the very audience they remove. An
  audience the official metric excludes can still be a segment of its own in a feature that
  audience uses.
- **The plan split and the time zone** also come from the `data` document.
- **Save reads.** The cost of each table is in the `data` document, and a date filter does not
  make an unpartitioned view cheaper. Put several cuts in one query with `UNION ALL` over the same
  `WITH`: the columns are billed once.
- **Counting:** a person is `COUNT(DISTINCT <person id>)`, and an object is `COUNT(DISTINCT` its
  id. People do not add up across features, nor across the steps of a funnel.

## Reading as product

- **Answer each question of the request in one sentence, with its number, before any table.**
- **Make the denominator explicit:** "X of Y (Z%)", where Y is who could have done it. For a
  feature behind a flag, Y is who has the flag and used the surface the feature lives in, never
  the whole base.
- **Separate what the data shows from what is inference**, and say which is which. A system event
  says something happened, not why.
- **Check what the event really counts.** A mode the person never sees, folded into an event that
  means "the person saw it", inflates the number. Read the event's modes and values before
  counting them as one.
- **Every number carries the window it came from.** A detail from a query with another window
  says that window beside it.
- **Compare** with the baseline (`.bb/<slug>/measure.md`, or the spec's `Baseline:`) or with the
  week before, when there is one.
- **The measurement gaps go into the answer**: an entry point that never sends, an id that belongs
  to the conversation and not to the object, an event that mixes giving up with failing. Each
  distorts the next reading if nobody knows about it, so number them for whoever keeps the events.
- **Close with "What changes for the product"**, in two to four plain sentences, and the caveats.

## When the code disagrees with the question

The question often carries a premise about how the product behaves. Check it in the code, on the
default branch's remote tip, before measuring around it. When the code contradicts the premise,
say so plainly and treat the premise as one more hypothesis: measuring half a behavior and calling
it whole is the error this step exists to catch.
