# Inspira — Style Reference
> Traditional discourse, focus on the future.

**Theme:** light
**Brand:** Inspira (a ferramenta — feminine)
**Substrate:** Brisa DS (sub-brands inherit semantic layer)

Inspira is the reference brand for AI in the Brazilian legal market. The visual language sits at the intersection of *Direito* and innovation: authoritative without rigidity, modern without flippancy. A foundation of clean white surfaces and a blue-tinted neutral palette anchors the system; Cornflower Blue is the welcoming face, Rich Black is the gravitational anchor for primary action and elegance, Tropical Indigo is reserved for AI moments. Typography is Poppins only, restricted to three weights — discipline over variety. Components are defined by semantic intent, never raw hex, so the same surface adapts cleanly when this brand is overridden by a sub-brand.

## The Five Principles (ranked)

When two principles conflict, the higher-ranked one wins.

1. **Dar Pé** — Accessibility and predictability. Keyboard-first, focus always visible, WCAG AA minimum.
2. **Clareza** — Every element has one direct purpose. Zero ambiguity in labels, errors, empty states.
3. **Ritmo e Fluidez** — Motion serves understanding (100–300ms, never >500ms). If it doesn't help comprehension, remove it.
4. **Segurança e Transparência** — Destructive actions name what's destroyed. Trust is engineered, not assumed.
5. **Leveza** — Whitespace is a feature. Remove before adding.

Full text: `principles.md`. The principles are the design contract — DESIGN.md describes the visual material; principles describe the behavior the material is in service of.

## Tokens — Colors

Inspira uses a **two-layer color system**. Components reference only the semantic layer. Primitives are brand-specific scales (50–950) defined in the `primitives.css` section of `tokens/tokens-css.md`.

### Semantic — Background

| Token | Reference | Role |
|---|---|---|
| `--color-bg-primary` | `--color-white` `#ffffff` | Default page and surface background |
| `--color-bg-secondary` | `--color-cool-gray-50` `#f4f7f9` | Alternating sections, subtle elevation |
| `--color-bg-tertiary` | `--color-cool-gray-100` `#ecf0f3` | Nested surfaces, deeper elevation |
| `--color-bg-inverse` | `--color-rich-black-900` `#1e3791` | Dark surfaces, hero inverse, footer |
| `--color-bg-brand-subtle` | `--color-cornflower-blue-50` `#f0f5fe` | Brand-tinted backgrounds (info banners, brand sections) |
| `--color-bg-highlight` | `--color-cornflower-blue-100` `#dee7fb` | Selected hover states, soft emphasis |
| `--color-bg-selected` | `--color-cornflower-blue-200` `#c5d7f8` | Active selection (table rows, list items) |

### Semantic — Text

| Token | Reference | Role |
|---|---|---|
| `--color-text-primary` | `--color-cool-gray-950` `#2d3139` | Body, primary content, main headings |
| `--color-text-secondary` | `--color-cool-gray-800` `#5b6478` | Secondary text, descriptions |
| `--color-text-tertiary` | `--color-cool-gray-600` `#8995ae` | Metadata, supporting copy, placeholders |
| `--color-text-disabled` | `--color-cool-gray-300` `#c6d1db` | Disabled state text |
| `--color-text-inverse` | `--color-white` `#ffffff` | Text on dark surfaces |
| `--color-text-brand` | `--color-rich-black-900` `#1e3791` | Strong brand text moments |
| `--color-text-link` | `--color-rich-black-900` `#1e3791` | Inline links (hover → `--color-rich-black-950`) |
| `--color-text-on-color` | `--color-white` `#ffffff` | Text on saturated/branded fills |

### Semantic — Border

