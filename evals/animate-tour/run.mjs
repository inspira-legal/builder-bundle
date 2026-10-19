// node run.mjs trigger  [--models haiku,sonnet,opus] [--runs 5]
// node run.mjs scenario ID [--models haiku,sonnet,opus]
//
// Runs the scenarios of scenarios.json against plugins/bb through the Claude Agent SDK, with no
// user or project settings, so only bb is loaded. A trigger run reads the first Skill call. A
// scenario run answers AskUserQuestion from the scenario's answers, replies in text when a turn
// ends on a question, and grades the transcript against expected_behavior. Each run writes its
// transcript and checks to results/DATE/. Each scenario run gets a studio of its own (MOTION_HOME
// in a temporary folder, linked to the installed ~/Motion), so runs never share a scene.
import { query } from "@anthropic-ai/claude-agent-sdk";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
  existsSync,
  symlinkSync,
} from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PLUGIN = resolve(HERE, "../../plugins/bb");
const FIXTURES = join(HERE, "fixtures");
const MOTION = join(homedir(), "Motion");
const TOUR = join(PLUGIN, "skills", "animate-tour", "scripts", "tour.mjs");
// The studio of the run being graded. A scenario run points it at its own studio.
let STUDIO = MOTION;
let SCENES = join(STUDIO, "scenes");

// A studio that shares ~/Motion's install and starts with empty scenes/ and out/.
function makeStudio() {
  if (!existsSync(join(MOTION, ".studio-version")))
    throw new Error("The studio is not installed: run /bb:reel or tour.mjs prepare once.");
  const dir = mkdtempSync(join(tmpdir(), "bb-eval-motion-"));
  for (const name of readdirSync(MOTION))
    if (!["scenes", "out", ".DS_Store"].includes(name))
      symlinkSync(join(MOTION, name), join(dir, name));
  mkdirSync(join(dir, "scenes"));
  mkdirSync(join(dir, "out"));
  return dir;
}

function useStudio(dir) {
  STUDIO = dir;
  SCENES = join(dir, "scenes");
}

// True when the path resolves inside SCENES, so "scenes-backup/" and "scenes/../.." stay out.
function inScenes(p) {
  const rel = relative(SCENES, resolve(String(p)));
  return rel !== "" && !rel.startsWith("..") && !isAbsolute(rel);
}

