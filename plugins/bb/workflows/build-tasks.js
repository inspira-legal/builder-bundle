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

// Cost is bought with the model and capability is kept with `effort`, so the two dials move
// together and only one of them is about price. A tier that cut the reasoning of the case that
// needs it would be saving money on the answer instead of on the lookup.
const CHEAP_MODEL = "sonnet";

// A name the platform does not know takes down the dispatch, and every one of these arrives from
// a caller that read a spec, so the set is checked here rather than trusted. `haiku` left the
// build with the cheap tier's move to `sonnet`, so a payload that still names it is dropped and
// said out loud like any other unknown name.
const KNOWN_MODELS = ["sonnet", "opus"];

const MANIFESTO_REF = "plugin-level references/consult-manifesto.md";

// One agent answers every note, so the shape is an array and `index` is what pairs an
// answer back to the note it answers. The index set is what the script checks: an agent that
// dropped a note would otherwise leave that note reading as `intact`.
const REUSE_VERDICTS = {
  type: "object",
  required: ["verdicts"],
  properties: {
    verdicts: {
      type: "array",
      items: {
        type: "object",
        required: ["index", "verdict", "note"],
        properties: {
          index: { type: "number", description: "the note this answers, numbered as sent" },
          verdict: { type: "string", enum: ["intact", "moved", "gone"] },
          note: { type: "string" },
          where: { type: "string", description: "the new path, required when moved" },
        },
      },
    },
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
    worktree: { type: "string", description: "the worktree's absolute path, when built in one" },
    conventions: { type: "string" },
    blocker: { type: "string" },
  },
};

// `landed` and `conflicts` together have to account for every commit the landing agent was
// handed: the script checks that, since a commit neither landed nor named as a conflict would
// otherwise vanish between one phase and the next.
const LAND_RESULT = {
  type: "object",
  required: ["landed", "conflicts", "checksGreen", "conventions"],
  properties: {
    landed: { type: "array", items: { type: "number" } },
    conflicts: {
      type: "array",
      items: {
        type: "object",
        required: ["n", "with", "files"],
        properties: {
          n: { type: "number", description: "the task whose commit did not land" },
          with: { type: "array", items: { type: "number" } },
          files: { type: "array", items: { type: "string" } },
        },
      },
    },
    checksGreen: { type: "boolean" },
    blocker: { type: "string" },
    conventions: { type: "string" },
  },
};