| Token | Reference | Role |
|---|---|---|
| `--color-border-default` | `--color-cool-gray-200` `#dce3e9` | Default borders, dividers |
| `--color-border-subtle` | `--color-cool-gray-100` `#ecf0f3` | Faint separators, low-weight grouping |
| `--color-border-strong` | `--color-cool-gray-300` `#c6d1db` | Stronger borders for emphasis |
| `--color-border-focus` | `--color-cornflower-blue-300` `#9dbdf3` | Focus rings (always visible — Dar Pé) |
| `--color-border-brand` | `--color-rich-black-900` `#1e3791` | Brand-strong borders |
| `--color-border-error` | `--color-madder-500` `#e94a5a` | Error states on inputs |

### Semantic — Interactive

| Token | Reference | Role |
|---|---|---|
| `--color-interactive-primary` | `--color-rich-black-950` `#070c21` | **Primary CTA fill — the "do this" button** |
| `--color-interactive-primary-hover` | `--color-rich-black-900` `#1e3791` | Primary CTA hover |
| `--color-interactive-primary-text` | `--color-white` `#ffffff` | Text on primary CTA |
| `--color-interactive-secondary` | `--color-cornflower-blue-400` `#6a97eb` | Secondary action fill |
| `--color-interactive-secondary-hover` | `--color-cornflower-blue-300` `#9dbdf3` | Secondary hover |
| `--color-interactive-secondary-text` | `--color-white` `#ffffff` | Text on secondary |
| `--color-interactive-neutral` | `--color-cool-gray-200` `#dce3e9` | Neutral button fill |
| `--color-interactive-destructive` | `--color-madder-600` `#d62c3d` | Destructive action (after confirmation) |
| `--color-interactive-ghost` | `transparent` | Ghost buttons (text only, hover reveals subtle bg) |
| `--color-interactive-accent-from` | `--color-cornflower-blue-400` `#6a97eb` | Accent gradient start (AI moments) |
| `--color-interactive-accent-to` | `--color-tropical-indigo-400` `#9970ff` | Accent gradient end (AI moments) |
| `--color-interactive-focus-ring` | `--color-cornflower-blue-300` `#9dbdf3` | Universal focus ring (Dar Pé) |

### Semantic — Feedback

| Token | Reference | Role |
|---|---|---|
| `--color-feedback-critical-bg` | `--color-madder-50` `#fef2f3` | Error banner background |
| `--color-feedback-critical-text` | `--color-madder-700` `#b32231` | Error banner text |
| `--color-feedback-warning-bg` | `--color-saffron-50` `#fdf9ed` | Warning banner background |
| `--color-feedback-warning-text` | `--color-saffron-950` `#3e180a` | Warning banner text |
| `--color-feedback-success-bg` | `--color-keppel-green-50` `#f1fcf8` | Success banner background |
| `--color-feedback-success-text` | `--color-keppel-green-700` `#186d5f` | Success banner text |
| `--color-feedback-info-bg` | `--color-cornflower-blue-50` `#f0f5fe` | Info banner background |
| `--color-feedback-info-text` | `--color-rich-black-900` `#1e3791` | Info banner text |

### Brand Primitives — Faces

The full 50–950 scales live in the `primitives.css` section of `tokens/tokens-css.md`. Below are the **brand faces** — the canonical shade of each color, what each one *signals*.

| Name | Face | Token | Emotional role |
|---|---|---|---|
| Cornflower Blue | `#6a97eb` | `--color-cornflower-blue-400` | Calmos e tecnológicos — welcoming + serious. The primary brand face. |
| Rich Black | `#070c21` | `--color-rich-black-950` | Sérios, seguros e elegantes — authority, gravity, primary CTAs. |
| Tropical Indigo | `#9970ff` | `--color-tropical-indigo-400` | Criativos e futurista — AI moments only. Earns impact by scarcity. |
| Keppel Green | `#26ba9d` | `--color-keppel-green-500` | Inovadores e revitalizantes — success, positive transformation. |
| Madder | `#d62c3d` | `--color-madder-600` | Urgency, error, destructive (post-confirmation only). |
| Saffron | `#ebc26a` | `--color-saffron-300` | Caution, non-blocking warnings, quota notifications. |
| Cool Gray | `#8995ae` | `--color-cool-gray-600` | The workhorse neutral. Blue-tinted, never pure gray. |

