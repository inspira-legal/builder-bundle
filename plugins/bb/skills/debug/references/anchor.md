# Step 1: the anchor

Every investigation stands on something real before it guesses: a business id, a trace, a time
window, or a log line, in a named environment. This step gets there with the fewest reads.

## Check the login and open the run

```bash
python3 scripts/gcloud_read.py login
python3 scripts/gcloud_read.py start
```

`login` checks the cloud login and the warehouse credential without printing a token. When it
says the login expired or is missing, stop and ask the person to run `gcloud auth login` (and
`gcloud auth login --update-adc` for the warehouse); the skill can't log in for them. When a
credential or a role fails later in the run, read the `bb-debug:access` document and give the
person its step for that case.

`start` prints the run directory, `RUN_DIR`. Keep it for the whole run.

## Read the environments document

Read every document the `bb-debug:environments` tag returns, whole, as the plugin-level
`references/company-definitions.md` states. It names the projects, which are development, the
regions, the services and the log retention. Name its key and title in the report.

When the `wave` CLI or the tag fails, say so in one line, take the project from the person, and
go on from the repository's code. The guard then keeps every database path closed, because that
document is the only list of development projects.

## Settle the environment

The request names the environment, or the skill asks before any read. Ask with
`AskUserQuestion`, one option per environment the document lists, at most four, each with its
projects in the description; with more than four, offer the four the symptom points at and let
the tool's free text take the rest. Without the document, or with only one environment, ask for
the project id or confirm the one environment in a single question.

The environment decides the projects every read targets. A read never moves to another
environment's project to find more data.

## Find the anchor

| what the person has          | the first read                                                              |
| ---------------------------- | --------------------------------------------------------------------------- |
| a business id                | `logs` for that id in each project and service the system runs in           |
| a trace                      | `logs` with `--filter 'trace:"TRACE"'`, which joins the request and app log |
| a time window                | the first 5xx in the request log, then the app log around it                |
| only the symptom             | the request log's 5xx and the app log's errors in a recent window           |
| nothing shows in that window | the last deploy before the symptom, through `gcloud run revisions list`     |

A read always carries a window and a limit. With no window from the person, start with the last
hour, and widen it a step at a time (six hours, a day, the retention) only while the reads come
back empty. An example in an invented system:

```bash
python3 scripts/gcloud_read.py logs --project pebble-prod-1 --resource cloud_run_revision \
  --service notes-api --since 2026-03-02T10:00:00Z --until 2026-03-02T11:00:00Z --limit 200 \
  --filter 'jsonPayload.note_id="n-81"'
```

The field that holds a business id comes from the `service` document; with none, from the code
that writes the log line. A field outside the guard's defaults is asked for with `--field`.

## When the anchor doesn't settle

| WHEN                                                | THEN                                                              |
| --------------------------------------------------- | ----------------------------------------------------------------- |
| the id is found in no project of that environment   | the report says so and lists every project and service it checked |
| the id shows up in more than one project or service | follow each one, and keep them apart through the report           |
| the symptom is older than the log retention         | go to the warehouse sink, in `references/sources.md`              |
| no anchor exists and no error shows in the window   | the report says no evidence was found, and lists what it checked  |
