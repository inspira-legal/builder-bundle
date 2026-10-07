"""Tests for the locks in db_read.py, with no network and no credential.

Usage:
    python3 db_read_test.py

Lock 2 is tested against a fake dry-run answer. Every network call is replaced by one that
fails the test, so a case lock 1 refuses also proves nothing left the machine. The data is
invented: a product called Orbit, with boards.
"""

import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location("db", pathlib.Path(__file__).with_name("db_read.py"))
db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db)


def no_network(*_a, **_k):
    raise AssertionError("tried to use the network")


db.BigQuery.post = no_network
db.BigQuery.token = no_network

failures = []


def case(name, fn, refused):
    try:
        fn()
        ok, got = not refused, "passed"
    except db.Refusal as r:
        ok, got = refused, f"refused: {r}"
    except AssertionError as e:
        ok, got = False, f"ERROR: {e}"
    print(f"{'ok    ' if ok else 'FAILED'} | {name} | {got}")
    if not ok:
        failures.append(name)


# ---- lock 1: the text of the query, no network ------------------------------------------
text = [
    ("plain SELECT", "SELECT 1 AS x", False),
    ("WITH ... SELECT", "WITH a AS (SELECT 1 AS x) SELECT * FROM a", False),
    ("SELECT in parentheses", "(SELECT 1)", False),
    ("semicolon at the end", "SELECT 1;\n", False),
    ("; inside a string", "SELECT 'a;b' AS x", False),
    ("; inside a comment", "-- a; b\nSELECT 1 /* c; d */", False),
    ("DELETE", "DELETE FROM `p.d.t` WHERE TRUE", True),
    ("CREATE", "CREATE TABLE `p.d.t` AS SELECT 1 AS x", True),
    ("INSERT", "INSERT INTO `p.d.t` (x) VALUES (1)", True),
    ("UPDATE", "UPDATE `p.d.t` SET x = 1 WHERE TRUE", True),
    ("MERGE", "MERGE `p.d.t` T USING `p.d.s` S ON T.x = S.x WHEN MATCHED THEN DELETE", True),
    ("DROP", "DROP TABLE `p.d.t`", True),
    ("EXPORT DATA", "EXPORT DATA OPTIONS(uri='gs://b/*.csv', format='CSV') AS SELECT 1", True),
    ("script with two SELECTs", "SELECT 1;\nSELECT 2;", True),
    ("script with DECLARE", "DECLARE x INT64 DEFAULT 1;\nSELECT x;", True),
    ("SELECT then DELETE", "SELECT 1; DELETE FROM `p.d.t` WHERE TRUE", True),
    ("DELETE behind a comment", "/* SELECT */ DELETE FROM `p.d.t` WHERE TRUE", True),
    ("empty query", "  -- nothing\n", True),
]
for name, sql, refused in text:
    case(f"text: {name}", lambda s=sql: db.check_text(s), refused)


# ---- lock 2: the type the database returns ----------------------------------------------
def job(kind, gb=1.0):
    q = {"totalBytesProcessed": str(int(gb * 1e9))}
    if kind:
        q["statementType"] = kind
    return {"statistics": {"totalBytesProcessed": str(int(gb * 1e9)), "query": q}}


bq = db.BigQuery("orbit-analytics")
for kind, refused in [
    ("SELECT", False),
    ("DELETE", True),
    ("CREATE_TABLE_AS_SELECT", True),
    ("SCRIPT", True),
    ("INSERT", True),
    (None, True),
]:
    case(f"dry run classifies as {kind or 'nothing'}", lambda k=kind: bq.check_dry_run(job(k)), refused)


# ---- lock 3: cost -----------------------------------------------------------------------
case("cost of 17.4 GB", lambda: db.check_cost(17.4), False)
case("cost of 25 GB", lambda: db.check_cost(25.0), True)


# ---- locks 4 and 5: the output ------------------------------------------------------------
def output(cols, rows):
    return db.BigQuery.normalize(
        {
            "schema": {"fields": [{"name": c, "type": "STRING"} for c in cols]},
            "rows": [{"f": [{"v": v} for v in row]} for row in rows],
        }
    )


