# Opening a front

A side session sees only its brief. It does not see this conversation, the person's
earlier answers or the other fronts, so the brief is all the context it will ever have.
This page covers what the brief carries, the rules every brief repeats, how a front proves
its work, and how it stays off the person's screen.

## The brief

Write it in `start_session`'s `prompt`. With `context: "fresh"`, also write the shared
goal, the decisions so far and how this front fits in `background`, which the call
requires, 80 characters or more. A brief carries eight things:

1. **The person's exact words**, in quotes. A paraphrase loses the detail the side
   session needs to judge an edge case.
2. **The goal and what done means**: the observable result, and the step it ends on (a
   PR open with green CI, a report, a board of screenshots).
3. **The files and areas** the front touches, as far as the orchestrator knows them.
4. **The decisions already made**, so the side session does not ask them again.
5. **What not to do**: the areas another front owns, and anything the person ruled out.
6. **The standing rules** below, every one of them.
7. **How to validate**: the commands, the app run, the behaviors to walk.
8. **How to report**: what goes back by `SendMessage`, which files go to the notes
   folder, and that a question for the person comes to the orchestrator.

Give each side session a short `name` and a title that says what the front does. Write
every brief in the language the person speaks, and keep the person's quotes as they
said them.

## The standing rules

Every brief repeats these, whatever the front:

- **The person's global rules, copied word for word** from their global `CLAUDE.md` and
  the project's. A rule like "checks run only in CI, nothing locally" is a rule of the
  brief whenever the person has it, not an example to pick from.
- **No force push and no rebase on a shared branch.** Bring the base in with a merge.
- **Turn Auto-fix on when the PR opens** (`set_monitor` with `auto_fix: true`). The app
  asks the person to approve the switch, so the brief says the front asks for it.
- **Name the bb skill the front runs**: `/bb:spec`, `/bb:brisar`, `/bb:implement`,
  `/bb:review` or `/bb:ship`.
- **On an interface front, design comes before code.** The front shows screenshots
  first, two variations wherever there is a choice, and asks through `AskUserQuestion`
  with the recommended pick first. It writes the code only after the person approves.
  For a larger design, the front runs `/bb:brisar`.

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
