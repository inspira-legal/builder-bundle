# The pattern of Inspira's animated tours

The pattern comes from three places in the app: the **Análise em Tabela** tour
(`TabularTourDialog`), the **Gestão de Projetos** tour (`ProjectsTourDialog`) and the launch GIF
of **Acompanhamento Processual** (`CaseTrackingLaunchModal`). This page is a copy of
`frontend-projects` at `origin/main` on 2026-10-15 (`7d472a7f9`). In code mode, the repo's
current files win over this copy where the two differ.

The sections below go from the story to the pixels: the narrative, the stage, the palette, the
motion, the recurring pieces and the modal around the art.

## 1. Narrative

- **Use 3 to 5 steps, one idea per step.** Both tours have 4. Each step answers one question:
  "how do I start?", "how does the core work?", "what do I get?".
- **Step 1 is always "create"**, and it is the only step that may exist without a screenshot,
  because it is a piece of the pattern and not a screen. A dashed card sits in the center with
  the feature's icon in a gray square, a short caption and the create button pulsing, with the
  cursor tapping it. The button's label is the starting action the person described ("Adicionar
  processo"), and the icon is the feature's icon in the app menu. Ask when you don't know it.
- **The middle steps show the mechanism** with a miniature of the real interface: the table,
  the phase board, the task card. Use the product's labels, never invented vocabulary.
- **The last step shows the result**: the finished report, the answer with its source.
- **Example data is fictional and plausible**: `Contrato_01.pdf`, "Marina Alves", `R$ 1,2M`,
  an invented CNJ number. Never show real data about a client, a lawsuit or a person, even when
  it appears in the screenshots you received.
  - **Always replace** names of people and companies, lawsuit numbers, CPF and CNPJ, amounts,
    specific dates and file names that come from the screenshots. Replace them even when they
    look fictional: that costs less than finding out later they belonged to a client.
  - **Keep** the vocabulary of the product and of the law: phase and column names, docket entry
    types such as "Publicação" and "Conclusão", courts such as "TJSP", case classes such as
    "Agravo de Instrumento".
- The step's title and body sit **outside** the art (in the modal, below it). The art does not
  repeat the text: at most a caption of 2 to 5 words.

## 2. Stage

- The animated area is **404 × 212 px**: the 452px card less 24px of padding on each side.
- The background is a vertical gradient `sky-2 → neutral-1`. In the modal, the frame adds a
  `neutral-3` border and `rounded-xl`. The stage itself, and so the GIF, has no border and no
  corner, like the Acompanhamento Processual GIF.
- The content is **centered**, in a block **220 to 320px** wide, with room left on both sides.
  A dense screen (a table, a timeline) may reach **360px**, with at least 6px free above and
  below.
- **When a screen does not fit**, reduce in this order. (1) Remove the columns and fields that
  do not tell the step's idea. (2) Cut to 2 or 3 example rows. (3) Truncate the secondary text
  with an ellipsis (`.truncate`). Keep the type at 11px or more, and keep fixed-format
  identifiers (a CNJ number, a CPF or CNPJ) whole: show the full value or leave it out.
- White surfaces (`neutral-1`) sit on the gradient, with a `neutral-5` border (strong) or a
  `neutral-3` border (soft). The dashed line of "an empty place, an action" is 1.5px `neutral-6`.
- The type is small: `caption-sm` (11px) for nearly everything, `body-sm` (13px) for an item's
  main name, `button` (13px) on the call to action. Weights 400, 500 and 600. The font is
  Poppins.

## 3. Palette

Every `StepArt.tsx` declares these aliases at its top, with these values. The scene has the
same classes (`.t-dark`, `.b` and so on).

| Alias (code)    | Tailwind class                 | Scene class    | Hex       |
| --------------- | ------------------------------ | -------------- | --------- |
| `BORDER`        | `border-neutral-5`             | `.b`           | `#dcdee0` |
| `BORDER_SOFT`   | `border-neutral-3`             | `.b-soft`      | `#eef0f3` |
| `BORDER_DASHED` | `border-neutral-6`             | `.b-dash`      | `#d0d3d6` |
| `TEXT_DARK`     | `text-neutral-10`              | `.t-dark`      | `#363f49` |
| `TEXT_MUTED`    | `text-neutral-9`               | `.t-muted`     | `#656c74` |
| `TEXT_FAINT`    | `text-neutral-8`               | `.t-faint`     | `#8e9399` |
| `BG_TABLE`      | `bg-neutral-2`                 | `.bg-table`    | `#f6f7f9` |
| `BG_LAVENDER`   | `bg-sky-2`                     | `.bg-lavender` | `#ecf2fd` |
| `ACCENT_BLUE`   | `text-sky-10`                  | `.t-accent`    | `#5187ec` |
| `TEXT_INDIGO`   | `text-[var(--gradient-4c-to)]` | `.t-indigo`    | `#2d3aa1` |

