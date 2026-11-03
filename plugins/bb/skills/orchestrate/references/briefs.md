# Opening a front

A side session sees only its brief. It does not see this conversation, the person's
earlier answers or the other fronts, so the brief is all the context it will ever have.
This page covers what the brief carries, how a front is named, the scope and the skill it
names, the rules every brief repeats, how a front reports and proves its work, and how it
stays off the person's screen.

## The brief

Write it in `start_session`'s `prompt`. With `context: "fresh"`, also write the shared
goal, the decisions so far and how this front fits in `background`, which the call
requires, 80 characters or more. A brief carries ten things:

1. **The front marker**: a line that says the session is a front of `/bb:orchestrate`,
   names the orchestrator's session id (the `local_…` id `SendMessage` takes in `to`), and
   points to `<plugin-root>/references/front-contract.md`. The line also says that every
   question goes to the orchestrator through `SendMessage`, whatever the skill says, so a
   skill with no front line of its own follows the contract too.
2. **The person's exact words**, in quotes. A paraphrase loses the detail the side
   session needs to judge an edge case.
3. **The goal and what done means**: the observable result, and the step it ends on (a
   PR open with green CI, a report, a board of screenshots).
4. **The scope**, as the next section sets it.
5. **The bb skill to run**, picked by the route below.
6. **The files and areas** the front touches, as far as the orchestrator knows them.
7. **The decisions already made**, so the side session does not ask them again. When the
   code the front touches has a record under `.bb/<slug>/` (a spec, a discovery, a
   design), name its path so the front reads it.
8. **What not to do**: the areas another front owns, and anything the person ruled out.
9. **How to validate**: the commands, the app run, the behaviors to walk.
10. **How to report**, as "How to report" says, with the notes folder's path, and the
    standing rules below, every one of them.

Give each side session a title and a `name` as "Naming a front" says, and open it with
`wake_when_done: true`, so a front that stops idle on a question wakes the orchestrator.

Write the brief and its `background` in English. `<plugin-root>/references/doc-style.md`
puts a string the person reads in their language; the traffic between sessions is read
by sessions, so it is English, which costs fewer tokens across a run. That covers the
brief, the front's questions and reports, and every message the orchestrator sends a
front. The person's words keep the language they were said in: the brief quotes the
request as said, and an answer goes back to the front quoted as the person gave it. What
the person reads, the questions the orchestrator asks and the reports it gives, stays in
their language.

## Naming a front

The sidebar is how the person tells the fronts apart, so every front carries one title
pattern and one `name` rule. This section holds both, and when a title changes.

**The title** is an English imperative, a verb and the outcome, in sentence case and under
60 characters: "Fix session naming in orchestrate", "Add debug skill", "Migrate sites
to Cloudflare". It says what the front delivers. The stage (spec, build, PR), the repo
and the bb skill the front runs stay out of it, because the sidebar already shows the PR
and its state. A skill appears only when it is the thing being built. When the title would
pass 60 characters, write a shorter one.

**The `name`** is the front's slug: the `.bb/<slug>/` folder its spec lives in and the
branch it works on. Pick the slug when you open the front, then make the `name` with the
script, passing the `name`s of the run's live sessions:

```
python3 scripts/front_name.py <slug> --live <name> <name> ...
```

It prints `{slug, name, cut, collision}`. Pass `name` as `start_session`'s `name`, and the
full `slug` as `branch_name`; the app wraps the branch in the person's branch prefix and a
suffix, so the slug is the part of the branch name that matches the spec folder. Always
pass `name`: when it is omitted, `start_session` derives one from the title and cuts it
mid-word. A slug over 24 characters keeps its full form in the branch and the spec folder,
and the `name` is cut at the last hyphen that fits (`orchestrate-session-naming` becomes
`orchestrate-session`). `start_session` does not enforce a unique `name`, but linked
sessions and `SendMessage` reach a front by it, so two live fronts with one `name` are
ambiguous. When `collision` is true, pick another slug and run the script again before the
start. Pass `--live` only the `name`s of sessions that are not archived: an archived
front has left the run, so its `name` is free again. The build front of a spec front that
stopped at the spec takes its slug once the spec front is archived (`references/cleanup.md`,
"When a front ends").

A front with no spec (an error for `/bb:debug`, a PR for `/bb:takeover`) gets the slug of
its branch, made from its title: pass the title to the script and use the `slug` it
prints.

**The slug in the brief.** Write the slug into the brief as the one the front's
`/bb:spec` uses for `.bb/<slug>/` and the branch it works on. When `/bb:spec` finds that
folder taken by another spec, it suffixes the slug and reports it; the `name` stays.

