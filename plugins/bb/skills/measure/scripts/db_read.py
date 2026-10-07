"""Read-only query to the company's database, through five locks.

Usage:
    python3 db_read.py QUERY.sql --database DATABASE --project PROJECT
    python3 db_read.py QUERY.sql --database DATABASE --project PROJECT --run

Without --run the script only measures what the query would read. With --run it measures,
and runs the query when every lock passes. The database and the project come from the
company's `data` document (references/company-definitions.md at the plugin root).

The locks live here, and not in the text of whoever calls the script, because a skill's text
can be forgotten and code cannot. Five, in this order:

1. Local, no network: one statement, and it starts as a read (SELECT or WITH). A DELETE, a
   CREATE or a script is refused before anything leaves the machine.
2. The database classifies the statement in a dry run. Anything it does not call a read is
   refused, including when it names no type at all.
3. Cost: above MAX_GB, refused. The same ceiling travels with the real run, so the database
   refuses on its side too. Rewrite the query to fit; never raise the ceiling.
4. Output columns: a column that names a person or a conversation (name, email, user_id,
   trace_id...) is refused before any row is shown.
5. Output content: a value shaped like an email, or a long free text, refuses the whole
   output. Locks 4 and 5 are a net, not a guarantee: only aggregate numbers leave here.

Locks 1, 3, 4 and 5 are the same for every database. Lock 2, the dry run, the real run and
the credential belong to an adapter, one per database. BigQuery is the first; a database with
no adapter is refused by name.

Standard library only, so it runs on any machine with Python 3.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

MAX_GB = 20  # cost ceiling, in GB read per query
LONG_TEXT = 300  # characters; an aggregate number or an event label never comes close
TIMEOUT_MS = 120000
MAX_ROWS = 1000

# A column that points at a person, a customer or a conversation. The name is only a net:
# `email AS x` passes it, which is why the content is checked too (EMAIL and LONG_TEXT).
# A column naming a thing (`event_name`, `plan_name`) passes; one naming who did it does not.
# The name is matched in snake_case, so `accountBillingId` is read as `account_billing_id`.
WHO = (
    r"user|person|people|pessoa|usuario|member|client|cliente|customer|account|tenant|org"
    r"|organization|organizacao|workspace|company|empresa|office|escritorio|lawyer|advogado"
    r"|owner|author|actor|visitor|anonymous|pseudo|device|session|trace|chat|conversation"
    r"|thread|distinct"
)
PERSONAL = re.compile(
    r"^(name|nome|username|cpf|cnpj|oab|ssn|phone|telefone|celular|mobile|razao_?social"
    r"|nome_?fantasia)$"
    r"|^(name|nome)_"
    r"|(^|_)(full|first|last|given|family|display|" + WHO + r")_?(name|nome)$"
    r"|e_?mail"
    r"|(^|_)(" + WHO + r")_?id$"
    r"|(^|_)(" + WHO + r")(_[a-z0-9]+)+_id$"  # a role word further back: user_pseudo_id
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class Refusal(Exception):
    """The query or its output did not pass a lock. The message says which one and why."""


def fail(message: str) -> None:
    """Stop with a message on stdout, where the caller reads it, and a non-zero exit."""
    print(message)
    sys.exit(1)


# ---- lock 1: local, no network ---------------------------------------------------------


def code_only(sql: str) -> str:
    """Replace comments, quoted strings and backtick names with a space.

    What is left is the code, so a `;` inside a string or a comment is never counted as a
    statement boundary, and the first word is read from the code itself.
    """
    out, i, n = [], 0, len(sql)
    while i < n:
        c, two, three = sql[i], sql[i : i + 2], sql[i : i + 3]
        if two == "--" or c == "#":
            end = sql.find("\n", i)
            i = n if end == -1 else end
            out.append(" ")
        elif two == "/*":
            end = sql.find("*/", i + 2)
            i = n if end == -1 else end + 2
            out.append(" ")
        elif three in ("'''", '"""'):
            end = sql.find(three, i + 3)
            i = n if end == -1 else end + 3
            out.append(" '' ")
        elif c in ("'", '"', "`"):
            j = i + 1
            while j < n and sql[j] != c:
                j += 2 if sql[j] == "\\" else 1
            i = j + 1
            out.append(" '' " if c != "`" else " t ")
        else:
            out.append(c)
            i += 1
    return "".join(out)