outputs = [
    ("aggregate with event_name", ["event_name", "people"], [["board_sub_shared", "119"]], False),
    ("column email", ["email", "n"], [["x", "1"]], True),
    ("column user_email", ["user_email"], [["x"]], True),
    ("column name", ["name"], [["x"]], True),
    ("column client_name", ["client_name", "n"], [["x", "1"]], True),
    ("column user_id", ["user_id"], [["abc"]], True),
    ("column trace_id", ["trace_id"], [["abc"]], True),
    ("email disguised as another column", ["x"], [["someone@example.com"]], True),
    ("long text disguised", ["x"], [["a" * 301]], True),
    ("plan and origin", ["plan", "origin", "people"], [["pro", "toolbar", "40"]], False),
    ("column person_id", ["person_id", "n"], [["p1", "3"]], True),
    ("column client_id", ["client_id", "n"], [["c1", "3"]], True),
    ("column customer_id", ["customer_id"], [["c1"]], True),
    ("column account_id", ["account_id"], [["a1"]], True),
    ("column nome_completo", ["nome_completo"], [["x"]], True),
    ("column nome_cliente", ["nome_cliente"], [["x"]], True),
    ("column razao_social", ["razao_social"], [["x"]], True),
    ("column owner_name", ["owner_name"], [["x"]], True),
    ("a thing's name: plan_name", ["plan_name", "people"], [["pro", "40"]], False),
    ("a thing's name: feature_name", ["feature_name", "people"], [["boards", "40"]], False),
    ("a thing's id: board_id count", ["board_id", "n"], [["b1", "3"]], False),
    ("camelCase: accountBillingId", ["accountBillingId", "n"], [["a1", "3"]], True),
    ("camelCase: portalUserId", ["portalUserId"], [["u1"]], True),
    ("camelCase: workspaceId", ["workspaceId"], [["w1"]], True),
    ("camelCase: userID", ["userID"], [["u1"]], True),
    ("camelCase in a nested record", ["r.accountBillingId"], [["a1"]], True),
    ("compound: account_billing_id", ["account_billing_id"], [["a1"]], True),
    ("compound: user_pseudo_id", ["user_pseudo_id"], [["p1"]], True),
    ("column workspace_id", ["workspace_id"], [["w1"]], True),
    ("column organization_id", ["organization_id"], [["o1"]], True),
    ("column device_id", ["device_id"], [["d1"]], True),
    ("column anonymous_id", ["anonymous_id"], [["x1"]], True),
    ("column visitor_id", ["visitor_id"], [["v1"]], True),
    ("column actor_id", ["actor_id"], [["a1"]], True),
    ("a thing's id: event_id", ["event_id", "n"], [["e1", "3"]], False),
    ("a thing's id: plan_id", ["plan_id", "people"], [["pro", "40"]], False),
    ("a thing's id: document_id", ["document_id", "n"], [["d1", "3"]], False),
    ("a thing's id in camelCase: boardId", ["boardId", "n"], [["b1", "3"]], False),
    ("a count of people: user_count", ["user_count"], [["40"]], False),
    ("ends in id, names no one: paid, valid", ["paid", "valid", "users"], [["40", "38", "41"]], False),
    ("a thing next to a role: account_valid", ["account_valid", "n"], [["true", "3"]], False),
]
for name, cols, rows, refused in outputs:
    case(f"output: {name}", lambda c=cols, r=rows: db.check_output(output(c, r)), refused)

case(
    "output: email inside a nested record",
    lambda: db.check_output(
        db.BigQuery.normalize(
            {
                "schema": {
                    "fields": [
                        {"name": "r", "type": "RECORD", "fields": [{"name": "x", "type": "STRING"}]}
                    ]
                },
                "rows": [{"f": [{"v": {"f": [{"v": "a@b.com"}]}}]}],
            }
        )
    ),
    True,
)
case(
    "output: person column inside a nested record",
    lambda: db.check_output(
        db.BigQuery.normalize(
            {
                "schema": {
                    "fields": [
                        {"name": "r", "type": "RECORD", "fields": [{"name": "email", "type": "STRING"}]}
                    ]
                },
                "rows": [{"f": [{"v": {"f": [{"v": "x"}]}}]}],
            }
        )
    ),
    True,
)


# ---- the adapter: which database, which project -------------------------------------------
case("database: bigquery", lambda: db.adapter("bigquery", "orbit-analytics"), False)
case("database: BigQuery, any case", lambda: db.adapter("BigQuery", "orbit-analytics"), False)
case("database: one with no adapter", lambda: db.adapter("snowflake", "orbit"), True)
case("project: domain-scoped id", lambda: db.adapter("bigquery", "orbit.example:orbit-analytics"), False)
case("project: a path in the id", lambda: db.adapter("bigquery", "orbit/../../x"), True)
case("project: empty", lambda: db.adapter("bigquery", ""), True)



# ---- the error paths: a clean message on stdout, never a traceback ----------------------------
import contextlib
import io
import urllib.error


def stops_cleanly(fn):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            fn()
    except SystemExit as e:
        if e.code == 1 and out.getvalue().strip():
            return
        raise AssertionError(f"exit {e.code!r} with stdout {out.getvalue()!r}")
    raise AssertionError("did not stop")


def unreachable(*_a, **_k):
    raise urllib.error.URLError("no route to host")


def run_main(argv):
    old = sys.argv
    sys.argv = argv
    try:
        db.main()
    finally:
        sys.argv = old


case(
    "a missing query file stops cleanly",
    lambda: stops_cleanly(
        lambda: run_main(["db_read.py", "/nonexistent/q.sql", "--database", "bigquery", "--project", "orbit-analytics"])
    ),
    False,
)
fresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fresh)
fresh.BigQuery.token = lambda self: "t"
fresh.urllib.request.urlopen = unreachable
case(
    "no network stops cleanly",
    lambda: stops_cleanly(lambda: fresh.BigQuery("orbit-analytics").post("/jobs", {})),
    False,
)


class GatewayError(urllib.error.HTTPError):
    def __init__(self):
        super().__init__("https://x", 502, "Bad Gateway", {}, None)

    def read(self, *_a):
        return b"<html>502 Bad Gateway</html>"


def bad_gateway(*_a, **_k):
    raise GatewayError()


fresh.urllib.request.urlopen = bad_gateway
case(
    "an HTTP error with no JSON body stops cleanly",
    lambda: stops_cleanly(lambda: fresh.BigQuery("orbit-analytics").post("/queries", {})),
    False,
)


def run_error_hides_the_value():
    leak = "Bad int64 value: someone@example.com"
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            db.BigQuery.normalize(
                {"error": {"message": leak, "status": "INVALID_ARGUMENT", "errors": [{"reason": "invalidQuery", "message": leak}]}}
            )
    except SystemExit:
        pass
    printed = out.getvalue()
    if "someone@example.com" in printed or "invalidQuery" not in printed:
        raise AssertionError(f"the run error printed {printed!r}")


case("a failed run shows the reason, never the row's value", run_error_hides_the_value, False)

print()
print(f"{len(failures)} failure(s)" if failures else "every lock behaved as expected")
sys.exit(1 if failures else 0)