## Tokens — Typography

**Rule: Poppins only.** No serif companions. No display fonts. No exceptions in v1.

### Family

```css
--font-poppins: 'Poppins', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

### Weights — only three valid values

| Weight | CSS | Use for |
|---|---|---|
| Regular | `400` | Body, field values, descriptions, captions |
| Medium | `500` | Labels, button text, active nav, subtle emphasis |
| Semibold | `600` | Titles, headings, CTAs on heavy surfaces |

Never Bold (700+). Never Light (300 or below). The three-weight palette covers every legitimate case.

### Type Scale — Display (moments, not paragraphs)

| Token | Size | Line height | Letter spacing | When |
|---|---|---|---|---|
| `--text-title` | 32px | 150% | -2% | Page-level hero titles |
| `--text-title-sm` | 24px | 160% | -1% | Section titles, modal headings |
| `--text-subtitle` | 20px | 160% | 0% | Subheadings inside long-form content |
| `--text-subtitle-sm` | 18px | 160% | 0% | Card titles, secondary subheadings |

Tight letter-spacing at larger sizes is intentional — it keeps display text feeling crafted, not default.

### Type Scale — Body (reading)

| Token | Size | Line height | When |
|---|---|---|---|
| `--text-body-lg` | 16px | 160% | Long-form reading, primary article body |
| `--text-body` | 14px | 160% | **Default body text.** Product UI, descriptions. |
| `--text-body-sm` | 13px | 150% | Dense tables, metadata |
| `--text-caption` | 12px | 150% | Timestamps, labels under icons |
| `--text-caption-sm` | 11px | 150% | Legal fine print, badges |

### Type Scale — Action (interactive)

| Token | Size | Line height | Letter spacing | When |
|---|---|---|---|---|
| `--text-button-lg` | 14px | 100% | 0.1% | Page-level primary CTAs |
| `--text-button` | 13px | 100% | 0.1% | **Default button.** Most UI buttons. |
| `--text-button-sm` | 12px | 100% | 0.1% | Dense toolbars, inline actions |
| `--text-button-xs` | 11px | 150% | 0px | Chips, filters |

Buttons use **100% line-height** because they're single-line by rule. Slight positive letter-spacing (`0.1%`) preserves legibility at small sizes.

### Type Scale — Link

| Token | Size | Line height | When |
|---|---|---|---|
| `--text-link` | 13px | 150% | Inline links inside body, navigation |
| `--text-link-sm` | 11px | 150% | Footer links, tertiary navigation |

### Hierarchy in practice

A typical Inspira screen uses **no more than 3 type roles**: one display + one body + one caption. A fourth role is a hierarchy smell, not a styling need.

## Tokens — Spacing & Shapes

**Density:** comfortable
**Base unit:** 4px (the spacing scale is built on multiples of 4)

### Spacing Scale

| Token | Value |
|---|---|
| `--space-px` | 1px |
| `--space-0-5` | 2px |
| `--space-1` | 4px |
| `--space-1-5` | 6px |
| `--space-2` | 8px |
| `--space-2-5` | 10px |
| `--space-3` | 12px |
| `--space-3-5` | 14px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-7` | 28px |
| `--space-8` | 32px |
| `--space-9` | 36px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-14` | 56px |
| `--space-16` | 64px |
| `--space-20` | 80px |
| `--space-24` | 96px |

### Border Radius

| Token | Value | Use for |
|---|---|---|
| `--radius-xs` | 4px | Tight badges, pills, dense chips |
| `--radius-sm` | 8px | Inputs, small buttons |
| `--radius-md` | 12px | Default buttons, default cards |
| `--radius-lg` | 16px | Elevated cards, prominent surfaces |
| `--radius-xl` | 24px | Hero cards, marquee surfaces |
| `--radius-full` | 9999px | Pills, avatar, tag chips |

Rounder corners feel lighter (Leveza). Use the radius scale to signal weight.

### Size Tokens (heights for controls)

| Token | Value | Use for |
|---|---|---|
| `--size-xs` | 20px | Inline tags, dense chips |
| `--size-sm` | 24px | Compact controls |
| `--size-md` | 32px | Default control height (input, button) |
| `--size-lg` | 40px | Large CTA height |
| `--size-xl` | 48px | Hero CTA, prominent inputs |

### Breakpoints

| Token | Value |
|---|---|
| `--breakpoint-xs` | 640px |
| `--breakpoint-sm` | 768px |
| `--breakpoint-md` | 1024px |
| `--breakpoint-lg` | 1366px |
| `--breakpoint-xl` | 1440px |

### Border Widths

| Token | Value |
|---|---|
| `--border-width-thin` | 1px |
| `--border-width-medium` | 2px |
| `--border-width-thick` | 3px |

## Surfaces

| Level | Token | Value | Purpose |
|---|---|---|---|
| 0 | `--color-bg-primary` | `#ffffff` | Default page surface |
| 1 | `--color-bg-secondary` | `#f4f7f9` | Alternating sections, subtle differentiation |
| 2 | `--color-bg-tertiary` | `#ecf0f3` | Nested surfaces, deeper grouping |
| Inverse | `--color-bg-inverse` | `#1e3791` | Dark contexts, footer, hero inverse |
| Brand | `--color-bg-brand-subtle` | `#f0f5fe` | Brand-tinted sections |

