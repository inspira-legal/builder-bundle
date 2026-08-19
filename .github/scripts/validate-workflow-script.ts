#!/usr/bin/env bun
/**
 * Validates the workflow scripts the plugin ships (any .js directly under a
 * `workflows/` directory) against what the Workflow platform demands of them.
 *
 * Usage:
 *   bun validate-workflow-script.ts                   # scan current directory
 *   bun validate-workflow-script.ts /path/to/dir      # scan specific directory
 *   bun validate-workflow-script.ts a.js b.js         # validate specific files
 */

import { readFile } from "fs/promises";
import { basename, dirname } from "path";

import {
  type FileIssues,
  type ValidationIssue,
  reportAndExit,
  resolveTargets,
  runMain,
} from "./lib/validate-common";

/**
 * These break `resumeFromRunId`: a resumed run replays the script and would take a
 * different path on the second pass. The platform throws on them at runtime, which is
 * mid-build; here it is a failed commit.
 */
const FORBIDDEN_CALLS = [
  { label: "Date.now()", regex: /\bDate\s*\.\s*now\s*\(/ },
  { label: "new Date()", regex: /\bnew\s+Date\s*\(/ },
  { label: "Math.random()", regex: /\bMath\s*\.\s*random\s*\(/ },
];

const META_REGEX = /export\s+const\s+meta\s*=\s*\{/;
const PARALLEL_REGEX = /\bparallel\s*\(/g;

/** A `/` here opens a regex literal rather than dividing; anything else is division. */
const KEYWORDS_BEFORE_REGEX = new Set([
  "return",
  "typeof",
  "instanceof",
  "in",
  "of",
  "new",
  "delete",
  "void",
  "throw",
  "case",
  "do",
  "else",
  "yield",
  "await",
]);

function regexCanStart(out: string[], at: number): boolean {
  let j = at - 1;
  while (j >= 0 && /\s/.test(out[j])) j--;
  if (j < 0) return true;

  const ch = out[j];
  if (/[)\]}"'`]/.test(ch)) return false;
  if (!/[A-Za-z0-9_$]/.test(ch)) return true;

  let k = j;
  while (k >= 0 && /[A-Za-z0-9_$]/.test(out[k])) k--;
  return KEYWORDS_BEFORE_REGEX.has(out.slice(k + 1, j + 1).join(""));
}

type Frame = { kind: "code"; braces: number } | { kind: "template" };

/**
 * Replaces every character that isn't code — comment bodies, string bodies, template text,
 * regex bodies — with a space, so the scanners below read only code while every index still
 * lands on the same line. Without it a `parallel(` inside a comment counted as a call and a
 * literal `${` inside a plain string read as interpolation. Template `${` and `}` survive as
 * themselves: that pair is what makes a `meta` block non-literal, and what sits between them
 * is real code.
 */
function blankNonCode(source: string): string {
  const out = source.split("");
  const n = source.length;
  const stack: Frame[] = [{ kind: "code", braces: 0 }];
  let i = 0;

  const blank = (at: number) => {
    if (out[at] !== "\n") out[at] = " ";
  };

  while (i < n) {
    const top = stack[stack.length - 1];
    const ch = source[i];
    const next = source[i + 1];

    if (top.kind === "template") {
      if (ch === "`") {
        stack.pop();
        i++;
      } else if (ch === "\\") {
        blank(i);
        if (i + 1 < n) blank(i + 1);
        i += 2;
      } else if (ch === "$" && next === "{") {
        stack.push({ kind: "code", braces: 0 });
        i += 2;
      } else {
        blank(i);
        i++;
      }
      continue;
    }

    if (ch === "/" && next === "/") {
      while (i < n && source[i] !== "\n") blank(i++);
      continue;
    }

    if (ch === "/" && next === "*") {
      blank(i);
      blank(i + 1);
      i += 2;
      while (i < n && !(source[i] === "*" && source[i + 1] === "/")) blank(i++);
      if (i < n) {
        blank(i);
        blank(i + 1);
        i += 2;
      }
      continue;
    }

    if (ch === '"' || ch === "'") {
      i++;
      // An unterminated quote stops at the newline instead of swallowing the rest of the file.
      while (i < n && source[i] !== ch && source[i] !== "\n") {
        if (source[i] === "\\") {
          blank(i);
          if (i + 1 < n) blank(i + 1);
          i += 2;
          continue;
        }
        blank(i++);
      }
      if (i < n && source[i] === ch) i++;
      continue;
    }

    if (ch === "`") {
      stack.push({ kind: "template" });
      i++;
      continue;
    }

    if (ch === "/" && regexCanStart(out, i)) {
      i++;
      let inClass = false;
      while (i < n && source[i] !== "\n") {
        const c = source[i];
        if (c === "\\") {
          blank(i);
          if (i + 1 < n) blank(i + 1);
          i += 2;
          continue;
        }
        if (c === "[") inClass = true;
        else if (c === "]") inClass = false;
        else if (c === "/" && !inClass) break;
        blank(i++);
      }
      if (i < n && source[i] === "/") i++;
      continue;
    }

    if (ch === "{") {
      top.braces++;
      i++;
      continue;
    }

    if (ch === "}") {
      // Depth zero inside an interpolation: this brace closes it, so hand the template back.
      if (top.braces === 0 && stack.length > 1) stack.pop();
      else top.braces--;
      i++;
      continue;
    }

    i++;
  }

  return out.join("");
}

/** The span from `export const meta = {` to its matching brace, or null when absent. */
function findMetaBlock(code: string): { start: number; end: number } | null {
  const match = code.match(META_REGEX);
  if (!match || match.index === undefined) return null;

  const open = match.index + match[0].length - 1;
  let depth = 0;
  for (let i = open; i < code.length; i++) {
    const ch = code[i];
    if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) return { start: open, end: i + 1 };
    }
  }
  return null;
}

/**
 * A workflow script is neither a module nor a plain script: it carries `export const meta`
 * and a top-level `return` with top-level `await`, which no single parse mode accepts. The
 * platform runs the body inside an async function, so the parse gets the same shape: the
 * `export` keyword dropped and the source wrapped. The prefix carries no newline, so a
 * reported line number still points at the real line.
 */
function probeOf(source: string): string {
  return `async function __probe() {${source.replace(/\bexport\s+const\b/g, "const")}\n}`;
}

function lineOf(source: string, index: number): number {
  return source.slice(0, index).split("\n").length;
}

function validateSource(source: string): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  try {
    new Bun.Transpiler({ loader: "js" }).transformSync(probeOf(source));
  } catch (err) {
    issues.push({
      level: "error",
      message: `Does not parse: ${err instanceof Error ? err.message : err}`,
    });
    return issues; // Nothing below says anything useful about a file that won't parse.
  }

  const code = blankNonCode(source);

  const meta = findMetaBlock(code);
  if (meta === null) {
    issues.push({
      level: "error",
      message: 'Missing "export const meta = { ... }": the platform requires it first',
    });
  } else if (code.slice(meta.start, meta.end).includes("${")) {
    issues.push({
      level: "error",
      message: 'Interpolation inside "export const meta": it must be a pure literal',
    });
  }

  const parallels = code.match(PARALLEL_REGEX) ?? [];
  if (parallels.length !== 1) {
    issues.push({
      level: "error",
      message: `Found ${parallels.length} parallel() calls, expected exactly 1: the tasks share one working tree, so only stage zero fans out`,
    });
  }

  for (const { label, regex } of FORBIDDEN_CALLS) {
    const hit = code.match(regex);
    if (hit && hit.index !== undefined) {
      issues.push({
        level: "error",
        message: `${label} on line ${lineOf(code, hit.index)}: it throws at runtime and would break resume`,
      });
    }
  }

  return issues;
}

function isWorkflowScript(filePath: string): boolean {
  return filePath.endsWith(".js") && basename(dirname(filePath)) === "workflows";
}

async function main() {
  const { baseDir, files, notes } = await resolveTargets(process.argv.slice(2), isWorkflowScript);

  console.log(`Validating ${files.length} workflow scripts...\n`);

  const reports: FileIssues[] = [];

  for (const path of files) {
    const source = await readFile(path, "utf-8");
    reports.push({ path, issues: validateSource(source) });
  }

  reportAndExit(baseDir, reports, notes, "workflow scripts");
}

runMain(main);
