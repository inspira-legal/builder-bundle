"""Every read /bb:debug makes in a running environment, through one guard.

Usage:
    python3 gcloud_read.py start
    python3 gcloud_read.py close RUN_DIR
    python3 gcloud_read.py pull RUN_DIR IMAGE
    python3 gcloud_read.py login
    python3 gcloud_read.py logs --project P --resource TYPE [--service S] --since T --until T
                                --limit N [--filter F] [--field PATH ...]
    python3 gcloud_read.py metrics --project P --metric TYPE [--service S] --since T --until T
                                   --aligner A [--align SECONDS] --limit N [--filter F]
    python3 gcloud_read.py gcloud GROUP... VERB [POSITIONALS] --project P [FLAGS]
    python3 gcloud_read.py warehouse QUERY.sql --project P [--id VALUE] [--run]
    python3 gcloud_read.py sql QUERY.sql --project P --limit N
    python3 gcloud_read.py docdb --project P --database D --collection C --op find|count|aggregate
                                 [--filter JSON] [--pipeline JSON] [--field F ...] [--limit N]
    python3 gcloud_read.py check DRAFT.md [--id VALUE ...]

The skill and its investigators call the cloud CLI, the warehouse and a database only through
this script, so the rules below hold whatever a prompt says:

- Reads only. `gcloud` runs a command whose path is made of known groups and ends on a read
  verb. A write verb is refused, and the command is printed for the person with what it
  changes and whether it can be undone. Anything else is refused as unknown.
- Bounded. `logs` needs a project, a resource type, a window (--since, --until) and a limit. A
  result as long as its limit is reported as truncated. `metrics` reads one metric type the
  same way (a window, an aligner, a limit on points) from the monitoring API, which the cloud CLI
  has no read verb for.
- Rows projected. A log entry, a warehouse row and a database row print named fields, never a
  whole entry or document. A field beyond the defaults is asked for by name, and a field that
  holds an object prints a placeholder instead of the object.
- Checked output. Every value printed passes the personal data check: an email, a personal
  document number (CPF, CNPJ) or a text above LONG_TEXT characters is redacted, and the output
  ends by saying how many were.
- Masked. A service prints its environment variable names and whether each is a secret
  reference, never a value. A scheduler job and a queued task print through a field list that
  leaves headers and bodies out. Any other read prints only the names of a map of variables
  (environmentVariables, substitutions, an instance's metadata items) and drops keys named like a
  header, a token, a password, a secret or a body. Flags that change the identity a read runs
  under (--account, --flags-file and the like) are refused, and so is a second --project.
- Databases in development only. `sql` and `docdb` open only for a project the company's
  `bb-debug:environments` document lists as development, and the script reads that list itself
  with the `wave` CLI: there is no argument that widens it. The list is the lines of a top-level
  fenced block whose info string is `bb-debug-development`, one project id per line. A document without
  the block, a project missing from it, or a documentation base that can't be reached closes
  every database path. `sql` (PostgreSQL, through `psql` and the PG* environment variables)
  opens the session read only and runs one SELECT, lexed as PostgreSQL (`#` is an operator
  there, and a `$` or an E'...' string is refused). `docdb` (MongoDB, through `mongosh` and the
  BB_DEBUG_MONGO_URI environment variable) runs only the find, count or aggregation it builds,
  and refuses a stage that writes or runs code on the server.
- The warehouse past retention. `warehouse` reuses /bb:measure's locks (the plugin's
  scripts/db_read.py: one read statement, the dry run's classification, the byte ceiling on both
  runs, no column that names a person and no email or free text in the rows), then admits only an
  aggregate (every selected field an aggregate, or a GROUP BY, never a window) or rows filtered by
  one business id, passed as --id and written `= @id`, with no OR, NOT or set operation.
- A draft the skill wrote. `check` runs a report or a postmortem draft through the same check,
  plus every business id the run touched (--id), and names the line of each hit, never the
  value. It exits 1 when it finds one, so the text is fixed before the person sees it.
- Temporary files. `start` makes the run's own directory and deletes the ones an interrupted run
  left behind once they are a day old. `pull` records each image it pulls there, and `close`
  deletes the directory with those images.

The development list, the database query filter and the warehouse scope check are nets, not
guarantees; the agent's `tools:` list and the skill's text keep the other calls on this path.

Standard library only.
"""

import csv
import datetime as dt
import importlib.util
import io
import json
import os
import pathlib
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

_db_spec = importlib.util.spec_from_file_location(
    "db_read", pathlib.Path(__file__).resolve().parents[3] / "scripts" / "db_read.py"
)
db = importlib.util.module_from_spec(_db_spec)
_db_spec.loader.exec_module(db)  # one set of warehouse locks for /bb:measure and /bb:debug

Refusal = db.Refusal
fail = db.fail

MAX_LIMIT = 1000  # rows per read
LONG_TEXT = 500  # characters; above it a value reads as free text (a prompt, a document, a note)
TIMEOUT = 900  # seconds per process; a long read runs in the background, not past this
DAY = 86400
RUN_PREFIX = "bb-debug-"
ENV_TAG = "bb-debug:environments"
DEV_BLOCK = "bb-debug-development"
MONGO_URI_ENV = "BB_DEBUG_MONGO_URI"
PROJECT = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]\Z")
NAME = re.compile(r"^[A-Za-z0-9_.-]{1,100}\Z")
FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
LOGIN = (
    "the cloud login expired or is missing; run `gcloud auth login` yourself (the guard can't "
    "log in for you), then run the read again"
)
OBJECT = "[an object: ask for a field inside it by name]"