Inspira does not currently define elevation shadows. Surface differentiation uses background shifts and borders, in line with Leveza. Adding a shadow scale is an open question (see Gaps).

## Gradients

Gradients are first-class in Inspira. Use them rarely and intentionally — if a gradient appears on every screen, none of them feel special.

| Gradient | Tokens (from → to) | Use for |
|---|---|---|
| Primary | `--color-cornflower-blue-400` → `--color-cornflower-blue-800` | Default brand gradient, hero depth |
| Accent (AI) | `--color-cornflower-blue-400` → `--color-tropical-indigo-400` | AI / innovation moments, accent buttons |
| Positive | `--color-cornflower-blue-400` → `--color-keppel-green-500` | Transformation, wellness, milestones |
| Subtle Primary | `--color-cornflower-blue-50` → `--color-cornflower-blue-100` | Soft brand washes |
| Subtle Accent | `--color-cornflower-blue-50` → `--color-tropical-indigo-100` | Soft AI hints |
| Spectrum (4-stop) | `cornflower-100` → `cornflower-400` → `tropical-indigo-400` → `rich-black-950` | Flagship brand moments only |
| Spectrum Green (4-stop) | `cornflower-100` → `cornflower-400` → `keppel-500` → `rich-black-950` | Flagship positive moments only |

## Components

Components are described by **semantic role**, not raw hex. This keeps the system portable across sub-brands. When implementing in code, use `var(--color-interactive-primary)` etc. — never hardcode a primitive.

### Primary CTA Button
**Role:** The single "do this" action per screen.

Filled `--color-interactive-primary` (Rich Black `#070c21`), `--color-interactive-primary-text` (white), `--radius-md` corners, `--size-md` height (40px for `--size-lg`), padding `--space-3` × `--space-5`, `--text-button` weight Medium. Hover → `--color-interactive-primary-hover`. Focus ring `--color-border-focus`, 2px offset.

### Secondary Action Button
**Role:** Supporting actions adjacent to primary CTA.

Filled `--color-interactive-secondary` (Cornflower Blue `#6a97eb`), white text, `--radius-md`, same height/padding as Primary. Hover → `--color-interactive-secondary-hover`. Use when there's a clear visual hierarchy between primary and supporting action.

### Neutral Button
**Role:** Tertiary actions, cancel, dismiss.

Filled `--color-interactive-neutral` (Cool Gray 200), `--color-text-primary` text, `--radius-md`. Used when neither primary nor secondary visual weight is appropriate.

### Ghost Button
**Role:** Lowest-emphasis interactions, table-row actions, header utility links.

