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

import { readdir, readFile } from "fs/promises";
import { basename, dirname, join, relative, resolve } from "path";

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

interface ValidationIssue {
  level: "error" | "warning";
  message: string;
}

/** The block from `export const meta = {` to its matching brace, or null when absent. */
function findMetaBlock(source: string): string | null {
  const match = source.match(META_REGEX);
  if (!match || match.index === undefined) return null;

  const open = match.index + match[0].length - 1;
  let depth = 0;
  for (let i = open; i < source.length; i++) {
    const ch = source[i];
    if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) return source.slice(open, i + 1);
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

  const meta = findMetaBlock(source);
  if (meta === null) {
    issues.push({
      level: "error",
      message: 'Missing "export const meta = { ... }": the platform requires it first',
    });
  } else if (meta.includes("${")) {
    issues.push({
      level: "error",
      message: 'Interpolation inside "export const meta": it must be a pure literal',
    });
  }

  const parallels = source.match(PARALLEL_REGEX) ?? [];
  if (parallels.length !== 1) {
    issues.push({
      level: "error",
      message: `Found ${parallels.length} parallel() calls, expected exactly 1: the tasks share one working tree, so only stage zero fans out`,
    });
  }

  for (const { label, regex } of FORBIDDEN_CALLS) {
    const hit = source.match(regex);
    if (hit && hit.index !== undefined) {
      issues.push({
        level: "error",
        message: `${label} on line ${lineOf(source, hit.index)}: it throws at runtime and would break resume`,
      });
    }
  }

  return issues;
}

function isWorkflowScript(filePath: string): boolean {
  return filePath.endsWith(".js") && basename(dirname(filePath)) === "workflows";
}

async function findWorkflowScripts(baseDir: string): Promise<string[]> {
  const results: string[] = [];

  async function walk(dir: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === ".git") continue;
        await walk(fullPath);
      } else if (isWorkflowScript(fullPath)) {
        results.push(fullPath);
      }
    }
  }

  await walk(baseDir);
  return results;
}

async function main() {
  const args = process.argv.slice(2);

  let files: string[];
  let baseDir: string;

  if (args.length > 0 && args.every((a) => a.endsWith(".js"))) {
    baseDir = process.cwd();
    files = args.map((a) => resolve(a)).filter(isWorkflowScript);
  } else {
    baseDir = args[0] || process.cwd();
    files = await findWorkflowScripts(baseDir);
  }

  let totalErrors = 0;

  console.log(`Validating ${files.length} workflow scripts...\n`);

  for (const filePath of files) {
    const rel = relative(baseDir, filePath);
    const source = await readFile(filePath, "utf-8");
    const issues = validateSource(source);

    if (issues.length > 0) {
      console.log(rel);
      for (const issue of issues) {
        const prefix = issue.level === "error" ? "  ERROR" : "  WARN ";
        console.log(`${prefix}: ${issue.message}`);
        if (issue.level === "error") totalErrors++;
      }
      console.log();
    }
  }

  console.log("---");
  console.log(`Validated ${files.length} workflow scripts: ${totalErrors} errors`);

  if (totalErrors > 0) process.exit(1);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(2);
});
