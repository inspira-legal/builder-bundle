export const meta = {
  name: "build-tasks",
  description: "Builds a bb spec one agent per task, after proving the ground",
  phases: [
    { title: "Ground", detail: "reuse notes and the project's checks, once" },
    { title: "Build", detail: "one agent per task, sequential, one working tree" },
  ],
};

// A check that failed and then passed on a re-run with no file changed in between is
// the whole definition of a flake here. Nothing else earns a retry.
const RETRY_CAP = 3;

// Past this many characters the agent condenses its oldest entries itself.
const NOTE_CEILING = 1500;

const MANIFESTO_REF = "plugin-level references/consult-manifesto.md";

const REUSE_VERDICT = {
  type: "object",
  required: ["verdict", "note"],
  properties: {
    verdict: { type: "string", enum: ["intact", "moved", "gone"] },
    note: { type: "string" },
    where: { type: "string", description: "the new path, when moved" },
  },
};

const CHECKS_RESULT = {
  type: "object",
  required: ["commands", "ran", "green"],
  properties: {
    commands: { type: "array", items: { type: "string" } },
    ran: { type: "boolean" },
    green: { type: "boolean" },
    blocker: { type: "string" },
  },
};

const TASK_RESULT = {
  type: "object",
  required: ["n", "status", "conventions"],
  properties: {
    n: { type: "number" },
    status: { type: "string", enum: ["green", "red", "skipped", "underspecified"] },
    verify: {
      type: "object",
      properties: {
        kind: { type: "string", enum: ["command", "reading", "ci"] },
        result: { type: "string", enum: ["passed", "failed", "pending"] },
        evidence: { type: "string" },
      },
    },
    commit: { type: ["string", "null"] },
    conventions: { type: "string" },
    blocker: { type: "string" },
  },
};

function reusePrompt(note) {
  return `A spec's reuse note says the build should extend existing code. Find out whether it still exists.

The note: ${note}

Read the repo. Return "intact" if the code the note names is where it says, "moved" with
the path you found in "where" when it exists elsewhere, and "gone" when nothing in the repo
answers to it any more. Do not edit anything. A near-match under a different name is
"moved", not "gone"; only nothing at all is "gone".`;
}

// The authority chain below restates implement's step 4 on purpose: this string is what the
// agent reads at runtime, and it has no way to follow a pointer at a doc. Both copies change
// together.
function checksPrompt(hint) {
  return `Resolve this project's checks, then run all of them once.

${hint ? `The caller resolved this hint already: ${hint}` : "The caller resolved no hint."}

Resolve in this order of authority: CLAUDE.md and docs, then CI workflow files, then
package.json / justfile / Makefile / pyproject.toml. Run what CI runs, not a subset.

Then run every command you resolved, once. Running them is the point: it proves the run may
execute each one and it establishes the green baseline for the build.

Return "commands" with every command you resolved (an empty list when the project has none),
"ran" false when a command could not be executed at all, "green" false when the tree is
already failing a check, and "blocker" naming which command and why. Do not fix anything and
do not edit any file: you are the baseline, not the first task.`;
}

function taskPrompt(t, conventions, checks, specPath) {
  const deps = t.dep && t.dep.length ? t.dep.join(", ") : "nothing";
  const behaviors = t.behaviors && t.behaviors.length ? t.behaviors.join(", ") : "none cited";
  return `Build one task of a spec you did not write, in a repo you have not seen.

The spec: ${specPath}. Read it whole before touching anything: the opening and the free top
half describe the thing, and the fixed sections are the contract. Build to \`## Behavior\`,
stay inside \`## Out of scope\`.

Your task is ${t.n}: ${t.title}
It delivers: ${t.delivers}
It has to satisfy behaviors: ${behaviors}
It builds on tasks: ${deps}
Its \`verify:\` is: ${t.verify}

What earlier tasks established (names, paths, signatures, patterns chosen, and any reuse
target that moved). This outranks a path the spec names:
${conventions || "nothing was recorded; the spec is all you have."}

The project's checks: ${checks && checks.length ? checks.join(" && ") : "none were found"}

Your steps:

1. Re-read \`## Tasks\` on disk (also \`## Tarefas\`, the older spelling; a spec carrying
   both headings gets both enumerated, in file order). If task ${t.n} is already \`- [x]\`,
   return immediately with status "skipped" and the conventions you received, unchanged. The
   run is resumable and what already landed must not be redone.
2. Build the task. A stack choice the spec left open (framework, package manager, tooling)
   is settled against the manifesto first: ${MANIFESTO_REF}.
3. Satisfy \`verify:\`. A command gets run, and "result" is "passed" or "failed". "reading"
   means self-inspection: read what you produced against the behaviors this task cites and
   return short evidence. "CI" is out of reach in here, so return "pending", which is neither
   a pass nor a failure. Every \`verify:\` runs.
4. Run the project's checks and fix what broke. Re-run a failed check at most ${RETRY_CAP}
   times, and only while no file changed between runs: a check that fails and then passes
   with the tree untouched is a flake. Once a file changed, the failure is yours to fix.
5. Commit only the files this task touched, together with its \`- [ ]\` to \`- [x]\` in the
   same commit, on the branch already checked out. Conventional style, and no AI attribution
   anywhere in the message. The commit is the checkpoint.
6. Return the structured result, with "conventions" carrying the note you received plus what
   you established: names and paths you introduced, signatures other tasks will call, a
   pattern you chose among alternatives. Nothing already written in the spec. Past roughly
   ${NOTE_CEILING} characters, condense your oldest entries before returning.

A check still red after the retries, a \`verify:\` that came back "failed", or a spec too
underspecified to build against all mean the same thing: do not commit, do not revert. Leave
the tree as it is for diagnosis and return the blocker. A \`verify:\` still "pending" is a
green task: it commits, and the pending rides out to ship.`;
}