The other colors the tours use:

| Use                 | Token                                                                      | Hex                   |
| ------------------- | -------------------------------------------------------------------------- | --------------------- |
| Main call to action | `bg-navy-3`, text `neutral-1`                                              | `#1c264f`             |
| Cursor              | `navy-base-dark` with a `neutral-1` outline                                | `#070c20`             |
| Selected item       | border `sky-4`, background `sky-1`, ring `0 0 0 3px rgba(106,151,235,.15)` | `#cfdffc` / `#fafcff` |
| Active cell         | background `sky-2`, inner outline 1.5px `sky-9`                            | `#ecf2fd` / `#6a96ea` |
| Status ok           | `bg-success-2` with `text-success-9` (or `-8`)                             | `#b7ede2` / `#046b57` |
| Status attention    | `bg-warning-2` with `text-warning-8`                                       | `#ffe9bd` / `#e39600` |
| High, critical      | dot `warning-7`, dot `critical-7`                                          | `#f0a10a` / `#bd081d` |
| Progress bar        | track `neutral-3`, fill `sky-6`                                            | `#eef0f3` / `#a8c3f5` |
| Phase stripe        | `border-t-4` in `warning-6`, `sky-6`, `blue-6`                             | from the tokens       |

Every color comes from the design system. When a screenshot shows a color these tables do not
list, use the closest token in the same role (a green "ok" becomes `success`, a highlight blue
becomes `sky`), and say at delivery which screenshot color became which token. Shadows appear
in two places only: the selected item's ring and the cursor's shadow. The app's review accepts
those `shadow-[...]` as an illustration exception.

Radii: `xs` 4, `sm` 8, `md` 10, `lg` 12, `xl` 16. Cards and tables use `lg`, the call to action
`md`, pills `full`.

## 4. Motion

The vocabulary below is closed: reuse these movements as they are. The rules after it say how
to combine them.

### Vocabulary

| Name        | Keyframe                                                              | Duration and curve                                                         | Use                                                 |
| ----------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------- |
| `dlgIn`     | `opacity 0→1`, `translateY(10px) scale(.985)→none`                    | `.28s cubic-bezier(.25,1,.5,1) both`                                       | The modal card's entrance (code mode only)          |
| `stepIn`    | `opacity 0→1`, `translateY(6px)→none`                                 | `.3s cubic-bezier(.25,1,.5,1) both`                                        | One block that enters whole (step 1, the task card) |
| `pop`       | `0%{opacity 0; translateY(6px) scale(.94)} 60%{opacity 1} 100%{none}` | `.4s cubic-bezier(.25,1,.5,1) forwards`, the element starts at `opacity-0` | Elements that enter one by one                      |
| `cursorTap` | `0,100% 0,0 · 45% -2,-2 · 55% 1,1` (px)                               | `1.6s ease-in-out infinite`                                                | The cursor tapping                                  |
| `glowPulse` | `box-shadow 0 0 0 0 rgba(106,151,235,.45) → 0 0 0 7px transparent`    | `2s ease-in-out infinite`                                                  | The tap target pulsing                              |
| `checkPop`  | `opacity 0→1`, `scale(.4)→none`                                       | `.28s cubic-bezier(.25,1,.5,1) forwards`                                   | A checklist item getting checked                    |
| `sheetRise` | `opacity 0→1`, `translateY(10px)→none`                                | `.4s cubic-bezier(.25,1,.5,1) both`                                        | A document or report rising                         |
| `barFill`   | `width 0→N%`                                                          | `.9s cubic-bezier(.25,1,.5,1) .5s both`                                    | A progress bar (N equals the number on screen)      |
| `taskMove`  | moves a card one column to the right, holds, fades and comes back     | `3.6s cubic-bezier(.4,0,.2,1) infinite`                                    | An item changing place (a drag)                     |

### Rules

