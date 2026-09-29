# Design checklist

The canonical design-system pass over the UI a branch changed, the single source of
truth behind `/bb:review`'s design front, so a surface is judged identically on every
run. **Conformance and consistency only**: whether the UI works for everyone is the
a11y front, whether the code around it is clean is the quality front, and whether the
words are right is brisar's Deliver.

**The citation rule does the most work here.** Every finding names the source it
deviates from: the token file and line, the component's path, the states a component
documents, or the branch's own visual direction. A deviation with no source to cite is
an opinion, and it is dropped, not reported. The sources and their resolution order are
`front-design.md`'s.

**Scope rule:** only what this branch added or changed. Drift in lines the branch never
touched is one closing line of existing debt, never an item to fix here.

## The four criteria

- **Tokens**: a raw value where a token exists. A hex or `rgb()` where the palette has
  the color, a pixel count where the spacing scale has the step, a font size or weight
  off the type scale, a radius, shadow, or duration the tokens already name. The
  finding cites the token that should be there. A raw value with **no** token covering
  it is not a finding; note the gap once at the end, it is the design system's debt,
  not the diff's.
- **Components**: a rebuild of something the DS ships. A local button, dialog, input,
  badge, or card that duplicates an existing component (search the component source
  before concluding it does not exist); a DS component bent past its API, styles
  overridden until it is a fork wearing the component's name; a variant invented
  inline when the component already offers one.
- **States**: interaction built without the states its component documents. The DS
  component or the visual direction names hover, focus, active, disabled, loading,
  empty, or error for this kind of element, and the diff ships the element without
  them. Cite where the states are documented; the focus ring's visibility and keyboard
  reach stay with the a11y front.
- **Consistency**: the same thing done two ways inside the diff, two spacings for the
  same gap, two greys for the same role, a heading level chosen for its size; and,
  when the branch has a visual direction (`.bb/<slug>/design.md`), the built surface
  drifting from the hierarchy and components that direction states.

## Priorities

Exactly one per finding:

- **High**: the source explicitly forbids it, or the diff ships a second source of
  truth, a rebuilt component, a shadow palette.
- **Medium**: a raw value where a token exists, a missing documented state, a DS
  component bent past its API.
- **Low**: drift inside a scale that still reads fine, a neighboring token where
  another was intended, and in-diff inconsistencies with no user-visible cost yet.

## What this checklist is not

- Contrast ratios, accessible names, keyboard, and focus order: the a11y front
  (`front-a11y.md`), even when the failing value is a color. A color that breaks the
  palette is a design finding here even when its contrast passes there.
- Reuse of generic code (helpers, hooks, utilities): the quality front. When the
  duplicate is a DS component, the finding is this front's, cited against the
  component it rebuilds.
- Copy, voice, and tone: brisar's Deliver phase, which reads the brand references.
