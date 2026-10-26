"""Every read /bb:debug makes in a running environment, through one guard.

Usage:
    python3 gcloud_read.py start
    python3 gcloud_read.py close RUN_DIR
    python3 gcloud_read.py pull RUN_DIR IMAGE
    python3 gcloud_read.py login
    python3 gcloud_read.py logs --project P --resource TYPE [--service S] --since T --until T
                                --limit N [--filter F] [--field PATH ...]
    python3 gcloud_read.py gcloud GROUP... VERB [POSITIONALS] --project P [FLAGS]
    python3 gcloud_read.py warehouse QUERY.sql --project P [--id VALUE] [--run]
    python3 gcloud_read.py sql QUERY.sql --project P --limit N
    python3 gcloud_read.py docdb --project P --database D --collection C --op find|count|aggregate
                                 [--filter JSON] [--pipeline JSON] [--field F ...] [--limit N]

The skill and its investigators call the cloud CLI, the warehouse and a database only through
this script, so the rules below hold whatever a prompt says:

- Reads only. `gcloud` runs a command whose path is made of known groups and ends on a read
  verb. A write verb is refused, and the command is printed for the person with what it
  changes and whether it can be undone. Anything else is refused as unknown.
- Bounded. `logs` needs a project, a resource type, a window (--since, --until) and a limit. A
  result as long as its limit is reported as truncated.
- Rows projected. A log entry, a warehouse row and a database row print named fields, never a
  whole entry or document. A field beyond the defaults is asked for by name, and a field that
  holds an object prints a placeholder instead of the object.
- Checked output. Every value printed passes the personal data check: an email, a personal
  document number (CPF, CNPJ) or a text above LONG_TEXT characters is redacted, and the output
  ends by saying how many were.
- Masked. A service prints its environment variable names and whether each is a secret
  reference, never a value. A scheduler job and a queued task print through a field list that
  leaves headers and bodies out. Any other read drops keys named like a header, a token, a
  password, a secret or a body.
- Databases in development only. `sql` and `docdb` open only for a project the company's
  `bb-debug:environments` document lists as development, and the script reads that list itself
  with the `wave` CLI: there is no argument that widens it. The list is the lines of a fenced
  block whose info string is `bb-debug-development`, one project id per line. A document without
  the block, a project missing from it, or a documentation base that can't be reached closes
  every database path. `sql` (PostgreSQL, through `psql` and the PG* environment variables)
  opens the session read only and runs one SELECT. `docdb` (MongoDB, through `mongosh` and the
  BB_DEBUG_MONGO_URI environment variable) runs only the find, count or aggregation it builds,
  and refuses a stage that writes or runs code on the server.
- The warehouse past retention. `warehouse` reuses /bb:measure's locks (db_read.py: one read
  statement, the dry run's classification, the byte ceiling on both runs), then admits only an
  aggregate or rows filtered by one business id, passed as --id and written `= @id`.
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

_db_spec = importlib.util.spec_from_file_location(
    "db_read", pathlib.Path(__file__).resolve().parents[2] / "measure" / "scripts" / "db_read.py"
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
PROJECT = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
NAME = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")
LOGIN = (
    "the cloud login expired or is missing; run `gcloud auth login` yourself (the guard can't "
    "log in for you), then run the read again"
)

# ---- the personal data check -------------------------------------------------------------

DOCUMENT = re.compile(
    r"(?<![\w./-])(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{11}|\d{14})(?![\w/-])"
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
        return self.text(v) if isinstance(v, str) else v

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
            value = "[an object: ask for a field inside it by name]"
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
    if not a.resource or not re.match(r"^[a-z_]+$", a.resource):
        raise Refusal("a log read needs --resource, the resource type (e.g. cloud_run_revision)")
    if not a.since or not a.until:
        raise Refusal("a log read needs a window: pass --since and --until")
    since, until = parse_time(a.since, "--since"), parse_time(a.until, "--until")
    if until <= since:
        raise Refusal("--until must come after --since")
    check_limit(a.limit)
    if a.service and not re.match(r"^[a-z0-9-]+$", a.service):
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
BANNED_FLAGS = ("--format", "--log-http", "--verbosity", "--impersonate-service-account")
HIDDEN = re.compile(r"header|token|password|secret|^body$|^payload$", re.I)
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
    """The command path and its verb, for a read. Anything else raises Refusal."""
    words = [w for w in args if not w.startswith("-")]
    lead = next((i for i, w in enumerate(words) if w not in ("alpha", "beta")), len(words))
    if words[lead : lead + 1] == ["run"]:  # the Cloud Run group, not the verb `tasks run` uses
        words = words[:lead] + words[lead + 1 :]
    write = next((w for w in words if w in WRITES), None)
    if write:
        what, undo = WRITES[write]
        raise Refusal(
            f"`{write}` writes, and the guard only reads. If it is what the investigation needs, "
            f"the person runs it:\n  gcloud {shlex.join(args)}\n"
            f"what it changes: {what}\nundo: {undo}"
        )
    path = []
    for word in args:
        if word.startswith("-"):
            break
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
    return [{"name": e.get("name"), "secret": bool(pick(e, "valueFrom.secretKeyRef"))} for e in env]


def masked(v):
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if k == "env" and isinstance(x, list):
                out[k] = env_names(x)
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
            raise Refusal(f"{flag} is the guard's to set; drop it")
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

BLOCK = re.compile(r"^```" + DEV_BLOCK + r"[ \t]*\n(.*?)^```", re.M | re.S)


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
        for block in BLOCK.findall(body or ""):
            for line in block.splitlines():
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
ID_VALUE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


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
    if id_value is None:
        if not AGGREGATE.search(code):
            raise Refusal(
                "rows not filtered by one business id; rewrite it as an aggregate (COUNT, SUM...) "
                "or pass --id and filter with `WHERE <id field> = @id`"
            )
        return sql
    if not ID_VALUE.match(id_value):
        raise Refusal("--id holds characters an id doesn't have")
    if not re.search(r"\bWHERE\b[\s\S]*=\s*@id\b", code, re.I):
        raise Refusal("rows filtered by one id need `WHERE <id field> = @id`")
    if re.search(r"\bOR\b", code, re.I):
        raise Refusal("an OR can widen the filter past one id; keep it to the one id")
    return re.sub(r"@id\b", f"'{id_value}'", sql)


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
    show_rows(result["header"], result["rows"], out, db.MAX_ROWS)
    if result["total"] > len(result["rows"]) and len(result["rows"]) < db.MAX_ROWS:
        print(f"-- truncated: {len(result['rows'])} of {result['total']} rows; aggregate further")


def sql(a, out: Out) -> None:
    require_dev(a.project)
    text = read_query(a.query)
    db.check_text(text)
    check_projection(text)
    if "\\" in db.code_only(text):
        raise Refusal("a backslash outside a string reads as a psql command; send SQL only")
    limit = check_limit(a.limit)
    body = text.rstrip().rstrip(";")
    wrapped = f"SELECT * FROM (\n{body}\n) AS bb_read LIMIT {limit}"
    env = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
    code, stdout, err = call(["psql", "-X", "-v", "ON_ERROR_STOP=1", "--csv", "-c", wrapped], env=env)
    if code:
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
        out.emit(doc)
    if len(docs) >= a.limit:
        print(f"-- truncated: {len(docs)} documents, as many as the limit; narrow the filter")


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
    code, _, err = call(["docker", "pull", a.image])
    if code:
        fail(f"could not pull {a.image}: {first_line(err)}")
    with open(d / "images", "a", encoding="utf-8") as f:
        f.write(a.image + "\n")
    print(f"-- pulled {a.image}; `close` deletes it with the run")


# ---- the command line --------------------------------------------------------------------


def parser():
    import argparse

    p = argparse.ArgumentParser(description="Every read /bb:debug makes, through one guard.")
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
    return p


COMMANDS = {
    "start": start, "close": close, "pull": pull, "login": login, "logs": logs,
    "warehouse": warehouse, "sql": sql, "docdb": docdb,
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
    if argv[:1] in (["gcloud"], ["logs"], ["warehouse"], ["sql"], ["docdb"]):
        out.close()


if __name__ == "__main__":
    main()