// The exact commands the harness runs: tour.mjs's verbs and a few reads, no shell operators.
const Q = (re) => `(?:"${re}"|${re})`;
const SLUG = "[a-z0-9-]+";
const TOUR_CMD = new RegExp(
  `^node ${Q(TOUR.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))} ` +
    `(?:prepare(?: --force)?|new ${SLUG}(?: --from [a-z0-9-]+)?|` +
    `record ${SLUG}(?: --quality (?:light|high))?(?: --steps \\d+(?: \\d+)*)?)$`,
);
const READ_CMD = /^(?:ls|file|du|stat)(?: (?:-[a-zA-Z]+|"[^"`$\\]*"|[\w./~@+-]+))*$/;
const allowedBash = (cmd) => TOUR_CMD.test(cmd.trim()) || READ_CMD.test(cmd.trim());
const DATE = new Date().toISOString().slice(0, 10);
const OUT = join(HERE, "results", DATE);
const SCENARIOS = JSON.parse(readFileSync(join(HERE, "scenarios.json"), "utf8"));

const args = process.argv.slice(2);
const flag = (name, dflt) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? dflt : args[i + 1];
};
const MODELS = flag("models", "haiku,sonnet,opus").split(",");

function baseOptions(model, extra = {}) {
  return {
    model,
    cwd: mkdtempSync(join(tmpdir(), "bb-eval-")),
    settingSources: [],
    plugins: [{ type: "local", path: PLUGIN }],
    systemPrompt: { type: "preset", preset: "claude_code" },
    ...extra,
  };
}

// Trigger: the first Skill call of a run is the pick.
async function triggerRun(model, prompt) {
  const abort = new AbortController();
  let pick = "NONE";
  let resolved = model;
  let text = "";
  try {
    for await (const m of query({
      prompt,
      options: baseOptions(model, { tools: ["Skill"], maxTurns: 2, abortController: abort }),
    })) {
      if (m.type === "system" && m.subtype === "init") resolved = m.model;
      if (m.type !== "assistant") continue;
      for (const c of m.message.content) {
        if (c.type === "text") text += c.text;
        if (c.type === "tool_use" && c.name === "Skill") {
          pick = c.input.skill?.replace(/^\//, "") ?? "NONE";
          abort.abort();
        }
      }
    }
  } catch (e) {
    if (!abort.signal.aborted) throw e;
  }
  return { pick, resolved, text: text.slice(0, 300) };
}

async function pool(items, size, fn) {
  const out = [];
  let i = 0;
  await Promise.all(
    Array.from({ length: size }, async () => {
      while (i < items.length) {
        const k = i++;
        out[k] = await fn(items[k]);
      }
    }),
  );
  return out;
}

async function runTrigger() {
  const sc = SCENARIOS.find((s) => s.id === "trigger");
  const runs = Number(flag("runs", sc.runs_per_model));
  const jobs = [];
  for (const model of MODELS)
    for (const q of sc.queries) for (let n = 0; n < runs; n++) jobs.push({ model, q });
  const results = await pool(jobs, 6, async (j) => ({
    model: j.model,
    query: j.q.query,
    expected: j.q.expected_skill,
    ...(await triggerRun(j.model, j.q.query)),
  }));
  mkdirSync(OUT, { recursive: true });
  writeFileSync(join(OUT, "trigger.json"), JSON.stringify(results, null, 2));
  console.log("| Query | Expected | " + MODELS.join(" | ") + " |");
  console.log("| --- | --- | " + MODELS.map(() => "---").join(" | ") + " |");
  for (const q of sc.queries) {
    const cells = MODELS.map((model) => {
      const rs = results.filter((r) => r.model === model && r.query === q.query);
      const hits = rs.filter((r) => r.pick === q.expected_skill).length;
      const misses = rs.filter((r) => r.pick !== q.expected_skill).map((r) => r.pick);
      return `${hits}/${rs.length}` + (misses.length ? ` (${misses.join(", ")})` : "");
    });
    console.log(`| ${q.query} | ${q.expected_skill} | ${cells.join(" | ")} |`);
  }
  const models = [...new Set(results.map((r) => `${r.model}=${r.resolved}`))];
  console.log("\nModels: " + models.join(", "));
}

// Scenario: the answers a person gives, per scenario.
const optText = (q) =>
  [q.question, q.header, ...(q.options ?? []).map((o) => `${o.label} ${o.description ?? ""}`)].join(
    "\n",
  );
// The label first: a description may name the other mode ("then the GIF of the same art").
const choose = (q, re) =>
  (q.options ?? []).find((o) => re.test(o.label)) ??
  (q.options ?? []).find((o) => re.test(`${o.label} ${o.description ?? ""}`));

const RESPONDERS = {
  "gif-from-screenshots": {
    answer(q) {
      const t = optText(q);
      if (/GIF/i.test(t) && /c[oó]digo|code|dentro|inside/i.test(t))
        return choose(q, /GIF|fora|outside/i);
      if (/\blight\b|\bleve\b/i.test(t)) return choose(q, /\blight\b|\bleve\b/i);
      if (/plano|plan|passos|steps/i.test(t))
        return choose(q, /aprov|approve|sim|yes|segu|go ahead|pode|produz|ok/i);
      return undefined;
    },
    reply(ctx) {
      if (ctx.recorded) return null;
      if (ctx.turn >= 6) return null;
      return "GIF para o e-mail de lançamento, fora do app, qualidade leve. Se for o plano, está aprovado: pode produzir.";
    },
  },
  "no-browser": {
    answer(q) {
      const t = optText(q);
      if (/print|screenshot|captur/i.test(t)) return choose(q, /print|screenshot|captur/i);
      if (/\bhigh\b|\balta\b/i.test(t)) return choose(q, /\bhigh\b|\balta\b/i);
      return undefined;
    },
    reply(ctx) {
      if (ctx.picked || ctx.turn >= 2) return null;
      ctx.picked = true;
      ctx.events.push({ turn: ctx.turn, type: "pick", via: "text" });
      return "Vou mandar prints.";
    },
  },
};

async function scenarioRun(sc, model) {
  const responder = RESPONDERS[sc.id];
  const ctx = {
    turn: 0,
    events: [],
    byId: new Map(),
    recorded: false,
    picked: false,
    resolved: model,
    cost: 0,
  };
  const canUseTool = async (name, input) => {
    if (name === "AskUserQuestion") {
      const answers = {};
      for (const q of input.questions) {
        const o = responder.answer(q) ?? q.options?.[0];
        answers[q.question] = o?.label ?? "";
      }
      ctx.events.push({ turn: ctx.turn, type: "answer", answers });
      if (
        sc.id === "no-browser" &&
        Object.values(answers).some((a) => /print|screenshot|captur/i.test(a))
      )
        ctx.picked = true;
      return { behavior: "allow", updatedInput: { ...input, answers } };
    }
    if (name === "Write" || name === "Edit")
      return inScenes(input.file_path)
        ? { behavior: "allow", updatedInput: input }
        : {
            behavior: "deny",
            message: `The eval harness only allows writes under ${SCENES}.`,
          };
    if (name === "Bash") {
      return allowedBash(input.command)
        ? { behavior: "allow", updatedInput: input }
        : { behavior: "deny", message: "The eval harness denied this command." };
    }
    if (["Read", "Glob", "Grep", "Skill", "ToolSearch", "TodoWrite"].includes(name))
      return { behavior: "allow", updatedInput: input };
    return { behavior: "deny", message: `The eval harness does not allow ${name}.` };
  };

  let prompt = sc.query.replaceAll("FIXTURES", FIXTURES);
  let session;
  while (prompt) {
    ctx.turn++;
    ctx.events.push({ turn: ctx.turn, type: "user", text: prompt });
    for await (const m of query({
      prompt,
      options: baseOptions(model, {
        resume: session,
        canUseTool,
        maxTurns: 80,
        maxBudgetUsd: 10,
        additionalDirectories: [FIXTURES, STUDIO],
        env: { ...process.env, MOTION_HOME: STUDIO },
      }),
    })) {
      if (m.type === "system" && m.subtype === "init") {
        session = m.session_id;
        ctx.resolved = m.model;
      }
      if (m.type === "result") ctx.cost += m.total_cost_usd ?? 0;
      // The tool's outcome: a denied or failed call comes back with is_error.
      if (m.type === "user" && Array.isArray(m.message.content))
        for (const c of m.message.content) {
          const e = c.type === "tool_result" && ctx.byId.get(c.tool_use_id);
          if (!e) continue;
          const text = Array.isArray(c.content)
            ? c.content.map((x) => x.text ?? `[${x.type}]`).join("\n")
            : String(c.content ?? "");
          e.result = { ok: !c.is_error, text: text.slice(0, 1500) };
          if (e.result.ok && isTool(e, "Bash", /tour\.mjs\\?"?\s+record/)) ctx.recorded = true;
        }
      if (m.type !== "assistant") continue;
      for (const c of m.message.content) {
        if (c.type === "text") ctx.events.push({ turn: ctx.turn, type: "text", text: c.text });
        if (c.type === "tool_use") {
          const e = { turn: ctx.turn, type: "tool", id: c.id, name: c.name, input: c.input };
          ctx.events.push(e);
          ctx.byId.set(c.id, e);
        }
      }
    }
    prompt = responder.reply(ctx);
  }
  return ctx;
}

// Grading.
const REAL_DATA = [
  "Mariana",
  "Couto Ribeiro",
  "Henrique",
  "Vasconcelos",
  "Vale Sereno",
  "Alto Ipê",
  "1023456-78",
  "0457821-33",
  "48.320",
  "112.900",
  "Parecer_Locacao",
  "12/08/2024",
  "03/05/2024",
  "21/09/2024",
];
const isTool = (e, name, re) =>
  e.type === "tool" && e.name === name && (!re || re.test(JSON.stringify(e.input)));
// A call that ran and succeeded, per its tool_result.
const succeeded = (e) => e.result?.ok === true;
const isProduction = (e) =>
  (e.type === "tool" && (e.name === "Write" || e.name === "Edit") && inScenes(e.input.file_path)) ||
  isTool(e, "Bash", /tour\.mjs\\?"?\s+(new|record)/);
const askText = (e) => (e.input.questions ?? []).map(optText).join("\n") + JSON.stringify(e.input);
const firstIndex = (evs, f) => {
  const i = evs.findIndex(f);
  return i === -1 ? Infinity : i;
};

// The GIFs and stills the run left in the studio's out/.
function outputs() {
  const out = join(STUDIO, "out");
  if (!existsSync(out)) return [];
  return readdirSync(out, { recursive: true }).map((f) => join(out, f));
}

function sceneContents(evs) {
  const dirs = new Set();
  for (const e of evs) {
    if (e.type !== "tool") continue;
    if ((e.name === "Write" || e.name === "Edit") && inScenes(e.input.file_path))
      dirs.add(dirname(e.input.file_path));
    const m = e.name === "Bash" && e.input.command.match(/tour\.mjs"?\s+new\s+(\S+)/);
    if (m) dirs.add(join(SCENES, m[1]));
  }
  return [...dirs]
    .map((d) => join(d, "index.html"))
    .filter(existsSync)
    .map((f) => readFileSync(f, "utf8"));
}

const GRADERS = {
  "gif-from-screenshots"(evs, scenes, files) {
    const prod = firstIndex(evs, isProduction);
    const firstRecord = firstIndex(evs, (e) => isTool(e, "Bash", /tour\.mjs\\?"?\s+record/));
    const lastRecord = evs.findLastIndex((e) => isTool(e, "Bash", /tour\.mjs\\?"?\s+record/));
    const asked = (re, before) =>
      evs.some(
        (e, i) =>
          i < before &&
          ((e.type === "tool" && e.name === "AskUserQuestion" && re.test(askText(e))) ||
            (e.type === "text" && re.test(e.text))),
      );
    const planAsk = evs.findIndex((e) => {
      if (!isTool(e, "AskUserQuestion")) return false;
      const t = askText(e);
      const marks = (t.match(/(passo|step|etapa)\s*\d|\\n\s*\|?\s*\d\s*[|.)]/gi) ?? []).length;
      return marks >= 3;
    });
    // The plan is shown to the person and becomes the caption, so it counts as much as the scene.
    const planText = planAsk === -1 ? "" : askText(evs[planAsk]);
    const leaked = REAL_DATA.filter((s) => planText.includes(s) || scenes.includes(s));
    const lightRecord = evs.find(
      (e) => isTool(e, "Bash", /tour\.mjs\\?"?\s+record\s+\S+.*--quality\s+light/) && succeeded(e),
    );
    const slug = lightRecord?.input.command.match(/record\s+(\S+)/)?.[1];
    const after = evs.slice(planAsk === -1 ? 0 : planAsk);
    const saysReplaced = after.some(
      (e) =>
        (e.type === "text" && /substitu|fict[ií]ci|trocad|replac/i.test(e.text)) ||
        (isTool(e, "AskUserQuestion") && /substitu|fict[ií]ci|trocad|replac/i.test(askText(e))),
    );
    const finalTurn = evs.at(-1)?.turn;
    const finalText =
      evs.filter((e) => e.type === "text" && e.turn === finalTurn).at(-1)?.text ?? "";
    return {
      asks_mode: asked(
        /fora do app|dentro do app|inside the app|outside the app|onde .{0,40}(usad|usar|vai)|c[oó]digo.{0,60}GIF|GIF.{0,60}c[oó]digo/i,
        prod,
      ),
      // The question or an option label, not a description: a mode option may mention both qualities.
      asks_quality: evs.some(
        (e, i) =>
          i < firstRecord &&
          ((isTool(e, "AskUserQuestion") &&
            e.input.questions.some((q) =>
              /qualidade|quality|\blight\b|\bhigh\b/i.test(
                [q.question, ...(q.options ?? []).map((o) => o.label)].join("\n"),
              ),
            )) ||
            (e.type === "text" && /(qualidade|quality)[^?]*\?/i.test(e.text))),
      ),
      plan_in_question: planAsk !== -1 && planAsk < prod,
      real_data_replaced:
        planAsk !== -1 && scenes.length > 0 && leaked.length === 0 && saysReplaced,
      // The record succeeded and its full GIF is on disk.
      records_with_tour_mjs:
        !!slug && files.some((f) => f.endsWith(join(slug, "light", `${slug}-full.gif`))),
      // A Read of a still that the record wrote, and that came back without error.
      reads_stills: evs.some(
        (e, i) =>
          i > firstRecord &&
          isTool(e, "Read", /out\/.+\.png/) &&
          succeeded(e) &&
          files.includes(resolve(e.input.file_path)),
      ),
      closes_with_plain_question:
        lastRecord !== -1 &&
        !evs.slice(lastRecord).some((e) => isTool(e, "AskUserQuestion")) &&
        /\?/.test(finalText.slice(-400)),
      _leaked: leaked,
    };
  },
  "no-browser"(evs) {
    const pick = firstIndex(
      evs,
      (e) =>
        e.type === "pick" ||
        (e.type === "answer" &&
          Object.values(e.answers).some((a) => /print|screenshot|captur/i.test(a))),
    );
    const before = evs.slice(0, pick);
    const afterPick = evs.slice(pick + 1);
    const inPlugin = (e) =>
      JSON.stringify(e.input).includes(PLUGIN) ||
      /skills\/animate-tour/.test(JSON.stringify(e.input));
    const switched = before.filter(
      (e) =>
        e.type === "tool" &&
        !["Skill", "AskUserQuestion", "ToolSearch", "TodoWrite"].includes(e.name) &&
        // Reading the skill's own files is not another source.
        !(
          (["Read", "Glob", "Grep"].includes(e.name) ||
            isTool(e, "Bash", /"command":"\s*(cd [^"&]*&&\s*)?(ls|wc|cat|head)\b/)) &&
          inPlugin(e)
        ) &&
        !isTool(e, "Bash", /tour\.mjs\\?"?\s+prepare/),
    );
    const finalText = afterPick
      .filter((e) => e.type === "text")
      .map((e) => e.text)
      .join("\n");
    return {
      says_no_browser: before.some(
        (e) =>
          (e.type === "text" && /navegador|browser|chrome/i.test(e.text)) ||
          (isTool(e, "AskUserQuestion") && /navegador|browser|chrome/i.test(askText(e))),
      ),
      offers_choice: before.some(
        (e) =>
          isTool(e, "AskUserQuestion") &&
          /chrome/i.test(askText(e)) &&
          /print|screenshot|captur/i.test(askText(e)),
      ),
      no_switch_before_pick: pick !== Infinity && switched.length === 0,
      waits_after_pick:
        pick !== Infinity &&
        !afterPick.some(isProduction) &&
        /print|screenshot|captur/i.test(finalText),
      _switched: switched.map((e) => `${e.name} ${JSON.stringify(e.input).slice(0, 120)}`),
    };
  },
};

async function runScenario(id) {
  const sc = SCENARIOS.find((s) => s.id === id);
  mkdirSync(OUT, { recursive: true });
  // One model after the other, each in a studio of its own.
  for (const model of MODELS) {
    useStudio(makeStudio());
    const ctx = await scenarioRun(sc, model);
    const scenes = sceneContents(ctx.events).join("\n");
    const files = outputs();
    const checks = GRADERS[id](ctx.events, scenes, files);
    const passed = Object.entries(checks).filter(
      ([k, v]) => !k.startsWith("_") && v === true,
    ).length;
    const total = Object.keys(checks).filter((k) => !k.startsWith("_")).length;
    const trim = (e) =>
      e.input
        ? {
            ...e,
            input: JSON.parse(
              JSON.stringify(e.input, (k, v) =>
                typeof v === "string" && v.length > 4000 ? v.slice(0, 4000) + "…" : v,
              ),
            ),
          }
        : e;
    writeFileSync(
      join(OUT, `${id}-${model}.json`),
      JSON.stringify(
        {
          model,
          resolved: ctx.resolved,
          cost_usd: ctx.cost,
          studio: STUDIO,
          checks,
          scenes,
          files,
          events: ctx.events.map(trim),
        },
        null,
        2,
      ),
    );
    console.log(
      `\n${id} on ${model} (${ctx.resolved}): ${passed}/${total}, $${ctx.cost.toFixed(2)}`,
    );
    for (const [k, v] of Object.entries(checks)) console.log(`  ${k}: ${JSON.stringify(v)}`);
  }
}

// Grades a saved run again, after a grader changes.
function regrade(file) {
  const r = JSON.parse(readFileSync(file, "utf8"));
  const id = Object.keys(GRADERS).find((k) => file.includes(k));
  useStudio(r.studio ?? MOTION);
  r.scenes ??= sceneContents(r.events).join("\n");
  r.checks = GRADERS[id](r.events, r.scenes, r.files ?? []);
  writeFileSync(file, JSON.stringify(r, null, 2));
  console.log(file, JSON.stringify(r.checks));
}

if (args[0] === "trigger") await runTrigger();
else if (args[0] === "regrade") args.slice(1).forEach(regrade);
else if (args[0] === "scenario" && GRADERS[args[1]]) await runScenario(args[1]);
else
  console.log(
    "usage: node run.mjs trigger | scenario <gif-from-screenshots|no-browser> [--models a,b]",
  );
