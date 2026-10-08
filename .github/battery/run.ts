#!/usr/bin/env bun
/**
 * The skill battery: which skill does the model pick for a request, given one copy of
 * the plugin? It measures the choice and nothing after it.
 *
 * Usage:
 *   bun .github/battery/run.ts <plugin-dir> <requests.json> --ceiling <usd>
 *       [--model <alias>] [--jobs <n>] [--timeout <seconds>] [--json <out.json>]
 *
 * The requests file is a JSON array of
 *   { "request": "revisa o que eu mudei", "expect": "review", "lang": "pt", "kind": "direct" }
 * where `expect` is a skill folder of the plugin under test or "none", `lang` is "pt" or
 * "en", and `kind` is free text the report carries along.
 *
 * Every request runs three times, and it is a hit when at least two runs fire the
 * expected skill (or no skill of the plugin, where "none" is expected). A run is one
 * headless `claude -p` turn: the first assistant turn is the choice, a Skill call in it
 * names the skill, anything else is "none". `--max-turns 1` ends the run there, and
 * `--permission-mode dontAsk` refuses whatever the turn tried beyond reading.
 *
 * Isolation, so the score does not depend on the machine:
 * - `--setting-sources project,local` in a fresh fixture: the user's plugins, skills and
 *   settings stay out, and the fixture has no project settings of its own. The init event
 *   of every run is checked, and a plugin other than the copy under test aborts the run.
 * - The copy is staged in a temp directory, with its hook commands run under a temp
 *   HOME, so the session hook cannot rewrite anything in the real ~/.claude and carries
 *   the frame a session with no profile sees.
 * - The variables a host Claude session exports are dropped before spawning, so the
 *   battery behaves the same from a terminal and from inside a session.
 *
 * It costs money on every run and needs a signed-in Claude, which is why it runs by hand
 * and never in CI. The ceiling is the most the battery may spend: a run that could pass
 * it is not started, and the partial result is printed.
 */

import { type ChildProcess, spawn, spawnSync } from "child_process";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from "fs";
import { tmpdir } from "os";
import { basename, join, resolve } from "path";
import { parseArgs } from "util";

const RUNS_PER_REQUEST = 3;
const HITS_NEEDED = 2;

interface Request {
  request: string;
  expect: string;
  lang: "pt" | "en";
  kind?: string;
}

type Outcome =
  | { kind: "skill"; skill: string; cost: number }
  | { kind: "none"; firstTool?: string; cost: number }
  | { kind: "error"; reason: string; cost: number; unbilled?: boolean };

class Abort extends Error {}

// ---------------------------------------------------------------- arguments

function usage(message?: string): never {
  if (message) console.error(`battery: ${message}\n`);
  console.error(
    "usage: bun .github/battery/run.ts <plugin-dir> <requests.json> --ceiling <usd>\n" +
      "       [--model <alias>] [--jobs <n>] [--timeout <seconds>] [--json <out.json>]",
  );
  process.exit(1);
}

function readOptions() {
  let parsed;
  try {
    parsed = parseArgs({
      args: process.argv.slice(2),
      allowPositionals: true,
      options: {
        ceiling: { type: "string" },
        model: { type: "string" },
        jobs: { type: "string", default: "4" },
        timeout: { type: "string", default: "240" },
        json: { type: "string" },
      },
    });
  } catch (error) {
    usage((error as Error).message);
  }
  const { values, positionals } = parsed;
  if (positionals.length !== 2) usage("takes a plugin directory and a requests file");
  const ceiling = Number(values.ceiling);
  if (!values.ceiling || !(ceiling > 0)) usage("--ceiling <usd> is required and above zero");
  const jobs = Math.max(1, Math.floor(Number(values.jobs)) || 1);
  const timeout = Math.max(10, Number(values.timeout) || 240);
  return {
    pluginDir: resolve(positionals[0]),
    requestsFile: resolve(positionals[1]),
    ceiling,
    model: values.model,
    jobs,
    timeoutMs: timeout * 1000,
    jsonOut: values.json ? resolve(values.json) : undefined,
  };
}

function readPlugin(dir: string): { name: string; version: string } {
  const manifest = join(dir, ".claude-plugin", "plugin.json");
  if (!existsSync(manifest)) usage(`${dir} is not a plugin: no .claude-plugin/plugin.json`);
  const data = JSON.parse(readFileSync(manifest, "utf8"));
  return { name: String(data.name), version: String(data.version ?? "") };
}

