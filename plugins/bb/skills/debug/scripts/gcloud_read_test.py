"""Tests for the rules in gcloud_read.py, with no network, no cloud CLI and no credential.

Usage:
    python3 gcloud_read_test.py

Every process the guard would start goes through `call`, which the tests replace with a fake
that answers from invented data and records what it was asked to run. A case the guard refuses
before any process starts also proves nothing ran. The data is invented: a product called
Pebble, a notes app, with the projects pebble-dev-1 and pebble-prod-1.
"""

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time
import types

spec = importlib.util.spec_from_file_location("g", pathlib.Path(__file__).with_name("gcloud_read.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def no_network(*_a, **_k):
    raise AssertionError("tried to use the network")


g.db.BigQuery.post = no_network
g.db.BigQuery.token = no_network
g.db.urllib.request.urlopen = no_network

calls = []


def nothing_runs(argv, env=None):
    raise AssertionError(f"tried to run {argv[0]}")


def answering(table):
    """A fake `call`: the first key that starts the argv answers (code, out, err)."""

    def fake(argv, env=None):
        calls.append((argv, env))
        for prefix, answer in table.items():
            if tuple(argv[: len(prefix)]) == prefix:
                return answer
        raise AssertionError(f"tried to run {argv}")

    return fake


failures = []


def case(name, fn, refused):
    calls.clear()
    try:
        fn()
        ok, got = not refused, "passed"
    except g.Refusal as r:
        ok, got = refused, f"refused: {str(r).splitlines()[0]}"
    except AssertionError as e:
        ok, got = False, f"ERROR: {e}"
    except SystemExit as e:
        ok, got = False, f"ERROR: exit {e.code}"
    print(f"{'ok    ' if ok else 'FAILED'} | {name} | {got}")
    if not ok:
        failures.append(name)
    g.call = nothing_runs


def printed(fn):
    """Run fn and return what it printed; a clean stop (exit 1 with a message) counts too."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            fn()
        except SystemExit as e:
            if e.code != 1 or not out.getvalue().strip():
                raise AssertionError(f"exit {e.code!r} with stdout {out.getvalue()!r}")
    return out.getvalue()


def expect(cond, message):
    if not cond:
        raise AssertionError(message)


def run(argv):
    return printed(lambda: g.main(argv))


g.call = nothing_runs
PROD, DEV = "pebble-prod-1", "pebble-dev-1"
ENV_DOC = (
    "# Pebble environments\n\npebble-prod-1 is production. Nothing here says pebble-prod-1 is "
    "development.\n\n```bb-debug-development\npebble-dev-1  # the shared sandbox\n```\n"
)


def wave_with(body):
    item = {"id": "d1", "data": {"key": "DOC-7", "tags": ["bb-debug:environments"], "body": body}}
    return {("wave", "doc", "list"): (0, json.dumps([item]), "")}


# ---- reads only: the verb decides ---------------------------------------------------------
reads = [
    ("describe a service", ["run", "services", "describe", "notes-api", "--project", PROD, "--region", "r1"]),
    ("list revisions", ["run", "revisions", "list", "--project", PROD, "--region", "r1"]),
    ("describe a queue", ["tasks", "queues", "describe", "sync", "--project", PROD]),
    ("describe a scheduler job", ["scheduler", "jobs", "describe", "nightly", "--project=" + PROD]),
    ("list image tags", ["container", "images", "list-tags", "gcr.io/x/notes", "--project", PROD]),
    ("beta list", ["beta", "run", "services", "list", "--project", PROD]),
]
for name, args in reads:
    case(f"read: {name}", lambda a=args: g.classify(a), False)

writes = [
    ("rerun a task", ["tasks", "run", "projects/p/tasks/9", "--queue", "sync", "--project", PROD]),
    ("fire a job", ["scheduler", "jobs", "run", "nightly", "--project", PROD]),
    ("execute a Cloud Run job", ["run", "jobs", "execute", "reindex", "--project", PROD]),
    ("change a flag", ["run", "services", "update", "notes-api", "--update-env-vars", "FLAG=1"]),
    ("deploy", ["run", "deploy", "notes-api", "--image", "gcr.io/x/notes:2"]),
    ("purge a queue", ["tasks", "queues", "purge", "sync", "--project", PROD]),
    ("delete a task", ["tasks", "delete", "9", "--queue", "sync", "--project", PROD]),
    ("a group the guard doesn't know", ["secrets", "delete", "api-key", "--project", PROD]),
    ("a read verb hidden as a flag value", ["--billing-project", "list", "tasks", "delete", "9"]),
]
for name, args in writes:
    case(f"write: {name}", lambda a=args: g.classify(a), True)


def write_prints_the_command():
    args = ["tasks", "run", "projects/p/tasks/9", "--queue", "sync", "--project", PROD]
    text = run(["gcloud", *args])
    expect("gcloud tasks run projects/p/tasks/9 --queue sync" in text, f"no command in {text!r}")
    expect("what it changes:" in text and "undo: none" in text, f"no change or undo in {text!r}")


case("write: the refusal prints the command, what it changes and its undo", write_prints_the_command, False)

unknown = [
    ("a secret's value", ["secrets", "versions", "access", "latest", "--project", PROD]),
    ("an access token", ["auth", "print-access-token"]),
    ("a database session", ["sql", "connect", "notes-db", "--project", PROD]),
    ("an unbounded log read", ["logging", "read", "severity>=ERROR", "--project", PROD]),
    ("a log tail", ["run", "services", "logs", "tail", "notes-api", "--project", PROD]),
    ("no verb", ["run", "services", "--project", PROD]),
]
for name, args in unknown:
    case(f"refused: {name}", lambda a=args: g.classify(a), True)

flags = [
    ("no project", ["run", "services", "list", "--region", "r1"], True),
    ("the caller's own --format", ["run", "services", "list", "--project", PROD, "--format=yaml"], True),
    ("--log-http, which prints the token", ["run", "services", "list", "--project", PROD, "--log-http"], True),
]
for name, args, refused in flags:
    case(f"gcloud flags: {name}", lambda a=args: g.gcloud(a, g.Out()), refused)


# ---- masked: a service, a scheduler job and a queued task ----------------------------------
SERVICE = {
    "metadata": {"name": "notes-api", "labels": {"cloud.googleapis.com/location": "r1"}},
    "spec": {
        "template": {
            "metadata": {"annotations": {"autoscaling.knative.dev/maxScale": "4", "client.knative.dev/user-image": "x"}},
            "spec": {
                "containerConcurrency": 80,
                "timeoutSeconds": 300,
                "containers": [
                    {
                        "image": "gcr.io/x/notes@sha256:abc",
                        "resources": {"limits": {"memory": "512Mi", "cpu": "1"}},
                        "env": [
                            {"name": "STORE_KEY", "value": "invented-value-123"},
                            {"name": "SIGNING_SECRET", "valueFrom": {"secretKeyRef": {"name": "sign", "key": "latest"}}},
                        ],
                        "startupProbe": {"httpGet": {"httpHeaders": [{"name": "X-Probe", "value": "invented-probe"}]}},
                    }
                ],
            },
        }
    },
    "status": {"latestReadyRevisionName": "notes-api-00042", "traffic": [{"revisionName": "notes-api-00042", "percent": 100}]},
}
JOB = {
    "name": "projects/p/locations/r1/jobs/nightly",
    "schedule": "0 3 * * *",
    "state": "ENABLED",
    "httpTarget": {"uri": "https://notes.invalid/sync", "httpMethod": "POST", "headers": {"Authorization": "Bearer invented-token"}, "body": "aW52ZW50ZWQ="},
}
TASK = {
    "name": "projects/p/locations/r1/queues/sync/tasks/9",
    "dispatchCount": 3,
    "httpRequest": {"url": "https://notes.invalid/sync", "headers": {"X-Api-Key": "invented-key"}, "body": "aW52ZW50ZWQ="},
}


def masks(args, answer, present, absent):
    def go():
        g.call = answering({("gcloud",): (0, json.dumps(answer), "")})
        text = run(["gcloud", *args])
        expect(calls and calls[-1][0][-1] == "--format=json", f"format not forced: {calls}")
        for p in present:
            expect(p in text, f"{p!r} missing from {text!r}")
        for a in absent:
            expect(a not in text, f"{a!r} printed in {text!r}")

    return go


case(
    "masked: a service prints env names and secret flags, never values or probe headers",
    masks(
        ["run", "services", "describe", "notes-api", "--project", PROD, "--region", "r1"],
        SERVICE,
        ['"STORE_KEY"', '"secret": true', '"secret": false', "notes-api-00042", "512Mi"],
        ["invented-value-123", "invented-probe", "X-Probe", "sign", "user-image"],
    ),
    False,
)
case(
    "masked: a scheduler job leaves its headers and body out",
    masks(["scheduler", "jobs", "describe", "nightly", "--project", PROD], JOB, ["0 3 * * *", "POST"], ["invented-token", "Authorization", "aW52ZW50ZWQ="]),
    False,
)
case(
    "masked: a queued task leaves its headers and body out",
    masks(["tasks", "describe", "9", "--queue", "sync", "--project", PROD], TASK, ['"dispatchCount": 3'], ["invented-key", "X-Api-Key", "aW52ZW50ZWQ="]),
    False,
)
case(
    "masked: any other read drops header, token and secret keys and env values",
    masks(
        ["run", "revisions", "describe", "notes-api-00042", "--project", PROD],
        {"spec": {"containers": [{"env": [{"name": "A", "value": "invented-env"}]}]}, "oidcToken": {"x": "y"}, "metadata": {"name": "rev"}},
        ['"A"', "rev"],
        ["invented-env", "oidcToken"],
    ),
    False,
)


# ---- empty and denied: said plainly, naming the project ------------------------------------
def says(answer, needles, args=None):
    def go():
        g.call = answering({("gcloud",): answer})
        text = run(["gcloud", *(args or ["run", "services", "list", "--project", PROD])])
        for n in needles:
            expect(n in text, f"{n!r} missing from {text!r}")
        expect("no traffic" not in text, f"reads as no traffic: {text!r}")

    return go


case("denied: names the project, never an empty answer", says((1, "", "ERROR: (gcloud) PERMISSION_DENIED: x"), [PROD, "denied"]), False)
case("empty: names the project", says((0, "[]", ""), [PROD, "nothing"]), False)
case("login expired: asks the person to log in", says((1, "", "ERROR: Reauthentication failed."), ["gcloud auth login", "can't"]), False)
case("gcloud missing: says so", says((127, "", "gcloud is not installed"), ["not installed"]), False)


def login_ok_never_prints_the_token():
    g.call = answering({("gcloud", "auth"): (0, "ya29.invented-token\n", "")})
    text = run(["login"])
    expect("ok" in text and "invented-token" not in text, f"login printed {text!r}")


case("login: checks the credential and never prints the token", login_ok_never_prints_the_token, False)


# ---- bounded: logs need a project, a resource, a window and a limit -------------------------
def logs_args(**over):
    base = {"project": PROD, "resource": "cloud_run_revision", "service": "notes-api", "since": "2026-03-02T10:00:00Z", "until": "2026-03-02T11:00:00Z", "filter": None, "limit": 3, "field": []}
    base.update(over)
    return types.SimpleNamespace(**base)


bounds = [
    ("every bound given", {}, False),
    ("no window", {"since": None, "until": None}, True),
    ("no end of window", {"until": None}, True),
    ("no limit", {"limit": None}, True),
    ("a limit past the ceiling", {"limit": 5000}, True),
    ("no project", {"project": None}, True),
    ("no resource", {"resource": None}, True),
    ("a window that ends before it starts", {"until": "2026-03-02T09:00:00Z"}, True),
    ("a time with no zone", {"since": "2026-03-02T10:00:00"}, True),
    ("a quote in the service name", {"service": 'notes" OR "x'}, True),
    ("a field path that isn't one", {"field": ["jsonPayload.a b"]}, True),
]
for name, over, refused in bounds:

    def go(o=over, r=refused):
        g.call = answering({("gcloud", "logging", "read"): (0, "[]", "")})
        printed(lambda: g.logs(logs_args(**o), g.Out()))

    case(f"logs: {name}", go, refused)

ENTRIES = [
    {
        "timestamp": "2026-03-02T10:15:00.123Z",
        "severity": "ERROR",
        "trace": "projects/pebble-prod-1/traces/4bf92f3577b34da6a3ce929d0e0e4736",
        "resource": {"type": "cloud_run_revision", "labels": {"service_name": "notes-api"}},
        "jsonPayload": {
            "message": "sync failed for note",
            "stage": "upload",
            "error_type": "TimeoutError",
            "note_id": "n-81",
            "owner_note": "a private note the owner wrote",
            "ctx": {"a": 1},
        },
    },
    {"timestamp": "2026-03-02T10:16:00Z", "severity": "INFO", "textPayload": "contact ana@pebble.invalid", "resource": {"labels": {"service_name": "notes-api"}}},
    {"timestamp": "2026-03-02T10:17:00Z", "httpRequest": {"requestMethod": "POST", "status": 503, "latency": "30.1s", "userAgent": "invented-agent"}},
]


def projected():
    g.call = answering({("gcloud", "logging", "read"): (0, json.dumps(ENTRIES), "")})
    text = run(["logs", "--project", PROD, "--resource", "cloud_run_revision", "--service", "notes-api", "--since", "2026-03-02T10:00:00Z", "--until", "2026-03-02T11:00:00Z", "--limit", "3", "--field", "jsonPayload.note_id", "--field", "jsonPayload.ctx"])
    argv = calls[-1][0]
    flt = argv[3]
    for part in ['resource.type="cloud_run_revision"', 'timestamp>="2026-03-02T10:00:00Z"', 'timestamp<="2026-03-02T11:00:00Z"', 'service_name="notes-api"']:
        expect(part in flt, f"{part!r} missing from the filter {flt!r}")
    expect(f"--project={PROD}" in argv and "--limit=3" in argv, f"bounds missing from {argv}")
    for p in ['"stage": "upload"', '"error_type": "TimeoutError"', '"trace": "4bf92f3577b34da6a3ce929d0e0e4736"', '"jsonPayload.note_id": "n-81"', '"status": 503', "ask for a field inside it by name", "truncated"]:
        expect(p in text, f"{p!r} missing from {text!r}")
    for a in ["a private note", "owner_note", "invented-agent", "ana@pebble.invalid", '"a": 1']:
        expect(a not in text, f"{a!r} printed in {text!r}")


case("logs: named fields only, a field by name, the rest left out, truncated at the limit", projected, False)


def not_truncated():
    g.call = answering({("gcloud", "logging", "read"): (0, json.dumps(ENTRIES[:1]), "")})
    text = printed(lambda: g.logs(logs_args(), g.Out()))
    expect("truncated" not in text, f"called truncated below the limit: {text!r}")


case("logs: below the limit is not truncated", not_truncated, False)


def logs_empty_names_project():
    g.call = answering({("gcloud", "logging", "read"): (0, "[]", "")})
    text = printed(lambda: g.logs(logs_args(), g.Out()))
    expect(PROD in text and "no traffic" not in text, f"empty read said {text!r}")


case("logs: an empty answer names the project", logs_empty_names_project, False)


# ---- the personal data check ----------------------------------------------------------------
def redacts(value, needles, count):
    def go():
        out = g.Out()
        text = printed(lambda: (out.emit(value), out.close()))
        for n in needles:
            expect(n not in text, f"{n!r} printed in {text!r}")
        expect(f"{count} value(s) redacted" in text, f"wrong count in {text!r}")

    return go


checks = [
    ("an email", {"m": "from ana@pebble.invalid"}, ["ana@pebble.invalid"], 1),
    ("a formatted CPF", {"m": "cpf 123.456.789-09 failed"}, ["123.456.789-09"], 1),
    ("a formatted CNPJ", {"m": "12.345.678/0001-95"}, ["12.345.678/0001-95"], 1),
    ("a bare CPF", {"m": "doc=12345678909"}, ["12345678909"], 1),
    ("a long free text", {"m": "lorem " * 120}, ["lorem lorem"], 1),
    ("inside a list", {"m": ["ana@pebble.invalid", "bo@pebble.invalid"]}, ["pebble.invalid"], 2),
    ("a trace, a time and a task id stay", {"t": "4bf92f3577b34da6a3ce929d0e0e4736", "at": "2026-03-02T10:15:00Z", "task": "1234567890123456789"}, [], 0),
]
for name, value, needles, count in checks:
    case(f"personal data: {name}", redacts(value, needles, count), False)


def keeps_technical():
    out = g.Out()
    value = {"t": "4bf92f3577b34da6a3ce929d0e0e4736", "task": "1234567890123456789", "rev": "notes-api-00042"}
    expect(out.value(value) == value, f"changed {out.value(value)!r}")


case("personal data: technical ids pass unchanged", keeps_technical, False)


# ---- databases in development only, the list read from the documentation base -------------
dev = [
    ("a development project", wave_with(ENV_DOC), DEV, False),
    ("production, though prose names it", wave_with(ENV_DOC), PROD, True),
    ("a project missing from the list", wave_with(ENV_DOC), "pebble-dev-2", True),
    ("a document with no development block", wave_with("pebble-dev-1 is development"), DEV, True),
    ("no environments document", {("wave", "doc", "list"): (0, "[]", "")}, DEV, True),
    ("the wave CLI missing", {("wave",): (127, "", "wave is not installed")}, DEV, True),
    ("the wave session expired", {("wave",): (1, "wave: 401: sessao expirada", "")}, DEV, True),
    ("an answer that isn't JSON", {("wave",): (0, "<html>", "")}, DEV, True),
]
for name, table, project, refused in dev:

    def go(t=table, p=project):
        g.call = answering(t)
        g.require_dev(p)

    case(f"development: {name}", go, refused)


def body_by_show():
    g.call = answering(
        {
            ("wave", "doc", "list"): (0, json.dumps([{"id": "d1", "data": {"key": "DOC-7"}}]), ""),
            ("wave", "doc", "show", "d1"): (0, json.dumps({"id": "d1", "data": {"body": ENV_DOC}}), ""),
        }
    )
    g.require_dev(DEV)


case("development: a list without the body reads it with show", body_by_show, False)


def no_widening_argument():
    for name in ("sql", "docdb"):
        options = g.parser()._subparsers._group_actions[0].choices[name]._option_string_actions
        expect(not any("dev" in o or "environment" in o for o in options), f"{name} takes {list(options)}")


case("development: no argument can widen the list", no_widening_argument, False)


# ---- SQL in a development database: read only, one SELECT, named fields ----------------------
tmp = pathlib.Path(tempfile.mkdtemp(prefix="gcloud-read-test-"))


def query_file(text):
    path = tmp / f"q{len(list(tmp.iterdir()))}.sql"
    path.write_text(text)
    return str(path)


def sql_case(text, project=DEV, limit="2", psql=(0, "note_id,status\nn-81,failed\n", "")):
    def go():
        g.call = answering({**wave_with(ENV_DOC), ("psql",): psql})
        out = run(["sql", query_file(text), "--project", project, "--limit", limit])
        if "refused:" in out:
            raise g.Refusal(out)
        return out

    return go


sqls = [
    ("a SELECT of named fields", "SELECT note_id, status FROM notes WHERE note_id = 'n-81'", DEV, False),
    ("a count", "SELECT COUNT(*) AS n FROM notes", DEV, False),
    ("production", "SELECT note_id FROM notes", PROD, True),
    ("a DELETE", "DELETE FROM notes", DEV, True),
    ("a transaction set to write", "SET TRANSACTION READ WRITE", DEV, True),
    ("two statements", "SELECT 1; DELETE FROM notes", DEV, True),
    ("SELECT *", "SELECT * FROM notes", DEV, True),
    ("SELECT t.*", "SELECT n.* FROM notes n", DEV, True),
    ("a psql command", "SELECT 1 \\! rm -rf /", DEV, True),
]
for name, text, project, refused in sqls:
    case(f"sql: {name}", sql_case(text, project), refused)


def sql_read_only_session():
    out = sql_case("SELECT note_id, status FROM notes -- the last one;")()
    argv, env = calls[-1]
    expect(argv[0] == "psql" and "-X" in argv, f"psql argv {argv}")
    expect(env["PGOPTIONS"] == "-c default_transaction_read_only=on", f"session not read only: {env.get('PGOPTIONS')}")
    expect(argv[-1].endswith("\n) AS bb_read LIMIT 2"), f"not bounded: {argv[-1]!r}")
    expect('"note_id": "n-81"' in out and "truncated" not in out, out)


case("sql: the session opens read only and the query is wrapped in its limit", sql_read_only_session, False)


def sql_redacts_and_truncates():
    out = sql_case("SELECT note_id, contact FROM notes", psql=(0, "note_id,contact\nn-1,ana@pebble.invalid\nn-2,x\n", ""))()
    expect("ana@pebble.invalid" not in out and "1 value(s) redacted" in out and "truncated" in out, out)


case("sql: output passes the personal data check and a full page is truncated", sql_redacts_and_truncates, False)


# ---- the document database: only find, count and an aggregation that doesn't write ---------
def doc_args(**over):
    base = {"project": DEV, "database": "pebble", "collection": "notes", "op": "find", "filter": '{"status": "failed"}', "pipeline": None, "field": ["status", "note_id"], "limit": 5}
    base.update(over)
    return types.SimpleNamespace(**base)


docs = [
    ("a find with named fields", {}, False),
    ("a count", {"op": "count", "field": []}, False),
    ("an aggregation that groups", {"op": "aggregate", "pipeline": '[{"$group": {"_id": "$status", "n": {"$sum": 1}}}]', "field": ["n"]}, False),
    ("$out", {"op": "aggregate", "pipeline": '[{"$out": "copy"}]'}, True),
    ("$merge", {"op": "aggregate", "pipeline": '[{"$merge": {"into": "copy"}}]'}, True),
    ("$merge inside a $facet", {"op": "aggregate", "pipeline": '[{"$facet": {"a": [{"$merge": "x"}]}}]'}, True),
    ("$where in the filter", {"filter": '{"$where": "this.a == 1"}'}, True),
    ("$function in a stage", {"op": "aggregate", "pipeline": '[{"$addFields": {"x": {"$function": {}}}}]'}, True),
    ("a find with no fields named", {"field": []}, True),
    ("a find with no limit", {"limit": None}, True),
    ("a filter that isn't an object", {"filter": "[1]"}, True),
    ("a collection name with code in it", {"collection": "notes'); db.dropDatabase(); ('"}, True),
]
for name, over, refused in docs:
    case(f"docdb: {name}", lambda o=over: g.doc_script(doc_args(**o)), refused)


def doc_script_shape():
    script = g.doc_script(doc_args())
    for p in ["process.env.BB_DEBUG_MONGO_URI", '{"status": 1, "note_id": 1}', ".limit(5)", "EJSON.parse("]:
        expect(p in script, f"{p!r} missing from {script!r}")
    agg = g.doc_script(doc_args(op="aggregate", pipeline='[{"$group": {"_id": "$status", "n": {"$sum": 1}}}]', field=["n"]))
    expect('{\\"$project\\": {\\"n\\": 1}}, {\\"$limit\\": 5}' in agg, f"aggregation not projected and limited: {agg!r}")


case("docdb: the script projects, limits, and reads the connection from the environment", doc_script_shape, False)


def doc_production_refused_before_anything():
    g.call = answering(wave_with(ENV_DOC))
    g.docdb(doc_args(project=PROD), g.Out())


case("docdb: production is refused before mongosh runs", doc_production_refused_before_anything, True)


def doc_uri_off_the_command_line():
    os.environ[g.MONGO_URI_ENV] = "mongodb://invented-user:invented-pass@localhost:27017"
    try:
        g.call = answering({**wave_with(ENV_DOC), ("mongosh",): (0, '[{"_id": "n-1", "status": "failed"}]', "")})
        out = printed(lambda: g.docdb(doc_args(), g.Out()))
        argv = calls[-1][0]
        expect(not any("invented-pass" in a for a in argv), f"the connection string is on the command line: {argv}")
        expect('"status": "failed"' in out, out)
    finally:
        del os.environ[g.MONGO_URI_ENV]


case("docdb: the connection string never reaches the command line", doc_uri_off_the_command_line, False)


# ---- the warehouse past retention: measure's locks, then an aggregate or one id --------------
def wh(text, id_value=None, kind="SELECT", gb=1.0, execute=False, rows=None):
    def go():
        def post(self, path, body):
            if path == "/jobs":
                return {"statistics": {"totalBytesProcessed": str(int(gb * 1e9)), "query": {"statementType": kind}}}
            fields = [{"name": "stage"}, {"name": "n"}]
            return {"schema": {"fields": fields}, "rows": [{"f": [{"v": c} for c in r]} for r in rows or []], "totalRows": str(len(rows or []))}

        g.db.BigQuery.post = post
        try:
            argv = ["warehouse", query_file(text), "--project", PROD] + (["--id", id_value] if id_value else []) + (["--run"] if execute else [])
            out = run(argv)
        finally:
            g.db.BigQuery.post = no_network
        if "refused:" in out:
            raise g.Refusal(out)
        return out

    return go


warehouse = [
    ("an aggregate", "SELECT stage, COUNT(*) AS n FROM logs.app GROUP BY stage", None, False),
    ("rows filtered by one id", "SELECT time, stage FROM logs.app WHERE note_id = @id", "n-81", False),
    ("rows with no id and no aggregate", "SELECT time, message FROM logs.app WHERE severity = 'ERROR'", None, True),
    ("an id with no WHERE on it", "SELECT time, stage FROM logs.app", "n-81", True),
    ("an id widened by OR", "SELECT time FROM logs.app WHERE note_id = @id OR TRUE", "n-81", True),
    ("an id that carries a quote", "SELECT time FROM logs.app WHERE note_id = @id", "n'81", True),
    ("SELECT *", "SELECT * FROM logs.app WHERE note_id = @id", "n-81", True),
    ("a DELETE", "DELETE FROM logs.app WHERE TRUE", None, True),
]
for name, text, id_value, refused in warehouse:
    case(f"warehouse: {name}", wh(text, id_value), refused)

case("warehouse: the dry run classifies it as a write", wh("SELECT COUNT(*) AS n FROM logs.app", kind="DELETE"), True)
case("warehouse: above the byte ceiling on the real run", wh("SELECT COUNT(*) AS n FROM logs.app", gb=25.0, execute=True), True)


def wh_substitutes_and_redacts():
    query = "SELECT stage, COUNT(*) AS n FROM logs.app WHERE note_id = @id GROUP BY stage"
    out = wh(query, "n-81", execute=True, rows=[["upload", "ana@pebble.invalid"]])()
    expect("dry run: would read 1.00 GB" in out and '"stage": "upload"' in out, out)
    expect("ana@pebble.invalid" not in out and "1 value(s) redacted" in out, out)


case("warehouse: dry run first, then the rows pass the personal data check", wh_substitutes_and_redacts, False)
case("warehouse: the id lands as a literal", lambda: expect(g.check_scope("SELECT a FROM t WHERE b = @id", "n-81").endswith("b = 'n-81'"), "no literal"), False)


# ---- temporary files: one directory per run, swept a day later -------------------------------
def with_base(fn):
    def go():
        old = tempfile.tempdir
        tempfile.tempdir = str(tmp / "base")
        pathlib.Path(tempfile.tempdir).mkdir(exist_ok=True)
        try:
            fn(pathlib.Path(tempfile.tempdir).resolve())
        finally:
            tempfile.tempdir = old

    return go


def start_and_close(base):
    g.call = answering({("docker", "image", "rm"): (0, "", "")})
    d = pathlib.Path(run(["start"]).splitlines()[0])
    expect(d.is_dir() and d.parent == base and d.name.startswith("bb-debug-"), f"run directory {d}")
    (d / "images").write_text("gcr.io/x/notes@sha256:abc\n")
    run(["close", str(d)])
    expect(not d.exists(), "the run directory survived close")
    expect(calls and calls[-1][0][-1] == "gcr.io/x/notes@sha256:abc", f"the pulled image wasn't removed: {calls}")


def sweeps_a_day_later(base):
    g.call = answering({("docker", "image", "rm"): (0, "", "")})
    old, fresh, other = base / "bb-debug-old", base / "bb-debug-fresh", base / "someone-else"
    for d in (old, fresh, other):
        d.mkdir()
    two_days = time.time() - 2 * 86400
    os.utime(old, (two_days, two_days))
    os.utime(other, (two_days, two_days))
    text = run(["start"])
    expect(not old.exists() and fresh.exists() and other.exists(), f"swept wrong: {sorted(p.name for p in base.iterdir())}")
    expect("deleted 1" in text, text)


def close_refuses_outside(base):
    g.close(types.SimpleNamespace(run=str(tmp)), g.Out())


case("temporary files: start makes the run's directory, close deletes it with its images", with_base(start_and_close), False)
case("temporary files: a directory left behind is deleted once a day old", with_base(sweeps_a_day_later), False)
case("temporary files: close refuses a directory start didn't make", with_base(close_refuses_outside), True)

shutil.rmtree(tmp, ignore_errors=True)
print()
print(f"{len(failures)} failure(s)" if failures else "every rule behaved as expected")
sys.exit(1 if failures else 0)