- **Entrances run once and end visible.** Every entrance uses `forwards` or `both` and settles
  at opacity 1. A looping fade leaves the element half transparent in the middle of the cycle,
  a bug the Tabela tour already fixed once.
- **Stagger siblings by `.15s`** (`0, .15, .3, .45`). A closing element (a callout, a secondary
  button) may come later, at `.65s` to `.9s`. The whole chain of entrances ends by about
  **1.2s**.
- **Loop one point of attention per step, at most.** It is usually the cursor (`cursorTap`) on a
  pulsing target (`glowPulse`), or a movement that tells the action (`taskMove`). The rest of
  the scene holds still once it has entered.
- **Curves:** `cubic-bezier(.25,1,.5,1)` for entrances, `ease-in-out` for pulses,
  `cubic-bezier(.4,0,.2,1)` for moves.
- **Reduced motion:** in code, `@media (prefers-reduced-motion: reduce)` sets duration, delay and
  iteration to their end inside the modal's scope, and everything lands on its final state. In a
  GIF, each step's settled `.png` plays that role (the Acompanhamento Processual modal shows the
  still frame and has a pause button).
- **Prefix:** in code, the keyframes take the tour's prefix (`ttd-`, `ptd-`, and a new one for
  the new feature). In the scene, the prefix is `tour-`.

These curves are the app's, and the GIF has to match the app. So a tour scene follows this page,
not the spring rules of the studio's `CLAUDE.md`: those govern `/bb:reel` films.

### A new movement

Create a new keyframe only when no movement in the table tells the action, the way `taskMove`
was created for "drag between phases". When you create one, give it a single action and the same
family of curves, and write a comment that says what it tells and which measure it depends on
(`taskMove` translates 120px, one column plus one gap, and the column's constant sits beside it).

## 5. Recurring pieces

- **Cursor:** always this SVG, 20 × 20, with the shadow `drop-shadow(0 2px 3px rgba(7,12,33,.3))`.
  It is anchored at the target's bottom right corner (`-right-3.5 -bottom-3.5`):

  ```html
  <svg viewBox="0 0 24 24" fill="#070c20" stroke="#ffffff" stroke-width="1.2">
    <path d="M5 3l6.5 16 2.2-6.6L20 10.5 5 3z" />
  </svg>
  ```

- **The art's call to action:** 38px high, `px-4.5`, `rounded-md`, `bg-navy-3`, the `Plus` icon
  and a short label ("Novo projeto", "Criar análise"), with `glowPulse`.
- **Step 1's dashed card:** 220px, `rounded-xl`, a 1.5px `neutral-6` dashed border, 18px of
  padding, and the icon in a 40 × 40 `bg-neutral-3 rounded-lg` square.
- **Icons:** only the design system's (`@inspira-legal/ui/Icon` in code, `assets/icons` in the
  scene), at sizes `xs` 12 and `sm` 16.

## 6. The modal around the art (code mode only)

The art lives inside a frame that is the same in every tour, and this skill leaves that frame as
it is:

- An overlay `bg-navy-base-dark/55` with `backdrop-blur-[3px]`, a 452px card
  (`max-w-[calc(100vw-2rem)]`), `rounded-xl`, and the `dlgIn` entrance.
- A 30 × 30 close button in the top right corner.
- The body, `px-6 pt-5.5 pb-4.5`: the art (212px, `mb-4.5`), the badge "Bem-vindo à
  &lt;Feature&gt;" (a `sky-2` pill with a `sky-9` dot), the title
  `text-subtitle semibold tracking-[-0.01em]`, and the body `text-body-sm neutral-9` through
  `<Trans>` (it accepts `<strong>`), inside `aria-live='polite'`.
- The footer: "Voltar" (only after step 1), "Passo X de N" (`caption-sm neutral-6`) and the main
  `navy-3` button with `ArrowRight`. On the last step the button becomes the create call to
  action ("Criar meu primeiro projeto") and calls the page's real action.
- **The last button's label has to fit the footer.** The three pieces sit on one line, none of
  them wraps or shrinks (`whitespace-nowrap`, `shrink-0`), and the label gets about 200px of the
  card's 404px: around 26 characters at `text-button`. "Criar meu primeiro projeto" fits;
  "Fazer minha primeira pesquisa" pushes the button out of the card. Write the label to that
  budget in the step plan ("Fazer a primeira pesquisa", "Pesquisar agora"), and check it on
  screen, since a wide letter costs more than a narrow one.
