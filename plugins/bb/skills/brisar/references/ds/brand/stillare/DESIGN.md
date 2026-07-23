# Stillare — Style Reference
> Destila ruído em essência. Sub-brand of Inspira.

**Theme:** flexible (light + dark) — **gray-forward in both**
**Brand:** Stillare (Inspira's meeting-intelligence product — destila reuniões em decisões, contexto, dúvidas e tarefas — feminine, "ela")
**Substrate:** Brisa DS (sub-brand inheriting from Inspira)
**Visual idiom:** Slate-forward "knowledge command center" — calm neutral volume, one surgical accent
**Status:** **prescriptive** — this DESIGN.md is written to *build* the platform, not to document an existing prototype. Where LexFlow's spec was reverse-engineered from Pencil, Stillare's is forward-engineered from brand intent + reference reads. Tokens here are the source of truth until `brand/stillare/tokens/` is generated.

Stillare nasce da ideia de **destilar**: transformar excesso em essência, fazer a informação gotejar até revelar o que importa. Em meio a transcrições longas, dispersas e cheias de ruído, ela identifica **gotas valiosas** — decisões tomadas, o contexto que sustenta cada escolha, dúvidas que ainda precisam de resposta, tarefas que movem o próximo passo. Ela revela o racional por trás das decisões e evidencia os princípios que orientam o time, mesmo quando não ditos. *Se a reunião é o fluxo, Stillare é a inteligência que condensa.*

The visual language serves that metaphor literally: **the noise is gray, the drop is blue.** A calm, desaturated slate fills the volume; Cornflower Blue marks only what was distilled out as valuable. The brand's role is **isonomy with Inspira via Cornflower** — the same welcoming blue face the parent uses (`#6a97eb` ≈ Stillare `#6a96ea`), so a user moving between Inspira and Stillare feels one family, even though Stillare trades the parent's white canvas for a gray one.

## The Five Principles (inherited)

Stillare inherits Brisa's ranked five — full text in `../principles.md`. Sub-brands do not redefine principles; they redefine pigment. Stillare's reading of each:

1. **Dar Pé** — accessibility, predictability. Contrast ≥ 4.5:1 on body in *both* themes (the gray canvas makes this the easiest principle to fail — see Theming). Focus ring always visible.
2. **Clareza** — one direct purpose per element. The whole product is a clareza engine; the UI must not add noise back. A distilled drop reads in one glance.
3. **Ritmo e Fluidez** — motion 100–300ms, never >500ms. Stillare ships explicit motion tokens (below) — Inspira does not yet.
4. **Segurança e Transparência** — every distilled claim is traceable to its source line in the transcript. A drop with no source is a bug, not a feature (see SourceTag / grounding).
5. **Leveza** — whitespace is a feature. On a gray canvas, leveza comes from *air*, not from color.

## What Stillare Inherits, Overrides, and Adds

This is the sub-brand contract.

### Inherits from Inspira (do not redefine)

- The five principles, in priority order.
- **Type family:** Poppins as the primary sans.
- **Type weights:** Regular (400), Medium (500), Semibold (600). No Bold, no Light.
- **Type rules:** no italics, no all-caps, ≤ 3 type roles per screen, body ≥ 13px.
- **Spacing philosophy:** 4pt base, 8pt grid; the full Inspira spacing ladder (up to `--space-24`).
- **Semantic token contract:** components reference semantic tokens, never primitives. This is what lets light↔dark and Inspira↔Stillare swap cleanly.
- **Cornflower Blue as the family thread.** Stillare's accent IS Inspira's Cornflower face. Do not pick a different blue.
- **Brand outcomes:** Consistência, Autoridade, Reconhecimento.

### Overrides Inspira

| Concern | Inspira | Stillare |
|---|---|---|
| Canvas | White (`#ffffff` page) | **Gray.** Light theme pages on `slate-50` (`#f4f6f8`), cards on white. Dark theme pages on `slate-950` (`#15171c`). |
| Theme | Light only (v1) | **Flexible:** light + dark, both gray-forward. Same semantic tokens resolve per theme. |
| Neutral family | Cool Gray (blue-tinted, `#8995ae` face) | **Slate Gray** (`#6f7a93` face) — the brand's protagonist color, slightly more saturated/cooler than Cool Gray. Used everywhere. |
| Primary CTA fill | Rich Black `#070c21` | **Cornflower accent** `#6a96ea` (single accent — see below). No Rich Black equivalent. |
| CTA dual hierarchy | Primary (Rich Black) + Secondary (Cornflower) | **Single accent** for the primary action; slate neutrals for everything else. |
| Tropical Indigo (AI accent) | First-class, gradient endpoints | **Not used.** Stillare's idiom is single-accent. Every Stillare surface is already AI — a separate "AI moment" color would be noise. |
| Spectrum gradients | First-class | Dropped. One quiet brand wash only (see Gradients). |
| Status semantics | Generic (success/warning/critical/info) | **Re-cast as the four entities** — Decisão / Princípio / Racional / Risco get first-class semantic color (see Tokens — The Four Entities). |
| Elevation | Shifts + borders, no shadows | Real shadows, theme-tuned (light: soft & cool; dark: deep). The gray canvas needs gentle elevation to separate surfaces. |

### Adds (gaps Inspira has, Stillare fills)

- **Dark theme** — a full parallel semantic set. Inspira is light-only; Stillare defines both.
- **Mono type family** — JetBrains Mono (same as LexFlow, for family coherence) for transcript text, timestamps, speaker IDs, cited snippets, and IDs.
- **The Four Entities color system** — `--color-entity-{decisao|principio|racional|risco}` semantic pairs (fg + bg) that classify distilled content. This is Stillare's signature contribution.
- **Source / grounding primitives** — every drop traces to a transcript line. `SourceTag`, `CitationRef`, `TranscriptPeek` (gap that getunblocked's "grounded answer" idiom inspired).
- **Motion + shadow + layout tokens** — same families LexFlow added (candidates for promotion to Inspira).

## Theming — light + dark, gray-forward

Stillare is the first Brisa brand designed theme-flexible from day one. The rule: **components reference semantic tokens only; the theme layer remaps them.** An `<EntityCard>` written against `--color-bg-surface` and `--color-text-primary` renders correctly in both themes with zero component changes.

- Light is the default. Dark is opt-in via `[data-theme="dark"]` on `<html>` (or `.dark` class — pick one at scaffold and stay consistent).
- **Gray-forward in both:** light is *not* Inspira-white. The page is `slate-50`, not `#ffffff` — cards rise to white. This is what "mais cinza" means: the neutral is the star, white is the highlight.
- **Contrast is the watch item (Dar Pé).** Slate mid-tones (`slate-400`–`slate-600`) are tempting for secondary text but fail 4.5:1 on a `slate-50` page at small sizes. Validate every text/bg pairing in *both* themes. When in doubt, go one step darker (light) / lighter (dark).
- The Cornflower accent (`#6a96ea`) is the **one token that does not change** between themes — it's the family thread and the "drop." It reads on both gray canvases.

## Tokens — Colors

Two-layer system, same as the parent: components reference semantic tokens; primitives are brand scales. Stillare defines a **Slate** scale (neutral protagonist) and reuses **Cornflower** (accent).

### Primitives — Slate (the protagonist neutral)

Brand face is `slate-500` `#6f7a93` (the value the brand deck fixed). Full ramp:

| Token | Value | Token | Value |
|---|---|---|---|
| `--color-slate-50` | `#f4f6f8` | `--color-slate-500` | `#6f7a93` (face) |
| `--color-slate-100` | `#e9ecf1` | `--color-slate-600` | `#5a6377` |
| `--color-slate-200` | `#d4d9e1` | `--color-slate-700` | `#474e5e` |
| `--color-slate-300` | `#b3bacb` | `--color-slate-800` | `#353a46` |
| `--color-slate-400` | `#8d96ad` | `--color-slate-900` | `#23262e` |
| | | `--color-slate-950` | `#15171c` |

### Primitives — Cornflower (the accent / the drop)

Inherited from Inspira, face aligned to the brand deck's `#6a96ea`.

| Token | Value | Role |
|---|---|---|
| `--color-cornflower-50` | `#f0f5fe` | Accent wash |
| `--color-cornflower-100` | `#dbe7fc` | Soft accent bg |
| `--color-cornflower-200` | `#bcd1f9` | Accent bg / hover |
| `--color-cornflower-300` | `#93b4f3` | Accent border |
| `--color-cornflower-400` | `#6a96ea` | **Accent face — the drop. CTAs, links, focus ring.** |
| `--color-cornflower-500` | `#4a78d8` | Accent pressed |
| `--color-cornflower-600` | `#3a61c0` | Accent strong |

### Semantic — Background (light / dark)

| Token | Light | Dark | Role |
|---|---|---|---|
| `--color-bg-base` | `#f4f6f8` (slate-50) | `#15171c` (slate-950) | Page background |
| `--color-bg-surface` | `#ffffff` | `#1d2029` | Cards, panels — *rises* off the gray page |
| `--color-bg-elevated` | `#ffffff` (+ shadow) | `#262a35` | Dropdowns, modals, popovers |
| `--color-bg-input` | `#ffffff` | `#2d313d` | Form controls |
| `--color-bg-sunken` | `#eef1f5` | `#101216` | Transcript well, code/quote blocks — *sinks* below the page |

Note the inversion logic: in light, surfaces rise toward white; in dark, surfaces rise toward lighter slate. `--color-bg-sunken` is unique to Stillare — the transcript (the raw "fluxo") sits *recessed*, the distilled drops *rise* above it.

### Semantic — Text (light / dark)

| Token | Light | Dark | Role |
|---|---|---|---|
| `--color-text-primary` | `#1f232b` | `#e8eaef` | Body, primary content |
| `--color-text-secondary` | `#5a6377` (slate-600) | `#a9b1c2` | Secondary text, descriptions |
| `--color-text-muted` | `#8d96ad` (slate-400) | `#6f7a93` (slate face!) | Metadata, timestamps, placeholders |

In dark, the brand face `#6f7a93` lands naturally as muted text — the brand color appears as the quiet voice. Verify `--color-text-secondary` on `--color-bg-base` in light meets 4.5:1 (`#5a6377` on `#f4f6f8` ≈ 5.6:1 — passes).

### Semantic — Accent

| Token | Light & Dark | Role |
|---|---|---|
| `--color-accent` | `#6a96ea` | Primary interactive — links, CTAs, focus ring, the drop |
| `--color-accent-hover` | light `#4a78d8` / dark `#85a9ee` | Accent hover (darkens in light, lightens in dark) |
| `--color-accent-muted` | light `#dbe7fc` / dark `#243352` | Accent backgrounds, badge fills |
| `--color-accent-subtle` | light `#f0f5fe` / dark `#1a2233` | Soft accent wash, hover surfaces |

`--color-accent` is the single most important token in the sub-brand. It does not change across themes. Everything else is slate; this is the drop.

### Semantic — Border

| Token | Light | Dark | Role |
|---|---|---|---|
| `--color-border` | `#d4d9e1` (slate-200) | `#353a46` (slate-800) | Default borders, dividers |
| `--color-border-strong` | `#b3bacb` (slate-300) | `#474e5e` | Emphasis borders |
| `--color-border-subtle` | `#e9ecf1` (slate-100) | `#23262e` | Faint separators |

Focus ring: `--color-focus-ring: var(--color-accent)`, always visible (Dar Pé).

### Semantic — The Four Entities (the drops)

Stillare's signature. The four kinds of distilled content — the "gotas" — each get a first-class color pair (foreground + background). This replaces generic status semantics. Each pair must pass contrast in both themes.

> **Taxonomy note.** The brand deck framed the drops poetically as *decisões, contexto, dúvidas, tarefas*. The built product (Stillare v2 MVP) crystallized them into the four entity types below — **decisão, princípio, racional, risco** — which is the canonical taxonomy. The poetry stays in the intro; the system uses these four. The colors were tuned on the real product surface and dropped Rich Black + Tropical Indigo (per the single-accent rule), keeping four clearly distinct hues on the gray canvas.

| Entity | Meaning | FG / BG token | Color family |
|---|---|---|---|
| **Decisão** | A decision was made | `--color-entity-decisao-{fg\|bg}` | **Cornflower** — the most valuable drop *is* the accent |
| **Princípio** | A durable rule the team operates by (appears across sources) | `--color-entity-principio-{fg\|bg}` | **Strong Slate** — authority via dark neutral (inherits the gravity Rich Black used to carry) |
| **Racional** | The "why" / evidence behind a decision | `--color-entity-racional-{fg\|bg}` | **Keppel green** — the connective insight |
| **Risco** | A future situation that could hurt the team/product | `--color-entity-risco-{fg\|bg}` | **Madder** — danger (pairs with severity: média→Saffron, alta→Madder) |

| Token | Light | Dark |
|---|---|---|
| `--color-entity-decisao-fg` | `#3a61c0` | `#93b4f3` |
| `--color-entity-decisao-bg` | `#f0f5fe` | `#1a2233` |
| `--color-entity-principio-fg` | `#353a46` | `#cdd2db` |
| `--color-entity-principio-bg` | `#eef1f5` | `#2a2e38` |
| `--color-entity-racional-fg` | `#186d5f` | `#5fd6bd` |
| `--color-entity-racional-bg` | `#f1fcf8` | `#142a26` |
| `--color-entity-risco-fg` | `#b32231` | `#f0808c` |
| `--color-entity-risco-bg` | `#fdeef0` | `#2c1719` |

Short alias `--ent-{type}-{fg|bg}` is acceptable in prototypes. **Decisão owns the accent** — it's the only entity that borrows the brand's one saturated color; the other three sit quieter, by design.

### Semantic — Feedback (system states, not entities)

System feedback (errors, saving, success toasts) inherits Inspira's feedback colors unchanged: Madder critical, Saffron warning, Keppel success, Cornflower info. Keep these **distinct in usage** from the entity colors — an entity color classifies *content*, feedback reports *system state*. Risco (Madder) and a critical banner (also Madder) must not collide on one screen; separate them by component shape and placement.

### Semantic — CTA

| Token | Value | Role |
|---|---|---|
| `--cta-primary-bg` | `var(--color-accent)` | Primary action fill |
| `--cta-primary-fg` | `#ffffff` | Primary action text |
| `--cta-primary-hover` | `var(--color-accent-hover)` | Primary hover |
| `--cta-neutral-bg` | light `#ffffff` / dark `#2d313d` | Neutral fill (with border) |
| `--cta-neutral-fg` | `var(--color-text-primary)` | Neutral text |
| `--cta-ghost-fg` | `var(--color-text-secondary)` | Ghost text |
| `--cta-ghost-hover` | `var(--color-accent-subtle)` | Ghost hover bg |
| `--cta-danger-bg` | `#d62c3d` (Madder) | Destructive fill (post-confirmation) |
| `--cta-danger-fg` | `#ffffff` | Destructive text |

## Tokens — Typography

### Families

```css
--font-sans: "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
--font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
```

Poppins inherited from Inspira, unchanged (same three weights, no italics, no all-caps). Stillare adds **JetBrains Mono** — the same mono LexFlow uses, for family coherence. Mono is reserved for: **transcript text, timestamps, speaker IDs, cited snippets, IDs, and the `.mono` helper.** The transcript is *data* — it reads as mono; the distilled drops are *prose* — they read as Poppins. That contrast is meaningful: raw fluxo (mono) vs. condensed clareza (sans).

### Weights

Same three as Inspira. No deviation. Regular `400` (body, transcript), Medium `500` (labels, buttons, speaker names), Semibold `600` (titles, drop headings).

### Size Scale

Stillare uses a scale between Inspira's display-friendly ladder and LexFlow's dense one — it has long reading surfaces (transcripts) *and* dense metadata (timestamps, chips).

| Token | Size | Use |
|---|---|---|
| `--fs-11` | 11px | Micro labels, badge text |
| `--fs-12` | 12px | Caption, timestamps (mono), table cells |
| `--fs-13` | 13px | Default button, dense metadata |
| `--fs-14` | 14px | **Default body / UI.** Drop content. |
| `--fs-15` | 15px | Transcript body (slightly larger — it's read at length) |
| `--fs-17` | 17px | Subheadings, drop-group titles |
| `--fs-20` | 20px | Section titles, modal headings |
| `--fs-24` | 24px | Page titles |
| `--fs-32` | 32px | Hero / meeting title (empty states, report header) |

Line heights: `--lh-tight: 1.25`, `--lh-normal: 1.5`, `--lh-relaxed: 1.6` (transcript uses relaxed). Letter spacing: `--tracking-tight: -0.02em` (display only), `--tracking-mono: 0`.

## Tokens — Spacing & Shapes

### Spacing — 4pt base, 8pt grid (inherited from Inspira, full ladder)

Stillare keeps Inspira's full spacing ladder (`--space-px` … `--space-24`/96px) — it needs the larger steps for comfortable transcript reading and report layouts. See Inspira's `DESIGN.md` for the complete table.

### Spacing rhythm — in practice

Tokens don't make a layout breathe; rhythm does. Stillare's air is deliberately generous — on a gray canvas, crowding reads as anxiety and space reads as confidence. These are the defaults that make a Stillare screen feel calm and intentional rather than dense and nervous:

| Context | Value | Token |
|---|---|---|
| Gap between major page sections | 28px | `--space-7` |
| Page inset (content padding) | 28px top · 40px sides | `--space-7` / `--space-10` |
| Card / panel padding | 18–20px | `--space-4`–`--space-5` |
| Panel header padding | 16px × 20px | `--space-4` × `--space-5` |
| Gap between cards in a grid | 12–16px | `--space-3`–`--space-4` |
| List-row vertical padding | 12–14px | `--space-3`–`--space-3.5` |
| Label → its value | 3–6px | `--space-1`–`--space-1.5` |
| Max content width | 1240px | — |

Rules of thumb:
- **One altitude of generosity per nesting level.** Page sections breathe at 28px; rows *inside* a panel breathe at 12–14px. The hierarchy lives in the *ratio* between levels, not in absolute values — never let inner spacing rival outer spacing.
- **Group tight, separate wide.** A label sits 3px from its number; the next group is 28px away. Proximity does the grouping, so you need almost no dividers. A screen with good proximity looks composed; one with even spacing everywhere looks like a form.
- **Whitespace is the cheapest contrast.** Before reaching for a border or shadow to separate two things, add space. Space is the first move, a border the second, a shadow the third — in that order, always (Leveza).

### Border Radius

Between Inspira (rounder, lighter) and LexFlow (tighter, denser). Drops are cards that should feel calm and contained.

| Token | Value | Use |
|---|---|---|
| `--radius-xs` | 4px | Tight badges, chips |
| `--radius-sm` | 6px | Inputs, small controls |
| `--radius-md` | 10px | Default buttons, drop cards |
| `--radius-lg` | 14px | Elevated cards, modals |
| `--radius-xl` | 20px | Hero / report surfaces |
| `--radius-pill` | 9999px | Pills, drop-type chips, avatars |

### Shadows — theme-tuned

The gray canvas needs gentle elevation. Light shadows are soft and cool-tinted; dark shadows are deep.

| Token | Light | Dark |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(35,38,46,0.06)` | `0 1px 2px rgba(0,0,0,0.4)` |
| `--shadow-md` | `0 4px 12px rgba(35,38,46,0.08)` | `0 4px 12px rgba(0,0,0,0.5)` |
| `--shadow-lg` | `0 12px 28px rgba(35,38,46,0.12)` | `0 12px 32px rgba(0,0,0,0.6)` |

## Motion

| Token | Value |
|---|---|
| `--duration-fast` | 140ms |
| `--duration-normal` | 220ms |
| `--duration-slow` | 320ms |
| `--ease-out` | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` |

Satisfies Brisa's Ritmo principle (100–300ms). Signature motion: a drop **distilling** out of the transcript — a short fade+rise (`--duration-normal`, `--ease-out`) from the sunken transcript well up to a surface card. Use once per distillation event, never decoratively.

## Craft & Taste — what makes it feel alive

A token table is inert. These are the moves that give Stillare its pulse — the difference between *correct* and *crafted*. Treat them as defaults, not decorations. If a screen feels lifeless, it's almost always missing two or three of these.

1. **Mono numerals as instrument readout.** Every number that is *data* — counts, deltas, confidence %, timestamps, source totals, `⌘K` — renders in JetBrains Mono with `font-feature-settings: "tnum"` (tabular figures). It makes the product read like an instrument that *measures*, not a brochure that *describes*. Prose stays Poppins. This sans/mono split is the single most characterful decision in the system — lean on it hard.

2. **The accent is punctuation, not paint.** On a full screen the Cornflower should appear maybe five times: the active nav item, the two numbers in the greeting, the "destilado" chip, one primary button. That scarcity is what makes each one land. If you can't defend an accent as *the most valuable thing in its region*, make it slate.

3. **The 3px left bar.** Count cards and entity cards carry a 3px left border in their entity color — a quiet spine that classifies at a glance without shouting. This is Stillare's most repeatable signature; reach for it before a full colored background.

4. **Surfaces lift on contact; rows wash.** A card rests flat (`--shadow-sm`) and on hover gains `translateY(-1px)` + a stronger border over `--duration-normal`. A list *row* never lifts — it washes to `--bg-sunken`. Hover itself teaches the user what's a destination (lifts) vs. what's a row (washes).

5. **Confident, quiet headlines.** Page titles are `--fs-32` Semibold at `-0.02em` tracking — crafted, not default. And they state a fact about *your* memory ("Essa semana destilamos **15** entidades de **12** fontes") instead of naming the screen ("Dashboard"). The product talks; it doesn't label. Numbers in the headline are accent + mono — the one place data and brand color meet.

6. **The droplet, earned.** The distillation glyph appears only where something was *actually distilled* — the "destilado" chip, the AI activity row, the logo. It's the brand's verb. Never decorative, never a generic bullet.

7. **Restraint is the aesthetic.** Stillare looks expensive because it withholds: no gradients on cards, no shadows competing for attention, no second accent. The gray is not a background you tolerate — it *is* the taste. Every time you're tempted to add, remove first (Leveza), and let the one thing that survives be sharp. A Stillare screen should feel like it was *edited*, the way the product edits a meeting down to its drops.

## Layout

| Token | Value | Use |
|---|---|---|
| `--sidebar-width` | 264px | Left rail (meetings list / nav) |
| `--topbar-height` | 56px | Top app bar |
| `--content-max-width` | 1280px | Main content max |
| `--transcript-width` | 480px | Transcript panel (split view) |
| `--modal-width` | 560px | Modal default |

**Signature layout — the split.** A meeting view is a two-panel split: the **transcript** (raw fluxo) on one side in the sunken well (mono, recessed), the **distilled drops** on the other (Poppins, raised cards). Clicking a drop scrolls+highlights its source line in the transcript. This split *is* the product's core metaphor made spatial: fluxo ↔ essência.

## Surfaces

| Level | Token | Light | Dark | Purpose |
|---|---|---|---|---|
| −1 (sunken) | `--color-bg-sunken` | `#eef1f5` | `#101216` | Transcript well, quote blocks |
| 0 (page) | `--color-bg-base` | `#f4f6f8` | `#15171c` | Page background |
| 1 (surface) | `--color-bg-surface` | `#ffffff` | `#1d2029` | Drop cards, panels |
| 2 (elevated) | `--color-bg-elevated` | `#ffffff` + shadow | `#262a35` | Dropdowns, modals |
| 3 (input) | `--color-bg-input` | `#ffffff` | `#2d313d` | Form controls |

The sunken→raised ladder is the spatial spine: raw goes down, distilled comes up.

## Components

Components reference semantic tokens. The set below is **prescriptive** — it defines what to build, not what exists.

### Button — Primary / Neutral / Ghost / Danger
Same contract as the parent, accent-filled primary. Primary: `--cta-primary-bg` (accent), white text, `--radius-md`, `--fs-13` Medium, focus ring 2px offset. Neutral: surface bg + 1px border. Ghost: transparent, hover reveals `--color-accent-subtle`. Danger: Madder, post-confirmation only.

### EntityCard (the signature primitive)
**Role:** A single distilled entity — polymorphic across the four types (`decisao`, `principio`, `racional`, `risco`).

`--bg-surface`, `--radius-md`, `--shadow-sm`, `--space-4`–`--space-5` padding. Carries a **3px left bar** in `--color-entity-{type}-fg` (the quiet spine — see Craft & Taste) and a leading `EntityPill`. Title in Poppins Semibold `--fs-14`; summary in Regular `--color-text-secondary`, clamped to ~3 lines. Footer row: participant `AvatarStack` + mono source count + mono confidence %. Rests flat, **lifts on hover** (`translateY(-1px)` + stronger border). Always traces to source. Decisão gets the accent; the other three stay quiet.

Type-specific touches: **Risco** surfaces a severity badge (média→Saffron, alta→Madder). **Racional** can show a "Relacionada a" link to its decision. **Princípio** shows its source count prominently (a principle earns its status by recurring across sources).

### EntityPill
**Role:** The type label on an entity.
`--radius-pill`, `--fs-11` Medium, `--color-entity-{type}-bg` fill + `-fg` text, leading type icon (Lucide-style outlined). One per card.

### EntityDrawer
**Role:** The full entity — opened from any card. The lite version of the fluxo↔essência split.
Right-side drawer (`--drawer-width`). Header: type glyph + pill + edit/delete/close. Body: title, a "destilado pela IA" chip + mono confidence, an editable Resumo block (`--bg-sunken` inset), the schema fields, and **"Destilado a partir de N fontes"** — each source a clickable row that traces back to the origin. This is where grounding (Segurança rank-4) becomes tangible: entity → its sources, always one click away.

### TranscriptView / TranscriptLine
**Role:** The raw meeting fluxo.
Sits in `--color-bg-sunken`. Each line: mono timestamp (`--fs-12`, `--color-text-muted`) + speaker name (Poppins Medium) + utterance (mono `--fs-15` Regular, `--lh-relaxed`). Lines that sourced a drop get a subtle `--color-accent-subtle` left highlight. Clickable: selects the line, scrolls the linked drop.

### SourceTag / CitationRef (grounding — Segurança rank-4)
**Role:** Trace an entity to its origin. Inspired by the "grounded answer" idiom (every claim shows its source).
A small mono pill (`--fs-11`) like `[12:04 · Marina]` or a source-row that, on click, opens the source / scrolls to the cited line. **An entity without a traceable source is invalid.** The Ask (chat) surface carries this further — every answer lists the entities and sources it was built from ("nada vem do nada").

### MeetingHeader / SourceHeader
**Role:** The fluxo's identity.
Source title (`--fs-24` Semibold), date/duration/participants in `--color-text-secondary`, a distillation summary line ("N decisões · M princípios · K riscos") with mono counts. Avatars as participant stack.

### PrincipleChip
**Role:** Evidenced team principles (Stillare "evidencia os princípios que orientam o time").
A quiet slate pill surfacing an inferred operating principle, with a SourceTag to the moments that revealed it. Low emphasis — context family color.

### Card / Modal / Text Input / Sidebar Nav / Topbar / Avatar / Tag
Standard shells against semantic tokens — same contracts as the parent/LexFlow, adapted to slate + theme-flexible. Sidebar (264px) hosts the meetings list; active item gets `--color-accent-subtle` bg + accent left border.

## Gradients

Stillare is near-flat. One quiet wash only: `--gradient-wash` = `linear-gradient(180deg, var(--color-bg-base), var(--color-bg-sunken))` for report headers / empty states. No spectrum gradients, no Cornflower→Indigo accent gradient (that's Inspira's AI idiom — Stillare doesn't need it).

## Do's and Don'ts

### Do
- Keep the canvas **gray** — light pages on `slate-50`, not white. The neutral is the protagonist.
- Use the **single accent** (`#6a96ea`) for primary actions and Decisão entities. It's the drop; keep it scarce.
- Classify distilled content with the **Four Entities** color system; classify system state with **Feedback** colors — keep the two visually separable.
- Put the raw transcript in `--color-bg-sunken` (recessed) and distilled drops on `--color-bg-surface` (raised). Down = raw, up = essence.
- Use **JetBrains Mono** for transcript, timestamps, speaker IDs, cited snippets, IDs. Use **Poppins** for distilled prose.
- Attach a **SourceTag** to every drop. Grounding is non-negotiable (Segurança).
- Validate contrast in **both** themes — the gray canvas is where Dar Pé breaks first.
- Reference semantic tokens; let the theme layer remap light↔dark.

### Don't
- Don't use white (`#ffffff`) as the page background. That's Inspira. Stillare's page is `slate-50` / `slate-950`.
- Don't introduce Rich Black CTAs (Inspira's primary) or Tropical Indigo (Inspira's AI accent). Stillare is single-accent Cornflower.
- Don't pick a different blue for the accent — it must be the Cornflower family thread (`#6a96ea`).
- Don't render the transcript in Poppins or the distilled drops in mono — the sans/mono split carries meaning.
- Don't ship a drop without a source. Don't let "Question" drops and "Warning" banners (both Saffron) collide on one screen.
- Don't add color decoratively. On a gray canvas, every saturated pixel is a claim of value — spend it only on real drops and actions.
- Don't redefine the principles or the Poppins type rules (weights, no-italics, no-allcaps). Sub-brands inherit those.
- Don't use system/pure gray. The Slate ramp (`#6f7a93` family) is the only valid neutral.

## Imagery

Product-forward and restrained, like the parent. Dominant imagery is the **product itself**: source lists, entity cards, the source-tracing drawer, participant avatars.
- **Logo:** `visual/logos/usage.md` ships two SVGs inline — `stillare-logo.svg` (full lockup) and `stillare-iso.svg` (the distillation droplet). Both are built on Slate `#6f7a93` + Cornflower `#6a96ea` — the logo is the canonical proof of the palette. See `visual/logos/usage.md`. The droplet is the brand's verb (Craft & Taste #6): use it where distillation happens, never decoratively.
- **Icons:** Lucide-style outlined, moderate stroke, in `--color-text-secondary` or `--color-accent` (active). The droplet motif echoes the isotype — use sparingly.
- **Avatars:** solid slate circles with initials, deterministic from name hash. No random colors.
- **Photography:** essentially absent.
- **Illustration:** flat, geometric, slate-tinted; rare. A distillation/condensation visual (drops forming) is the one on-brand illustration motif.

## Components — In Scope (v1)

What the Setup Skill provisions for a Stillare-flavored project:

- Button (Primary, Neutral, Ghost, Danger)
- EntityCard + EntityPill (decisao / principio / racional / risco variants)
- EntityDrawer (with source-tracing), RationaleBlock, severity badge
- TranscriptView / TranscriptLine
- SourceTag / CitationRef / TranscriptPeek (grounding)
- MeetingHeader, PrincipleChip
- Card, Modal, Text Input, Sidebar Nav, Topbar, Avatar, Tag/Pill
- Theme toggle (light ↔ dark)

## Components — Out of Scope (for now)

- Live transcription / real-time streaming UI (v1 works on finished transcripts)
- Audio/video player surface
- Data table primitives
- Charts / analytics dashboards
- Rich text editor
- Multi-step wizard
- Toast/notification system (Feedback Banners cover inline state)

If a Stillare-derived project needs these, the Setup Skill logs the gap.

## Open Questions / Known Gaps

- **Token files.** This DESIGN.md is the source of truth until `brand/stillare/tokens/` is generated (`primitives.css`, `semantic.css` with light+dark, `dimensions.css`, `utilities.css`) following Inspira's architecture.
- **Slate ramp values.** The face (`#6f7a93`) is fixed by the brand deck; the 50–950 steps here are derived/prescriptive and should be tuned against real screens for even perceptual spacing.
- **Drop contrast in dark.** The four `-fg`/`-bg` pairs need a real audit at `--fs-11`/`--fs-12` on dark surfaces (Saffron and Keppel are the risk).
- **Theme mechanism.** `[data-theme]` attribute vs `.dark` class vs system `prefers-color-scheme` — pick at scaffold. Recommendation: `[data-theme]` with a system-default + manual toggle.
- **Display font.** We chose Poppins-faithful for v1. If Stillare later wants a more expressive headline voice (the way the reference sites use display type), that's a deliberate brand decision to revisit — not a v1 gap.
- **Drops vs Feedback overlap.** Question (Saffron) and Warning (Saffron) share a hue. If they ever co-occur, we may need to shift one. Flagged, not yet resolved.
- **Grounding affordance.** SourceTag interaction (peek hovercard vs scroll-to vs both) needs a usability pass — it's the trust-critical interaction.
- **Logo / wordmark.** Resolved (partial): `visual/logos/` now ships `stillare-logo.svg` + `stillare-iso.svg` with a `usage.md` (clear space, min size, color rules). Still open: dedicated **light/dark theme lockups** aren't cut — the single SVGs recolor at most the Slate parts for dark; a proper inverse lockup may be wanted.
- **Live vs finished transcript.** v1 assumes a finished transcript. Real-time distillation (drops appearing as the meeting happens) is a different interaction model — out of scope, noted.

## Quick Start

### CSS Custom Properties

```css
:root {
  /* === Primitives — Slate === */
  --color-slate-50:  #f4f6f8;
  --color-slate-100: #e9ecf1;
  --color-slate-200: #d4d9e1;
  --color-slate-300: #b3bacb;
  --color-slate-400: #8d96ad;
  --color-slate-500: #6f7a93;  /* brand face */
  --color-slate-600: #5a6377;
  --color-slate-700: #474e5e;
  --color-slate-800: #353a46;
  --color-slate-900: #23262e;
  --color-slate-950: #15171c;

  /* === Primitives — Cornflower (accent / the drop) === */
  --color-cornflower-50:  #f0f5fe;
  --color-cornflower-100: #dbe7fc;
  --color-cornflower-200: #bcd1f9;
  --color-cornflower-300: #93b4f3;
  --color-cornflower-400: #6a96ea;  /* accent face */
  --color-cornflower-500: #4a78d8;
  --color-cornflower-600: #3a61c0;

  /* === Semantic — LIGHT (default) === */
  --color-bg-base:      var(--color-slate-50);
  --color-bg-surface:   #ffffff;
  --color-bg-elevated:  #ffffff;
  --color-bg-input:     #ffffff;
  --color-bg-sunken:    #eef1f5;

  --color-text-primary:   #1f232b;
  --color-text-secondary: var(--color-slate-600);
  --color-text-muted:     var(--color-slate-400);

  --color-accent:         var(--color-cornflower-400);
  --color-accent-hover:   var(--color-cornflower-500);
  --color-accent-muted:   var(--color-cornflower-100);
  --color-accent-subtle:  var(--color-cornflower-50);

  --color-border:         var(--color-slate-200);
  --color-border-strong:  var(--color-slate-300);
  --color-border-subtle:  var(--color-slate-100);
  --color-focus-ring:     var(--color-accent);

  /* Four Entities */
  --color-entity-decisao-fg:   #3a61c0;  --color-entity-decisao-bg:   #f0f5fe;
  --color-entity-principio-fg: #353a46;  --color-entity-principio-bg: #eef1f5;
  --color-entity-racional-fg:  #186d5f;  --color-entity-racional-bg:  #f1fcf8;
  --color-entity-risco-fg:     #b32231;  --color-entity-risco-bg:     #fdeef0;

  /* CTA */
  --cta-primary-bg:    var(--color-accent);
  --cta-primary-fg:    #ffffff;
  --cta-primary-hover: var(--color-accent-hover);
  --cta-neutral-bg:    #ffffff;
  --cta-neutral-fg:    var(--color-text-primary);
  --cta-ghost-fg:      var(--color-text-secondary);
  --cta-ghost-hover:   var(--color-accent-subtle);
  --cta-danger-bg:     #d62c3d;
  --cta-danger-fg:     #ffffff;

  /* Typography */
  --font-sans: "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --fs-11: 11px; --fs-12: 12px; --fs-13: 13px; --fs-14: 14px; --fs-15: 15px;
  --fs-17: 17px; --fs-20: 20px; --fs-24: 24px; --fs-32: 32px;
  --fw-regular: 400; --fw-medium: 500; --fw-semibold: 600;
  --lh-tight: 1.25; --lh-normal: 1.5; --lh-relaxed: 1.6;
  --tracking-tight: -0.02em; --tracking-mono: 0;

  /* Radius */
  --radius-xs: 4px; --radius-sm: 6px; --radius-md: 10px;
  --radius-lg: 14px; --radius-xl: 20px; --radius-pill: 9999px;

  /* Shadow (light) */
  --shadow-sm: 0 1px 2px rgba(35,38,46,0.06);
  --shadow-md: 0 4px 12px rgba(35,38,46,0.08);
  --shadow-lg: 0 12px 28px rgba(35,38,46,0.12);

  /* Motion */
  --duration-fast: 140ms; --duration-normal: 220ms; --duration-slow: 320ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Layout */
  --sidebar-width: 264px; --topbar-height: 56px;
  --content-max-width: 1280px; --transcript-width: 480px; --modal-width: 560px;
}

/* === Semantic — DARK === */
[data-theme="dark"] {
  --color-bg-base:      var(--color-slate-950);
  --color-bg-surface:   #1d2029;
  --color-bg-elevated:  #262a35;
  --color-bg-input:     #2d313d;
  --color-bg-sunken:    #101216;

  --color-text-primary:   #e8eaef;
  --color-text-secondary: #a9b1c2;
  --color-text-muted:     var(--color-slate-500); /* brand face as the quiet voice */

  --color-accent:         var(--color-cornflower-400); /* unchanged — the family thread */
  --color-accent-hover:   #85a9ee;
  --color-accent-muted:   #243352;
  --color-accent-subtle:  #1a2233;

  --color-border:         var(--color-slate-800);
  --color-border-strong:  var(--color-slate-700);
  --color-border-subtle:  var(--color-slate-900);

  --color-entity-decisao-fg:   #93b4f3;  --color-entity-decisao-bg:   #1a2233;
  --color-entity-principio-fg: #cdd2db;  --color-entity-principio-bg: #2a2e38;
  --color-entity-racional-fg:  #5fd6bd;  --color-entity-racional-bg:  #142a26;
  --color-entity-risco-fg:     #f0808c;  --color-entity-risco-bg:     #2c1719;

  --cta-neutral-bg: #2d313d;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg: 0 12px 32px rgba(0,0,0,0.6);
}

html, body {
  margin: 0; padding: 0;
  font-family: var(--font-sans);
  background: var(--color-bg-base);
  color: var(--color-text-primary);
  -webkit-font-smoothing: antialiased;
}

.mono { font-family: var(--font-mono); font-size: var(--fs-12); }
```

### Tailwind v4

```css
@theme {
  /* Inherit Inspira's parent @theme first, then override below. */

  /* Slate ramp + cornflower accent (primitives) */
  --color-slate-50: #f4f6f8;  --color-slate-500: #6f7a93;  --color-slate-950: #15171c;
  --color-accent:   #6a96ea;

  /* Light semantic defaults (page is slate-50, not white) */
  --color-bg-base:    #f4f6f8;
  --color-bg-surface: #ffffff;
  --color-bg-sunken:  #eef1f5;

  /* Type — mono addition */
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Radius overrides */
  --radius-md: 10px; --radius-lg: 14px; --radius-xl: 20px;
}
/* Dark variant via [data-theme="dark"] — see CSS block above for the full remap. */
```

## Sub-Brand Pattern Notes (for the Setup Skill)

When provisioning a Stillare-flavored project:

1. **Inherit** Inspira's principles (unchanged), Poppins + the three weights + type rules, and the full spacing ladder.
2. **Override** the neutral with the **Slate** ramp and set the **page to `slate-50`** (light) — the gray canvas is the brand.
3. **Override** the primary CTA to the single **Cornflower accent**; drop Rich Black and Tropical Indigo.
4. **Add** the **dark theme** (full semantic remap via `[data-theme="dark"]`), **JetBrains Mono**, the **Four Entities** color system, **shadow/motion/layout** tokens, and the **grounding** primitives (SourceTag).
5. **Provision** the split-view shell (transcript well + drops surface) if the artifact involves meeting intelligence (the default Stillare surface).

Minimum override surface: **Slate ramp + gray page + single Cornflower accent + the Four Entities.** Dark theme and the source-tracing drawer can be added incrementally, but they're the brand's signature — provision them early.