Transparent background, `--color-interactive-ghost-text` (Cool Gray 950) text. Hover reveals `--color-interactive-ghost-hover` (Cool Gray 50) background. `--radius-md`. Padding tight (`--space-2` × `--space-3`).

### Destructive Button
**Role:** Irreversible action — only after explicit confirmation copy.

Filled `--color-interactive-destructive` (Madder), white text. Never the default action on a screen. Required: confirmation dialog naming what's being destroyed (Segurança).

### Accent (AI) Button
**Role:** AI-powered or forward-looking features. Rare.

Linear gradient `--color-interactive-accent-from` → `--color-interactive-accent-to` (Cornflower → Tropical Indigo), white text, `--radius-md`. Reserved for AI surfaces — overuse defeats the signal.

### Text Input
**Role:** Form data entry.

`--color-bg-primary` background, `--color-border-default` 1px border, `--color-text-primary` text, `--color-text-tertiary` placeholder. `--radius-sm`, padding `--space-2` × `--space-3`. Focus → `--color-border-focus` 2px ring. Error → `--color-border-error` border + error text below.

### Card (Default)
**Role:** Content container, grouping related information.

`--color-bg-primary` background, `--color-border-subtle` 1px border, `--radius-md`, padding `--space-4` to `--space-6`. No shadow. Hover variant adds subtle bg shift, never elevation.

### Card (Brand-Tinted)
**Role:** Highlighted content, info sections, brand moments.

`--color-bg-brand-subtle` background, `--color-border-default` border, `--radius-md`, same padding as default card.

### Feedback Banner
**Role:** Inline state communication (info, success, warning, critical).

Each variant pairs `--color-feedback-{variant}-bg` with `--color-feedback-{variant}-text`, optional `--color-feedback-{variant}-border` 1px, icon in `--color-feedback-{variant}-icon`. `--radius-sm`, padding `--space-3` × `--space-4`.

### Tag / Pill
**Role:** Status, category, filter chip.

`--color-bg-secondary` or `--color-bg-brand-subtle` background, `--text-caption-sm` Medium weight, `--radius-full`, padding `--space-1` × `--space-2`.

## Do's and Don'ts

### Do
- Use **Rich Black** (`--color-interactive-primary`) for primary CTAs. Cornflower Blue is *secondary*, not primary.
- Reference semantic tokens in components (`--color-bg-primary`), never primitives (`--color-cool-gray-50`).
- Always show a focus ring (`--color-interactive-focus-ring`) — Dar Pé is rank-1, never compromised for aesthetics.
- Use Poppins exclusively, in Regular (400), Medium (500), or Semibold (600) only.
- Reserve Tropical Indigo (`#9970ff`) for AI moments. If it's everywhere, it's nowhere.
- Use Madder only for errors and post-confirmation destructive actions, never decoratively.
- Maintain ≤3 type roles per screen. A 4th role signals a hierarchy problem, not a styling need.
- Use Cool Gray (blue-tinted) for neutrals — never pure gray, which feels disconnected from the blue-forward palette.
- Use the radius scale (`--radius-xs` through `--radius-full`) — rounder corners signal lightness (Leveza).
- Use `var(...)` references for the Tailwind classes (e.g., `bg-bg-primary`, `text-text-primary`) so sub-brand overrides cascade automatically.

### Don't
- Don't use Cornflower Blue for primary CTAs — it's the secondary action color. The primary button is Rich Black.
- Don't introduce new colors. The 7 brand scales + 2 supplementary (blue, cyan) cover every legitimate need.
- Don't use italic Poppins. Inspira does not use italic for emphasis — use Semibold or color instead.
- Don't use ALL CAPS or `text-transform: uppercase` for headings.
- Don't use Bold (700+) or Light (300−). The three approved weights are non-negotiable.
- Don't use body copy below 13px. Caption sizes (12, 11) are for metadata only, never running prose.
- Don't apply gradients on every screen. They earn impact by scarcity.
- Don't hardcode hex values in components. Always reference semantic tokens.
- Don't add elevation shadows arbitrarily — Inspira uses surface shifts and borders for depth (Leveza). If shadows are needed, raise it as a gap (see below).
- Don't use destructive Madder fills as the default action — it must follow an explicit confirmation step (Segurança).
- Don't add letter-spacing to body text. The negative tracking values (`-2%`, `-1%`) are for display sizes only.