def check_text(sql: str) -> None:
    code = code_only(sql).strip().rstrip(";").strip()
    if not code:
        raise Refusal("the query is empty")
    if ";" in code:
        raise Refusal("more than one statement (a script); send a single query")
    first = re.match(r"[\s(]*([A-Za-z]+)", code)
    word = first.group(1).upper() if first else ""
    if word not in ("SELECT", "WITH"):
        raise Refusal(f"not a read: the query starts with {word or '?'}; only SELECT or WITH")


# ---- lock 3: cost ----------------------------------------------------------------------


def check_cost(gb: float) -> None:
    if gb > MAX_GB:
        raise Refusal(
            f"would read {gb:.2f} GB, above the {MAX_GB} GB ceiling; simplify the query, "
            "never raise the ceiling"
        )


# ---- locks 4 and 5: what may leave -----------------------------------------------------


def snake(column: str) -> str:
    """The last part of a column name in snake_case: `r.portalUserId` -> `portal_user_id`."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", column.split(".")[-1]).lower()


def check_output(result: dict) -> None:
    """`result` is the adapter's normalized output: column names and flattened values."""
    for column in result["columns"]:
        if PERSONAL.search(snake(column)):
            raise Refusal(
                f"the output has the column '{column}', which identifies a person or a "
                "conversation; return aggregate numbers only (e.g. COUNT(DISTINCT user_id))"
            )
    for value in result["values"]:
        text = str(value)
        if EMAIL.search(text):
            raise Refusal("the output has a value shaped like an email; no row was shown")
        if len(text) > LONG_TEXT:
            raise Refusal(
                f"the output has a text above {LONG_TEXT} characters, shaped like free text "
                "(a conversation, a prompt or a document); no row was shown"
            )


def show(result: dict) -> None:
    print(" | ".join(result["header"]))
    for row in result["rows"]:
        print(" | ".join("" if v is None else str(v) for v in row))
    if result["total"] > len(result["rows"]):
        print(f"-- showing {len(result['rows'])} of {result['total']} rows; aggregate further")


# ---- adapters: lock 2, the runs and the credential, one per database -------------------


