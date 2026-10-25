# Opening a front

A side session sees only its brief. It does not see this conversation, the person's
earlier answers or the other fronts, so the brief is all the context it will ever have.
This page covers what the brief carries, how the front proves its work, and the rule that
keeps the person's screen free.

## The brief

Write it in `start_session`'s `prompt`, with the shared goal in `background` when the
session starts `fresh`. A brief carries eight things:

1. **The person's exact words**, in quotes. A paraphrase loses the detail the side
   session needs to judge an edge case.
2. **The goal and what done means**: the observable result, and the step it ends on (a
   PR open with green CI, a report, a board of screenshots).
3. **The files and areas** the front touches, as far as the orchestrator knows them.
4. **The decisions already made**, so the side session does not ask them again.
5. **What not to do**: the areas another front owns, and anything the person ruled out.
6. **The person's global rules**: the ones from their `CLAUDE.md` that change how work
   runs, such as checks only in CI or the UI terms the product uses.
7. **How to validate**: the commands, the app run, the behaviors to walk.
8. **How to report**: what goes back by `SendMessage`, which files go to the shared notes
   folder, and that a question for the person comes to the orchestrator.

Add two standing instructions to every brief that ends in a PR: open it with Auto-fix on,
and name the bb skill the front runs (`/bb:spec`, `/bb:implement`, `/bb:review`,
`/bb:ship`).

Give each side session a short `name` and a title that says what the front does. Write
every brief in the language the person speaks, and keep the person's quotes as they
said them.

## Green CI alone is not done

A front that changes the interface proves it in the app before it reports done:

1. Run the app in an isolated instance, with its own debug port and its own data folder,
   so it never touches the instance the person is using.
2. Walk every behavior the change affects.
3. Take a screenshot of each state.
4. Fix what diverges from what was asked, and walk it again.
5. Send the person a board of the screenshots, through the orchestrator.

Write these steps into the brief of every interface front.

## The person's screen stays free

A side session never opens a native dialog on the person's machine: no folder picker, no
save dialog, no print dialog. In an Electron app it mocks `dialog` from the main process,
and in any app it works on test folders, never the person's real ones. Write this rule
into every brief whose front runs the app. A dialog that opens on the person's screen
interrupts what they are doing and can act on their real files.
