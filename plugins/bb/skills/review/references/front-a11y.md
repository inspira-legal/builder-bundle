# Front: a11y — the accessibility of the UI this branch touched

One finder, static, diff-scoped. It reads the markup and styles the branch
changed and finds the WCAG AA failures that are **visible in the source** — no
browser, no running page. The full audit of a rendered page is
`/bb:ui-accessibility`; this front is what a code review can prove from the diff
alone, and the gate offers the deeper one when the findings suggest it.

Criteria and the priority matrix come from the `ui-accessibility` skill — same
vocabulary, so a finding here reads the same as a finding there.

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
- **Contrast** — only when both colors are literal in the diff or resolvable
  through the design tokens the diff uses. Compute the ratio and name it (4.5:1
  for text, 3:1 for UI elements and large text). A color that resolves only at
  runtime is not a finding here — it's a reason to suggest
  `/bb:ui-accessibility`.
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

Priority per the `ui-accessibility` matrix: **Critical** (blocks access
entirely), **Major** (significantly degrades it), **Minor** (inconvenient but
workable), **Enhancement**. Cap 8.

## Scope discipline

- Only elements the diff added or changed. Pre-existing a11y debt in a file the
  branch happens to touch is not this branch's finding — if it's severe, it goes
  in one line at the end as a pointer to `/bb:ui-accessibility`, not as an item
  to fix here.
- A component that inherits its semantics from a design-system primitive is
  judged by what the diff passes it, not by the primitive's internals. Missing
  props (`aria-label` on an icon-only `Button`) are in scope; the primitive's own
  markup is not.
- When the repo's design system documents an accessibility contract (brisa-ds or
  a local one), a violation of it is a `rules` finding with the doc cited, not an
  a11y guess.