class BigQuery:
    """BigQuery over its REST API, with the person's application default credentials."""

    RENEW = (
        "the database credential expired or is missing; renew it with: "
        "gcloud auth login --update-adc (the company's access document has the rest)"
    )
    READ = "SELECT"  # the statement type BigQuery returns for a read
    PROJECT = re.compile(r"^(?:[a-z][a-z0-9.-]*:)?[a-z][a-z0-9-]{4,28}[a-z0-9]$")

    def __init__(self, project: str):
        if not self.PROJECT.match(project):
            raise Refusal(f"'{project}' is not a BigQuery project id")
        self.api = f"https://bigquery.googleapis.com/bigquery/v2/projects/{project}"

    def token(self) -> str:
        try:
            return subprocess.check_output(
                ["gcloud", "auth", "application-default", "print-access-token"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            fail(self.RENEW)

    def post(self, path: str, body: dict) -> dict:
        request = urllib.request.Request(
            self.api + path,
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 401:
                fail(self.RENEW)
            try:
                return json.loads(error.read())
            except ValueError:
                fail(f"the database answered HTTP {error.code}, with no readable error; try again")
        except urllib.error.URLError as error:
            fail(f"the database could not be reached ({error.reason}); check the network and try again")

    def dry_run(self, sql: str) -> dict:
        """A simulated job: nothing runs and nothing is billed.

        The simulated job, and not the `jobs.query` shortcut, is what returns the statement
        type in `statistics.query.statementType`.
        """
        return self.post(
            "/jobs",
            {"configuration": {"dryRun": True, "query": {"query": sql, "useLegacySql": False}}},
        )

    def check_dry_run(self, job: dict) -> float:
        """Lock 2. Returns the GB the query would read."""
        if "error" in job:
            fail("ERROR: " + job["error"]["message"])
        stats = job.get("statistics", {})
        kind = stats.get("query", {}).get("statementType")
        if kind != self.READ:
            raise Refusal(f"the database did not classify it as a read (type: {kind or 'none given'})")
        read = stats.get("totalBytesProcessed") or stats.get("query", {}).get("totalBytesProcessed")
        return int(read or 0) / 1e9

    def run(self, sql: str) -> dict:
        return self.post(
            "/queries",
            {
                "query": sql,
                "useLegacySql": False,
                "timeoutMs": TIMEOUT_MS,
                "maxResults": MAX_ROWS,
                "maximumBytesBilled": str(MAX_GB * 10**9),  # the ceiling again, on BigQuery's side
            },
        )

    @staticmethod
    def normalize(response: dict) -> dict:
        """The API's row format (f/v, records and lists) as columns, values and rows.

        A failed run reports only the error's reason, never its message: the database repeats
        the offending row's value there (`Bad int64 value: someone@example.com`), and that
        text would skip locks 4 and 5. The dry run already returned the message of any error
        in the query's text, so what fails here fails on the data.
        """
        if "error" in response:
            errors = response["error"].get("errors") or [{}]
            reason = errors[0].get("reason") or response["error"].get("status") or "unknown"
            fail(
                f"ERROR: the query failed while running (reason: {reason}); the database's "
                "message is not shown because it can carry a row's value. Check the casts and "
                "the functions applied to each column"
            )
        if not response.get("jobComplete", True):
            fail("the query ran past 2 minutes and did not return; simplify it or run it again")

        def names(fields, prefix=""):
            out = []
            for field in fields:
                name = prefix + field["name"]
                out.append(name)
                out += names(field.get("fields", []), name + ".")
            return out

        def flatten(v):
            if isinstance(v, dict):
                if "f" in v:
                    for cell in v["f"]:
                        yield from flatten(cell)
                elif "v" in v:
                    yield from flatten(v["v"])
            elif isinstance(v, list):
                for item in v:
                    yield from flatten(item)
            elif v is not None:
                yield v

        fields = response.get("schema", {}).get("fields", [])
        raw = response.get("rows", [])
        return {
            "columns": names(fields),
            "values": list(flatten(raw)),
            "header": [f["name"] for f in fields],
            "rows": [[cell.get("v") for cell in row["f"]] for row in raw],
            "total": int(response.get("totalRows", len(raw))),
        }


ADAPTERS = {"bigquery": BigQuery}


def adapter(database: str, project: str):
    cls = ADAPTERS.get(database.strip().lower())
    if cls is None:
        known = ", ".join(sorted(ADAPTERS))
        raise Refusal(f"no adapter for the database '{database}'; the guard speaks to: {known}")
    return cls(project)


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only query, through five locks.")
    parser.add_argument("query", help="a file holding one SQL query")
    parser.add_argument("--database", required=True, help="from the company's data document")
    parser.add_argument("--project", required=True, help="from the company's data document")
    parser.add_argument("--run", action="store_true", help="run the query when every lock passes")
    args = parser.parse_args()
    try:
        with open(args.query, encoding="utf-8") as f:
            sql = f.read()
    except OSError as error:
        fail(f"could not read the query file {args.query}: {error.strerror}")
    try:
        db = adapter(args.database, args.project)
        check_text(sql)
        gb = db.check_dry_run(db.dry_run(sql))
        print(f"-- would read {gb:.2f} GB")
        if not args.run:
            return
        check_cost(gb)
        result = db.normalize(db.run(sql))
        check_output(result)
        show(result)
    except Refusal as refusal:
        fail(f"refused: {refusal}")


if __name__ == "__main__":
    main()