# ---- the personal data check -------------------------------------------------------------

DOCUMENT = re.compile(
    r"(?<![\w./-])(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})(?![\w/-])"
    r"|(?<!\d)(?:\d{11}|\d{14})(?!\d)"  # bare digits count inside a URL or a key too
)


class Out:
    """Every value printed passes here; `close` says how many were redacted."""

    def __init__(self):
        self.redacted = {}

    def _hit(self, kind, n=1):
        self.redacted[kind] = self.redacted.get(kind, 0) + n

    def text(self, s: str) -> str:
        if len(s) > LONG_TEXT:
            self._hit("long text")
            return "[redacted: long text]"
        s, n = db.EMAIL.subn("[redacted: email]", s)
        if n:
            self._hit("email", n)
        s, n = DOCUMENT.subn("[redacted: document number]", s)
        if n:
            self._hit("document number", n)
        return s

    def value(self, v):
        if isinstance(v, dict):
            return {self.text(str(k)): self.value(x) for k, x in v.items()}
        if isinstance(v, list):
            return [self.value(x) for x in v]
        if isinstance(v, str):
            return self.text(v)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            checked = self.text(str(v))  # a CPF stored as a number is still a CPF
            return checked if checked != str(v) else v
        return v

    def emit(self, v) -> None:
        print(json.dumps(self.value(v), ensure_ascii=False))

    def close(self) -> None:
        total = sum(self.redacted.values())
        detail = ", ".join(f"{n} {kind}" for kind, n in sorted(self.redacted.items()))
        print(f"-- personal data check: {total} value(s) redacted" + (f" ({detail})" if total else ""))


def first_line(err: str) -> str:
    line = next((x.strip() for x in err.splitlines() if x.strip()), "no message")
    return Out().text(line)


# ---- processes ---------------------------------------------------------------------------


