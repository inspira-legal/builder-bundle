// The platform reads this before the script runs, so it is a literal and the same on every
// run. Declaring no `phases` is what frees `phase()` to take a title computed from the spec:
// a call with no matching entry gets a progress group of its own.
export const meta = {
  name: "build-tasks",
  description: "Builds a bb spec one agent per task, after proving the ground",
};

// Stage zero belongs to the script and not to any task, so its title is fixed. The one the
// spec did not name is the group a task before the first `###` heading joins.
const GROUND_PHASE = "Ground";
const IMPLICIT_PHASE = "Build";

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

// `scripts/resolve_checks.py` walks the authority chain before the dispatch, so this agent
// confirms a list instead of deriving one. The order is spelled out only for the caller that
// passed nothing: the string is what the agent reads at runtime, and it cannot follow a
// pointer at a doc.
function checksPrompt(resolved) {
  // Three different grounds, and an empty list is two of them: no payload at all, and a
  // payload whose whole chain came back empty. `source` is what separates them, so a repo
  // that genuinely has no checks is not sent to re-walk a chain that already answered.
  //
  // `unresolved` is the one part of the payload that is not an answer: what the resolver
  // saw and could not turn into something runnable. It travels as work to do rather than
  // as a list to confirm, because a stack whose runner the resolver cannot name arrives
  // here as an empty list otherwise, and an empty list reads as "no checks".
  const unresolved = (resolved && resolved.unresolved) || [];
  const leads = unresolved.map((u) => `\`${u.command}\` in ${u.where} (${u.reason})`).join("; ");

  let listed;
  if (!resolved) {
    listed = `No list was resolved for you, so resolve the checks yourself, highest authority first: the repo's own CLAUDE.md and docs, then CI workflow files, then package.json / justfile / Makefile / pyproject.toml.`;
  } else if (resolved.commands && resolved.commands.length) {
    const cut = resolved.truncated
      ? ` That list is cut at ${resolved.commands.length} of ${resolved.resolved_count} resolved; confirm the remaining ones from the same source before you run anything.`
      : "";
    const more = leads
      ? ` It also saw ${unresolved.length} command(s) in the same source it could not resolve, and they may be checks: ${leads}. Read those files and decide for yourself whether each one belongs in the list.`
      : "";
    listed = `The caller resolved these from ${resolved.source}, in order: ${resolved.commands.join(" && ")}. Take that as the list unless the repo contradicts it.${cut}${more}`;
  } else if (leads) {
    listed = `The caller walked the whole chain and resolved nothing runnable, but it did see ${unresolved.length} command(s) it could not resolve: ${leads}. Read those files and build the list yourself from what is there. An empty list is an answer only once you have looked.`;
  } else {
    listed = `The caller walked the whole chain and this project has no checks: no document, no CI workflow and no manifest named one. Confirm that and return an empty list. Do not go hunting for a suite that is not there.`;
  }

  return `Establish this project's green baseline: confirm its checks, then run all of them once.

${listed}

Run what CI runs, not a subset.

Then run every command, once. Running them is the point: it proves the run may execute each
one and it establishes the green baseline for the build.

Return "commands" with every command you confirmed (an empty list when the project has none),
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

1. Re-read \`## Tasks\` on disk. If task ${t.n} is already \`- [x]\`,
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

// `meta` is a literal, so the card's name and description read the same for every spec. The
// slug is the only identification left, and prose is how it reads like a title instead of a
// path fragment: `build-phases-and-cost` becomes `Build phases and cost`.
function asProse(slug) {
  const words = slug.split("-").join(" ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function counted(n, noun) {
  return `${n} ${noun}${n === 1 ? "" : "s"}`;
}

// `args.phases` names its members by `n`, so a task travels once in the payload and the walk
// keeps the spec's document order. Two things the caller cannot promise are settled here: a
// task no group claims sat before the first `###` heading, so it runs first under the
// fallback title, and a group whose every task was already ticked is dropped, because
// `phase()` fires as its group is entered and a header over nothing lies about the run.
function phaseGroups(tasks, phases) {
  if (!phases || !phases.length) return tasks.length ? [{ title: IMPLICIT_PHASE, tasks }] : [];

  const named = phases.map((p) => ({
    title: p.title,
    tasks: tasks.filter((t) => (p.tasks || []).includes(t.n)),
  }));
  const claimed = named.flatMap((g) => g.tasks.map((t) => t.n));
  const loose = tasks.filter((t) => !claimed.includes(t.n));

  return (loose.length ? [{ title: IMPLICIT_PHASE, tasks: loose }] : []).concat(
    named.filter((g) => g.tasks.length),
  );
}

const taskList = args.tasks || [];
// The count is the groups that will actually announce, not the ones the payload declares: on
// a resumed run a `###` group can arrive with no unticked task left in it.
const groups = phaseGroups(taskList, args.phases);

log(
  `${asProse(args.slug || "the spec")} · ${counted(taskList.length, "task")}, ${counted(groups.length, "phase")}`,
);

// Nothing unticked is nothing to build, and stage zero exists to prove the ground before
// task 1: with no task 1 it would run the project's checks and re-read every reuse note for
// a build that never happens. The skill checks this before invoking; the script holds the
// line for a caller that did not.
if (!taskList.length) {
  return {
    slug: args.slug,
    built: [],
    skipped: [],
    pendingVerify: [],
    stopped: null,
    conventions: "",
  };
}

phase(GROUND_PHASE);

const reuseNotes = args.reuseNotes || [];
const resolved = args.checks || null;

// A project whose top authority forbids running its checks locally is settled by
// `scripts/resolve_checks.py` before the dispatch. Sending the agent anyway spends a whole
// stage-zero round trip to come back `ran: false`, which stops the build over a policy
// instead of over the code.
const runChecks = !resolved || resolved.runnable !== false;

const ground = await parallel([
  ...reuseNotes.map(
    (note) => () =>
      agent(reusePrompt(note), {
        label: `reuse: ${note.slice(0, 40)}`,
        phase: GROUND_PHASE,
        schema: REUSE_VERDICT,
        effort: "low",
      }),
  ),
  ...(runChecks
    ? [
        () =>
          agent(checksPrompt(resolved), {
            label: "checks: confirm and run",
            phase: GROUND_PHASE,
            schema: CHECKS_RESULT,
            effort: "low",
          }),
      ]
    : []),
]);

const verdicts = ground.slice(0, reuseNotes.length);

// With no agent sent, the baseline is the policy itself, and `commands` is empty because an
// empty list is what the task agents may execute here.
const checks = runChecks ? ground[ground.length - 1] : { commands: [], ran: true, green: true };
if (!runChecks) {
  log(
    `the project's checks belong to CI here (${resolved.source || "project policy"}); stage zero runs none`,
  );
}

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

  if (runChecks) {
    if (!checks.commands.length) {
      log("no check was found in this project; building without a baseline");
    } else if (!checks.ran) {
      blockers.push(checks.blocker || "a check could not be executed");
    } else if (!checks.green) {
      blockers.push(checks.blocker || "the tree was already red");
    }
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
  for (const g of groups) {
    phase(g.title);
    for (const t of g.tasks) {
      const r = await agent(taskPrompt(t, conventions, checks.commands, args.specPath), {
        label: `task ${t.n}: ${t.title}`,
        phase: g.title,
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
    // A stop ends the run and not just its phase: the tasks share one working tree, so the
    // next phase would build on ground the stop left half-made. The later phases are never
    // announced either, because `phase()` fires as its group is entered.
    if (stopped) break;
  }
}

return { slug: args.slug, built, skipped, pendingVerify, stopped, conventions };
