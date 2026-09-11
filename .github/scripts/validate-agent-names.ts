#!/usr/bin/env bun
/**
 * Validates that every agent dispatch the plugin writes names an agent the platform can
 * resolve. The platform publishes a plugin's agents under the plugin's own name, so
 * `plugins/bb/agents/bb-reuse-check.md` answers to `bb:bb-reuse-check` and to nothing else,
 * and a name written bare throws at dispatch time, which is mid-run.
 *
 * The valid set is derived, never written down: each agent's frontmatter `name`, prefixed
 * with the `name` field of the plugin manifest. The frontmatter is what the platform
 * resolves, so it is what this reads, and an agent file whose basename disagrees with its
 * own `name` is itself an error.
 *
 * Two shapes fail: a bb agent's name written without the plugin prefix, and a prefixed name
 * with no such agent. Any other name passes in silence, so a skill that dispatches a
 * platform agent is not a false failure and no hand-kept list of platform agents has to stay
 * current.
 *
 * Usage:
 *   bun validate-agent-names.ts                     # scan plugins/bb/
 *   bun validate-agent-names.ts /path/to/dir        # scan specific directory
 *   bun validate-agent-names.ts a.js b.md           # validate specific files
 */

import { readFile } from "fs/promises";
import { basename, join, resolve, sep } from "path";

import {
  type FileIssues,
  type ValidationIssue,
  isAgentFile,
  lineOf,
  parseFrontmatter,
  reportAndExit,
  resolveTargets,
  runMain,
  walkFiles,
} from "./lib/validate-common";

/**
 * The rule spans the workflow script and the skills' prose, so the scope is both, and only
 * inside the plugin: `.bb/` and `CHANGELOG.md` quote a broken spelling in order to describe
 * it, and reading them would turn a record of the bug into the bug.
 */
const PLUGIN_DIR = resolve(import.meta.dir, "..", "..", "plugins", "bb");
const AGENTS_DIR = join(PLUGIN_DIR, "agents");
const PLUGIN_MANIFEST = join(PLUGIN_DIR, ".claude-plugin", "plugin.json");

/**
 * A dispatch is the two keys and nothing else: the workflow script's `agentType` and the
 * Agent tool's `subagent_type`, with the value quoted, bare or inside backticks. An agent
 * name mentioned anywhere else, a file path or a role named in a sentence, is not a dispatch.
 */
const DISPATCH_REGEX =
  /\b(agentType|subagent_type)\s*:\s*(?:"([^"\n]+)"|'([^'\n]+)'|`([^`\n]+)`|([A-Za-z0-9:_-]+))/g;

interface KnownAgents {
  /** The plugin's own name, the namespace the platform publishes its agents under. */
  prefix: string;
  /** Every agent's frontmatter `name`, unprefixed. */
  names: Set<string>;
  /** What the derivation found wrong, by agent file. */
  issues: Map<string, ValidationIssue[]>;
  /** What left the set underivable, so the run reports it instead of checking against nothing. */
  fatal: ValidationIssue[];
}

function keep(filePath: string): boolean {
  if (!filePath.startsWith(PLUGIN_DIR + sep)) return false;
  return filePath.endsWith(".js") || filePath.endsWith(".md");
}

function frontmatterName(markdown: string): string | null {
  const { frontmatter } = parseFrontmatter(markdown);
  const name = frontmatter["name"];
  return typeof name === "string" && name.trim() ? name.trim() : null;
}

/**
 * Reads the manifest and the agent files. A set that cannot be derived is not a clean run:
 * it comes back in `fatal`, so it reaches the caller on stdout with every other finding
 * rather than on a channel of its own.
 */
async function deriveKnownAgents(): Promise<KnownAgents> {
  const manifest = JSON.parse(await readFile(PLUGIN_MANIFEST, "utf-8")) as Record<string, unknown>;
  const declared = manifest["name"];
  const prefix = typeof declared === "string" ? declared.trim() : "";
  const fatal: ValidationIssue[] = [];

  if (!prefix) {
    fatal.push({
      level: "error",
      message: `${PLUGIN_MANIFEST}: no "name" field, so no namespace to check against`,
    });
  }

  const agentFiles = await walkFiles(AGENTS_DIR, isAgentFile);

  const names = new Set<string>();
  const issues = new Map<string, ValidationIssue[]>();

  for (const path of agentFiles) {
    const name = frontmatterName(await readFile(path, "utf-8"));
    const found: ValidationIssue[] = [];

    if (name === null) {
      found.push({
        level: "error",
        message: 'No frontmatter "name": that field is what the platform resolves the agent by',
      });
    } else {
      names.add(name);
      const expected = basename(path, ".md");
      if (name !== expected) {
        found.push({
          level: "error",
          message: `Frontmatter name "${name}" disagrees with the file name "${expected}": the two are what keep a dispatch and its agent from drifting apart unseen`,
        });
      }
    }

    if (found.length > 0) issues.set(path, found);
  }

  if (names.size === 0) {
    fatal.push({
      level: "error",
      message: `${AGENTS_DIR}: no agent names derived, which would read every correct dispatch as unknown`,
    });
  }

  return { prefix, names, issues, fatal };
}

function dispatchIssues(source: string, known: KnownAgents): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const namespace = `${known.prefix}:`;

  for (const match of source.matchAll(DISPATCH_REGEX)) {
    const key = match[1];
    const value = (match[2] ?? match[3] ?? match[4] ?? match[5] ?? "").trim();
    if (!value) continue;

    const line = lineOf(source, match.index ?? 0);

    if (known.names.has(value)) {
      issues.push({
        level: "error",
        message: `Line ${line}: \`${key}: ${value}\` is missing the plugin's namespace; the platform publishes that agent as \`${namespace}${value}\` and throws on the bare name`,
      });
    } else if (value.startsWith(namespace) && !known.names.has(value.slice(namespace.length))) {
      issues.push({
        level: "error",
        message: `Line ${line}: \`${key}: ${value}\` names an agent this plugin does not ship`,
      });
    }
  }

  return issues;
}

async function main() {
  const known = await deriveKnownAgents();

  if (known.fatal.length > 0) {
    console.log("No dispatch was checked: the set of agent names could not be derived.\n");
    reportAndExit(PLUGIN_DIR, [], known.fatal, "files");
    return;
  }

  // `keep()` already narrows to the plugin, so a bare run starts there instead of walking the
  // repo down to a directory it computed two lines above. It runs on every commit.
  const args = process.argv.slice(2);
  const { baseDir, files, notes } = await resolveTargets(
    args.length > 0 ? args : [PLUGIN_DIR],
    keep,
  );

  console.log(
    `Validating ${files.length} files under plugins/bb/ against ${known.names.size} agent names...\n`,
  );

  const reports: FileIssues[] = [];
  const pending = new Map(known.issues);

  for (const path of files) {
    const source = await readFile(path, "utf-8");
    const issues = [...(pending.get(path) ?? []), ...dispatchIssues(source, known)];
    pending.delete(path);
    reports.push({ path, issues });
  }

  for (const [path, issues] of pending) reports.push({ path, issues });

  reportAndExit(baseDir, reports, notes, "files");
}

runMain(main);