function readRequests(file: string, pluginDir: string): Request[] {
  let data: unknown;
  try {
    data = JSON.parse(readFileSync(file, "utf8"));
  } catch (error) {
    usage(`${file}: ${(error as Error).message}`);
  }
  if (!Array.isArray(data) || data.length === 0) usage(`${file}: not a non-empty JSON array`);
  const problems: string[] = [];
  data.forEach((item, i) => {
    const where = `${basename(file)}[${i}]`;
    if (typeof item?.request !== "string" || !item.request.trim())
      problems.push(`${where}: no request`);
    if (item?.lang !== "pt" && item?.lang !== "en") problems.push(`${where}: lang is "pt" or "en"`);
    const expect = item?.expect;
    if (typeof expect !== "string") problems.push(`${where}: no expect`);
    else if (expect !== "none" && !existsSync(join(pluginDir, "skills", expect, "SKILL.md")))
      problems.push(`${where}: expect "${expect}" is not a skill of the plugin under test`);
  });
  if (problems.length) usage(problems.join("\n"));
  return data as Request[];
}

// ---------------------------------------------------------------- isolation

/** The environment a run gets: the caller's, minus what a host Claude session exports. */
function cleanEnv(): NodeJS.ProcessEnv {
  const keep = new Set([
    "CLAUDE_CODE_OAUTH_TOKEN",
    "CLAUDE_CONFIG_DIR",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
  ]);
  const env = { ...process.env };
  const hosted = "CLAUDECODE" in env;
  for (const key of Object.keys(env)) {
    if (key.startsWith("CLAUDE") && !keep.has(key)) delete env[key];
  }
  // A host session points its children at its own proxy; a terminal user who set a
  // gateway keeps theirs.
  if (hosted) delete env.ANTHROPIC_BASE_URL;
  return env;
}

function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

/** The copy under test, staged so its hooks write into `home` instead of the real one. */
function stagePlugin(source: string, work: string): { dir: string; home: string } {
  const dir = join(work, "plugin", basename(source));
  const home = join(work, "home");
  mkdirSync(home, { recursive: true });
  cpSync(source, dir, {
    recursive: true,
    filter: (path) => !/[\\/](node_modules|\.git|__pycache__)$/.test(path),
  });
  const hooksFile = join(dir, "hooks", "hooks.json");
  if (existsSync(hooksFile)) {
    const prefix = `HOME=${shellQuote(home)} CLAUDE_PLUGIN_DATA=${shellQuote(join(home, "data"))} `;
    const hooks = JSON.parse(readFileSync(hooksFile, "utf8"));
    const visit = (node: unknown): void => {
      if (Array.isArray(node)) node.forEach(visit);
      else if (node && typeof node === "object") {
        const record = node as Record<string, unknown>;
        if (record.type === "command" && typeof record.command === "string")
          record.command = prefix + record.command;
        Object.values(record).forEach(visit);
      }
    };
    visit(hooks);
    writeFileSync(hooksFile, JSON.stringify(hooks, null, 2));
  }
  return { dir: realpathSync(dir), home };
}

/** A small git project on a feature branch with one uncommitted change, so requests
 * about "what I changed" or "open the PR" land where a builder would ask them. */
function makeFixture(work: string, env: NodeJS.ProcessEnv): string {
  const dir = join(work, "project");
  mkdirSync(join(dir, "src"), { recursive: true });
  writeFileSync(join(dir, "README.md"), "# Orbit\n\nA small task list API.\n");
  writeFileSync(
    join(dir, "package.json"),
    JSON.stringify({ name: "orbit", private: true, scripts: { test: "node --test" } }, null, 2) +
      "\n",
  );
  writeFileSync(
    join(dir, "src", "tasks.js"),
    "export function listTasks(store) {\n  return store.all();\n}\n",
  );
  const git = (...args: string[]) => {
    const r = spawnSync(
      "git",
      ["-c", "user.name=battery", "-c", "user.email=battery@example.invalid", ...args],
      {
        cwd: dir,
        env,
        encoding: "utf8",
      },
    );
    if (r.status !== 0) throw new Abort(`fixture: git ${args.join(" ")} failed: ${r.stderr}`);
  };
  git("init", "-q", "-b", "main");
  git("add", ".");
  git("commit", "-q", "-m", "feat: list tasks");
  git("checkout", "-q", "-b", "feature/filtro-de-tarefas");
  writeFileSync(
    join(dir, "src", "tasks.js"),
    "export function listTasks(store, done) {\n  return store.all().filter((t) => done === undefined || t.done === done);\n}\n",
  );
  return realpathSync(dir);
}

