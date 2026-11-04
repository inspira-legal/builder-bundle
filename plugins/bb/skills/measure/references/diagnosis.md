# The diagnosis: can this machine measure?

Read this on every run, right after the shell check in `SKILL.md`. A measurement that starts
without the tools fails halfway, often after the person already waited for a query, and the
failure reads as a problem with the data. The diagnosis finds the missing piece first and says
the one step that fixes it.

## Who logs in

The person always logs in themselves, in a terminal. The skill never asks for a token, never
reads one, never copies one and never shows one, and never runs a login command for the person.
The diagnosis only says which command to run. `scripts/diagnose.py` holds to the same rule: the
login check sends the token to `/dev/null` and keeps only whether one came back, and it never
prints the output of `wave doctor` or `gh auth status`, which name the person.

## The two halves

The checks run in this order, because each one needs the one before it.

1. **The documentation base**, before any company document is read:

   ```bash
   python3 scripts/diagnose.py docs
   ```

   It checks that the `wave` CLI is installed and that `wave doctor` passes.

2. **The access**, right after the `data` and `usage` documents are read, because they name what
   to check: the database, the project and the events table, and, when the `usage` document says
   the activation list lives in code, the repository, the file and the branch.

   ```bash
   python3 scripts/diagnose.py access --database DATABASE --project PROJECT --table TABLE \
     [--repo OWNER/REPO --path PATH --ref BRANCH]
   ```

   It checks the database's CLI and its login, then runs a dry run of a one-row query over the
   events table through the guard (`<plugin-root>/scripts/db_read.py`): nothing runs and nothing
   is billed. With `--repo`, it also checks `gh`, its login, read access to the repository and the
   catalog file on the branch.

Each check prints one line, `ok` or `stop`. The first `stop` ends the run with exit 1, and its line
is the step to give the person.

## What each stop says

| WHEN                                                 | THEN the person reads                                                       |
| ---------------------------------------------------- | --------------------------------------------------------------------------- |
| `wave` is not installed                              | install it with `inspira-legal/builder-setup`, whose README has the command |
| `wave doctor` fails                                  | run `wave doctor` in a terminal: it says what failed and how to log in      |
| `gcloud` is not installed                            | install it with Google's official guide, then log in                        |
| the `gcloud` login expired or was never made         | run `gcloud auth login --update-adc` in a terminal                          |
| the account cannot read the events table             | read the `access` document: which permission to ask for, and from whom      |
| the `data` document names a database with no adapter | the guard speaks to one database today; say so and stop                     |
| `gh` is not installed, or not logged in              | install it from cli.github.com, then run `gh auth login`                    |
| the account cannot read the catalog's repository     | ask the repository's owners for read access                                 |
| the catalog file is not on the branch                | say the `usage` document points at a file that is not there                 |

When the stop is on the database, read the `access` document (found by tag, as the plugin-level
`references/company-definitions.md` states) and add what it says: the permission's name and who
grants it. A stop on `wave` cannot read that document, so the step stays the one above.

## The one honest alternative

A stop ends the measurement. Say what stopped it, the step that fixes it, and that the person can
run `/bb:measure` again once it is done. Then offer one alternative, and only one: reviewing what
the person brought (a file, a chart, a number someone sent). That review reads what is on the
page, and every number in its answer carries the mark _not checked_, from the first line to the
last, because no query confirmed it. Never fill a gap with a number from memory, an earlier
session or a guess at what the query would have returned.

## When the diagnosis passes

Say it in one line, with the checks that ran, and go on to the next step. The person does not need
the list of `ok` lines.