// The role and the whole read protocol belong to `agents/bb-reuse-check.md`, which the
// harness delivers as the system prompt. What is left here is what only the caller has: the
// notes and their numbering.
function reusePrompt(notes) {
  const numbered = notes.map((note, i) => `${i}. ${note}`).join("\n");
  return `A spec's reuse notes say the build should extend code that already exists. Find out whether each one still does.

The notes, numbered by the index your answer carries:

${numbered}

Answer every note, one entry per index, and do not edit anything.`;
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

// `together` is the one fork in the contract: a task that shares its phase with others is built
// in a worktree of its own, and what it would otherwise do on the shared tree (tick its box, run
// the checks, extend the note) moves to the landing agent, which sees the whole phase at once.
// Nothing about the phase's other members enters the prompt: the resume cache is keyed on it, and
// the same task has to send the same string whichever of its neighbours already landed.
function taskPrompt(t, conventions, checks, specPath, together) {
  const start = together
    ? `1. Start from the run branch. You are in a git worktree of your own, and other tasks of the
   same phase are being built at the same time, each in its own. The first entry
   \`git worktree list --porcelain\` prints is the main checkout, and its \`branch\` is the run
   branch. When your HEAD is not that branch's tip, \`git reset --hard\` to it before anything
   else: the phase builds on the branch as the previous phase left it.
2. Re-read \`## Tasks\` on disk. If task ${t.n} is already \`- [x]\`,
   return immediately with status "skipped" and an empty "conventions". The run is resumable
   and what already landed must not be redone.`
    : `1. Re-read \`## Tasks\` on disk. If task ${t.n} is already \`- [x]\`,
   return immediately with status "skipped" and the conventions you received, unchanged. The
   run is resumable and what already landed must not be redone.`;

  const k = together ? 1 : 0;

  const checking = together
    ? `${4 + k}. Run none of the project's checks here: they run once over the whole phase after it
   lands, on the run branch.`
    : `${4 + k}. Run the project's checks and fix what broke. Re-run a failed check at most ${RETRY_CAP}
   times, and only while no file changed between runs: a check that fails and then passes
   with the tree untouched is a flake. Once a file changed, the failure is yours to fix.`;

  const committing = together
    ? `${5 + k}. Commit only the files this task touched, in exactly one commit, and leave \`## Tasks\`
   as it is: each box is ticked as its task lands on the run branch. Conventional style, and no
   AI attribution anywhere in the message. Return the sha in "commit" and your worktree's
   absolute path in "worktree".`
    : `${5 + k}. Commit only the files this task touched, together with its \`- [ ]\` to \`- [x]\` in the
   same commit, on the branch already checked out. Conventional style, and no AI attribution
   anywhere in the message. The commit is the checkpoint.`;

  const noting = together
    ? `${6 + k}. Return the structured result, with "conventions" carrying only what you established:
   names and paths you introduced, signatures other tasks will call, a pattern you chose among
   alternatives, a technical gap you settled. Leave out the note you received and anything
   already written in the spec: the notes of the whole phase are joined after it lands. Keep
   it short.`
    : `${6 + k}. Return the structured result, with "conventions" carrying the note you received plus what
   you established: names and paths you introduced, signatures other tasks will call, a
   pattern you chose among alternatives, a technical gap you settled. Nothing already written
   in the spec. Past roughly ${NOTE_CEILING} characters, condense your oldest entries before
   returning.`;

  const checksLine = together
    ? ""
    : `\nThe project's checks: ${checks && checks.length ? checks.join(" && ") : "none were found"}\n`;

  return `Build one task of a spec you did not write, in a repo you have not seen.

The spec: ${specPath}. Read it whole before touching anything: the opening and the free top
half describe the thing, and the fixed sections are the contract. Build to \`## Behavior\`,
stay inside \`## Out of scope\`. \`## Attention points\` names the technical risks the author
saw, each with where it lives: handle the ones your task meets, and the way through each one
is yours to choose.

Your task is ${t.n}: ${t.title}
It delivers: ${t.delivers}
Its \`verify:\` is: ${t.verify}

What earlier tasks established (names, paths, signatures, patterns chosen, and any reuse
target that moved). This outranks a path the spec names:
${conventions || "nothing was recorded; the spec is all you have."}
${checksLine}
The spec says what gets built and how it behaves. A technical detail it leaves open (a name,
a file layout, a library, an algorithm) is yours to settle with the code open: decide, build,
and record the choice in the convention note. "underspecified" is for the one gap a decision
of yours cannot close: a business rule or a behavior your task needs that the spec does not
state, or that contradicts another.

Your steps:

${start}
${2 + k}. Build the task. A stack choice the spec left open (framework, package manager, tooling)
   is settled against the manifesto first: ${MANIFESTO_REF}.
${3 + k}. Satisfy \`verify:\`. A command gets run, and "result" is "passed" or "failed". "reading"
   means self-inspection: read what you produced against what the task delivers and the
   \`## Behavior\` rows it touches, and return short evidence. "CI" is out of reach in here, so
   return "pending", which is neither a pass nor a failure. Every \`verify:\` runs.
${checking}
${committing}
${noting}

A check still red after the retries, a \`verify:\` that came back "failed", or a spec too
underspecified to build against all mean the same thing: do not commit, do not revert. Leave
the tree as it is for diagnosis and return the blocker.${together ? " Name your worktree's path in the blocker, since that tree is where the diagnosis happens." : ""} A \`verify:\` still "pending" is a
green task: it commits, and the pending rides out to ship.`;
}

// The landing agent is the one place a phase's parallel work meets the run branch, so it owns
// everything that would collide there if each task did it for itself: the cherry-picks, the ticks
// in the one `spec.md`, the `## Open` lines for the tasks that stopped, the checks, and the join
// of the notes. `landed` is ordered by `n` so two runs of the same phase land in the same order.
function landPrompt(title, specPath, landed, failed, conventions, checks) {
  const commits = landed.map((o) => `- task ${o.t.n} (${o.t.title}): ${o.r.commit}`).join("\n");
  const stoppedList = failed
    .map(
      (o) =>
        `- task ${o.t.n} (${o.t.title}): ${o.failed.status}: ${o.failed.blocker || "no blocker given"}`,
    )
    .join("\n");
  const notes = landed
    .map((o) => `- task ${o.t.n}: ${o.r.conventions || "nothing new"}`)
    .join("\n");

  const openStep = failed.length
    ? `
3. Record each task that did not come back green under \`## Open\` in the spec, one line per
   task naming the task, its status and its blocker, in place of a lone \`Nothing.\` there.
   Commit that change alone, conventional style (\`docs(spec): ...\`).`
    : "";
  const n = failed.length ? 1 : 0;

  return `Land one phase of a build on the run branch.

The phase "${title}" of the spec ${specPath} built its tasks at the same time, each in a git
worktree of its own, and each green one left one commit there. You are in the main checkout,
on the run branch, and that branch is where they land.

${commits ? `The commits to land, in this order:\n${commits}` : "No task of this phase came back green, so there is no commit to land."}
${stoppedList ? `\nThe tasks of this phase that did not come back green, which land nothing:\n${stoppedList}\n` : ""}
The note the phase started from:
${conventions || "nothing was recorded."}

What each green task established:
${notes || "nothing."}

The project's checks: ${checks && checks.length ? checks.join(" && ") : "none were found"}

Your steps:

1. Confirm the checkout is on a branch and its tree is clean. A detached HEAD or a dirty tree is
   a blocker: return it and touch nothing.
2. Land each commit in the order above with \`git cherry-pick <sha>\`. Right after one lands
   clean, flip that task's \`- [ ]\` to \`- [x]\` in \`## Tasks\` of the spec and fold it into the
   same commit with \`git commit --amend --no-edit\`: a landed task and its tick are one
   checkpoint. When a pick stops on a conflict, take the conflicted files from
   \`git diff --name-only --diff-filter=U\`, run \`git cherry-pick --abort\`, and record it under
   "conflicts": the task whose commit did not land, the tasks already landed in this phase whose
   commits touched those files (\`git show --name-only <sha>\`), and the files. Then go on with
   the next commit. Resolve no conflict yourself: two tasks that changed the same lines are the
   author's to reconcile.${openStep}
${3 + n}. When at least one commit landed and there are checks, run each once over the landed tree.
   Re-run a failed check at most ${RETRY_CAP} times, and only while no file changed between runs.
   Fix nothing: a check still red is a blocker naming the command, with "checksGreen" false.
   With no checks, or nothing landed, "checksGreen" is true.
${4 + n}. Return "landed" with the numbers of the tasks whose commits landed, "conflicts",
   "checksGreen", "blocker" when step 1 or a check stopped you, and "conventions": the note the
   phase started from plus what each landed task established, each entry as it came. Leave out
   what a task that did not land established. Past roughly ${NOTE_CEILING} characters, condense
   the oldest entries.

No AI attribution in any commit message.`;
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

// The platform rejects with an `Error`, but a thunk may reject with a plain value, and a blocker
// that reads `[object Object]` names nothing. The string form is the floor: at worst it repeats
// what the run's own `<failures>` already says.
function messageOf(err) {
  return (err && err.message) || String(err);
}

// The checks agent has two jobs behind one label, and only one of them is mechanical. Confirming
// a list `resolve_checks.py` already produced and running it reads a payload and executes it.
// Walking the authority chain with no list at all, opening the files the `unresolved` leads name
// to decide whether each one is a check, and confirming the rest of a truncated list from its own
// source are the judgments the resolver could not make, and that one keeps the session's tier.
function checksTier(resolved) {
  const mechanical =
    resolved &&
    resolved.commands &&
    resolved.commands.length &&
    !resolved.truncated &&
    !(resolved.unresolved && resolved.unresolved.length);
  return mechanical ? { model: CHEAP_MODEL, effort: "low" } : {};
}

// How hard a task is, is what only the reader of the spec knows, so it travels in the payload
// instead of being guessed from the task's own line here. Nothing is returned when the payload
// says nothing: an absent key is what makes an agent inherit the session's model, and passing
// `model: null` is not the same thing.
function taskTier(t) {
  return t.model && KNOWN_MODELS.includes(t.model) ? { model: t.model } : {};
}

// `args.phases` names its members by `n`, so a task travels once in the payload and the walk
// keeps the spec's document order. Two things the caller cannot promise are settled here: a
// task no group claims sat before the first `###` heading, so it runs first under the
// fallback title, and a group whose every task was already ticked is dropped, because
// `phase()` fires as its group is entered and a header over nothing lies about the run.
//
// `together` is what a `###` heading earns: its tasks were written to need nothing from each
// other. The fallback group never earns it, since tasks with no heading above them carry no such
// promise and keep the order they were written in. `dep:` is not read here at all: phase order
// replaced it, and a spec that still carries the field builds the same as one that does not.
function phaseGroups(tasks, phases) {
  if (!phases || !phases.length) {
    return tasks.length ? [{ title: IMPLICIT_PHASE, together: false, tasks }] : [];
  }

  const named = phases.map((p) => ({
    title: p.title,
    together: true,
    tasks: tasks.filter((t) => (p.tasks || []).includes(t.n)),
  }));
  const claimed = named.flatMap((g) => g.tasks.map((t) => t.n));
  const loose = tasks.filter((t) => !claimed.includes(t.n));

  return (loose.length ? [{ title: IMPLICIT_PHASE, together: false, tasks: loose }] : []).concat(
    named.filter((g) => g.tasks.length),
  );
}

// Every way a task result can fail to count as done, in one place, so the phase that runs one
// task and the phase that runs several read a return the same way. Null for a task that is done
// or skipped. A null return carries no blocker of its own, so one is written here: assigning it
// straight to `stopped` would read to the caller as a clean run over a half-built spec. A task
// whose `verify:` did not run is not done either, so green over a missing or failed verify is a
// contradiction the caller cannot see: `built` would name the task and ship would read it as
// proven. And a task built in a worktree lands through its sha, so green with none is a commit
// nobody can find.
function failureOf(r, t, together) {
  if (!r) return { n: t.n, status: "red", blocker: "lost agent (null return)" };
  if (r.status === "skipped") return null;
  if (r.status !== "green") return r;
  const proven = r.verify && (r.verify.result === "passed" || r.verify.result === "pending");
  if (!proven) {
    return {
      n: r.n,
      status: "red",
      blocker: r.verify
        ? `task ${r.n} returned green with verify ${r.verify.result}`
        : `task ${r.n} returned green with no verify result`,
    };
  }
  if (together && !r.commit) {
    return { n: r.n, status: "red", blocker: `task ${r.n} returned green with no commit to land` };
  }
  return null;
}

const taskList = args.tasks || [];
// The count is the groups that will actually announce, not the ones the payload declares: on
// a resumed run a `###` group can arrive with no unticked task left in it.
const groups = phaseGroups(taskList, args.phases);

log(
  `${asProse(args.slug || "the spec")} · ${counted(taskList.length, "task")}, ${counted(groups.length, "phase")}`,
);

// Every name is read before stage zero and not at the call that uses it: a typo reaching the
// platform would take down a run that had already proved its ground, and a whole stage zero is
// what it would waste. Dropped rather than fatal, and said out loud, because a silent fallback
// to the session's model reads as the tier the caller asked for.
const unknownTier = taskList.filter((t) => t.model && !KNOWN_MODELS.includes(t.model));
if (unknownTier.length) {
  log(
    `${counted(unknownTier.length, "task")} asked for a model this script does not know (${unknownTier.map((t) => `${t.n}: ${t.model}`).join(", ")}); the session's model is used instead`,
  );
}

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

// The tier is read before the fan-out so the run can say which of the checks agent's two jobs
// this payload gave it. Silent, the expensive branch reads as the cheap one.
const groundTier = checksTier(resolved);
if (runChecks && !groundTier.model) {
  log(
    "the check list needs judgment the resolver could not make; that agent keeps the session's model",
  );
}

// A dispatch that never happened and an agent that ran and answered nothing reach the code below
// the same way, as an empty slot, and only the platform's message tells them apart. Each thunk
// records its own cause on the way past, so the stop can name it.
const dispatchError = { reuse: "", checks: "" };

// Two thunks at most, and the reuse one carries every note: a subagent's context floor is
// paid per agent and re-read on every turn it takes, so eight notes over eight agents pay
// that floor eight times for eight lookups of three tool calls each.
const ground = await parallel([
  ...(reuseNotes.length
    ? [
        () =>
          agent(reusePrompt(reuseNotes), {
            label: `reuse: ${counted(reuseNotes.length, "note")}`,
            phase: GROUND_PHASE,
            agentType: "bb:bb-reuse-check",
            schema: REUSE_VERDICTS,
            // `Grep` on a symbol and a verdict per note is the whole job, and the schema is
            // what shapes the answer, so nothing here is bought by a stronger model.
            effort: "low",
            model: CHEAP_MODEL,
          }).catch((err) => {
            dispatchError.reuse = messageOf(err);
            log(`the reuse agent could not run: ${dispatchError.reuse}`);
            // Re-thrown rather than swallowed: the slot stays empty, `parallel()` still reports
            // the failure, and the script runs on to build the stop out of what was recorded.
            throw err;
          }),
      ]
    : []),
  ...(runChecks
    ? [
        () =>
          agent(checksPrompt(resolved), {
            label: "checks: confirm and run",
            phase: GROUND_PHASE,
            schema: CHECKS_RESULT,
            ...groundTier,
          }).catch((err) => {
            dispatchError.checks = messageOf(err);
            log(`the checks agent could not run: ${dispatchError.checks}`);
            throw err;
          }),
      ]
    : []),
]);

const reuseResult = reuseNotes.length ? ground[0] : null;
const verdicts = (reuseResult && reuseResult.verdicts) || [];

// With no agent sent, the baseline is the policy itself, and `commands` is empty because an
// empty list is what the task agents may execute here.
const checks = runChecks ? ground[ground.length - 1] : { commands: [], ran: true, green: true };
if (!runChecks) {
  log(
    `the project's checks belong to CI here (${resolved.source || "project policy"}); stage zero runs none`,
  );
}

// The index set is what proves coverage, and the count is not: an answer that repeats one
// index and drops another has the right length, and the dropped note never reaches the
// filters below, which read the answers and cannot look for one that is missing. So it would
// read as `intact` and the build would extend code nobody looked for.
const answered = new Set(verdicts.map((v) => v.index));
const unanswered = reuseNotes.map((_, i) => i).filter((i) => !answered.has(i));
const stray = verdicts.filter((v) => !(v.index >= 0 && v.index < reuseNotes.length));

// `moved` is the one verdict that carries a path, and a schema cannot make a field required
// on a single enum value. Unchecked, a missing `where` renders as the literal `undefined` in
// the convention note every task agent then reads.
const placeless = verdicts.filter((v) => v.verdict === "moved" && !v.where);

// A lost stage-zero agent is a stop of its own: proceeding would build on ground nobody
// proved. A malformed answer is the same stop.
let stopped = null;
if (reuseNotes.length && !reuseResult) {
  stopped = {
    n: 0,
    status: "red",
    blocker: dispatchError.reuse
      ? `the reuse agent could not run: ${dispatchError.reuse}`
      : "the reuse agent returned nothing",
  };
} else if (unanswered.length) {
  stopped = {
    n: 0,
    status: "red",
    blocker: `${counted(unanswered.length, "reuse note")} of ${reuseNotes.length} went unanswered (${unanswered.join(", ")}); stage zero proved nothing`,
  };
} else if (stray.length) {
  stopped = {
    n: 0,
    status: "red",
    blocker: `the reuse agent returned ${counted(stray.length, "verdict")} against an index no note carries; stage zero proved nothing`,
  };
} else if (placeless.length) {
  stopped = {
    n: 0,
    status: "red",
    blocker: `a reuse target moved with no path to it: ${placeless.map((v) => v.note).join("; ")}`,
  };
} else if (!checks) {
  stopped = {
    n: 0,
    status: "red",
    blocker: dispatchError.checks
      ? `the checks agent could not run: ${dispatchError.checks}`
      : "the checks agent returned nothing",
  };
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

// One task at a time, on the shared tree: the fallback group, and a `###` group left with a
// single unticked task, which is the way a task ran before phases ran together.
async function runInLine(g) {
  for (const t of g.tasks) {
    const r = await agent(taskPrompt(t, conventions, checks.commands, args.specPath, false), {
      label: `task ${t.n}: ${t.title}`,
      phase: g.title,
      schema: TASK_RESULT,
      ...taskTier(t),
    });
    const failed = failureOf(r, t, false);
    if (failed) return failed;
    if (r.status === "skipped") {
      skipped.push(r.n);
      continue;
    }
    conventions = r.conventions;
    if (r.verify.result === "pending") pendingVerify.push(r.n);
    built.push(r.n);
  }
  return null;
}

// Every task of the phase at once, each in a worktree, then one landing agent over what came
// back. A red task cancels nothing: its neighbours were written to need nothing from it, so the
// green ones land and the run stops before the next phase, with the red one in `## Open`. The
// checks run once, after the landing, because a copy of the suite per worktree is memory this
// machine does not have.
async function runTogether(g) {
  log(`${g.title}: ${counted(g.tasks.length, "task")} run together, each in a worktree of its own`);

  const results = await parallel(
    g.tasks.map(
      (t) => () =>
        agent(taskPrompt(t, conventions, [], args.specPath, true), {
          label: `task ${t.n}: ${t.title}`,
          phase: g.title,
          schema: TASK_RESULT,
          isolation: "worktree",
          ...taskTier(t),
        }),
    ),
  );

  const outcomes = g.tasks.map((t, i) => ({
    t,
    r: results[i],
    failed: failureOf(results[i], t, true),
  }));
  const failed = outcomes.filter((o) => o.failed);
  const green = outcomes.filter((o) => !o.failed && o.r.status !== "skipped");
  skipped.push(...outcomes.filter((o) => !o.failed && o.r.status === "skipped").map((o) => o.t.n));

  if (!green.length && !failed.length) return null;

  const land = await agent(
    landPrompt(g.title, args.specPath, green, failed, conventions, checks.commands),
    {
      label: `land: ${g.title}`,
      phase: g.title,
      schema: LAND_RESULT,
      // Cherry-picks, ticks and one run of the checks are mechanical; naming a conflict and
      // condensing the note are the judgment, and the cheap tier carries both.
      model: CHEAP_MODEL,
    },
  );

  const causes = failed.map(
    (o) => `task ${o.t.n} ${o.failed.status}: ${o.failed.blocker || "no blocker given"}`,
  );

  if (!land) {
    const waiting = green.map((o) => `task ${o.t.n} at ${o.r.commit}`).join(", ");
    causes.push(
      `the landing agent of "${g.title}" returned nothing; ${waiting || "no commit"} still waits in its worktree`,
    );
    return { n: g.tasks[0].n, status: "red", blocker: causes.join(" | ") };
  }

  const greenNs = green.map((o) => o.t.n);
  const landedNs = greenNs.filter((n) => (land.landed || []).includes(n));
  const conflicts = (land.conflicts || []).filter(
    (c) => greenNs.includes(c.n) && !landedNs.includes(c.n),
  );
  const unaccounted = greenNs.filter(
    (n) => !landedNs.includes(n) && !conflicts.some((c) => c.n === n),
  );

  green
    .filter((o) => landedNs.includes(o.t.n))
    .forEach((o) => {
      built.push(o.t.n);
      if (o.r.verify.result === "pending") pendingVerify.push(o.t.n);
    });

  // The agent's join is the note, since it condensed it; the script's own join is the floor for
  // an agent that landed work and returned no note, so what the phase established still travels.
  const joined = [conventions]
    .concat(
      green
        .filter((o) => landedNs.includes(o.t.n))
        .map((o) => `task ${o.t.n}: ${o.r.conventions || ""}`),
    )
    .filter(Boolean)
    .join("\n");
  conventions = land.conventions || joined;

  conflicts.forEach((c) => {
    const others = (c.with || []).length ? `tasks ${c.n} and ${c.with.join(", ")}` : `task ${c.n}`;
    causes.push(
      `${others} changed the same lines in ${(c.files || []).join(", ") || "files the landing did not name"}; task ${c.n} did not land`,
    );
  });
  if (unaccounted.length) {
    causes.push(
      `the landing agent neither landed nor named a conflict for task(s) ${unaccounted.join(", ")}`,
    );
  }
  if (!land.checksGreen) {
    causes.push(land.blocker || `the checks went red after "${g.title}" landed`);
  } else if (land.blocker) {
    causes.push(land.blocker);
  }

  if (!causes.length) return null;
  // A lone red task is handed back as it came, so its status (`underspecified` included) reaches
  // the caller intact; anything more is one stop carrying every cause, like stage zero's.
  if (causes.length === 1 && failed.length === 1) return failed[0].failed;
  const first = failed.length ? failed[0].t.n : conflicts.length ? conflicts[0].n : g.tasks[0].n;
  return { n: first, status: "red", blocker: causes.join(" | ") };
}

if (!stopped) {
  for (const g of groups) {
    phase(g.title);
    stopped = g.together && g.tasks.length > 1 ? await runTogether(g) : await runInLine(g);
    // A stop ends the run and not just its phase: the next phase builds on what this one landed,
    // and a half-landed phase is not that ground. The later phases are never announced either,
    // because `phase()` fires as its group is entered.
    if (stopped) break;
  }
}

return { slug: args.slug, built, skipped, pendingVerify, stopped, conventions };