function preflight(env: NodeJS.ProcessEnv): void {
  const r = spawnSync("claude", ["auth", "status"], { env, encoding: "utf8" });
  if (r.error) throw new Abort("the `claude` command was not found on PATH");
  let status: { loggedIn?: boolean; authMethod?: string } = {};
  try {
    status = JSON.parse(r.stdout);
  } catch {
    return; // an older CLI without JSON status: the first run will say it
  }
  if (
    !status.loggedIn &&
    (!status.authMethod || status.authMethod === "none") &&
    !env.ANTHROPIC_API_KEY
  )
    throw new Abort(
      "Claude Code is not signed in for headless runs. Run `claude auth login` in a terminal, then run the battery again.",
    );
}

// ---------------------------------------------------------------- one run

interface RunContext {
  pluginDir: string;
  fixture: string;
  env: NodeJS.ProcessEnv;
  model?: string;
  timeoutMs: number;
  seenModel?: string;
  live: Set<ChildProcess>;
}

function runOnce(ctx: RunContext, request: string, budget: number): Promise<Outcome> {
  const args = [
    "-p",
    "--output-format",
    "stream-json",
    "--verbose",
    "--max-turns",
    "1",
    "--permission-mode",
    "dontAsk",
    "--no-session-persistence",
    "--setting-sources",
    "project,local",
    "--strict-mcp-config",
    "--plugin-dir",
    ctx.pluginDir,
    "--max-budget-usd",
    budget.toFixed(4),
  ];
  if (ctx.model) args.push("--model", ctx.model);

  return new Promise((done) => {
    const child = spawn("claude", args, {
      cwd: ctx.fixture,
      env: ctx.env,
      stdio: ["pipe", "pipe", "pipe"],
    });
    ctx.live.add(child);
    let buffer = "";
    let stderr = "";
    let skill: string | undefined;
    let firstTool: string | undefined;
    let turnEnded = false;
    let breach: string | undefined;
    let result: { cost: number; error?: string } | undefined;
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, ctx.timeoutMs);

    const handle = (event: any) => {
      if (event.type === "system" && event.subtype === "init") {
        ctx.seenModel ??= event.model;
        let loaded = false;
        for (const plugin of event.plugins ?? []) {
          const path = plugin?.path ? safeRealpath(plugin.path) : "";
          if (path === ctx.pluginDir) loaded = true;
          else breach = `also loaded ${plugin?.name ?? "?"} at ${plugin?.path ?? "?"}`;
        }
        // A copy that failed to load would score every run as none and read as a real score.
        if (!loaded) breach ??= "the plugin under test did not load";
        if (breach) child.kill("SIGKILL");
      } else if (event.type === "assistant" && !turnEnded) {
        for (const block of event.message?.content ?? []) {
          if (block?.type !== "tool_use") continue;
          if (block.name === "Skill" && !skill)
            skill = String(block.input?.skill ?? block.input?.command ?? "");
          firstTool ??= block.name;
        }
      } else if (event.type === "user") {
        turnEnded = true;
      } else if (event.type === "result") {
        const cost = Number(event.total_cost_usd) || 0;
        const text = typeof event.result === "string" ? event.result : "";
        const failed =
          event.terminal_reason === "api_error" ||
          /failed to authenticate/i.test(text) ||
          (event.is_error === true && event.subtype !== "error_max_turns");
        result = { cost, error: failed ? text || "api error" : undefined };
        if (event.subtype === "error_max_budget_usd") result.error = "budget";
      }
    };

    child.stdout.on("data", (chunk: Buffer) => {
      buffer += chunk.toString();
      let newline: number;
      while ((newline = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, newline).trim();
        buffer = buffer.slice(newline + 1);
        if (!line) continue;
        try {
          handle(JSON.parse(line));
        } catch {
          // a line that is not JSON is the CLI's own noise
        }
      }
    });
    child.stderr.on("data", (chunk: Buffer) => (stderr += chunk.toString()));
    child.stdin.end(request);

    child.on("close", () => {
      clearTimeout(timer);
      ctx.live.delete(child);
      const cost = result?.cost ?? 0;
      if (breach) return done({ kind: "error", reason: `isolation: ${breach}`, cost });
      if (result?.error && /authenticate/i.test(result.error))
        return done({ kind: "error", reason: `auth: ${result.error}`, cost });
      if (skill) return done({ kind: "skill", skill: skill.replace(/^\//, ""), cost });
      if (!result) {
        const reason = timedOut
          ? "timeout"
          : stderr.trim().split("\n").pop() || "exited without a result";
        return done({ kind: "error", reason, cost, unbilled: true });
      }
      if (result.error) return done({ kind: "error", reason: result.error, cost });
      return done({ kind: "none", firstTool, cost });
    });
  });
}

function safeRealpath(path: string): string {
  try {
    return realpathSync(path);
  } catch {
    return resolve(path);
  }
}

// ---------------------------------------------------------------- the battery

function label(outcome: Outcome): string {
  if (outcome.kind === "skill") return outcome.skill;
  if (outcome.kind === "none") return outcome.firstTool ? `none (${outcome.firstTool})` : "none";
  return `error (${outcome.reason.slice(0, 60)})`;
}

function bbSkill(outcome: Outcome, plugin: string): string | null {
  if (outcome.kind !== "skill") return null;
  return outcome.skill.startsWith(`${plugin}:`) ? outcome.skill.slice(plugin.length + 1) : null;
}

function runHit(expect: string, outcome: Outcome, plugin: string): boolean {
  if (outcome.kind === "error") return false;
  const fired = bbSkill(outcome, plugin);
  return expect === "none" ? fired === null : fired === expect;
}

function money(usd: number): string {
  return `US$ ${usd.toFixed(2)}`;
}

function duration(ms: number): string {
  const s = Math.round(ms / 1000);
  return s >= 60 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${s}s`;
}

async function main(): Promise<number> {
  const options = readOptions();
  const plugin = readPlugin(options.pluginDir);
  const requests = readRequests(options.requestsFile, options.pluginDir);
  const env = cleanEnv();
  preflight(env);

  const work = mkdtempSync(join(tmpdir(), "bb-battery-"));
  const cleanup = () => rmSync(work, { recursive: true, force: true });
  const children = new Set<Promise<unknown>>();
  const live = new Set<ChildProcess>();
  for (const [signal, code] of [
    ["SIGINT", 130],
    ["SIGTERM", 143],
    ["SIGHUP", 129],
  ] as const)
    process.on(signal, () => {
      for (const child of live) child.kill("SIGKILL");
      cleanup();
      process.exit(code);
    });

  try {
    const staged = stagePlugin(options.pluginDir, work);
    const ctx: RunContext = {
      pluginDir: staged.dir,
      fixture: makeFixture(work, env),
      env,
      model: options.model,
      timeoutMs: options.timeoutMs,
      live,
    };

    const results: Outcome[][] = requests.map(() => []);
    const queue: number[] = requests.flatMap((_, i) => Array(RUNS_PER_REQUEST).fill(i));
    const started = Date.now();
    let spent = 0;
    let estimate = 0; // the dearest run so far: what the next one is assumed to cost
    let inFlight = 0;
    let retries = 0;
    let stopped = false;
    let fatal: string | undefined;

    const priced = async (i: number): Promise<Outcome> => {
      const budget = Math.max(0.01, options.ceiling - spent - Math.max(0, inFlight - 1) * estimate);
      const outcome = await runOnce(ctx, requests[i].request, budget);
      // A run killed before its result was billed all the same: price it at the dearest so far.
      const unbilled = outcome.kind === "error" && outcome.unbilled;
      spent += unbilled ? Math.max(estimate, 0.01) : outcome.cost;
      estimate = Math.max(estimate, outcome.cost);
      return outcome;
    };

    const attempt = async (i: number): Promise<Outcome> => {
      const outcome = await priced(i);
      if (outcome.kind === "error" && /^(auth|isolation)/.test(outcome.reason)) {
        fatal = outcome.reason;
        return outcome;
      }
      if (outcome.kind !== "error" || outcome.reason === "budget") return outcome;
      // The retry is one more run, so it passes the same ceiling check a new run does.
      if (spent + inFlight * estimate > options.ceiling)
        return { kind: "error", reason: "budget", cost: 0 };
      retries++;
      return priced(i);
    };

    // Until one run has a price, only one runs; after that, a run starts only when the
    // spend plus every run in flight, each priced at the dearest so far, stays under.
    const canStart = () => {
      if (inFlight > 0 && estimate === 0) return false;
      return spent + (inFlight + 1) * estimate <= options.ceiling;
    };

    await new Promise<void>((finish) => {
      const pump = () => {
        while (!stopped && !fatal && queue.length && inFlight < options.jobs && canStart()) {
          const i = queue.shift()!;
          inFlight++;
          const p = attempt(i).then((r) => {
            inFlight--;
            children.delete(p);
            results[i].push(r);
            if (r.kind === "error" && r.reason === "budget") stopped = true;
            process.stderr.write(`  [${requests[i].expect}] ${label(r)}\n`);
            pump();
          });
          children.add(p);
        }
        if (inFlight === 0) {
          if (queue.length && !fatal && !canStart()) stopped = true;
          if (!queue.length || stopped || fatal) finish();
        }
      };
      pump();
    });

    if (fatal) throw new Abort(fatal);

    // ------------------------------------------------------------ the report
    const measured = requests
      .map((req, i) => ({ req, runs: results[i] }))
      .filter(
        (r) =>
          r.runs.length === RUNS_PER_REQUEST &&
          !r.runs.some((x) => x.kind === "error" && x.reason === "budget"),
      );
    const scored = measured.map(({ req, runs }) => {
      const hits = runs.filter((r) => runHit(req.expect, r, plugin.name)).length;
      const falseFires =
        req.expect === "none" ? runs.filter((r) => bbSkill(r, plugin.name) !== null).length : 0;
      return { req, runs, hits, hit: hits >= HITS_NEEDED, falseFires };
    });
    const hitCount = scored.filter((s) => s.hit).length;
    const partial = measured.length < requests.length;
    const pct = measured.length ? (100 * hitCount) / measured.length : 0;
    const runCount = results.reduce((n, r) => n + r.length, 0) + retries;

    const lines: string[] = [];
    lines.push(
      `Battery: ${plugin.name} ${plugin.version} from ${options.pluginDir}`,
      `Model: ${ctx.seenModel ?? options.model ?? "account default"} · ${requests.length} requests × ${RUNS_PER_REQUEST} runs`,
      "",
      `Score: ${hitCount}/${measured.length} (${pct.toFixed(1)}%)`,
    );
    if (partial)
      lines.push(
        `Partial: stopped at the cost ceiling, ${measured.length} of ${requests.length} requests measured`,
      );
    const falseFires = scored.reduce((n, s) => n + s.falseFires, 0);
    lines.push(`False fires: ${falseFires} runs`, "", "Misses by skill");

    const misses = scored.filter((s) => !s.hit);
    if (!misses.length) lines.push("  none");
    const bySkill = new Map<string, typeof misses>();
    for (const miss of misses)
      bySkill.set(miss.req.expect, [...(bySkill.get(miss.req.expect) ?? []), miss]);
    for (const [skill, items] of [...bySkill].sort(([a], [b]) => a.localeCompare(b))) {
      const note = skill === "none" ? ", false fires" : "";
      lines.push(`  ${skill} (${items.length}${note})`);
      for (const item of items) {
        const mark = item.req.lang === "en" ? "[en] " : "";
        lines.push(`    - ${mark}"${item.req.request}" → ${item.runs.map(label).join(", ")}`);
      }
    }
    lines.push(
      "",
      `Cost: ${money(spent)} over ${runCount} runs (${retries} retried), ${duration(Date.now() - started)}, ceiling ${money(options.ceiling)}`,
    );
    console.log(lines.join("\n"));

    if (options.jsonOut) {
      writeFileSync(
        options.jsonOut,
        JSON.stringify(
          {
            plugin: { ...plugin, dir: options.pluginDir },
            model: ctx.seenModel ?? options.model ?? null,
            requestsFile: options.requestsFile,
            score: {
              hits: hitCount,
              measured: measured.length,
              total: requests.length,
              percent: pct,
            },
            partial,
            falseFires,
            cost: { usd: spent, runs: runCount, retried: retries, ceiling: options.ceiling },
            requests: requests.map((req, i) => {
              const s = scored.find((x) => x.req === req);
              return { ...req, runs: results[i].map(label), hit: s ? s.hit : null };
            }),
          },
          null,
          2,
        ) + "\n",
      );
    }
    return partial ? 3 : 0;
  } finally {
    await Promise.allSettled([...children]);
    cleanup();
  }
}

main().then(
  (code) => process.exit(code),
  (error) => {
    console.error(`battery: ${error instanceof Abort ? error.message : (error as Error).stack}`);
    process.exit(1);
  },
);
