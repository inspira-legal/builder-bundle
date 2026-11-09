"""Check that this machine can measure, before any query: the tools, the logins, the access.

Usage:
    python3 diagnose.py docs
    python3 diagnose.py access --database DATABASE --project PROJECT --table TABLE
                               [--repo OWNER/REPO --path PATH --ref BRANCH]

`docs` runs first, before any company document is read: can the documentation base be read?
`access` runs once the `data` and `usage` documents are read, because they name the database,
the project, the events table and, when the activation list lives in code, the repository and
the file. The two halves are references/diagnosis.md in this skill.

Each check prints one line, `ok` or `stop`, and the first `stop` ends the run with exit 1: a
later check depends on the one before it. A stop names the step the person takes, in a
terminal. The person always logs in themselves. This script never asks for, reads, copies or
shows a token: the login check sends the token to /dev/null and keeps only whether one came
back, and the output of `wave doctor` and `gh auth status`, which name the person, is never
printed.

The database checks reuse the guard (scripts/db_read.py at the plugin root): its adapter owns
the CLI, the login command and the messages, and the read check is a dry run through the guard
itself, so nothing runs and nothing is billed.

Standard library only.
"""

import argparse
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

GUARD = pathlib.Path(__file__).resolve().parents[3] / "scripts" / "db_read.py"
_spec = importlib.util.spec_from_file_location("db_read", GUARD)
db = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(db)

TIMEOUT = 60  # seconds; a check that hangs is a stop, never a wait without end
SETUP = "inspira-legal/builder-setup"
WAVE_MISSING = (
    f"the wave CLI is not installed; install it with {SETUP} (its README has the command for "
    "each system), then run this again"
)
WAVE_FAILED = (
    "the wave session expired or the documentation base did not answer; run `wave doctor` in "
    "a terminal: it says what failed and how to log in again"
)
GH_MISSING = (
    "the gh CLI is not installed; install it from https://cli.github.com, then log in from a "
    "terminal with: gh auth login"
)
GH_LOGGED_OUT = "gh is not logged in; log in from a terminal with: gh auth login"
PAIR = (
    "--repo and --path go together: the repository and the catalog file the usage document "
    "names; pass both, or neither when the list does not live in code"
)

# A table id, an `owner/repo` and a file path go into a command or a query, so each is held
# to the characters its kind uses. Anything else is refused before it reaches a command. A
# table id keeps `:` for a domain-scoped project, such as `example.com:orbit.events.all`.
TABLE = re.compile(r"^[A-Za-z0-9_.:-]+$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PATH = re.compile(r"^[A-Za-z0-9_.@/-]+$")
REF = re.compile(r"^[A-Za-z0-9_./-]+$")


def which(name):
    return shutil.which(name)


def run(command, keep_output=True):
    """Run a command; return (exit code, stdout). With keep_output false, stdout is discarded.

    A command that cannot start or that hangs past TIMEOUT returns a non-zero code, so the
    check it belongs to stops instead of raising.
    """
    try:
        done = subprocess.run(
            command,
            stdout=subprocess.PIPE if keep_output else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return done.returncode, done.stdout if keep_output else ""


class Stop(Exception):
    """A check failed. The message is the step the person takes."""


def report(name, detail, ok=True):
    print(f"{'ok  ' if ok else 'stop'} | {name} | {detail}")


# ---- the documentation base ----------------------------------------------------------------


def check_docs():
    if which("wave") is None:
        raise Stop(("wave", WAVE_MISSING))
    code, _ = run(["wave", "doctor"], keep_output=False)
    if code != 0:
        raise Stop(("wave", WAVE_FAILED))
    report("wave", "installed, and `wave doctor` passes")


# ---- the database --------------------------------------------------------------------------


def check_database(database, project, table):
    try:
        adapter = db.adapter(database, project)
    except db.Refusal as refusal:
        raise Stop(("database", str(refusal)))
    if not TABLE.match(table):
        raise Stop(("database", f"'{table}' is not a table id; take it from the data document"))
    cli = type(adapter)
    if which(cli.CLI) is None:
        raise Stop((cli.CLI, cli.INSTALL))
    code, _ = run(cli.TOKEN, keep_output=False)
    if code != 0:
        raise Stop((cli.CLI, cli.RENEW))
    report(cli.CLI, "installed, and the login is valid")

    probe = f"SELECT 1 AS probe FROM `{table}` LIMIT 1\n"
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as f:
        f.write(probe)
    try:
        command = [sys.executable, str(GUARD), f.name, "--database", database, "--project", project]
        code, out = run(command)
    finally:
        os.unlink(f.name)
    if code != 0:
        lines = [line for line in out.splitlines() if line.strip()]
        raise Stop(("database", lines[-1] if lines else "the dry run failed with no message"))
    report("database", f"a dry run over {table} passes: nothing ran, nothing was billed")


# ---- the code, when the activation list lives there ----------------------------------------


def check_repo(repo, path, ref):
    if not REPO.match(repo):
        raise Stop(("gh", f"'{repo}' is not an OWNER/REPO; take it from the usage document"))
    if which("gh") is None:
        raise Stop(("gh", GH_MISSING))
    code, _ = run(["gh", "auth", "status"], keep_output=False)
    if code != 0:
        raise Stop(("gh", GH_LOGGED_OUT))
    code, _ = run(["gh", "api", f"repos/{repo}", "--silent"], keep_output=False)
    if code != 0:
        raise Stop(
            (
                "gh",
                f"your GitHub account cannot read {repo}, where the usage document says the "
                "activation list lives: the name is wrong, or the account has no read access. "
                "Check the name against the usage document, then ask the repository's owners "
                "for read access",
            )
        )
    report("gh", f"logged in, and {repo} is readable")
    if not PATH.match(path) or ".." in path.split("/") or not REF.match(ref):
        raise Stop(("catalog", f"'{path}' on '{ref}' is not a file path and a branch"))
    code, _ = run(["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}", "--silent"], keep_output=False)
    if code != 0:
        raise Stop(
            (
                "catalog",
                f"{repo} has no {path} on {ref}; the usage document points at a file that is not "
                "there, so say so and read no copy",
            )
        )
    report("catalog", f"{path} is readable on {ref}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check that this machine can measure.")
    sub = parser.add_subparsers(dest="half", required=True)
    sub.add_parser("docs", help="the documentation base: the wave CLI and its session")
    access = sub.add_parser("access", help="the database and, when named, the repository")
    access.add_argument("--database", required=True, help="from the company's data document")
    access.add_argument("--project", required=True, help="from the company's data document")
    access.add_argument("--table", required=True, help="the events table the data document names")
    access.add_argument("--repo", help="OWNER/REPO, when the usage document puts the list in code")
    access.add_argument("--path", help="the catalog file in that repository")
    access.add_argument("--ref", default="main", help="the branch the usage document names")
    args = parser.parse_args(argv)
    try:
        if args.half == "docs":
            check_docs()
        else:
            if bool(args.repo) != bool(args.path):
                raise Stop(("catalog", PAIR))
            check_database(args.database, args.project, args.table)
            if args.repo:
                check_repo(args.repo, args.path, args.ref)
    except Stop as stop:
        name, detail = stop.args[0]
        report(name, detail, ok=False)
        return 1
    print("the diagnosis passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
