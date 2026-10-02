# Measure a live feature

Read this when the mode is "measure a feature": adoption, entry point, funnel, plan split or
return of something already shipped. It is the order of cuts a real measurement settled on, and
the order matters: each cut depends on the one before it, so the window and the denominator are
right before anything is counted against them.

The queries below are shapes. Table names, column names and filters come from the `data`
document, and the comment `-- the filters of the data document` stands for them. They are written
in the SQL dialect of the guard's first adapter; another database rewrites them in its own.

## 1. The inventory and the properties

The inventory from `method.md`, over the feature's prefix, plus a column of people in the segments
the `data` document flags (a trial, for instance). Right after it, the properties each event
really carries, with the values of the ones that are categories:

```sql
WITH e AS (
  SELECT event_name, SAFE.PARSE_JSON(properties) AS p
  FROM `EVENTS_TABLE`
  WHERE event_time >= TIMESTAMP('START')
    -- the filters of the data document
    AND event_name LIKE 'PREFIX%'
)
SELECT event_name, k AS property, COUNT(*) AS events,
       STRING_AGG(DISTINCT IF(k IN ('origin', 'source', 'action', 'format', 'mode'),
                              JSON_VALUE(p[k]), NULL), ', ' LIMIT 12) AS examples
FROM e, UNNEST(JSON_KEYS(p, 1)) AS k
GROUP BY 1, 2 ORDER BY 1, 2
```

Compare with the event contract in the code. A declared value that never shows up is a
measurement gap, not a zero.

## 2. The real start

When the feature sits behind a flag, count by day how many people carry it, in the column the
`data` document names for flags:

```sql
SELECT DATE(event_time) AS day,
       COUNT(DISTINCT IF('FLAG' IN UNNEST(FLAGS_COLUMN), person_id, NULL)) AS people_with_flag
FROM `EVENTS_TABLE`
WHERE event_time >= TIMESTAMP('START')
  -- the filters of the data document
GROUP BY 1 ORDER BY 1
```

The jump in the count is the opening to customers. What comes before it is a hand-picked list:
show it in the weekly chart and leave it out of the rates. In the measurement this method comes
from, the documents gave one date and the flag opened weeks later.

## 3. The denominator

Who could have used it: has the flag and used the surface the feature lives in. The whole base is
never the denominator of a feature behind a flag. Without a flag, the denominator is who used that
surface in the window, like who opened the page or the area. Say in the answer which denominator
you chose and why.

## 4. The entry point

When the opening event carries an origin, count by entry point three ways: openings, people and
objects. Then take each object's first entry point and see what happened to it. An automatic
opening is an arrival, not neglect, and objects that only ever opened on their own can still be
used.

## 5. What happened to each object

Groups that do not mix, to answer "how do they use it". Cross each object by its outcome (exported
or not, for instance) and by how it was worked (edited by hand, changed by the AI, both, neither).
A split like that shows what no per-person funnel can, such as most exported objects leaving with
no edit at all.

Check what the id stands for. An id that belongs to the conversation, and not to the object, counts
conversations.

## 6. The paths that look like one

A capability can have more than one door. Ask the event contract which doors exist before
concluding that a capability is barely used: one door can carry several times the traffic of
the other, and a reading of "nobody uses it" may only hold for the smaller door.

Check in the code the behavior the question itself assumes. A request can rest on "doing X replaces
Y" when the code only replaces it in one case and refuses in the other, with no event for the
refusal. Without that read, the analysis counts half the problem and calls it whole.

Mind the logic of discovery. When an action only appears after a gesture (a menu that opens on a
selection), who never makes the gesture never sees the action (that is discovery), and who makes
it and picks nothing has seen it (that is preference).

## 7. By plan and by week

- **By plan:** the plans the `data` document lists, and the total. A trial goes apart when the
  feature is part of the trial experience. Old plans appear only when they can reach the surface.
- **By week:** people per week on the main steps, with the incomplete week marked.
- **The return:** of who used it in a week, how many used it in the next one (the person and week
  table joined to itself, shifted 7 days). It says whether the feature turns into a habit.

## 8. Quality and cost

Only a source the `data` document names for quality or cost. Check its window first, with the
first and last day it covers and how many runs it holds: a source that stopped before the
feature shipped measures nothing about it. When the feature is newer, say that quality and cost
stayed out and why, and keep whatever baseline exists.

## 9. The close

One sentence per question of the request, with its number and the window it came from. Then "What
changes for the product", tied to the open decisions of the feature's spec (its `## Open`). Then
the measurement gaps, as a numbered list, so each one can become a ticket for whoever keeps the
events.