**Renaming.** The `name` never changes after the start. The title changes only when the
front's work changes: you reuse the front for another task, or the scope grows or shrinks
until the old title misleads. A new stage, a PR opening or a front finishing keeps the
title; archiving is what closes a front. Rename with `set_session_title` on the front's
session. When the person set the title themselves, the app asks them to approve the new
one: tell them which approval is waiting. In an unattended run the call can decline
instead, so read its result and tell the person the title stayed. When they decline, the
title stays, and you do not ask again.

## The scope

A code front runs at the full scope unless the person asked for less: build, review and
ship, up to a PR with green CI, with no merge. Write the scope in the brief in those
words, so `/bb:implement` reads it and asks nothing, and the exit gate of `/bb:spec` takes it
as the answer to what runs after the build.

When the person asks for less in the request, the brief sets that scope instead. A build
only stops at a green, committed branch. A merge stays with the orchestrator, and only
for a PR the person authorized (see `references/landing.md`).

## The skill route

Pick the skill from what the person asked for, and name it in the brief:

| the request                                    | the skill the front runs         |
| ---------------------------------------------- | -------------------------------- |
| a feature or a change of behavior              | `/bb:spec`, then `/bb:implement` |
| an idea or a diffuse problem                   | `/bb:discover` or `/bb:spec`     |
| an interface to design                         | `/bb:brisar`, then `/bb:spec`    |
| an idea that needs research first              | `/bb:research`, then `/bb:spec`  |
| an error in DEV or PROD                        | `/bb:debug`                      |
| someone else's PR to adopt or bring up to date | `/bb:takeover`                   |
| a branch to read for bugs                      | `/bb:review`                     |
| a built branch to land                         | `/bb:ship`                       |

`/bb:maintain-repo` only reads the repo, so the orchestrator runs it in place, with no front.
When the route names a skill the installed plugin lacks, name the closest skill that
exists and tell the person which one the front runs.

## The standing rules

Every brief repeats these, whatever the front:

- **The person's global rules, copied word for word** from their global `CLAUDE.md` and
  the project's. A rule like "checks run only in CI, nothing locally" is a rule of the
  brief whenever the person has it, not an example to pick from.
- **Work in a worktree of your own.** A code front that opened with no worktree, as when
  the session's folder is not a git repository, creates its own with `git worktree add`
  on a new branch before it touches a file, and works only there.
- **No force push and no rebase on a shared branch.** Bring the base in with a merge.
- **Turn Auto-fix on when the PR opens** (`set_monitor` with `auto_fix: true`). The app
  asks the person to approve the switch, so the brief says the front asks for it.
- **On an interface front, design comes before code.** The front shows screenshots
  first, two variations wherever there is a choice, and sends the choice to the
  orchestrator with the recommended pick first. It writes the code only after the person
  approves. A front that runs `/bb:brisar` meets this rule through brisar's own phases
  and gates.

## How to report

Write this section into every brief:

- **A question for the person** goes to the orchestrator through `SendMessage`, with its
  options and the recommended pick, as the front contract says. Then the front waits.
- **A page** (a board, a report, a design) is published as an Artifact, and its URL goes
  to the orchestrator in the same message that says what the page shows.
- **A local file** (a screenshot, a video) goes to the notes folder, and its path goes to
  the orchestrator.
- **The final report**, at done or at a blocker, carries the result, the PR url with the
  state of its CI, and the blockers.

## The notes folder

The notes folder is a folder outside the repository, created by the orchestrator for the
run, where side sessions leave what does not fit a message: screenshots, boards, long
reports and hand-over notes. Name its path in every brief. The orchestrator reads what
lands there and sends the files to the person with `SendUserFile`. A folder outside the
repository keeps the run's material out of every branch.

## Green CI alone is not done

A front that changes what the person sees proves it in a running instance before it
reports done:

1. Run the project in an isolated instance (the next section says how for each kind of
   project), so it never touches the instance the person is using.
2. Walk every behavior the change affects.
3. Take a screenshot of each state.
4. Fix what diverges from what was asked, and walk it again.
5. Send the person a board of the screenshots, through the orchestrator.

Write these steps into the brief of every interface front.

## The person's screen and files stay untouched

A side session works on its own instance and on test data, never on the person's. What
that takes depends on the project:

| kind of project | the isolated instance                                                   |
| --------------- | ----------------------------------------------------------------------- |
| desktop app     | its own debug port and data folder; native dialogs mocked               |
| web app         | its own dev-server port and an isolated browser profile; a test account |
| CLI             | a temporary home or config folder, and test folders as input            |

**When the project is a desktop app**, the front opens no native dialog on the person's
machine: no folder picker, no save dialog, no print dialog. In an Electron app it mocks
`dialog` from the main process. A dialog that opens on the person's screen interrupts
what they are doing and can act on their real files. Write this rule into every brief
whose front runs the app.
