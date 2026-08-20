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

/** `Date["now"]()` reaches the same calls past the three above, and only ever on purpose. */
const SUBSCRIPTED_GLOBAL_REGEX = /\b(Date|Math)\s*\[/;

const META_REGEX = /export\s+const\s+meta\s*=\s*\{/;
const PARALLEL_REGEX = /\bparallel\s*\(/g;
const LOOP_REGEX = /\b(?:for|while|do)\b/;

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

/** The heads whose closing `)` is followed by a statement, which a regex may open. */
const CONTROL_HEADS = new Set(["if", "while", "for", "switch", "catch", "with"]);

/** The index of the last non-space character at or before `from`, or -1. */
function prevCode(out: string[], from: number): number {
  let j = from;
  while (j >= 0 && /\s/.test(out[j])) j--;
  return j;
}

/** The identifier ending at `end`, with where it starts; an empty word when none ends there. */
function wordEndingAt(out: string[], end: number): { word: string; start: number } {
  let k = end;
  while (k >= 0 && /[A-Za-z0-9_$]/.test(out[k])) k--;
  return { word: out.slice(k + 1, end + 1).join(""), start: k + 1 };
}

function regexCanStart(out: string[], at: number): boolean {
  const j = prevCode(out, at - 1);
  if (j < 0) return true;

  const ch = out[j];
  // `if (ok) /re/.test(x)` opens a statement with a regex, so a `)` means division only when it
  // closed a value. Read as division, the regex body stays in the code stream, where a
  // `parallel(` or a `Date.now(` inside it counts as the call it spells.
  if (ch === ")") {
    let depth = 0;
    let k = j;
    for (; k >= 0; k--) {
      if (out[k] === ")") depth++;
      else if (out[k] === "(" && --depth === 0) break;
    }
    return k >= 0 && CONTROL_HEADS.has(wordEndingAt(out, prevCode(out, k - 1)).word);
  }
  if (/[\]}"'`]/.test(ch)) return false;
  if (!/[A-Za-z0-9_$]/.test(ch)) return true;

  const { word, start } = wordEndingAt(out, j);
  // A keyword reached through a property access is a property name: `obj.in / 2` divides, and
  // reading it as a regex swallows the code after it, hiding whatever call lives there.
  if (out[prevCode(out, start - 1)] === ".") return false;
  return KEYWORDS_BEFORE_REGEX.has(word);
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

type MetaBlock = { start: number; end: number };

/** The span from `export const meta = {` to its matching brace, or null when absent. */
function findMetaBlock(code: string): MetaBlock | null {
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

/** The bare words a literal may contain; every other identifier is a reference. */
const META_LITERAL_WORDS = new Set(["true", "false", "null", "undefined"]);
const IDENTIFIER_REGEX = /[A-Za-z_$][A-Za-z0-9_$]*/g;
const PHASES_KEY_REGEX = /\bphases\s*:\s*\[/;
const PHASE_CALL_REGEX = /\bphase\s*\(/g;
const TITLE_REGEX = /\btitle\s*:\s*(['"])(.*?)\1/g;

/**
 * The platform reads `meta` before the script runs, so a variable, a call or a spread there
 * has nothing to resolve against: it has to be a pure literal, which the interpolation check
 * alone does not prove. Inside the block every identifier is either a property key, which a
 * `:` follows, or a value, and a value that is a bare word is one of the four above.
 */
function metaLiteralIssues(code: string, meta: MetaBlock): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const block = code.slice(meta.start, meta.end);

  for (const hit of block.matchAll(IDENTIFIER_REGEX)) {
    if (hit.index === undefined) continue;
    // The exponent of `1e3` and the digits of `0x1f` match as identifiers; a digit before
    // the match is what tells them apart from a word standing on its own.
    if (hit.index > 0 && /[0-9]/.test(block[hit.index - 1])) continue;
    if (META_LITERAL_WORDS.has(hit[0])) continue;
    if (/^\s*:/.test(block.slice(hit.index + hit[0].length))) continue;

    issues.push({
      level: "error",
      message: `"${hit[0]}" on line ${lineOf(code, meta.start + hit.index)} inside "export const meta": it must be a pure literal, so no variables and no calls`,
    });
  }

  const spread = block.indexOf("...");
  if (spread !== -1) {
    issues.push({
      level: "error",
      message: `Spread on line ${lineOf(code, meta.start + spread)} inside "export const meta": it must be a pure literal`,
    });
  }

  return issues;
}

/** How many entries `meta.phases` declares, or null when the block declares no `phases`. */
function countPhaseEntries(block: string): number | null {
  const key = block.match(PHASES_KEY_REGEX);
  if (!key || key.index === undefined) return null;

  let depth = 0;
  let braces = 0;
  let entries = 0;

  for (let i = key.index + key[0].length - 1; i < block.length; i++) {
    const ch = block[i];
    if (ch === "[") depth++;
    else if (ch === "]") {
      depth--;
      if (depth === 0) break;
    } else if (ch === "{") {
      if (depth === 1 && braces === 0) entries++;
      braces++;
    } else if (ch === "}" && braces > 0) braces--;
  }

  return entries;
}

/** The titles the phase() calls pass, read off the source because `code` has its strings blanked. */
function calledTitles(source: string, code: string, meta: MetaBlock): (string | null)[] {
  const titles: (string | null)[] = [];
  for (const hit of code.matchAll(PHASE_CALL_REGEX)) {
    const at = hit.index ?? 0;
    if (at >= meta.start && at < meta.end) continue;
    const arg = source.slice(at + hit[0].length).match(/^\s*(['"])(.*?)\1\s*\)/);
    titles.push(arg ? arg[2] : null);
  }
  return titles;
}

/**
 * The platform matches a `meta.phases` entry to a `phase()` call by title, so counts that agree
 * while the titles do not are still a progress display that lies: the declared entry never fires,
 * and the call arrives with no entry of its own.
 */
function phaseIssues(source: string, code: string, meta: MetaBlock): ValidationIssue[] {
  const declared = countPhaseEntries(code.slice(meta.start, meta.end));
  if (declared === null) return [];

  const called = calledTitles(source, code, meta);
  if (declared !== called.length) {
    return [
      {
        level: "error",
        message: `meta.phases declares ${declared} entries against ${called.length} phase() calls: the platform matches them by title, so a stale declaration is a progress display that lies`,
      },
    ];
  }

  const titles = [...source.slice(meta.start, meta.end).matchAll(TITLE_REGEX)].map((hit) => hit[2]);
  // A computed title reads as null and a titleless entry leaves the two lists uneven; either way
  // there is nothing to compare by name, and the count above is the whole check.
  if (titles.length !== declared || called.some((title) => title === null)) return [];

  const orphans = called.filter((title) => !titles.includes(title));
  const unused = titles.filter((title) => !called.includes(title));
  if (!orphans.length && !unused.length) return [];

  return [
    {
      level: "error",
      message: `meta.phases and the phase() calls disagree on titles (declared, never called: ${unused.join(", ") || "none"}; called, never declared: ${orphans.join(", ") || "none"}): the platform matches them by title, so each side without a partner becomes a progress group of its own`,
    },
  ];
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

  // `?.(` is an optional call and `?.` an optional access. Both are flattened, at the same width
  // so every line number below still lands on the real line, because `Date?.now?.()` is the
  // forbidden call spelled around the check for it.
  const code = blankNonCode(source)
    .replace(/\?\.(\s*\()/g, "  $1")
    .replace(/\?\./g, " .");

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
  } else {
    issues.push(...metaLiteralIssues(code, meta));

    const block = code.slice(meta.start, meta.end);
    // A `phases` entry carries `title` and `detail`, so either key here is meta's own.
    for (const key of ["name", "description"]) {
      if (!new RegExp(`\\b${key}\\s*:`).test(block)) {
        issues.push({
          level: "error",
          message: `"export const meta" declares no ${key}: the platform reads it for the permission dialog and for the workflow list`,
        });
      }
    }

    issues.push(...phaseIssues(source, code, meta));
  }

  const parallels = [...code.matchAll(PARALLEL_REGEX)];
  if (parallels.length !== 1) {
    issues.push({
      level: "error",
      message: `Found ${parallels.length} parallel() calls, expected exactly 1: the tasks share one working tree, so only stage zero fans out`,
    });
  } else {
    const loop = code.match(LOOP_REGEX);
    const fanOut = parallels[0].index ?? 0;
    if (loop && loop.index !== undefined && loop.index < fanOut) {
      issues.push({
        level: "error",
        message: `The parallel() call on line ${lineOf(code, fanOut)} comes after the loop on line ${lineOf(code, loop.index)}: stage zero proves the ground before the first task runs, so the fan-out precedes the task loop`,
      });
    }
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

  const subscript = code.match(SUBSCRIPTED_GLOBAL_REGEX);
  if (subscript?.index !== undefined) {
    issues.push({
      level: "error",
      message: `${subscript[1]}[...] on line ${lineOf(code, subscript.index)}: a subscript reaches the calls above past the check for them`,
    });
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
