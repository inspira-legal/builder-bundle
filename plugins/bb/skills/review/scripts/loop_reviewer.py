#!/usr/bin/env python3
"""Find and run the review loop's outside reviewer.

  loop_reviewer.py detect
      -> {"reviewer": "codex" | "bb-review-verifier", "path": str | null, "version": str | null}
  loop_reviewer.py run --repo DIR --prompt-file FILE [--timeout SECONDS]
      -> {"ok": bool, "output": str, "error": str | null, "exit_code": int | null}

`run` invokes the outside reviewer read only and returns its last message verbatim; the
caller parses it. Stdlib only.
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile

FALLBACK = "bb-review-verifier"


def detect():
    path = shutil.which("codex")
    if not path:
        return {"reviewer": FALLBACK, "path": None, "version": None}
    try:
        proc = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=30
        )
        version = (proc.stdout or proc.stderr).strip() or None
        if proc.returncode != 0:
            return {"reviewer": FALLBACK, "path": path, "version": None}
    except (OSError, subprocess.TimeoutExpired):
        return {"reviewer": FALLBACK, "path": path, "version": None}
    return {"reviewer": "codex", "path": path, "version": version}


def run(repo, prompt_file, timeout):
    path = shutil.which("codex")
    if not path:
        return {"ok": False, "output": "", "error": "codex not on PATH", "exit_code": None}
    try:
        with open(prompt_file, encoding="utf-8") as fh:
            prompt = fh.read()
    except OSError as exc:
        return {"ok": False, "output": "", "error": str(exc), "exit_code": None}
    fd, out_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    cmd = [
        path,
        "exec",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--cd",
        repo,
        "--output-last-message",
        out_path,
        "-",
    ]
    try:
        # Its own process group (POSIX), so a timeout also stops whatever codex spawned.
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            _, stderr = proc.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            if hasattr(os, "killpg"):
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            proc.communicate()
            return {"ok": False, "output": "", "error": f"timeout after {timeout}s", "exit_code": None}
        with open(out_path, encoding="utf-8") as fh:
            output = fh.read().strip()
    except OSError as exc:
        return {"ok": False, "output": "", "error": str(exc), "exit_code": None}
    finally:
        try:
            os.remove(out_path)
        except OSError:
            pass
    ok = proc.returncode == 0 and bool(output)
    error = None if ok else (stderr.strip()[-2000:] or "empty output")
    return {"ok": ok, "output": output, "error": error, "exit_code": proc.returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detect")
    run_p = sub.add_parser("run")
    run_p.add_argument("--repo", required=True)
    run_p.add_argument("--prompt-file", required=True)
    run_p.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    result = detect() if args.cmd == "detect" else run(args.repo, args.prompt_file, args.timeout)
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
