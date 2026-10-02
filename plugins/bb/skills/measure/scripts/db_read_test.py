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

print()
print(f"{len(failures)} failure(s)" if failures else "every lock behaved as expected")
sys.exit(1 if failures else 0)