// Nothing unticked is nothing to build, and stage zero exists to prove the ground before
// task 1: with no task 1 it would run the project's checks and re-read every reuse note for
// a build that never happens. The skill checks this before invoking; the script holds the
// line for a caller that did not.
if (!args.tasks || args.tasks.length === 0) {
  return {
    slug: args.slug,
    built: [],
    skipped: [],
    pendingVerify: [],
    stopped: null,
    conventions: "",
  };
}

phase("Ground");

const reuseNotes = args.reuseNotes || [];
const ground = await parallel([
  ...reuseNotes.map(
    (note) => () =>
      agent(reusePrompt(note), {
        label: `reuse: ${note.slice(0, 40)}`,
        phase: "Ground",
        schema: REUSE_VERDICT,
        effort: "low",
      }),
  ),
  () =>
    agent(checksPrompt(args.checksHint), {
      label: "checks: resolve and run",
      phase: "Ground",
      schema: CHECKS_RESULT,
      effort: "low",
    }),
]);

const verdicts = ground.slice(0, reuseNotes.length);
const checks = ground[ground.length - 1];

// A lost stage-zero agent is a stop of its own: proceeding would build on ground nobody proved.
let stopped = null;
const lost = verdicts.filter((v) => !v).length;
if (lost) {
  stopped = { n: 0, status: "red", blocker: `${lost} reuse-note agent(s) returned nothing` };
} else if (!checks) {
  stopped = { n: 0, status: "red", blocker: "the checks agent returned nothing" };
}

let conventions = "";

if (!stopped) {
  const gone = verdicts.filter((v) => v.verdict === "gone");
  const moved = verdicts.filter((v) => v.verdict === "moved");

  // Both stage-zero agents have already returned, so one stop carries every blocker they
  // found: naming the first alone costs a whole round trip to discover the second.
  const blockers = [];

  if (gone.length) {
    blockers.push(`reuse note points at code that is gone: ${gone.map((v) => v.note).join("; ")}`);
  }

  if (!checks.commands.length) {
    log("no check was found in this project; building without a baseline");
  } else if (!checks.ran) {
    blockers.push(checks.blocker || "a check could not be executed");
  } else if (!checks.green) {
    blockers.push(checks.blocker || "the tree was already red");
  }

  if (blockers.length) {
    stopped = { n: 0, status: "red", blocker: blockers.join(" | ") };
  }

  // `moved` is not a stop: the path travels forward and outranks the one the spec names.
  if (moved.length) {
    conventions = moved.map((v) => `moved: ${v.note} is now at ${v.where}`).join("\n");
    log(`${moved.length} reuse target(s) moved; the new paths travel in the convention note`);
  }
}

const built = [];
const skipped = [];
const pendingVerify = [];

if (!stopped) {
  phase("Build");
  for (const t of args.tasks) {
    const r = await agent(taskPrompt(t, conventions, checks.commands, args.specPath), {
      label: `task ${t.n}: ${t.title}`,
      phase: "Build",
      schema: TASK_RESULT,
    });
    // A null return carries no blocker of its own, so the script writes one: assigning it
    // straight to `stopped` would read to the caller as a clean run over a half-built spec.
    if (!r) {
      stopped = { n: t.n, status: "red", blocker: "lost agent (null return)" };
      break;
    }
    if (r.status === "skipped") {
      skipped.push(r.n);
      continue;
    }
    if (r.status !== "green") {
      stopped = r;
      break;
    }
    // A task whose `verify:` did not run is not done, so green over a missing or failed
    // verify is a contradiction the caller cannot see: `built` would name the task and
    // ship would read it as proven.
    const proven = r.verify && (r.verify.result === "passed" || r.verify.result === "pending");
    if (!proven) {
      stopped = {
        n: r.n,
        status: "red",
        blocker: r.verify
          ? `task ${r.n} returned green with verify ${r.verify.result}`
          : `task ${r.n} returned green with no verify result`,
      };
      break;
    }

    conventions = r.conventions;
    if (r.verify.result === "pending") pendingVerify.push(r.n);
    built.push(r.n);
  }
}

return { slug: args.slug, built, skipped, pendingVerify, stopped, conventions };
