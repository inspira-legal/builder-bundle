# Front: a11y — WCAG AA over the UI

Two scopes, one method:

- **Diff scope** (default inside a review) — one finder over the markup and
  styles the branch changed, static, no browser. What a code review can prove
  from the diff alone.
- **Surface scope** (`## Auditing a whole surface` below) — the user points at a
  folder, a set of files, or a running page and asks for an audit. Same criteria,
  wider scope, and a rendered page unlocks the checks source can't settle.

Criteria and the priority matrix are shared by both, so findings read the same
either way.

## What's checkable from source

- **Semantics** — a `div`/`span` carrying a click handler, role, or tab index
  where a `button`/`a`/`input` belongs; heading levels skipped; landmarks missing
  on a new page or region; a list built from non-list elements.
- **Names** — an image, icon button, or icon-only link with no accessible name
  (`alt`, `aria-label`, `aria-labelledby`, visually-hidden text); an `alt` that
  repeats the surrounding text or describes the file; a new `<title>`-less SVG
  used as content.
- **Forms** — an input with no associated `<label>` (`for`/`id` or wrapping); a
  placeholder used as the only label; a required field marked only by color or an
  asterisk; a validation error not wired to its field via `aria-describedby`;
  `aria-invalid` missing on a field the diff can put in an error state.
- **Keyboard** — an interaction reachable only by mouse (`onClick` without a key
  handler on a non-native control); `tabindex` greater than 0; a focus trap in a
  new modal/drawer/menu, or one with no escape path (`Escape`, focus return to
  the trigger); focus moved without a reason the user can perceive.
- **Focus visibility** — an `outline: none` / `focus:outline-none` with no
  replacement focus style on the same element.
- **Live regions and state** — new async content (toast, loading state, result
  count, error banner) with no `aria-live`/`role="status"`; a toggle whose state
  lives only in a class name instead of `aria-expanded`/`aria-pressed`/
  `aria-selected`.
- **Contrast** — only when both colors are literal in the source or resolvable
  through the design tokens it uses. Compute the ratio and name it (4.5:1 for
  text, 3:1 for UI elements and large text). A color that resolves only at
  runtime is a finding only in surface scope with the page rendered; in diff scope
  it's reported as out of static reach.
- **Motion and media** — a new animation with no `prefers-reduced-motion`
  branch; autoplay without a control; video/audio added with no captions or
  transcript path.

## Finding shape

```
# | file:line | critério WCAG (nome + número) | o que falha | quem é bloqueado | prioridade | fix
```

`quem é bloqueado` is this front's `failure_scenario` — the user-visible
consequence, stated as the person and the block: "quem navega por teclado não
alcança o botão de confirmar", "leitor de tela anuncia 'botão' sem dizer o quê".
A finding that can't name who loses access isn't one.

Exactly one priority per finding: **Critical** (blocks access entirely),
**Major** (significantly degrades it), **Minor** (inconvenient but workable),
**Enhancement** (better, not required). Cap 8 in diff scope; no cap in surface
scope.

## Scope discipline (diff scope)

- Only elements the diff added or changed. Pre-existing a11y debt in a file the
  branch happens to touch is not this branch's finding — if it's severe, it goes
  in one line at the end as "dívida existente, fora do diff", not as an item to
  fix here.
- A component that inherits its semantics from a design-system primitive is
  judged by what the diff passes it, not by the primitive's internals. Missing
  props (`aria-label` on an icon-only `Button`) are in scope; the primitive's own
  markup is not.
- When the repo's design system documents an accessibility contract (brisa-ds or
  a local one), a violation of it is a `rules` finding with the doc cited, not an
  a11y guess.

## Auditing a whole surface

When the ask is an audit rather than a review of a branch — "auditoria de
acessibilidade", "checa acessibilidade dessa pasta/página", a WCAG check before
merging, the Deliver phase of `/bb:brisar` asking for depth — this front runs
standalone: no diff, no other fronts, no curation question. There may be no git
repository and no branch; the scope is whatever the user pointed at.

1. **Establish the scope.** A folder or file set → enumerate the UI files under it
   (Glob) and read them. A URL or a dev server → open it with the preview/browser
   tools and read the rendered page. Both → do both; the rendered page is the
   authority where they disagree. Nothing named → the UI files of the current
   project.
2. **Walk every criterion above** across that scope, not just the changed lines.
   Fan out one agent per criterion group (semantics+names, forms, keyboard+focus,
   live regions+state, contrast+motion) when the surface is more than a handful of
   files; the barrier and the verify pass in `verify.md` still apply.
3. **With the page rendered, settle what source can't**: computed contrast from
   the actual colors, real tab order and focus visibility (`Tab` through it), what
   a screen reader would announce (the accessibility tree via `read_page`), live
   regions firing on a state change, reflow at 320px and at 200% zoom.
4. **Report grouped by priority**, Critical first, each finding with where
   (file/element), the WCAG criterion that fails, who is blocked, and a concrete
   fix. Close with `WCAG AA: pass | fail | partial` plus the count per priority.
5. **Gate**: offer to fix the Critical/Major findings (`act-apply-fixes.md`), then
   "Encerrar aqui".
