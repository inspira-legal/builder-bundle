#!/usr/bin/env bun
/**
 * Validates YAML frontmatter in SKILL.md files.
 *
 * Usage:
 *   bun validate-frontmatter.ts                    # scan current directory
 *   bun validate-frontmatter.ts /path/to/dir       # scan specific directory
 *   bun validate-frontmatter.ts file1.md file2.md  # validate specific files
 */

import { parse as parseYaml } from "yaml";
import { readdir, readFile } from "fs/promises";
import { basename, join, relative, resolve } from "path";

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

function validateSkill(frontmatter: Record<string, unknown>): ValidationIssue[] {
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

  return issues;
}

async function findSkillFiles(baseDir: string): Promise<{ path: string }[]> {
  const results: { path: string }[] = [];

  async function walk(dir: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === ".git") continue;
        await walk(fullPath);
      } else if (entry.name === "SKILL.md") {
        results.push({ path: fullPath });
      }
    }
  }

  await walk(baseDir);
  return results;
}

async function main() {
  const args = process.argv.slice(2);

  let files: { path: string }[];
  let baseDir: string;

  if (args.length > 0 && args.every((a) => a.endsWith(".md"))) {
    baseDir = process.cwd();
    files = args.map((a) => ({ path: resolve(a) }));
  } else {
    baseDir = args[0] || process.cwd();
    files = await findSkillFiles(baseDir);
  }

  let totalErrors = 0;

  console.log(`Validating ${files.length} skill files...\n`);

  for (const { path: filePath } of files) {
    const rel = relative(baseDir, filePath);
    const content = await readFile(filePath, "utf-8");
    const result = parseFrontmatter(content);

    const issues: ValidationIssue[] = [];

    if (result.error) {
      issues.push({ level: "error", message: result.error });
    } else {
      issues.push(...validateSkill(result.frontmatter));
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
