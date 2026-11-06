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
2. **Fill each placeholder the document marks**, the way the document says. The list of activation
   events comes from where the `usage` document says it lives, read at a version as
   `activation-list.md` states. Every week the query shows is counted with that one list.
3. **Set the dates** for the week asked, as the document explains.
4. Run it through the guard:

   ```bash
   python3 <plugin-root>/scripts/db_read.py QUERY.sql --database DATABASE --project PROJECT --run
   ```

**To check the computation**, run the week the document gives as its reference and compare with
its reference numbers. When they do not match, the query or the document broke: say that instead
of giving the number.

When the list changed since the last measurement, the answer splits the difference into list and
behavior (`activation-list.md`): a change of list moves the metric without anybody changing
behavior.

## What the answer carries

1. **The week asked has to be closed.** When it has not ended, say the number is partial, or use
   the last closed week.
2. **The metric and the secondary ones the document lists**, in total and by the splits it names,
   compared with the last saved measurement, and the version of the list each was counted with.
3. **What changed, at the feature level.** Cut who counted by feature, and say which feature moved
   the difference.
4. **What changed in the catalog since the last measurement.** Run the week's inventory, save its
   output, and compare today's snapshot with the one the last measurement saved:

   ```bash
   python3 scripts/catalog_changes.py catalog.csv PREVIOUS_FOLDER/catalog.csv --inventory INVENTORY.out
   ```

   It lists the events that entered or left the activation list, those that left the catalog, every
   event new in the catalog with its decision, the renames, and the events that fired outside the
   catalog, each with its people, most fired first. A new event that is not an activation event and
   reaches many people is worth a line: if the company's rule says it should count, the metric is
   low until the catalog changes. The series carries no date for an event's entry, because the list
   applies to every week alike.

5. **Where the team's number and the company's dashboard differ.** When the `data` document names
   the company's dashboard and its number for the same week is not the team's, point at the
   difference of definition the team's document describes (who is left out, which days count), so
   whoever sees both knows why. Give the dashboard's link beside the number.
