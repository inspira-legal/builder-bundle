# Code mode: the tour inside the app

Code mode is for a person working in the `frontend-projects` repository (the app lives in
`apps/inspira`). It produces a `<Feature>TourDialog` shaped like the tours that already exist,
ready for a PR. The sections below go in the order of the work: read, write the folder, wire it
in, turn the screenshots into steps, and verify.

## 1. Read before writing

Read the repo's current files, not only the copies in `references/examples/`. Where the repo and
the copy differ, the repo wins:

- `apps/inspira/src/pages/Projects/components/ProjectsTourDialog/` (`index.tsx`, `StepArt.tsx`,
  `types.ts`, `ProjectsTourDialog.spec.tsx`). It is the **mold**, and it already uses
  `useHeadlessModal`.
- `apps/inspira/src/pages/DocumentVault/components/TabularTourDialog/StepArt.tsx`, the other
  reference art.
- `apps/inspira/src/hooks/useHeadlessModal/index.ts`.
- `CODE_REVIEW_GUIDE.md` at the monorepo's root (scoped per project), searched for `StepArt` and
  `TourDialog`. Onboarding illustrations may carry their own SVG. The guide lists the two
  `shadow-[...]` of `TabularTourDialog/StepArt.tsx` as occurrences that remain, so a new
  `shadow-[...]` (the selected item's ring) goes with the guide's escape: a `ds-allow: REASON`
  comment on its line, or on the line above it in JSX.

When Projects is no longer the newest tour, take the newest as the mold:

```bash
git log --diff-filter=A --format=%ad --name-only -- 'apps/inspira/src/**/*TourDialog/index.tsx'
```

## 2. Write the folder

In `apps/inspira/src/pages/PAGE/components/FEATURETourDialog/`:

| File                         | What it holds                                                                                                                                                                                                                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `index.tsx`                  | A copy of `ProjectsTourDialog`'s frame: `KEYFRAMES` with the new prefix, `TITLE_KEYS` and `BODY_KEYS` as literal tuples, `useHeadlessModal`, `useLocalStorage`, the events. Only the names, the prefix, the keys and the final call to action change.                                                   |
| `StepArt.tsx`                | The palette aliases (`pattern.md`, section 3) copied as they are, the `Cursor`, one component per step (`StepCreate`, then one per mechanism, then the result), `STEPS`, `STEP_COUNT` and `StepArt`.                                                                                                    |
| `types.ts`                   | `FEATURETourDialogProps { enabled: boolean; onCreate: () => void }`, with the create action named for the feature.                                                                                                                                                                                      |
| `FEATURETourDialog.spec.tsx` | The same cases as Projects' spec: it opens when `enabled` and not seen, it moves between steps, "Voltar" shows only after step 1, finishing calls the create action and stores the seen flag, it closes by the X, by Escape and by an outside click with the right `reason`, and it tracks every event. |

The keyframe prefix is short and its own: `ttd-` (tabular), `ptd-` (projects). For a new
feature, use its initials plus `td-` (for example `aptd-` for Acompanhamento Processual), and the
same prefix on the scope class (`PREFIXscope`) of the reduced motion rule.

## 3. Wire it in

| Where                                       | What                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/shared/enums.ts`, `LocalStorageKeys`   | `featureTourSeen = 'feature-tour-seen'`                                                                                                                                                                                                                                                                                                                                                                     |
| `src/lib/i18n/locales/pt-BR/NAMESPACE.json` | A `tour` block with `badge`, `finish`, `progress` and `stepN.{title, body, art*}`. Close, back and next come from `common.close`, `common.back` and `common.tutorial.next`, as in Projects. Every string of the art is an `art*` key: the `i18next/no-literal-string` lint rejects loose text. Today `pt-BR` is the only locale; when `ls src/lib/i18n/locales/` shows more, the key goes into all of them. |
| `analytics.config.ts`                       | A `feature_tour` group in the `e` syntax, copied from `projects_tour`: `view: e.impression({})`, `next` and `prev` as `e.click({ step: e.number() })`, `finish: e.click({})`, and `dismiss: e.click({ reason: e.enum(['close_button', 'escape', 'outside']), step: e.number() })`. No `legacy`: the catalog has `legacyNames: true`, and these names follow the convention.                                 |
| `src/lib/events/types.ts`                   | The lines `feature_tour_ip_view`, `_ck_next`, `_ck_prev`, `_ck_finish` and `_ck_dismiss`, under a section comment. `events.track` only takes an id whose derived `legacy` name (`LegacyNameOf` in `catalog.ts`) is a key here, and reads its properties from that line.                                                                                                                                     |
| The feature's page                          | `<FEATURETourDialog enabled={...} onCreate={...} />` beside the create dialog that the final call to action opens (see `pages/Projects/index.tsx`). `enabled` turns true only when the page loaded without an error and sits on its entry screen.                                                                                                                                                           |

## 4. Turn the screenshots into steps

1. List what each screenshot shows and which question of the user it answers.
2. Group them into 3 to 5 ideas, one per step. Step 1 is "create", the last one is "the result".
3. For each step, choose **the miniature**: the smallest crop of the real screen that tells the
   idea, with the screen's real labels and icons. Reuse the i18n keys that already exist for
   product labels (`projects.phases.triage`, `documentVault.tabularReview.table.documentColumn`),
   and create `art*` keys only for the fictional data.
4. For each step, choose **the movement** from the table in `pattern.md`, section 4: what enters
   in a stagger, and which single point of attention loops.

The step plan goes to the person for approval (SKILL.md, step 3) before any code.

## 5. Verify

- Run `pnpm --filter inspira lint`, `ts:check`, `spell:check` and `test:ci` (the new spec at
  least). The app's `lint` is `oxfmt . && oxlint --fix .`: it formats and fixes the whole app,
  not only the tour. Run `git status` after it, and leave out of the branch any change outside
  the tour's files and its wiring.
- Run the app (`pnpm --filter inspira dev`), open the page with `localStorage` cleared for the
  new key, and go through the steps. Compare with the screenshots and with an existing tour open
  beside it: the same frame, the same rhythm.
- Turn on "reduce motion" in the system and check that each step shows already settled.
- On the last step, look at the footer: "Voltar", "Passo N de N" and the final call to action fit
  inside the card, with the button's right edge before the card's padding. A label that pushes
  the button out goes back to the budget of `pattern.md`, section 6, and gets shorter.
- At phone width (375px) the card shrinks through its `max-w`, and the art stays inside it. Look
  at the last step's footer there too, and when even the existing tours overflow at that width,
  say so instead of changing the shared frame.

The same tour often needs a GIF later, for communication or the help center. Once the code is
approved, port each step component to a scene (`gif-mode.md`): the classes and the aliases map
one to one (`pattern.md`, section 3).
