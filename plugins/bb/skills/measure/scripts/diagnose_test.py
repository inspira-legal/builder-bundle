"""Tests for diagnose.py, with no network, no CLI and no credential.

Usage:
    python3 diagnose_test.py

Every command the diagnosis would run is replaced by a fake that answers from a table, and the
fake records how it was called: a test proves both what the person reads and that the login
check never kept a token. The data is invented: a product called Orbit.
"""

import contextlib
import importlib.util
import io
import pathlib
import sys

spec = importlib.util.spec_from_file_location("diagnose", pathlib.Path(__file__).with_name("diagnose.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

failures = []
TOKEN = " ".join(d.db.BigQuery.TOKEN)
GUARD = str(d.GUARD)


class Machine:
    """A fake machine: which tools exist, and what each command answers."""

    def __init__(self, tools=("wave", "gcloud", "gh"), answers=None):
        self.tools = set(tools)
        self.answers = answers or {}
        self.calls = []

    def which(self, name):
        return f"/usr/bin/{name}" if name in self.tools else None

    def run(self, command, keep_output=True):
        key = "guard" if GUARD in command else " ".join(command)
        self.calls.append((key, keep_output))
        return self.answers.get(key, (0, ""))


def diagnose(machine, argv):
    d.which, d.run = machine.which, machine.run
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = d.main(argv)
    return code, out.getvalue()


def case(name, machine, argv, code, *expected, absent=()):
    got, printed = diagnose(machine, argv)
    problems = []
    if got != code:
        problems.append(f"exit {got}, expected {code}")
    problems += [f"no {text!r}" for text in expected if text not in printed]
    problems += [f"printed {text!r}" for text in absent if text in printed]
    print(f"{'ok    ' if not problems else 'FAILED'} | {name} | {'; '.join(problems) or 'passed'}")
    if problems:
        failures.append(name)
    return machine


ACCESS = ["access", "--database", "bigquery", "--project", "orbit-analytics", "--table", "orbit-analytics.events.all"]
REPO = ["--repo", "orbit/app", "--path", "src/events.config.ts", "--ref", "main"]
WHO = "someone@example.com"

# ---- the documentation base ----------------------------------------------------------------
case("docs: all ready", Machine(), ["docs"], 0, "ok   | wave", "the diagnosis passed")
case("docs: wave not installed", Machine(tools=("gcloud",)), ["docs"], 1, "stop | wave", d.SETUP)
case(
    "docs: wave session expired, and doctor's output stays hidden",
    Machine(answers={"wave doctor": (1, f"auth ✗ 401\nquem {WHO}")}),
    ["docs"],
    1,
    "stop | wave",
    "`wave doctor`",
    absent=(WHO,),
)

# ---- the database --------------------------------------------------------------------------
m = case("access: all ready", Machine(), ACCESS, 0, "ok   | gcloud", "ok   | database", "the diagnosis passed")
if (TOKEN, False) not in m.calls or (TOKEN, True) in m.calls:
    print("FAILED | access: the login check keeps no token | the token command kept its output")
    failures.append("token")
else:
    print("ok     | access: the login check keeps no token | passed")
case(
    "access: gcloud not installed",
    Machine(tools=("wave",)),
    ACCESS,
    1,
    "stop | gcloud",
    "not installed",
    "https://cloud.google.com/sdk/docs/install",
)
case(
    "access: gcloud login expired",
    Machine(answers={TOKEN: (1, "")}),
    ACCESS,
    1,
    "stop | gcloud",
    "expired",
    "gcloud auth login --update-adc",
)
case(
    "access: no read permission",
    Machine(answers={"guard": (1, d.db.BigQuery.DENIED + "\n")}),
    ACCESS,
    1,
    "stop | database",
    "access document",
)
case(
    "access: a database with no adapter",
    Machine(),
    ["access", "--database", "snowflake", "--project", "orbit", "--table", "events"],
    1,
    "stop | database",
    "no adapter",
)
m = case(
    "access: a table id that carries a query is refused before any command",
    Machine(),
    ACCESS[:-1] + ["t` WHERE TRUE; DELETE FROM `t"],
    1,
    "is not a table id",
)
if m.calls:
    print("FAILED | access: the bad table id ran a command | " + repr(m.calls))
    failures.append("bad table ran")

# ---- the code, when the activation list lives there ----------------------------------------
case("repo: all ready", Machine(), ACCESS + REPO, 0, "ok   | gh", "ok   | catalog", "the diagnosis passed")
case("repo: gh not installed", Machine(tools=("wave", "gcloud")), ACCESS + REPO, 1, "stop | gh", "cli.github.com")
case(
    "repo: gh logged out, and its output stays hidden",
    Machine(answers={"gh auth status": (1, f"not logged in as {WHO}")}),
    ACCESS + REPO,
    1,
    "stop | gh",
    "gh auth login",
    absent=(WHO,),
)
case(
    "repo: no read access to the repository",
    Machine(answers={"gh api repos/orbit/app --silent": (1, "")}),
    ACCESS + REPO,
    1,
    "stop | gh",
    "cannot read orbit/app",
)
case(
    "repo: the catalog file is not there",
    Machine(answers={"gh api repos/orbit/app/contents/src/events.config.ts?ref=main --silent": (1, "")}),
    ACCESS + REPO,
    1,
    "stop | catalog",
    "no src/events.config.ts on main",
)
case("repo: a path that climbs out", Machine(), ACCESS + ["--repo", "orbit/app", "--path", "../x"], 1, "stop | catalog")
case(
    "repo: not an OWNER/REPO",
    Machine(),
    ACCESS + ["--repo", "orbit app", "--path", "src/events.config.ts"],
    1,
    "stop | gh",
    "not an OWNER/REPO",
)
for name, half in (("--path without --repo", REPO[2:4]), ("--repo without --path", REPO[0:2])):
    m = case(f"repo: {name} is refused before any command", Machine(), ACCESS + half, 1, "stop | catalog", "go together")
    if m.calls:
        print(f"FAILED | repo: {name} ran a command | " + repr(m.calls))
        failures.append(f"{name} ran")
case(
    "repo: the database stops first, and gh is never asked",
    Machine(answers={TOKEN: (1, "")}),
    ACCESS + REPO,
    1,
    "stop | gcloud",
    absent=("| gh |",),
)

print()
print(f"{len(failures)} failure(s)" if failures else "every check behaved as expected")
sys.exit(1 if failures else 0)