## Imagery

The visual language for imagery is product-forward and restrained:

- **Product screenshots** are the dominant imagery type, contained within cards or surfaces, demonstrating the tool's functionality with minimal surrounding context.
- **Photography** is rare. When used, it's restrained, professional, never lifestyle-bright.
- **Illustrations** lean abstract, geometric, using brand-tinted neutrals over saturated colors.
- **Icons** are outlined with moderate stroke weight in `--color-icon-default` (Cool Gray 950) or `--color-icon-secondary` (Cool Gray 600). Filled variants are reserved for state indicators (success, warning, critical icons in their respective feedback colors).
- **Density:** balanced. Imagery breaks up text without overwhelming it.

## Layout

- **Page max-width:** not strictly enforced in v1. Container patterns inherited from app context.
- **Section gap:** `--space-12` (48px) to `--space-16` (64px) between major sections.
- **Card padding:** `--space-4` to `--space-6` (16–24px) depending on density.
- **Element gap:** `--space-2` to `--space-4` (8–16px) for related controls.
- **Vertical rhythm:** comfortable, not dense. Whitespace is a feature (Leveza).
- **Navigation:** persistent top bar, minimal logo, distinct primary CTA in Rich Black.

Hero sections use `--color-bg-brand-subtle` or a primary gradient background. Alternating sections shift between `--color-bg-primary` and `--color-bg-secondary` for rhythm.

## Components — In Scope (v1)

The Setup Skill provisions these when scaffolding an Inspira project. Order is rough priority.

- Button (Primary, Secondary, Neutral, Ghost, Destructive, Accent variants)
- Text Input
- Card (Default, Brand-Tinted)
- Feedback Banner (info, success, warning, critical)
- Tag / Pill
- Avatar (single + grouped — see existing `app/src/components/Avatar`, `AvatarGroup`)
- Badge
- Dialog / Modal
- Top Navigation Bar
- Loading States (skeleton, spinner) — minimum viable

## Components — Out of Scope (for now)

Explicit "not yet." If a project needs these, the Setup Skill logs the gap.

- Data table (the existing `DecisionTable` is product-specific, not a DS primitive yet)
- Combobox / Multi-select
- Date picker
- Toast / Notification system (we have Feedback Banners, not toast)
- Drawer / Side panel
- Stepper / Wizard
- Rich text editor surfaces
- Charts / Data viz primitives
- File upload / Drag-and-drop zones
- Command palette / cmd-k

## Open Questions / Known Gaps

The DS feedback loop's home base. Every Setup Skill run that hits a missing piece adds an entry here.

- **Elevation/shadow scale.** Currently absent — the system uses bg shifts and borders. Question: do we need a 1–3 step shadow scale for cards-on-cards or true overlays? Decision deferred until a real product needs it.
- **Motion tokens.** Principles document the timings (100–300ms, easings) but there's no token file yet (`utilities.css`, in `tokens/tokens-css.md`, only covers font/opacity/z-index). Need: `--duration-fast: 150ms`, `--duration-base: 250ms`, `--ease-out: cubic-bezier(...)`.
- **Dark mode.** Inspira is light-only in v1. If a sub-brand or surface needs dark mode, semantics would need a parallel set — not yet defined.
- **Form patterns.** Input is defined; checkbox, radio, switch, select, textarea, slider — none yet. High priority for any real product.
- **Semantic.css migration.** README.md notes the hand-written `semantic.css` still uses old primitive names (navy, sky, neutral). The auto-generated `semantic.css` (cool-gray, rich-black, cornflower) is reference-only. Migration is pending.
- **Component layer in DS.** Currently `app/src/components/` mixes DS primitives (Avatar, Badge) with product surfaces (DecisionTable, SaveDecisionInFolderDialog). The DS does not yet have a clean component layer separate from the product app — this is the structural gap that motivates the Setup Skill.
- **Type token naming.** `tokens.json` uses semantic role names (title, body, button) under `typography`. Tailwind v4 expects `--text-*`. Need to confirm if the build script emits `--text-title` etc., and if not, how the action sizes are exposed.
- **Storybook coverage.** Only `button.md` and `dialog.md` exist in `app/docs/components/`. Every other component lacks a documented surface.
- **Logo usage rules.** `visual/logos/` has SVGs but no `usage.md` describing minimum size, clear space, allowed/forbidden contexts.

