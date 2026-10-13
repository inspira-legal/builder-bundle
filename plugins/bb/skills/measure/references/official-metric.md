# The official metric

Read this when the mode is "official metric": a metric the company or a team publishes on a
schedule, read for a closed week.

## The source is the document

The definition, who is left out, the splits, the official query and the reference numbers live in
one document: the team's `team` document, or the `metrics` document for a company metric. When a
definition changes, the document changes first. Read it whole on every run, never trusting an
earlier reading.

- **The documentation base does not answer:** stop and say it was the source that failed. Never
  fall back to a query saved from an earlier run.
- **The document changed since the last measurement:** say what changed in the definition before
  giving the number. The base keeps the earlier versions; compare with the one the last
  measurement read.

## Running the official query

1. Copy the document's `sql` block into the session's scratch space.
2. **Fill each placeholder the document marks**, the way the document says. A list of events that
   count as usage comes from where the `usage` document says the classification lives: a field in
   each event, a frozen list for an earlier period, or both.
3. **Set the dates** for the week asked, as the document explains.
4. Run it through the guard:

   ```bash
   python3 scripts/db_read.py QUERY.sql --database DATABASE --project PROJECT --run
   ```

**To check the computation**, run the week the document gives as its reference and compare with
its reference numbers. When they do not match, the query or the document broke: say that instead
of giving the number.

When the classification changed between two weeks, say so in the answer: a change of level moves
the metric without anybody changing behavior.

## What the answer carries

1. **The week asked has to be closed.** When it has not ended, say the number is partial, or use
   the last closed week.
2. **The metric and the secondary ones the document lists**, in total and by the splits it names,
   compared with the week before.
3. **What changed, at the feature level.** Cut who counted by feature, and say which feature moved
   the difference.
4. **The events that fired with no level.** Run the week's inventory, save its output, and compare
   it with the classification. When the classification is a list, the script does it:

   ```bash
   python3 scripts/unclassified.py INVENTORY.out CLASSIFIED.txt
   ```

   It lists each event that fired and is not classified, with its number of people, largest first.
   When one reaches many people, say the metric may be low, because a new event that should count
   is not counted. When the level is a field in each event, the same check is a query: the events
   whose field is empty.

5. **The events that started counting in the middle of the series.** Mark the date in the series.
