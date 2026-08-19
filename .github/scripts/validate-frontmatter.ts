#!/usr/bin/env bun
/**
 * Validates YAML frontmatter in SKILL.md files and in agent definitions
 * (any .md directly under an `agents/` directory).
 *
 * Usage:
 *   bun validate-frontmatter.ts                    # scan current directory
 *   bun validate-frontmatter.ts /path/to/dir       # scan specific directory
 *   bun validate-frontmatter.ts file1.md file2.md  # validate specific files
 */

import { parse as parseYaml } from "yaml";
import { readdir, readFile } from "fs/promises";
import { basename, dirname, join, relative, resolve } from "path";

/** Agents in this plugin are read-only roles; a write tool there is a defect, not a choice. */
const FORBIDDEN_AGENT_TOOLS = ["Write", "Edit", "MultiEdit", "NotebookEdit"];

const FRONTMATTER_REGEX = /^---\s*\n([\s\S]*?)---\s*\n?/;

interface ParseResult {
  frontmatter: Record<string, unknown>;
  error?: string;
}

function parseFrontmatter(markdown: string): ParseResult {
  const match = markdown.match(FRONTMATTER_REGEX);

  if (!match) {
    return { frontmatter: {}, error: "No frontmatter found" };
  }

  try {
    const parsed = parseYaml(match[1] || "");
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return { frontmatter: parsed as Record<string, unknown> };
    }
    return {
      frontmatter: {},
      error: `YAML parsed but result is not an object (got ${typeof parsed})`,
    };
  } catch (err) {
    return {
      frontmatter: {},
      error: `YAML parse failed: ${err instanceof Error ? err.message : err}`,
    };
  }
}

interface ValidationIssue {
  level: "error" | "warning";
  message: string;
}

type FileKind = "skill" | "agent";

function classify(filePath: string): FileKind | null {
  if (basename(filePath) === "SKILL.md") return "skill";
  if (filePath.endsWith(".md") && basename(dirname(filePath)) === "agents") return "agent";
  return null;
}

function validateFrontmatter(
  frontmatter: Record<string, unknown>,
  kind: FileKind,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (!frontmatter["name"] || typeof frontmatter["name"] !== "string") {
    issues.push({ level: "error", message: 'Missing required "name" field' });
  }
  if (!frontmatter["description"] || typeof frontmatter["description"] !== "string") {
    issues.push({
      level: "error",
      message: 'Missing required "description" field',
    });
  }

  if (kind === "agent") issues.push(...validateAgentTools(frontmatter["tools"]));

  return issues;
}

/**
 * The `tools:` list is how far the read-only rule is enforced rather than asked for,
 * so a write tool landing in it fails the build instead of waiting for review.
 */
function validateAgentTools(tools: unknown): ValidationIssue[] {
  if (tools === undefined) {
    return [
      {
        level: "error",
        message: 'Missing "tools" field: an agent without it inherits every tool',
      },
    ];
  }

  const listed = Array.isArray(tools)
    ? tools.map(String)
    : typeof tools === "string"
      ? tools.split(",")
      : null;

  if (listed === null) {
    return [
      {
        level: "error",
        message: `"tools" must be a list or a comma-separated string (got ${typeof tools})`,
      },
    ];
  }

  const names = listed.map((t) => t.trim()).filter(Boolean);
  const forbidden = names.filter((t) => FORBIDDEN_AGENT_TOOLS.includes(t) || t === "*");

  if (forbidden.length > 0) {
    const list = forbidden.join(", ");
    return [
      {
        level: "error",
        message: `Write-capable tools in "tools": ${list}; bb agents are read-only roles`,
      },
    ];
  }

  return [];
}

async function findValidatableFiles(baseDir: string): Promise<{ path: string; kind: FileKind }[]> {
  const results: { path: string; kind: FileKind }[] = [];

  async function walk(dir: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === ".git") continue;
        await walk(fullPath);
      } else {
        const kind = classify(fullPath);
        if (kind) results.push({ path: fullPath, kind });
      }
    }
  }

  await walk(baseDir);
  return results;
}

async function main() {
  const args = process.argv.slice(2);

  let files: { path: string; kind: FileKind }[];
  let baseDir: string;

  if (args.length > 0 && args.every((a) => a.endsWith(".md"))) {
    baseDir = process.cwd();
    files = args
      .map((a) => resolve(a))
      .map((path) => ({ path, kind: classify(path) }))
      .filter((f): f is { path: string; kind: FileKind } => f.kind !== null);
  } else {
    baseDir = args[0] || process.cwd();
    files = await findValidatableFiles(baseDir);
  }

  let totalErrors = 0;

  const skills = files.filter((f) => f.kind === "skill").length;
  console.log(`Validating ${skills} skill files and ${files.length - skills} agent files...\n`);

  for (const { path: filePath, kind } of files) {
    const rel = relative(baseDir, filePath);
    const content = await readFile(filePath, "utf-8");
    const result = parseFrontmatter(content);

    const issues: ValidationIssue[] = [];

    if (result.error) {
      issues.push({ level: "error", message: result.error });
    } else {
      issues.push(...validateFrontmatter(result.frontmatter, kind));
    }

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
  console.log(`Validated ${files.length} files: ${totalErrors} errors`);

  if (totalErrors > 0) process.exit(1);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(2);
});