## Quick Start

### CSS Custom Properties

```css
:root {
  /* Background */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f4f7f9;
  --color-bg-tertiary: #ecf0f3;
  --color-bg-inverse: #1e3791;
  --color-bg-brand-subtle: #f0f5fe;
  --color-bg-highlight: #dee7fb;
  --color-bg-selected: #c5d7f8;

  /* Text */
  --color-text-primary: #2d3139;
  --color-text-secondary: #5b6478;
  --color-text-tertiary: #8995ae;
  --color-text-disabled: #c6d1db;
  --color-text-inverse: #ffffff;
  --color-text-brand: #1e3791;
  --color-text-link: #1e3791;
  --color-text-on-color: #ffffff;

  /* Border */
  --color-border-default: #dce3e9;
  --color-border-subtle: #ecf0f3;
  --color-border-strong: #c6d1db;
  --color-border-focus: #9dbdf3;
  --color-border-brand: #1e3791;
  --color-border-error: #e94a5a;

  /* Interactive */
  --color-interactive-primary: #070c21;
  --color-interactive-primary-hover: #1e3791;
  --color-interactive-primary-active: #1a39b9;
  --color-interactive-primary-text: #ffffff;
  --color-interactive-secondary: #6a97eb;
  --color-interactive-secondary-hover: #9dbdf3;
  --color-interactive-secondary-text: #ffffff;
  --color-interactive-neutral: #dce3e9;
  --color-interactive-neutral-hover: #c6d1db;
  --color-interactive-neutral-text: #2d3139;
  --color-interactive-destructive: #d62c3d;
  --color-interactive-destructive-hover: #b32231;
  --color-interactive-destructive-text: #ffffff;
  --color-interactive-ghost: transparent;
  --color-interactive-ghost-hover: #f4f7f9;
  --color-interactive-ghost-text: #2d3139;
  --color-interactive-accent-from: #6a97eb;
  --color-interactive-accent-to: #9970ff;
  --color-interactive-focus-ring: #9dbdf3;

  /* Feedback */
  --color-feedback-critical-bg: #fef2f3;
  --color-feedback-critical-text: #b32231;
  --color-feedback-critical-border: #fcccd1;
  --color-feedback-warning-bg: #fdf9ed;
  --color-feedback-warning-text: #3e180a;
  --color-feedback-warning-border: #f1d796;
  --color-feedback-success-bg: #f1fcf8;
  --color-feedback-success-text: #186d5f;
  --color-feedback-success-border: #a1eed8;
  --color-feedback-info-bg: #f0f5fe;
  --color-feedback-info-text: #1e3791;
  --color-feedback-info-border: #c5d7f8;

  /* Typography — Family */
  --font-poppins: 'Poppins', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  /* Typography — Display Scale */
  --text-title: 32px;
  --leading-title: 1.5;
  --tracking-title: -0.64px;
  --text-title-sm: 24px;
  --leading-title-sm: 1.6;
  --tracking-title-sm: -0.24px;
  --text-subtitle: 20px;
  --leading-subtitle: 1.6;
  --tracking-subtitle: 0;
  --text-subtitle-sm: 18px;
  --leading-subtitle-sm: 1.6;
  --tracking-subtitle-sm: 0;

  /* Typography — Body Scale */
  --text-body-lg: 16px;
  --leading-body-lg: 1.6;
  --text-body: 14px;
  --leading-body: 1.6;
  --text-body-sm: 13px;
  --leading-body-sm: 1.5;
  --text-caption: 12px;
  --leading-caption: 1.5;
  --text-caption-sm: 11px;
  --leading-caption-sm: 1.5;

  /* Typography — Action Scale */
  --text-button-lg: 14px;
  --leading-button-lg: 1;
  --tracking-button-lg: 0.014px;
  --text-button: 13px;
  --leading-button: 1;
  --tracking-button: 0.013px;
  --text-button-sm: 12px;
  --leading-button-sm: 1;
  --tracking-button-sm: 0.012px;
  --text-button-xs: 11px;
  --leading-button-xs: 1.5;

  /* Typography — Link Scale */
  --text-link: 13px;
  --leading-link: 1.5;
  --text-link-sm: 11px;
  --leading-link-sm: 1.5;

  /* Typography — Weights */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  /* Spacing */
  --space-px: 1px;
  --space-0: 0px;
  --space-0-5: 2px;
  --space-1: 4px;
  --space-1-5: 6px;
  --space-2: 8px;
  --space-2-5: 10px;
  --space-3: 12px;
  --space-3-5: 14px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 28px;
  --space-8: 32px;
  --space-9: 36px;
  --space-10: 40px;
  --space-12: 48px;
  --space-14: 56px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;

  /* Sizes */
  --size-xs: 20px;
  --size-sm: 24px;
  --size-md: 32px;
  --size-lg: 40px;
  --size-xl: 48px;

  /* Border Radius */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* Border Widths */
  --border-width-none: 0px;
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 3px;

  /* Breakpoints */
  --breakpoint-xs: 640px;
  --breakpoint-sm: 768px;
  --breakpoint-md: 1024px;
  --breakpoint-lg: 1366px;
  --breakpoint-xl: 1440px;
}
```

