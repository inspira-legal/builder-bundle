/**
 * What every validator under `.github/scripts/` does the same way: walk a tree, resolve
 * argv into files, print issues, exit. Each validator keeps its own rules and its own
 * header line; the tree walk and the CLI shape live here so a change to either is made
 * once.
 */

import { readdir, stat } from "fs/promises";
import { join, relative, resolve } from "path";

const SKIP_DIRS = new Set(["node_modules", ".git"]);

export interface ValidationIssue {
  level: "error" | "warning";
  message: string;
}

export interface FileIssues {
  path: string;
  issues: ValidationIssue[];
}

export interface Targets {
  baseDir: string;
  files: string[];
  /** What argv named and this validator will not read; printed before the per-file issues. */
  notes: ValidationIssue[];
}

/** Every file under `baseDir` the predicate keeps, `node_modules` and `.git` skipped. */
export async function walkFiles(
  baseDir: string,
  keep: (filePath: string) => boolean,
): Promise<string[]> {
  const results: string[] = [];

  async function walk(dir: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(entry.name)) continue;
        await walk(fullPath);
      } else if (keep(fullPath)) {
        results.push(fullPath);
      }
    }
  }

  await walk(baseDir);
  return results;
}

/**
 * Splits argv into the files to validate. A path is a directory or a file by what it is on
 * disk: inferring that from the extension turned a mixed `dir file.js` call into a readdir
 * on a file, which exited 2 having validated nothing. Anything argv named explicitly and
 * this validator will not read comes back as a note, because a silent skip prints the same
 * "0 errors" a clean run does.
 */
export async function resolveTargets(
  args: string[],
  keep: (filePath: string) => boolean,
): Promise<Targets> {
  if (args.length === 0) {
    const baseDir = process.cwd();
    return { baseDir, files: await walkFiles(baseDir, keep), notes: [] };
  }

  const dirs: string[] = [];
  const files: string[] = [];
  const notes: ValidationIssue[] = [];

  for (const arg of args) {
    const path = resolve(arg);
    const stats = await stat(path).catch(() => null);

    if (stats === null) {
      notes.push({ level: "error", message: `${arg}: no such file or directory` });
    } else if (stats.isDirectory()) {
      dirs.push(path);
    } else if (keep(path)) {
      files.push(path);
    } else {
      notes.push({ level: "warning", message: `${arg}: not a file this validator reads, skipped` });
    }
  }

  const baseDir = dirs[0] ?? process.cwd();
  for (const dir of dirs) files.push(...(await walkFiles(dir, keep)));

  return { baseDir, files, notes };
}

/** Prints the notes, then one block per file with issues, then the tail. Exits 1 on any error. */
export function reportAndExit(
  baseDir: string,
  reports: FileIssues[],
  notes: ValidationIssue[],
  label: string,
): void {
  let totalErrors = 0;

  for (const note of notes) {
    console.log(`${prefixOf(note)}: ${note.message}`);
    if (note.level === "error") totalErrors++;
  }
  if (notes.length > 0) console.log();

  for (const { path, issues } of reports) {
    if (issues.length === 0) continue;
    console.log(relative(baseDir, path));
    for (const issue of issues) {
      console.log(`${prefixOf(issue)}: ${issue.message}`);
      if (issue.level === "error") totalErrors++;
    }
    console.log();
  }

  console.log("---");
  console.log(`Validated ${reports.length} ${label}: ${totalErrors} errors`);

  if (totalErrors > 0) process.exit(1);
}

function prefixOf(issue: ValidationIssue): string {
  return issue.level === "error" ? "  ERROR" : "  WARN ";
}

/** The tail every validator shares: an unexpected throw is exit 2, not a stack on stdout. */
export function runMain(main: () => Promise<void>): void {
  main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(2);
  });
}
