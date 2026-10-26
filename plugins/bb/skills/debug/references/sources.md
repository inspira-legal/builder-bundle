# Step 4: the sources, cheapest first

Each hypothesis is answered by the cheapest source that can answer it. Go down the list only
when the source above can't. Every read below goes through the guard, written `GUARD` here: in
the session it is `python3 scripts/gcloud_read.py`, and in a brief the full path. The project,
service, queue and field names are an invented system's; the real ones come from the map.

## 1. The app log and the request log, inside retention

The app log says what the code did, and the request log says what the caller got. Join them by
trace: the request log's 5xx gives the trace, and the app log for that trace gives the stage that
failed.

```bash
GUARD logs --project pebble-prod-1 --resource cloud_run_revision --service notes-api \
  --since 2026-03-02T10:00:00Z --until 2026-03-02T11:00:00Z --limit 100 \
  --filter 'httpRequest.status>=500'
GUARD logs --project pebble-prod-1 --resource cloud_run_revision --service notes-api \
  --since 2026-03-02T10:00:00Z --until 2026-03-02T11:00:00Z --limit 100 \
  --filter 'trace:"4bf92f3577b34da6a3ce929d0e0e4736"'
```

A queue's dispatch log lives under its own resource type (`cloud_tasks_queue`), and a scheduler
job's under its own (`cloud_scheduler_job`): read the one the map names. A field the defaults
don't print is asked for with `--field jsonPayload.stage`. A result as long as its limit is
truncated: narrow the window, never read it as a total.

## 2. The instance, before the code

Memory, restarts and revisions explain many errors the code doesn't. Check them before reading
the code for a bug.

```bash
GUARD gcloud run services describe notes-api --project pebble-prod-1 --region REGION
GUARD gcloud run revisions list --service notes-api --project pebble-prod-1 --region REGION
GUARD logs --project pebble-prod-1 --resource cloud_run_revision --service notes-api \
  --since ... --until ... --limit 50 --filter 'textPayload:"Memory limit"'
GUARD metrics --project pebble-prod-1 --service notes-api \
  --metric run.googleapis.com/container/memory/utilizations --aligner ALIGN_PERCENTILE_99 \
  --since 2026-03-02T10:00:00Z --until 2026-03-02T11:00:00Z --limit 200
```

The service description prints the image, the limits, the scaling, the concurrency and the
timeout, and the environment variable names only, with whether each is a secret reference. A
revision that changed right before the symptom points at the deploy.

A crash for memory is proved by the series, not by the log line alone: `metrics` prints one row
per revision with its points in time order, so it shows how close to the limit the instance ran
before the symptom and whether a fix brought it down. Memory and latency are distributions and
take a percentile aligner; a count or a rate takes `ALIGN_SUM` or `ALIGN_RATE`. `--align` is the
step in seconds (60 by default), and the limit counts points across every series.

## 3. The deployed image against the repository

The revision's image names the build. Find the commit it came from (an image tag, a build's
source, or the deploy history), and read the code at that commit, not at the local checkout:

```bash
GUARD gcloud artifacts docker images list REPOSITORY --project pebble-prod-1
git log --oneline DEPLOYED_SHA..origin/main -- PATH
```

What changed between the deployed commit and the default branch is a lead in both directions:
a bug already fixed but not deployed, or a fix assumed deployed that isn't.

## 4. The queue's configuration against the code and the infrastructure

```bash
GUARD gcloud tasks queues describe sync --project pebble-prod-1 --location REGION
GUARD gcloud scheduler jobs describe nightly --project pebble-prod-1 --location REGION
```

Compare the dispatch deadline, the retry limits and the rate against what the handler needs and
against the infrastructure files in the repository. A queue changed by hand drifts from those
files. A queued task and a scheduler job print through a field list that leaves their headers
and bodies out.

## 5. The warehouse sink, past the retention window

When the symptom is older than the log retention, the long-term log sink in the warehouse holds
it. Write the query to a file in `RUN_DIR`, dry run it, then run it:

```bash
GUARD warehouse RUN_DIR/01-failures-by-stage.sql --project pebble-prod-1
GUARD warehouse RUN_DIR/01-failures-by-stage.sql --project pebble-prod-1 --run
```

Only an aggregate (counts by stage, by hour, by error type) or rows filtered by one business id,
passed as `--id` and written `WHERE <id field> = @id`. A query that would list rows not filtered
by one id is refused; rewrite it as an aggregate. A refusal for cost is answered by narrowing the
query (fewer columns, a smaller date range), never by raising the ceiling. Never list customer
messages.

## 6. A development database, last

Only in a project the `environments` document lists as development; the guard reads that list
itself, and a project outside it is refused. The connection settings come from the `access`
document: the PG variables for a SQL database, `BB_DEBUG_MONGO_URI` for a document database, set
by the person in their own shell.

```bash
GUARD sql RUN_DIR/02-note-state.sql --project pebble-dev-1 --limit 20
GUARD docdb --project pebble-dev-1 --database pebble --collection notes --op count \
  --filter '{"status": "failed"}'
```

When the anchor points at a database in a non-development project, the guard refuses, and the
answer comes from the logs, the warehouse sink or the product's own API.

## Permission denied

A read denied in production is a refusal, not an empty answer. Read what the person can read
instead: the infrastructure files in the repository for configuration, the request logs for
behavior. The report says which source replaced which.
