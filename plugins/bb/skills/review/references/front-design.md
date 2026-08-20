# Front: design, deviations from the design system the project has

Two scopes, one method:

- **Diff scope** (default inside a review): one finder over the UI the branch changed,
  static, judged against the design source the repo carries. What a code review can
  prove from the diff and the source together.
- **Surface scope** (`## Reviewing a whole surface` below): the user points at a
  folder, a set of files, or a running page and asks for a design review. Same
  criteria, wider scope, and a rendered page unlocks the checks source can't settle.

The criteria are `design-checklist.md`, sibling of this file, shared by both scopes so
findings read the same either way. The discipline is the `rules` front's, applied to
design sources: **a finding is worth what its citation is worth**, so every finding
names what it deviates from, and one that cannot is dropped, never reported as a guess.

## 1. The design source

Resolve it before the front offers itself, in this order, keeping every rung that
resolves (they supplement each other):

1. **`design-context/` at the repo root**: the `tokens.md` and `components.md` that
   `/bb:brisar`'s scaffold writes. The distilled source, made for exactly this read.
2. **A token source the project itself reads**: a `tokens.json`, a stylesheet of CSS
   custom properties, or a Tailwind theme config. The file the build consumes is the
   authority on what a token is; a brand package that nothing imports is not one.
3. **The branch's visual direction**: `.bb/<slug>/design.md`, or `design/<surface>.md`
   plus its index, when the branch's spec folder carries one. It supplements the token
   and component sources with the intended hierarchy, components, and states for the
   surfaces this branch builds.

Nothing resolving makes the front **unavailable**, the same way no
`CODE_REVIEW_GUIDE.md` makes `rules` unavailable: with no source there is nothing to
cite, and the engine does not ship opinion. The report does not mention an unavailable
front; the probe (`fronts.md`) is where the decision lives.

Report at the top of the front's section which sources resolved and were judged
against. Rungs 1 and 2 disagreeing on a value is itself a finding, `design-context/` is
generated and can go stale against the source the build reads.

## 2. What's checkable

The four criteria of `design-checklist.md`, in short: **tokens** (a raw value where a
token exists), **components** (a rebuild of something the DS ships, or a component bent
past its API), **states** (interaction missing the states its component documents), and
**consistency** (the same thing done two ways inside the diff, or drift from the
branch's visual direction). The checklist carries the full definitions, the priorities,
and the boundaries; read it before finding anything.

The boundaries in one line each, because three neighbors border this front:

- Contrast, accessible names, keyboard, focus: the `a11y` front, even when the failing
  value is a color.
- Generic code reuse: the `quality` front; a duplicated **DS component** is this
  front's, cited against the component it rebuilds.
- Copy and voice: brisar's Deliver phase, not a review front.

## Finding shape

```
# | file:line | criterion (token, component, state, consistency) | what deviates | source cited | priority | fix
```

`source cited` is the citation the discipline demands: the token file and line, the
component's path, where the states are documented, or the design.md section. The
priorities are the checklist's: **High**, **Medium**, **Low**. Cap 8 in diff scope; no
cap in surface scope.

## Scope discipline (diff scope)

- Only elements the diff added or changed. Pre-existing drift in a file the branch
  happens to touch is not this branch's finding: one line at the end as existing debt.
- A raw value with no token covering it is the design system's gap, not the diff's
  deviation. One closing line names the gap; it is not an item.
- When the repo's `CODE_REVIEW_GUIDE.md` itself states a design rule, a violation of it
  is a `rules` finding with the guide cited, not a duplicate here. This front judges
  against the design sources; the guide stays the `rules` front's.

## Reviewing a whole surface

When the ask names a **surface** instead of a branch (a folder, a file set, a URL, a
running page: "design review of this page", "does this folder follow the design
system"), or brisar's Deliver gate asks for depth, this front runs standalone: no diff,
no other fronts, no curation question. The scope is whatever the user pointed at.

1. **Resolve the design source first.** Standalone changes nothing about §1: no source,
   no review, and say so with what would create one (a `design-context/`, a token file,
   or a visual direction from `/bb:brisar`).
2. **Establish the scope.** A folder or file set → enumerate the UI files under it
   (Glob) and read them. A URL or a dev server → open it with the preview/browser tools
   and read the rendered page. Both → both; the rendered page is the authority where
   they disagree.
3. **Walk the four criteria** across that scope, not just changed lines. Fan out one
   agent per criterion (tokens, components, states, consistency) when the surface is
   more than a handful of files; the barrier and the verify pass in `verify.md` still
   apply, with the enumerated file set as `scope_files` and **no report cap**.
4. **With the page rendered, settle what source can't**: the computed value where the
   cascade decides (which color actually painted, which spacing actually resolved),
   states reached by actually hovering and focusing, and consistency across breakpoints.
   Values still come from the source or the computed styles, never measured off a
   screenshot.
5. **Report grouped by priority**, High first, each finding with where, the criterion,
   the source cited, and a concrete fix. Close with the per-priority count and the one
   line of design-system gaps found along the way.
6. **Gate** (per the plugin-root `references/handoff-gate.md`): "Fix the High and
   Medium ones (Recommended)" → `act-apply-fixes.md`, then "Stop here".