def call(argv, env=None):
    """The one place a process starts, so the tests replace it. Returns (code, out, err)."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT, env=env)
    except FileNotFoundError:
        return 127, "", f"{argv[0]} is not installed"
    except subprocess.TimeoutExpired:
        return 124, "", f"{argv[0]} ran past {TIMEOUT} s; narrow the read"
    return p.returncode, p.stdout, p.stderr


def cloud_error(err: str, project: str) -> None:
    low = err.lower()
    if "reauthentication" in low or "gcloud auth login" in low or "unauthenticated" in low:
        fail(LOGIN)
    if "permission_denied" in low or "permission denied" in low or "403" in low:
        fail(
            f"the project {project} denied the read: no permission. This is a refusal, not an "
            "empty answer; the access document says which role to ask for"
        )
    if "not_found" in low or "not found" in low:
        fail(f"not found in the project {project}: {first_line(err)}")
    fail(f"the read failed in the project {project}: {first_line(err)}")


def empty(project: str, what: str) -> None:
    print(
        f"-- the project {project} answered with nothing for {what}. An empty answer doesn't show "
        f"the system was idle: check that {project} is the right project for it"
    )


def check_project(project) -> str:
    if not project or not PROJECT.match(project):
        raise Refusal(f"'{project or ''}' is not a project id; every read names its project")
    return project


def pick(obj, path: str):
    for part in path.split("."):
        if not isinstance(obj, dict) or part not in obj:
            return None
        obj = obj[part]
    return obj


# ---- logs: bounded and projected ---------------------------------------------------------

LOG_FIELDS = {
    "time": ["timestamp"],
    "severity": ["severity"],
    "service": [
        "resource.labels.service_name",
        "resource.labels.job_name",
        "resource.labels.queue_id",
        "resource.labels.function_name",
    ],
    "message": ["textPayload", "jsonPayload.message", "jsonPayload.msg", "jsonPayload.error"],
    "trace": ["trace"],
    "stage": ["jsonPayload.stage"],
    "error_type": ["jsonPayload.error_type", "jsonPayload.errorType", "jsonPayload.exception_type"],
    "method": ["httpRequest.requestMethod"],
    "status": ["httpRequest.status"],
    "latency": ["httpRequest.latency"],
}


def project_entry(entry: dict, extra) -> dict:
    row = {}
    for name, paths in LOG_FIELDS.items():
        value = next((v for v in (pick(entry, p) for p in paths) if v is not None), None)
        if value is not None:
            row[name] = value
    if isinstance(row.get("message"), (dict, list)):
        row["message"] = json.dumps(row["message"], ensure_ascii=False)
    if isinstance(row.get("trace"), str):
        row["trace"] = row["trace"].rsplit("/", 1)[-1]
    for path in extra:
        value = pick(entry, path)
        if isinstance(value, (dict, list)):
            value = OBJECT
        if value is not None:
            row[path] = value
    return row


def parse_time(value: str, flag: str) -> dt.datetime:
    try:
        moment = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise Refusal(f"{flag} '{value}' is not a timestamp like 2026-01-31T14:00:00Z")
    if moment.tzinfo is None:
        raise Refusal(f"{flag} '{value}' has no time zone; end it in Z or an offset")
    return moment.astimezone(dt.timezone.utc)


def check_limit(limit) -> int:
    if limit is None:
        raise Refusal("the read has no limit; pass --limit")
    if not 1 <= limit <= MAX_LIMIT:
        raise Refusal(f"--limit must be between 1 and {MAX_LIMIT}")
    return limit


def logs(a, out: Out) -> None:
    check_project(a.project)
    if not a.resource or not re.match(r"^[a-z_]+\Z", a.resource):
        raise Refusal("a log read needs --resource, the resource type (e.g. cloud_run_revision)")
    if not a.since or not a.until:
        raise Refusal("a log read needs a window: pass --since and --until")
    since, until = parse_time(a.since, "--since"), parse_time(a.until, "--until")
    if until <= since:
        raise Refusal("--until must come after --since")
    check_limit(a.limit)
    if a.service and not re.match(r"^[a-z0-9-]+\Z", a.service):
        raise Refusal(f"'{a.service}' is not a service name")
    for path in a.field:
        if not FIELD.match(path):
            raise Refusal(f"'{path}' is not a field path like jsonPayload.order_id")
    z = "%Y-%m-%dT%H:%M:%SZ"
    parts = [
        f'resource.type="{a.resource}"',
        f'timestamp>="{since.strftime(z)}"',
        f'timestamp<="{until.strftime(z)}"',
    ]
    if a.service:
        parts.append(f'resource.labels.service_name="{a.service}"')
    if a.filter:
        parts.append(f"({a.filter})")
    argv = ["gcloud", "logging", "read", " AND ".join(parts)]
    code, stdout, err = call(argv + [f"--project={a.project}", f"--limit={a.limit}", "--format=json"])
    if code:
        cloud_error(err, a.project)
    entries = json.loads(stdout or "[]")
    if not entries:
        empty(a.project, f"{a.resource} in this window")
    for entry in entries:
        out.emit(project_entry(entry, a.field))
    if len(entries) >= a.limit:
        print(f"-- truncated: {len(entries)} entries, as many as the limit; narrow the window")


# ---- metrics: a time series, aligned, bounded --------------------------------------------

MONITORING = "https://monitoring.googleapis.com/v3/projects/{}/timeSeries?{}"
METRIC = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.googleapis\.com/[a-z0-9_/.]+\Z")
ALIGNERS = (
    "ALIGN_MEAN", "ALIGN_MAX", "ALIGN_MIN", "ALIGN_SUM", "ALIGN_RATE", "ALIGN_DELTA",
    "ALIGN_PERCENTILE_99", "ALIGN_PERCENTILE_95", "ALIGN_PERCENTILE_50",
)


def fetch(url: str, token: str):
    """The one place the guard opens a URL, so the tests replace it. Returns (code, body)."""
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return 0, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    except urllib.error.URLError as error:
        return 1, str(error.reason)


def point_value(value: dict):
    for kind in ("doubleValue", "int64Value", "boolValue"):
        if kind in value:
            return value[kind]
    if "distributionValue" in value:  # the aligner's choice; a percentile aligner never lands here
        return value["distributionValue"].get("mean")
    return None


def metrics(a, out: Out) -> None:
    check_project(a.project)
    if not a.metric or not METRIC.match(a.metric):
        raise Refusal("a metric read needs --metric, the type (e.g. run.googleapis.com/container/memory/utilizations)")
    if not a.since or not a.until:
        raise Refusal("a metric read needs a window: pass --since and --until")
    since, until = parse_time(a.since, "--since"), parse_time(a.until, "--until")
    if until <= since:
        raise Refusal("--until must come after --since")
    if not a.aligner:
        raise Refusal(
            f"a metric read needs --aligner, one of {', '.join(ALIGNERS)}; a distribution "
            "(memory, latency) takes a percentile"
        )
    if not 60 <= a.align <= DAY:
        raise Refusal(f"--align is the step in seconds, between 60 and {DAY}")
    check_limit(a.limit)
    if a.service and not re.match(r"^[a-z0-9-]+\Z", a.service):
        raise Refusal(f"'{a.service}' is not a service name")
    parts = [f'metric.type="{a.metric}"']
    if a.service:
        parts.append(f'resource.labels.service_name="{a.service}"')
    if a.filter:
        parts.append(f"({a.filter})")
    z = "%Y-%m-%dT%H:%M:%SZ"
    query = urllib.parse.urlencode({
        "filter": " AND ".join(parts),
        "interval.startTime": since.strftime(z),
        "interval.endTime": until.strftime(z),
        "aggregation.alignmentPeriod": f"{a.align}s",
        "aggregation.perSeriesAligner": a.aligner,
        "pageSize": a.limit,  # with an aligner the page counts points, across every series
    })
    code, token, err = call(["gcloud", "auth", "print-access-token"])  # the token is never printed
    if code:
        fail(LOGIN)
    code, body = fetch(MONITORING.format(a.project, query), token.strip())
    if code == 401:
        fail(LOGIN)
    if code:
        try:
            body = json.loads(body)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            pass
        cloud_error(f"{code} {body}" if code == 403 else body, a.project)
    data = json.loads(body or "{}")
    series = data.get("timeSeries") or []
    if not series:
        empty(a.project, f"{a.metric} in this window")
    for s in series:
        out.emit({
            "metric": a.metric,
            "labels": {**(pick(s, "resource.labels") or {}), **(pick(s, "metric.labels") or {})},
            "points": [
                [pick(p, "interval.endTime"), point_value(p.get("value") or {})]
                for p in sorted(s.get("points") or [], key=lambda p: pick(p, "interval.endTime") or "")
            ],
        })
    if data.get("nextPageToken"):
        print(f"-- truncated: {a.limit} points, as many as the limit; narrow the window or widen --align")


# ---- gcloud: read verbs only, masked -----------------------------------------------------

READS = {"list", "describe", "get-iam-policy", "get-value", "list-tags"}
GROUPS = {
    "alpha", "beta", "run", "services", "revisions", "jobs", "executions", "domain-mappings",
    "tasks", "queues", "scheduler", "artifacts", "docker", "images", "tags", "repositories",
    "container", "sql", "instances", "databases", "projects", "pubsub", "topics",
    "subscriptions", "compute", "functions", "builds", "iam", "service-accounts", "config",
    "firestore", "indexes", "operations",
}
UNDO_CONFIG = "run the same update with the values a describe shows now, saved before the change"
WRITES = {
    "create": ("creates a resource", "delete what it created"),
    "delete": ("deletes the resource", "none: a deleted resource doesn't come back"),
    "update": ("changes the resource's configuration", UNDO_CONFIG),
    "patch": ("changes the resource's configuration", UNDO_CONFIG),
    "set": ("changes a setting", UNDO_CONFIG),
    "deploy": ("deploys a new revision and can move traffic to it", "update-traffic back to the previous revision"),
    "update-traffic": ("moves traffic between revisions", "update-traffic back to the earlier split"),
    "replace": ("replaces the resource's whole definition", "replace again with the earlier definition"),
    "run": ("fires it now, with every side effect it has", "none: what it did stays done"),
    "execute": ("fires it now, with every side effect it has", "none: what it did stays done"),
    "pause": ("stops the schedule or queue from dispatching", "resume"),
    "resume": ("starts the schedule or queue dispatching again", "pause"),
    "purge": ("deletes every task in the queue", "none: purged tasks don't come back"),
    "cancel": ("stops it mid-flight", "none: start it again from the beginning"),
    "rollback": ("returns to an earlier version", "roll forward to the version it left"),
    "set-iam-policy": ("replaces who can access it", "set the policy a get-iam-policy shows now"),
    "add-iam-policy-binding": ("grants a role", "remove-iam-policy-binding"),
    "remove-iam-policy-binding": ("revokes a role", "add-iam-policy-binding"),
    "enable": ("turns it on", "disable"),
    "disable": ("turns it off", "enable"),
    "restart": ("restarts it, dropping work in flight", "none: what was in flight is lost"),
    "import": ("loads data into it", "none without a backup taken before"),
    "export": ("writes its data out to storage", "delete the exported files"),
}
# Flags that change whose access a read runs under, what it logs, or what file feeds more flags.
BANNED_FLAGS = (
    "--format", "--log-http", "--verbosity", "--impersonate-service-account", "--account",
    "--access-token-file", "--credential-file-override", "--configuration", "--flags-file",
    "--trace-token",
)
HIDDEN = re.compile(r"header|token|password|secret|^body$|^payload$", re.I)
# Maps whose keys are variable names and whose values are the variables' values.
VALUE_MAPS = re.compile(
    r"^(environmentVariables|buildEnvironmentVariables|secretEnvironmentVariables|substitutions"
    r"|variables|envVars|env_vars)\Z"
)
JOB_FIELDS = [
    "name", "schedule", "timeZone", "state", "scheduleTime", "lastAttemptTime", "userUpdateTime",
    "attemptDeadline", "status", "retryConfig", "httpTarget.uri", "httpTarget.httpMethod",
    "pubsubTarget.topicName", "appEngineHttpTarget.relativeUri",
]
TASK_FIELDS = [
    "name", "createTime", "scheduleTime", "dispatchDeadline", "dispatchCount", "responseCount",
    "firstAttempt", "lastAttempt", "view", "httpRequest.url", "httpRequest.httpMethod",
    "appEngineHttpRequest.relativeUri",
]


def classify(args):
    """The command path and its verb, for a read. Anything else raises Refusal.

    A write verb counts only inside the command path: one after the read verb is a name
    (`describe import`), not a command.
    """
    path = []
    for word in args:
        if word.startswith("-"):
            break
        if word == "run" and all(p in ("alpha", "beta") for p in path):  # the Cloud Run group
            path.append(word)
            continue
        if word in WRITES:
            what, undo = WRITES[word]
            raise Refusal(
                f"`{word}` writes, and the guard only reads. If it is what the investigation needs, "
                f"the person runs it:\n  gcloud {shlex.join(args)}\n"
                f"what it changes: {what}\nundo: {undo}"
            )
        if word in READS:
            return path, word
        if word in ("logging", "logs"):
            raise Refusal("log reads go through `logs`, which bounds the window and the rows")
        if word not in GROUPS:
            raise Refusal(f"`{word}` is not a command group this guard reads through")
        path.append(word)
    raise Refusal("no read verb (list, describe...) after the command groups, before any flag")


def flag_value(args, flag):
    for i, word in enumerate(args):
        if word == flag and i + 1 < len(args):
            return args[i + 1]
        if word.startswith(flag + "="):
            return word.split("=", 1)[1]
    return None


def env_names(env) -> list:
    names = []
    for e in env:
        if isinstance(e, dict):
            names.append({"name": e.get("name"), "secret": bool(pick(e, "valueFrom.secretKeyRef"))})
        else:  # a build step's "NAME=value" string
            names.append({"name": str(e).split("=", 1)[0], "secret": False})
    return names


def masked(v):
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if k == "env" and isinstance(x, list):
                out[k] = env_names(x)
            elif VALUE_MAPS.match(k) and isinstance(x, dict):
                out[k] = sorted(x)  # the names, never the values
            elif k == "metadata" and isinstance(x, dict) and isinstance(x.get("items"), list):
                out[k] = {"items": [i.get("key") for i in x["items"] if isinstance(i, dict)]}
            elif not HIDDEN.search(k):
                out[k] = masked(x)
        return out
    if isinstance(v, list):
        return [masked(x) for x in v]
    return v


def only(obj: dict, paths) -> dict:
    return {p: pick(obj, p) for p in paths if pick(obj, p) is not None}


def service_view(s: dict) -> dict:
    template = pick(s, "spec.template") or {}
    annotations = pick(template, "metadata.annotations") or {}
    return {
        "name": pick(s, "metadata.name"),
        "region": (pick(s, "metadata.labels") or {}).get("cloud.googleapis.com/location"),
        "latest_ready_revision": pick(s, "status.latestReadyRevisionName"),
        "traffic": [
            {k: t.get(k) for k in ("revisionName", "percent", "tag") if k in t}
            for t in pick(s, "status.traffic") or []
        ],
        "scaling": {k: v for k, v in annotations.items() if k.startswith("autoscaling.knative.dev/")},
        "concurrency": pick(template, "spec.containerConcurrency"),
        "timeout_seconds": pick(template, "spec.timeoutSeconds"),
        "containers": [
            {
                "image": c.get("image"),
                "limits": pick(c, "resources.limits"),
                "env": env_names(c.get("env") or []),
            }
            for c in pick(template, "spec.containers") or []
        ],
    }


def view(path, item):
    if "scheduler" in path:
        return masked(only(item, JOB_FIELDS))
    if "tasks" in path and "queues" not in path:
        return masked(only(item, TASK_FIELDS))
    if path[-2:] == ["run", "services"]:
        return service_view(item)
    return masked(item)


def gcloud(args, out: Out) -> None:
    path, verb = classify(args)
    for flag in BANNED_FLAGS:
        if any(w == flag or w.startswith(flag + "=") for w in args):
            if flag == "--flags-file":
                raise Refusal("--flags-file can carry any flag past this check; pass flags inline")
            raise Refusal(f"{flag} is the guard's to set; drop it")
    if sum(1 for w in args if w == "--project" or w.startswith("--project=")) > 1:
        raise Refusal("--project appears more than once; gcloud would read the last one")
    project = check_project(flag_value(args, "--project"))
    code, stdout, err = call(["gcloud", *args, "--format=json"])
    if code:
        cloud_error(err, project)
    data = json.loads(stdout or "null")
    if data in (None, [], {}):
        empty(project, f"`{' '.join(path)} {verb}`")
        return
    for item in data if isinstance(data, list) else [data]:
        out.emit(view(path, item) if isinstance(item, dict) else item)


def login(_a, _out: Out) -> None:
    code, _, _ = call(["gcloud", "auth", "print-access-token"])  # the token is never printed
    if code:
        fail(LOGIN)
    code, _, _ = call(["gcloud", "auth", "application-default", "print-access-token"])
    print("-- cloud login: ok")
    print(
        "-- warehouse credential: ok"
        if code == 0
        else "-- warehouse credential: missing; the person renews it with gcloud auth login --update-adc"
    )


# ---- the development list, read from the documentation base ------------------------------

FENCE = re.compile(r"(`{3,})(.*)")


def dev_lines(body: str) -> list:
    """The lines of each top-level development fence. A fence inside a longer one is an example."""
    lines, found, i = body.splitlines(), [], 0
    while i < len(lines):
        opened = FENCE.match(lines[i])
        if not opened:
            i += 1
            continue
        run, info = opened.group(1), opened.group(2).strip()
        close = next((j for j in range(i + 1, len(lines)) if re.fullmatch(run + r"`*[ \t]*", lines[j])), None)
        if close is None:
            break  # an unclosed fence runs to the end of the document and lists nothing
        if info == DEV_BLOCK:
            found += lines[i + 1 : close]
        i = close + 1
    return found


def wave_json(argv):
    code, stdout, _ = call(argv)
    if code:
        return None
    try:
        return json.loads(stdout)
    except ValueError:
        return None


def dev_projects():
    """The development projects the environments document lists, or None when unreachable.

    Read here and never taken as an argument: a caller can't widen the list.
    """
    items = wave_json(["wave", "doc", "list", "--tag", ENV_TAG, "--json"])
    if not isinstance(items, list):
        return None
    projects = set()
    for item in items:
        if not isinstance(item, dict):
            return None
        body = (item.get("data") or {}).get("body")
        if body is None and item.get("id"):
            shown = wave_json(["wave", "doc", "show", str(item["id"]), "--json"])
            body = ((shown or {}).get("data") or {}).get("body") if isinstance(shown, dict) else None
        for line in dev_lines(body or ""):
            name = line.split("#", 1)[0].strip()
            if PROJECT.match(name):
                projects.add(name)
    return projects


def require_dev(project) -> str:
    check_project(project)
    devs = dev_projects()
    if devs is None:
        raise Refusal(
            "the documentation base could not be reached, so no project is known to be "
            "development: every database path stays closed"
        )
    if project not in devs:
        raise Refusal(
            f"{project} is not listed as development in the `{ENV_TAG}` document (its "
            f"`{DEV_BLOCK}` block): databases open only in development projects; read the logs, "
            "the warehouse sink or the API instead"
        )
    return project


# ---- SQL: the warehouse past retention, and a development database -----------------------

SELECT_STAR = re.compile(r"(?:\bSELECT\s+(?:DISTINCT\s+|ALL\s+|AS\s+STRUCT\s+)?|,\s*)(?:[\w$]+\s*\.\s*)*\*", re.I)
AGGREGATE = re.compile(r"\b(COUNT|COUNTIF|SUM|AVG|MIN|MAX|APPROX_COUNT_DISTINCT)\s*\(", re.I)
ID_VALUE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}\Z")


def read_query(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as error:
        fail(f"could not read the query file {path}: {error.strerror}")


def check_projection(sql: str) -> None:
    if SELECT_STAR.search(db.code_only(sql)):
        raise Refusal("SELECT * prints whole rows; name the fields the investigation needs")


def check_scope(sql: str, id_value) -> str:
    """Only an aggregate, or rows filtered by one business id. Returns the query to run."""
    code = db.code_only(sql)
    if re.search(r"\b(UNION|INTERSECT|EXCEPT)\b", code, re.I):
        raise Refusal("a set operation can add rows past the scope; send one SELECT")
    if len(re.findall(r"\bSELECT\b", code, re.I)) != 1:
        raise Refusal("one SELECT only: a WITH or a subquery can hide the filter of the outer read")
    if id_value is None:
        if re.search(r"\bOVER\s*\(", code, re.I):
            raise Refusal("a window function keeps every row; aggregate with GROUP BY instead")
        if not re.search(r"\bGROUP\s+BY\b", code, re.I) and not all(
            AGGREGATE.match(item) for item in select_items(code)
        ):
            raise Refusal(
                "rows not filtered by one business id; rewrite it as an aggregate (every selected "
                "field an aggregate, or a GROUP BY) or pass --id and filter with `WHERE <id field> = @id`"
            )
        return sql
    if not ID_VALUE.match(id_value):
        raise Refusal("--id holds characters an id doesn't have")
    if not re.search(r"\bWHERE\b[\s\S]*?[\w.`\]\)\s](?<![<>!])=\s*@id\b", code, re.I):
        raise Refusal("rows filtered by one id need `WHERE <id field> = @id`")
    if re.search(r"\b(OR|NOT)\b", code, re.I):
        raise Refusal("an OR or a NOT can widen the filter past one id; keep it to the one id")
    return re.sub(r"@id\b", f"'{id_value}'", sql)


def select_items(code: str) -> list:
    """The outer SELECT's items, split on the commas outside parentheses."""
    m = re.search(r"\bSELECT\b(?:\s+DISTINCT\b)?", code, re.I)
    if not m:
        return []
    items, depth, cur = [], 0, []
    for i in range(m.end(), len(code)):
        c = code[i]
        if depth == 0 and re.match(r"\bFROM\b", code[i:], re.I) and (i == 0 or not code[i - 1].isalnum()):
            break
        depth += c == "("
        depth -= c == ")"
        if c == "," and depth == 0:
            items.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    items.append("".join(cur).strip())
    return [i for i in items if i]