### Tailwind v4

The brand layer ships as `@theme` blocks in the four CSS files inline in `tokens/tokens-css.md` (`primitives.css`, `semantic.css`, `dimensions.css`, `utilities.css`). Write them out as `.css` files in your project (e.g. `src/brand/tokens/`) and import them in your `app.css`:

```css
@import "tailwindcss";
@import "./brand/tokens/primitives.css";
@import "./brand/tokens/semantic.css";
@import "./brand/tokens/dimensions.css";
@import "./brand/tokens/utilities.css";
```

Then use the generated utilities directly:

```html
<button class="bg-interactive-primary text-interactive-primary-text rounded-md px-5 py-3 text-button font-medium">
  Continuar
</button>

<div class="bg-bg-secondary border border-border-default rounded-md p-6">
  Card content
</div>
```

> **Source of truth:** `brand/tokens/tokens.json` (W3C Design Token Format). The CSS blocks in `brand/tokens/tokens-css.md` are auto-generated — run `pnpm tokens:build` to regenerate after editing `tokens.json`.

## Sub-Brand Override Pattern

Inspira is the **base brand** in the Brisa system. Sub-brands (Lexflow, Stillare, Site institucional) override the **primitive layer** while keeping the **semantic layer constant**. This means a Button component written against `--color-interactive-primary` automatically adapts when a sub-brand redefines what `interactive-primary` resolves to.

When creating a sub-brand DESIGN.md, the minimum override surface is:

1. **Primitives** — the brand's color scales (50–950) replace Inspira's.
2. **Brand faces** — which scale step is the "face" of each brand color.
3. **Semantic mappings** that genuinely differ (e.g., if the sub-brand uses Cornflower Blue as primary CTA instead of Rich Black, override `--color-interactive-primary`).
4. **Type family** if the sub-brand uses something other than Poppins.

Everything else — spacing, radius, sizes, breakpoints, the principles, typography rules, the component contracts — inherits unchanged.
