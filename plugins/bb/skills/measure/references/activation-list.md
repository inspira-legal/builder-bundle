# The activation list: read it, name its version, tell list from behavior

Read this when the question counts active people or activation events: an official metric of
usage, the active people of a feature, a retention. An _activation event_ is an event the company
counts as a person using the product, and the `usage` document says where the list of them lives
(the plugin-level `references/company-definitions.md`, `## The activation rule and the list`).

The list applies to the whole history. A measurement counts every week it shows with the list as
it stands that day, so a list that changed moves weeks already published, with nobody changing
behavior. The three sections below are how an answer stays honest about that: read the list at a
version, name the version, and split any difference into list and behavior.

## Read the list where the `usage` document says

- **A catalog in code.** Read it on the remote tip of the branch the document names, never in a
  local checkout, which is often behind. Take the tip's commit first, then read the file at that
  commit, so the version and the content are the same:

  ```bash
  gh api repos/OWNER/REPO/commits/BRANCH --jq .sha
  gh api "repos/OWNER/REPO/contents/PATH?ref=SHA" --jq .content | base64 -d
  ```

  The version is `OWNER/REPO@SHA` with the first 7 characters of the commit. Write the snapshot
  `catalog.csv` beside the queries, with the header `event,activation,renamed_from`: every event of
  the catalog, not only the activation ones, `yes` where the file marks an activation event, and
  the earlier names of a renamed event, all by the marks the `usage` document describes. Say how
  many events and activation events the snapshot holds; when the document gives a count, compare.

- **A table in the database.** Read it through the guard like any query, and take the version
  from the column the document names.
- **A frozen list.** Only to check a number published before the current list existed. Its version
  is the document's key and the version the documentation base shows for it.

When the list cannot be read where the document says, stop and name the source. Never fall back to
a local copy, an earlier snapshot or a list from memory.

## Put the list in the query

```bash
python3 scripts/catalog_changes.py catalog.csv --in-list
```

prints the activation events quoted for the query's `IN (...)`, with every earlier name of a
renamed event, so a rename counts as one event across the whole history.

When the `data` document says the table the query reads receives only part of the catalog's events,
count the activation events that table cannot see, and say that number in the answer.

## Name the version in every answer

Every number counted with the list carries its version: `list: OWNER/REPO@SHA, 12 activation
events`. A chat answer says it in the line under the number, a saved file in its `catalog:` line
(`deliver.md`).

## Compare with the last saved measurement

The last saved measurement is the newest section of `.bb/<slug>/measure.md`, with its number, its
`catalog:` line and the snapshot saved in its query folder. When there is none, say there is
nothing to compare with, and never stand in for it with a week from memory.

- **Same version:** the whole difference is behavior.
- **Another version:** split the difference in two, with three numbers, so it adds up exactly:
  1. **published**: the previous number, as the saved measurement wrote it;
  2. **recount**: the previous window counted again with today's list;
  3. **today**: today's window with today's list.

  The list moved the number by recount minus published, and behavior moved it by today minus
  recount. Say both, in points and in people.

- **A week already published, counted again with another version:** give the new number beside
  the published one, both versions named. The published number is never rewritten.

## What changed in the catalog

```bash
python3 scripts/catalog_changes.py catalog.csv PREVIOUS_FOLDER/catalog.csv --inventory NN-inventory.out
```

It lists, from the snapshot the previous measurement saved to today's:

- **The events that entered or left the activation list, and those that left the catalog.** These
  move the whole series. For an activation event that left, say how many people its exit took out:
  the active people of the window counted with it and without it, in one query, and the difference.
- **The events new in the catalog, each with its decision.** A reader can check each decision
  against the company's rule.
- **The renames**, counted as one event.
- **The events that fired outside the catalog**, with the inventory: a gap to number for whoever
  keeps the events.

The series carries no date for an event's entry: the list applies to every week alike.