def show_rows(header, rows, out: Out, limit: int) -> None:
    for row in rows:
        out.emit(dict(zip(header, row)))
    if len(rows) >= limit:
        print(f"-- truncated: {len(rows)} rows, as many as the limit; narrow the query")


def warehouse(a, out: Out) -> None:
    sql = read_query(a.query)
    db.check_text(sql)
    check_projection(sql)
    sql = check_scope(sql, a.id)
    bq = db.BigQuery(check_project(a.project))
    gb = bq.check_dry_run(bq.dry_run(sql))
    print(f"-- dry run: would read {gb:.2f} GB (ceiling {db.MAX_GB} GB)")
    if not a.run:
        return
    db.check_cost(gb)
    result = bq.normalize(bq.run(sql))
    db.check_output(result)  # /bb:measure's locks 4 and 5: no person column, no email, no free text
    show_rows(result["header"], result["rows"], out, db.MAX_ROWS)
    if result["total"] > len(result["rows"]) and len(result["rows"]) < db.MAX_ROWS:
        print(f"-- truncated: {len(result['rows'])} of {result['total']} rows; aggregate further")


def pg_code_only(text: str, keep_strings: bool = False) -> str:
    """PostgreSQL's code with its comments, strings and quoted names blanked.

    db.code_only reads BigQuery, where `#` opens a comment; in PostgreSQL `#` is an operator and
    `$tag$...$tag$` is a string, so reading this text that way hides a `;`. A `$` or an escape
    string (E'...') left in the code is refused instead of lexed: neither is needed to read rows.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        c, two = text[i], text[i : i + 2]
        if two == "--":
            end = text.find("\n", i)
            i = n if end == -1 else end
            out.append(" ")
        elif two == "/*":
            end = text.find("*/", i + 2)  # PostgreSQL nests comments; ending early only shows more code
            i = n if end == -1 else end + 2
            out.append(" ")
        elif c in ("'", '"'):
            if c == "'" and i and text[i - 1] in "eE" and (i < 2 or not text[i - 2].isalnum()):
                raise Refusal("an escape string (E'...') is not needed to read rows; use a plain '...'")
            j = i + 1
            while j < n:
                if text[j] == c and text[j + 1 : j + 2] == c:  # a doubled quote stays inside
                    j += 2
                elif text[j] == c:
                    break
                else:
                    j += 1
            out.append(text[i : j + 1] if keep_strings else " '' ")
            i = j + 1
        else:
            if c == "$":
                raise Refusal("a `$` (a parameter or a dollar-quoted string) is not needed to read rows")
            out.append(c)
            i += 1
    return "".join(out)


def sql(a, out: Out) -> None:
    require_dev(a.project)
    text = read_query(a.query)
    body = pg_code_only(text, keep_strings=True).strip().rstrip(";").strip()  # the text checked is the text run
    code = pg_code_only(body)
    if ";" in code:
        raise Refusal("more than one statement (a script); send a single query")
    first = re.match(r"[\s(]*([A-Za-z]+)", code)
    if not first or first.group(1).upper() not in ("SELECT", "WITH"):
        raise Refusal("not a read: only a SELECT or a WITH")
    if re.search(r"\bINTO\b", code, re.I):
        raise Refusal("SELECT ... INTO creates a table; read rows only")
    if SELECT_STAR.search(code):
        raise Refusal("SELECT * prints whole rows; name the fields the investigation needs")
    if "\\" in code:
        raise Refusal("a backslash outside a string reads as a psql command; send SQL only")
    limit = check_limit(a.limit)
    wrapped = f"SELECT * FROM (\n{body}\n) AS bb_read LIMIT {limit}"
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    code, stdout, err = call(["psql", "-X", "-w", "-v", "ON_ERROR_STOP=1", "--csv", "-c", wrapped], env=env)  # -w: no password prompt
    if code:
        if not any(os.environ.get(v) for v in ("PGHOST", "PGSERVICE")):
            fail(
                f"no database to connect to: set the PG* variables (PGHOST, PGPORT, PGUSER, "
                f"PGDATABASE) to the cloud-sql-proxy of {a.project}, as the access document says, "
                "then run the read again"
            )
        fail(f"the query failed in the development database of {a.project}: {first_line(err)}")
    rows = list(csv.reader(io.StringIO(stdout)))
    if len(rows) <= 1:
        empty(a.project, "this query")
        return
    show_rows(rows[0], rows[1:], out, limit)


# ---- the document database: only queries the guard builds --------------------------------

WRITE_STAGES = {"$out", "$merge"}
SERVER_CODE = {"$where", "$function", "$accumulator"}


def check_doc(v) -> None:
    if isinstance(v, dict):
        for k, x in v.items():
            if k in WRITE_STAGES:
                raise Refusal(f"the stage {k} writes; the guard runs reads only")
            if k in SERVER_CODE:
                raise Refusal(f"{k} runs code on the server; filter with plain operators")
            check_doc(x)
    elif isinstance(v, list):
        for x in v:
            check_doc(x)


def parse_json(text, kind, flag):
    try:
        value = json.loads(text)
    except ValueError:
        raise Refusal(f"{flag} is not valid JSON")
    if not isinstance(value, kind):
        raise Refusal(f"{flag} must be a JSON {'object' if kind is dict else 'list'}")
    return value


def doc_script(a) -> str:
    """The mongosh script for the read. The connection string stays in the environment."""
    for flag, value in (("--database", a.database), ("--collection", a.collection)):
        if not value or not NAME.match(value):
            raise Refusal(f"{flag} needs a plain name")
    filt = parse_json(a.filter or "{}", dict, "--filter")
    check_doc(filt)
    js = json.dumps
    head = (
        f"const c = connect(process.env.{MONGO_URI_ENV}).getSiblingDB({js(a.database)})"
        f".getCollection({js(a.collection)});\n"
    )
    if a.op == "count":
        return head + f"print(c.countDocuments(EJSON.parse({js(js(filt))})));"
    if not a.field:
        raise Refusal("name the fields to print with --field; a whole document never prints")
    for name in a.field:
        if not FIELD.match(name):
            raise Refusal(f"'{name}' is not a field path")
    limit = check_limit(a.limit)
    proj = {name: 1 for name in a.field}
    proj.setdefault("_id", 0)  # not returned unless a field names it
    if a.op == "find":
        read = f"c.find(EJSON.parse({js(js(filt))}), {js(proj)}).limit({limit}).toArray()"
    else:
        pipeline = parse_json(a.pipeline or "[]", list, "--pipeline")
        check_doc(pipeline)
        if filt:
            pipeline = [{"$match": filt}] + pipeline
        pipeline += [{"$project": proj}, {"$limit": limit}]
        read = f"c.aggregate(EJSON.parse({js(js(pipeline))})).toArray()"
    return head + f"print(EJSON.stringify({read}, null, 0, {{relaxed: true}}));"


def hide_objects(doc: dict, paths, prefix: str = "") -> dict:
    """A requested object prints a placeholder; the fields inside it are asked for by name."""
    shown = {}
    for key, value in doc.items():
        path = prefix + key
        if path in paths and isinstance(value, (dict, list)):
            shown[key] = OBJECT
        elif isinstance(value, dict):
            shown[key] = hide_objects(value, paths, path + ".")
        else:
            shown[key] = value
    return shown


def docdb(a, out: Out) -> None:
    require_dev(a.project)
    script = doc_script(a)
    if not os.environ.get(MONGO_URI_ENV):
        fail(
            f"set {MONGO_URI_ENV} to the development database's connection string (the access "
            "document says how); the guard reads it from the environment so it never shows on a "
            "command line"
        )
    code, stdout, err = call(["mongosh", "--nodb", "--quiet", "--eval", script])
    if code:
        fail(f"the query failed in the development database of {a.project}: {first_line(err)}")
    if a.op == "count":
        print(json.dumps({"count": json.loads(stdout.strip() or "0")}))
        return
    docs = json.loads(stdout or "[]")
    if not docs:
        empty(a.project, "this query")
        return
    for doc in docs:
        out.emit(hide_objects(doc, set(a.field)))
    if len(docs) >= a.limit:
        print(f"-- truncated: {len(docs)} documents, as many as the limit; narrow the filter")


# ---- a draft the skill wrote: the same check, before the person sees it ------------------


def check(a, _out: Out) -> None:
    try:
        text = pathlib.Path(a.draft).read_text(encoding="utf-8")
    except OSError as error:
        fail(f"could not read the draft {a.draft}: {error.strerror}")
    hits = 0
    for n, line in enumerate(text.splitlines(), 1):
        kinds = ["email"] * len(db.EMAIL.findall(line))
        kinds += ["document number"] * len(DOCUMENT.findall(line))
        kinds += ["a business id from the run"] * sum(line.count(i) for i in a.id if i)
        if kinds:
            hits += len(kinds)
            print(f"line {n}: {', '.join(kinds)}")  # where, never the value
    print(f"-- personal data check: {hits} value(s) found in the draft")
    if hits:
        sys.exit(1)


# ---- the run's temporary directory -------------------------------------------------------


def base() -> pathlib.Path:
    return pathlib.Path(tempfile.gettempdir()).resolve()


def run_dir(path: str) -> pathlib.Path:
    d = pathlib.Path(path).resolve()
    if d.parent != base() or not d.name.startswith(RUN_PREFIX) or not d.is_dir():
        raise Refusal(f"{path} is not a run directory `start` made")
    return d


def remove_run(d: pathlib.Path) -> None:
    images = d / "images"
    if images.is_file():
        for ref in images.read_text().split():
            call(["docker", "image", "rm", "-f", ref])
    shutil.rmtree(d, ignore_errors=True)


def start(_a, _out: Out) -> None:
    now, swept = time.time(), 0
    for d in base().glob(RUN_PREFIX + "*"):
        if d.is_dir() and not d.is_symlink() and now - d.stat().st_mtime > DAY:
            remove_run(d)
            swept += 1
    d = base() / f"{RUN_PREFIX}{time.strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(3)}"
    d.mkdir(mode=0o700)
    print(d)
    if swept:
        print(f"-- deleted {swept} run director(ies) an interrupted run left behind")


def close(a, _out: Out) -> None:
    d = run_dir(a.run)
    remove_run(d)
    print(f"-- deleted {d} and the images it pulled")


def pull(a, _out: Out) -> None:
    d = run_dir(a.run)
    inspected, _, _ = call(["docker", "image", "inspect", a.image])  # 0 when it was already local
    code, _, err = call(["docker", "pull", a.image])
    if code:
        fail(f"could not pull {a.image}: {first_line(err)}")
    if inspected == 0:  # `close` deletes only the images the run added
        print(f"-- {a.image} was already local; `close` keeps it")
        return
    with open(d / "images", "a", encoding="utf-8") as f:
        f.write(a.image + "\n")
    print(f"-- pulled {a.image}; `close` deletes it with the run")


# ---- the command line --------------------------------------------------------------------


def parser():
    import argparse

    p = argparse.ArgumentParser(
        description="Every read /bb:debug makes, through one guard.",
        epilog="A read of the cloud CLI's own: gcloud_read.py gcloud GROUP... VERB --project P [FLAGS]",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("start")
    sub.add_parser("login")
    for name in ("close", "pull"):
        s = sub.add_parser(name)
        s.add_argument("run")
        if name == "pull":
            s.add_argument("image")
    s = sub.add_parser("logs")
    for flag in ("--project", "--resource", "--service", "--since", "--until", "--filter"):
        s.add_argument(flag)
    s.add_argument("--limit", type=int)
    s.add_argument("--field", action="append", default=[])
    s = sub.add_parser("metrics")
    for flag in ("--project", "--metric", "--service", "--since", "--until", "--filter"):
        s.add_argument(flag)
    s.add_argument("--aligner", choices=ALIGNERS)
    s.add_argument("--align", type=int, default=60)
    s.add_argument("--limit", type=int)
    s = sub.add_parser("warehouse")
    s.add_argument("query")
    s.add_argument("--project")
    s.add_argument("--id")
    s.add_argument("--run", action="store_true")
    s = sub.add_parser("sql")
    s.add_argument("query")
    s.add_argument("--project")
    s.add_argument("--limit", type=int)
    s = sub.add_parser("docdb")
    for flag in ("--project", "--database", "--collection", "--filter", "--pipeline"):
        s.add_argument(flag)
    s.add_argument("--op", choices=("find", "count", "aggregate"), required=True)
    s.add_argument("--field", action="append", default=[])
    s.add_argument("--limit", type=int)
    s = sub.add_parser("check")
    s.add_argument("draft")
    s.add_argument("--id", action="append", default=[])
    return p


COMMANDS = {
    "start": start, "close": close, "pull": pull, "login": login, "logs": logs, "metrics": metrics,
    "warehouse": warehouse, "sql": sql, "docdb": docdb, "check": check,
}


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    out = Out()
    try:
        if argv[:1] == ["gcloud"]:  # the rest is gcloud's own command line, read by classify
            gcloud(argv[1:], out)
        else:
            a = parser().parse_args(argv)
            COMMANDS[a.command](a, out)
    except Refusal as refusal:
        fail(f"refused: {refusal}")
    if argv[:1] in (["gcloud"], ["logs"], ["metrics"], ["warehouse"], ["sql"], ["docdb"]):
        out.close()


if __name__ == "__main__":
    main()
