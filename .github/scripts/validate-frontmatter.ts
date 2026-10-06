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

import { readFile } from "fs/promises";
import { basename } from "path";

import {
  type FileIssues,
  type ValidationIssue,
  isAgentFile,
  parseFrontmatter,
  reportAndExit,
  resolveTargets,
  runMain,
} from "./lib/validate-common";

/** Agents in this plugin are read-only roles; a write tool there is a defect, not a choice. */
const FORBIDDEN_AGENT_TOOLS = ["Write", "Edit", "MultiEdit", "NotebookEdit"];

type FileKind = "skill" | "agent";

function classify(filePath: string): FileKind | null {
  if (basename(filePath) === "SKILL.md") return "skill";
  if (isAgentFile(filePath)) return "agent";
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

  if (kind === "skill" && typeof frontmatter["description"] === "string") {
    issues.push(...validateSkillDescription(frontmatter["description"]));
  }

  if (kind === "agent") issues.push(...validateAgentTools(frontmatter["tools"]));

  return issues;
}

/** claude.ai cuts the description at this length on upload; Claude Code reads it whole. */
const MAX_SKILL_DESCRIPTION = 1024;

/**
 * claude.ai rejects a skill whose description breaks its upload rules, while Claude Code
 * reads the file as is, so the defect only shows on claude.ai unless the build catches it.
 */
function validateSkillDescription(description: string): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (description.length > MAX_SKILL_DESCRIPTION) {
    issues.push({
      level: "error",
      message: `"description" has ${description.length} characters; claude.ai allows at most ${MAX_SKILL_DESCRIPTION}`,
    });
  }
  if (/[<>]/.test(description)) {
    issues.push({
      level: "error",
      message: '"description" contains "<" or ">"; claude.ai rejects XML tags there',
    });
  }

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

async function main() {
  const { baseDir, files, notes } = await resolveTargets(
    process.argv.slice(2),
    (p) => classify(p) !== null,
  );

  const skills = files.filter((f) => classify(f) === "skill").length;
  console.log(`Validating ${skills} skill files and ${files.length - skills} agent files...\n`);

  const reports: FileIssues[] = [];

  for (const path of files) {
    const content = await readFile(path, "utf-8");
    const result = parseFrontmatter(content);
    const issues: ValidationIssue[] = [];

    if (result.error) {
      issues.push({ level: "error", message: result.error });
    } else {
      issues.push(...validateFrontmatter(result.frontmatter, classify(path) as FileKind));
    }

    reports.push({ path, issues });
  }

  reportAndExit(baseDir, reports, notes, "files");
}

runMain(main);
