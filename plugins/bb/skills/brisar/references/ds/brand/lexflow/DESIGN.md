# Lexflow — Style Reference

> Chat-first dev tool, dark studio. Sub-brand of Inspira.

**Theme:** dark
**Brand:** Lexflow (Inspira's internal workflow + agent platform — for Inspirados)
**Substrate:** Brisa DS (sub-brand inheriting from Inspira)
**Visual idiom:** GitHub-Primer-inspired
**Source of canonical tokens (current):** `lexflow-full-uxpm/lexflow-merged/brisa.css` — extracted from Pencil v2.9. Migration into `brand/lexflow/tokens/` pending.

Lexflow is the developer-facing surface of Inspira's product family. Where the parent brand projects authority on a white canvas, Lexflow projects flow on a dark canvas — chat-first, agent-mediated, technically dense. Visually inspired by GitHub Primer (slate base, single saturated accent, semantic status pairs), it stays in lockstep with Inspira on typography (Poppins, three weights) and adds JetBrains Mono for code surfaces. The brand's role is **isonomy with Chat Inspira**: a user toggling between Inspira's external legal product and Lexflow's internal workflow product should feel they belong to the same family despite the inverted theme.

## The Five Principles (inherited)

Lexflow inherits Brisa's ranked five — full text in `../principles.md`. Sub-brands do not redefine principles; they redefine pigment.

1. **Dar Pé** — accessibility, predictability. Dark mode contrast ≥ 4.5:1 on body, focus ring always visible.
2. **Clareza** — one direct purpose per element.
3. **Ritmo e Fluidez** — motion 100–300ms, never >500ms. Lexflow ships explicit motion tokens (see below) — Inspira does not yet.
4. **Segurança e Transparência** — destructive actions name what's destroyed.
5. **Leveza** — whitespace is a feature, even on dark.

## What Lexflow Inherits, Overrides, and Adds

This is the sub-brand contract.

### Inherits from Inspira (do not redefine)

- The five principles, in priority order.
- **Type family:** Poppins as the primary sans.
- **Type weights:** Regular (400), Medium (500), Semibold (600). No Bold, no Light.
- **Type rules:** no italics, no all-caps, ≤ 3 type roles per screen, body ≥ 13px.
- **Spacing philosophy:** 4pt base, 8pt grid.
- **Component contract pattern:** components reference semantic tokens, never primitives.
- **Brand outcomes:** Consistência, Autoridade, Reconhecimento.

### Overrides Inspira

| Concern                     | Inspira                                            | Lexflow                                                                                              |
| --------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Theme                       | Light (`#ffffff` page)                             | Dark (`#0e1117` page)                                                                                |
| Primary CTA fill            | Rich Black `#070c21`                               | Accent `#6a96ea`                                                                                     |
| CTA dual hierarchy          | Primary (Rich Black) + Secondary (Cornflower Blue) | **Single accent** for primary action; neutrals for everything else                                   |
| Neutrals                    | Cool Gray (blue-tinted, light scale)               | Slate (GitHub-Primer-style dark scale)                                                               |
| Border radius scale         | 4 / 8 / 12 / 16 / 24                               | 4 / 6 / 8 / 10 / 14 (tighter)                                                                        |
| Status colors               | Madder / Saffron / Keppel / Cornflower             | GitHub Primer red / yellow / green / blue (`#f85149` / `#d29922` / `#3fb950` / `#6a96ea`)            |
| Surface elevation           | Background shifts + borders, no shadows            | Real shadows (dark mode demands them)                                                                |
| Tropical Indigo (AI accent) | First-class, gradient endpoints                    | Not used. Lexflow's dev-tool idiom doesn't need the AI accent — every Lexflow surface is already AI. |
| Spectrum gradients          | First-class                                        | Replaced by `DarkGradientCard` (chat hero only)                                                      |

### Adds (gaps Inspira has, Lexflow fills)

- **Motion tokens** — `--duration-fast/normal/slow`, `--ease-out`, `--ease-in-out`. Inspira's principles document the timings but no token file exists yet.
- **Shadow scale** — `--shadow-sm/md/lg/xl` with rgba 0.3–0.6 alpha (dark UIs need stronger elevation).
- **Layout tokens** — `--sidebar-width: 248px`, `--topbar-height: 56px`, `--content-max-width: 1200px`, `--drawer-width: 480px`, `--modal-width: 560px`. Inspira does not currently define these.
- **Mono type family** — JetBrains Mono for code blocks, references, technical chips.
- **Special chat surface** — `DarkGradientCard` (`#1C264F → #0E1634 → #070C20` at 163°) for chat hero/composer surfaces.
- **Chat primitives** — agent response composition kit (see Components).

## Tokens — Colors

Dark-first semantic palette. Component code references the semantic tokens (`--bg-card`, `--text-primary`, `--cta-primary-bg`); the canonical layer maps semantic → primitive.

### Semantic — Background

| Token                 | Value     | Role                        |
| --------------------- | --------- | --------------------------- |
| `--color-bg-base`     | `#0e1117` | Page background             |
| `--color-bg-surface`  | `#161b22` | Cards, panels               |
| `--color-bg-elevated` | `#1c2129` | Dropdowns, modals, popovers |
| `--color-bg-input`    | `#21262d` | Form controls, code blocks  |

Semantic aliases also defined: `--bg-page`, `--bg-card`, `--bg-modal`, `--bg-code`.

### Semantic — Accent

| Token                   | Value     | Role                                          |
| ----------------------- | --------- | --------------------------------------------- |
| `--color-accent`        | `#6a96ea` | Primary interactive — links, CTAs, focus ring |
| `--color-accent-muted`  | `#1f3a5f` | Accent backgrounds, badge fills               |
| `--color-accent-subtle` | `#131d2f` | Soft accent backgrounds, hover surfaces       |

The accent is intentionally close to Inspira's Cornflower Blue 400 (`#6a97eb`) — a 1-pixel divergence (`ea` vs `eb`). This is the single most important token in the sub-brand: it preserves family resemblance while everything else inverts.

### Semantic — Text

| Token                    | Value     | Role                                  |
| ------------------------ | --------- | ------------------------------------- |
| `--color-text-primary`   | `#e6edf3` | Body, primary content                 |
| `--color-text-secondary` | `#8b949e` | Secondary text, descriptions          |
| `--color-text-muted`     | `#6e7681` | Tertiary text, placeholders, metadata |

### Semantic — Border

| Token                     | Value                            | Role                          |
| ------------------------- | -------------------------------- | ----------------------------- |
| `--color-border`          | `#30363d`                        | Default borders, dividers     |
| `--color-border-emphasis` | `#484f58`                        | Stronger borders for emphasis |
| `--border-subtle`         | `color-mix(... 60% transparent)` | Faint separators              |

Focus ring is `--color-focus-ring: var(--color-accent)`.

### Semantic — Status

GitHub Primer pairs: each status has a foreground (saturated) and a background (muted, derived via `color-mix`).

| Status  | FG                          | BG                                | Use                            |
| ------- | --------------------------- | --------------------------------- | ------------------------------ |
| OK      | `--color-success` `#3fb950` | `--status-ok-bg` `#1a2d1a`        | Success states, healthy badges |
| Warning | `--color-warning` `#d29922` | `color-mix(warning 15%, bg-base)` | Caution, non-blocking alerts   |
| Danger  | `--color-danger` `#f85149`  | `color-mix(danger 15%, bg-base)`  | Errors, destructive states     |
| Neutral | `--color-text-secondary`    | `--color-bg-input`                | Default badge, no-state        |

### Semantic — CTA

| Token                 | Value                          | Role                              |
| --------------------- | ------------------------------ | --------------------------------- |
| `--cta-primary-bg`    | `var(--color-accent)`          | Primary action fill               |
| `--cta-primary-fg`    | `#ffffff`                      | Primary action text               |
| `--cta-primary-hover` | `color-mix(accent 85%, white)` | Primary hover (lightens slightly) |
| `--cta-neutral-bg`    | `var(--color-bg-input)`        | Neutral action fill               |
| `--cta-neutral-fg`    | `var(--color-text-primary)`    | Neutral text                      |
| `--cta-neutral-hover` | `var(--color-bg-elevated)`     | Neutral hover                     |
| `--cta-ghost-fg`      | `var(--color-text-secondary)`  | Ghost text                        |
| `--cta-ghost-hover`   | `var(--color-bg-input)`        | Ghost hover bg                    |
| `--cta-danger-bg`     | `var(--color-danger)`          | Destructive action fill           |
| `--cta-danger-fg`     | `#ffffff`                      | Destructive text                  |

## Tokens — Typography

### Families

```css
--font-sans:
  "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
--font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
```

Lexflow adds JetBrains Mono on top of Poppins. Mono is reserved for: code blocks, IDs, paths, technical chips, command palette input, log/console surfaces, and the `.mono` helper class.

### Weights

Same three as Inspira. No deviation.

| Weight   | CSS   | Use                 |
| -------- | ----- | ------------------- |
| Regular  | `400` | Body, descriptions  |
| Medium   | `500` | Labels, button text |
| Semibold | `600` | Titles, headings    |

### Size Scale

Lexflow uses a flatter, denser scale than Inspira (more sizes between 10–17px, fewer huge display sizes). This reflects the dev-tool density.

| Token     | Size   | Use                                        |
| --------- | ------ | ------------------------------------------ |
| `--fs-10` | 10.5px | Micro labels, badge text                   |
| `--fs-11` | 11px   | Caption-sm, dense metadata                 |
| `--fs-12` | 12px   | Caption, mono code, table cells            |
| `--fs-13` | 13px   | Default button, dense body                 |
| `--fs-14` | 14px   | **Default body.** Most UI.                 |
| `--fs-15` | 15px   | Slightly emphasized body                   |
| `--fs-17` | 17px   | Subheadings, section titles                |
| `--fs-22` | 22px   | Page titles, modal headings                |
| `--fs-28` | 28px   | Hero titles (chat empty state, onboarding) |

Line heights: `--lh-tight: 1.25`, `--lh-normal: 1.5`, `--lh-relaxed: 1.6`.
Letter spacing: `--tracking-tight: -0.02em` (display sizes), `--tracking-mono: 0` (mono).

### Hero Pattern

Chat empty state and onboarding use a **two-line accent-split heading** ("Transforme ideias / em automações.") — first line `--text-primary`, second line `--color-accent`. This is a Lexflow signature, not an Inspira pattern.

## Tokens — Spacing & Shapes

### Spacing — 4pt base, 8pt grid

| Token        | Value |
| ------------ | ----- |
| `--space-1`  | 4px   |
| `--space-2`  | 8px   |
| `--space-3`  | 12px  |
| `--space-4`  | 16px  |
| `--space-5`  | 20px  |
| `--space-6`  | 24px  |
| `--space-8`  | 32px  |
| `--space-10` | 40px  |
| `--space-12` | 48px  |

Same philosophy as Inspira (4pt base) but with a tighter ladder up to `--space-12` (Inspira goes to `--space-24` / 96px). Lexflow's higher density doesn't need huge spaces.

### Border Radius

Tighter than Inspira's scale.

| Token           | Value  | Use                            |
| --------------- | ------ | ------------------------------ |
| `--radius-xs`   | 4px    | Tight badges, code blocks      |
| `--radius-sm`   | 6px    | Inputs, chips, dense controls  |
| `--radius-md`   | 8px    | Default buttons, cards         |
| `--radius-lg`   | 10px   | Elevated cards, modals         |
| `--radius-xl`   | 14px   | Hero cards, prominent surfaces |
| `--radius-pill` | 9999px | Pills, avatar                  |

### Shadows (real, dark-mode-tuned)

Dark UIs need real shadows for elevation — surface shifts alone don't read on a dark page.

| Token         | Value                         |
| ------------- | ----------------------------- |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.3)`   |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.4)`  |
| `--shadow-lg` | `0 12px 32px rgba(0,0,0,0.5)` |
| `--shadow-xl` | `0 20px 48px rgba(0,0,0,0.6)` |

## Motion (Lexflow-defined, candidate for Inspira adoption)

| Token               | Value                            |
| ------------------- | -------------------------------- |
| `--duration-fast`   | 140ms                            |
| `--duration-normal` | 220ms                            |
| `--duration-slow`   | 320ms                            |
| `--ease-out`        | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| `--ease-in-out`     | `cubic-bezier(0.4, 0, 0.2, 1)`   |

These satisfy Brisa's Ritmo principle ("100–300ms, never >500ms"). They should migrate up to Inspira's `utilities.css` (in `tokens/tokens-css.md`) so all sub-brands inherit them — see Open Questions.

## Layout

| Token                 | Value  | Use                              |
| --------------------- | ------ | -------------------------------- |
| `--sidebar-width`     | 248px  | Persistent left nav              |
| `--topbar-height`     | 56px   | Top app bar                      |
| `--content-max-width` | 1200px | Main content column max          |
| `--drawer-width`      | 480px  | Side drawers (Context, Settings) |
| `--modal-width`       | 560px  | Modal default width              |

These are Lexflow-specific because Lexflow is a single-app shell (sidebar + topbar + content). Other Inspira products may have different shell needs and can opt out.

## Surfaces

| Level | Token                 | Value     | Purpose                                          |
| ----- | --------------------- | --------- | ------------------------------------------------ |
| 0     | `--color-bg-base`     | `#0e1117` | Page background                                  |
| 1     | `--color-bg-surface`  | `#161b22` | Cards, panels                                    |
| 2     | `--color-bg-elevated` | `#1c2129` | Dropdowns, modals, popovers (with `--shadow-md`) |
| 3     | `--color-bg-input`    | `#21262d` | Form controls, code surfaces                     |

Surface progression goes _up_ in luminance as elevation increases — opposite of the light-mode intuition where elevated surfaces are usually whiter. On dark, elevated = lighter slate.

### Special Surface — DarkGradientCard

The chat hero/composer uses a multi-stop dark gradient that is **not part of the standard surface ladder**. It's a single, unique brand surface for chat moments only.

```css
background: linear-gradient(163deg, #1c264f 0%, #0e1634 50%, #070c20 100%);
```

Use only in: chat empty state hero, composer card on Início, and the `chat-kit.html` showcase. Do not use as a generic card background — it earns its impact by scarcity.

## Components

Components reference semantic tokens. The component descriptions below mirror the prototype's primitives in `lexflow-merged/primitives.jsx` and `chat-primitives.jsx`.

### Button — Primary

**Role:** Default action, anywhere in product.

`--cta-primary-bg` (accent) fill, white text, `--radius-md` corners, `--space-2` × `--space-4` padding, `--fs-13` Medium, focus ring `--color-accent` 2px offset. Hover lightens via `color-mix(accent 85%, white)`.

### Button — Neutral

**Role:** Secondary actions, cancel, dismiss.

`--cta-neutral-bg` (input gray), `--cta-neutral-fg` (primary text), same radius/padding as primary. Hover → `--cta-neutral-hover`.

### Button — Ghost

**Role:** Lowest-emphasis, table-row actions, header utility.

Transparent, `--cta-ghost-fg` (text-secondary). Hover reveals `--cta-ghost-hover` background.

### Button — Danger

**Role:** Destructive, after confirmation only.

`--cta-danger-bg`, white text. Same shape as primary.

### Card (Default)

**Role:** Content container.

`--bg-card` (`#161b22`), `--color-border` 1px, `--radius-md`, padding `--space-4` to `--space-6`. Optional `--shadow-sm` for slight lift; default is borderless-flat.

### Modal / Dialog

**Role:** Focused interruption.

`--bg-modal` (`#1c2129`), `--color-border` 1px, `--radius-lg`, `--shadow-xl`, width `--modal-width` (560px). Backdrop `rgba(0,0,0,0.6)`.

### HealthBadge / StatusBadge

**Role:** Workflow execution status, system health.

Each variant pairs `--status-{state}-fg` with `--status-{state}-bg`, `--radius-pill`, `--fs-11` Medium. Tiny dot prefix optional.

### Text Input / Textarea

**Role:** Form data entry, chat composer.

`--bg-input` (`#21262d`), `--color-border` 1px, `--text-primary` text, `--text-muted` placeholder, `--radius-sm`. Focus → `--color-accent` border, no glow.

### Sidebar Nav

**Role:** Persistent left rail.

Width `--sidebar-width` (248px), `--bg-surface` background, items use ghost styling, active item gets `--color-accent-subtle` background + `--color-accent` left border accent.

### Topbar

**Role:** Persistent top app bar.

Height `--topbar-height` (56px), `--bg-base` background, `--color-border` bottom 1px. Hosts breadcrumb, search, user menu.

### Composer (Chat)

**Role:** Message input + starter chips inline.

`DarkGradientCard` surface, large rounded textarea (`--radius-xl`), three `<ComposerChip>` starters in the same row, send button on the right.

### Chat — Mid-Thread Primitives

Ported from Inspira's Chat UI Kit ("Fonte da verdade · Chat Agêntico"), adapted to LexFlow vocabulary.

| Component                      | Role                         | Notes                                                                                            |
| ------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------ |
| `<UserBubble>`                 | User message                 | Right-aligned, `--bg-input` fill                                                                 |
| `<AgentBubble>`                | Agent message wrapper        | Left-aligned, contains `<AgentHeader>` + body + `<ResumoBlock>` + chips                          |
| `<AgentHeader kind="...">`     | Classifies the response      | `kind`: `workflow` (proposing/explaining), `debug` (diagnosing execution)                        |
| `<ResumoBlock>`                | Key takeaway, prominent      | One-line distillation of the response                                                            |
| `<ReferenceTag variant="...">` | Inline reference             | `workflow` (gitBranch icon), `execution` (zap icon), `app` (layers icon), `external` (link icon) |
| `<ResourceCard>`               | Related resource block       | Polymorphic — workflow / execution / app variants                                                |
| `<ContextSidebar>`             | "Contexto usado (N)" overlay | Drawer with all sources consulted                                                                |
| `<FileChip>`                   | File reference inline        | Small pill with file icon + name                                                                 |
| `<HoverCard>`                  | Reference preview on hover   | Lightweight popover                                                                              |

### Hero Title (chat empty / onboarding)

**Role:** Two-line accent-split heading.

```jsx
<HeroTitle>
  <span>Transforme ideias</span>
  <span className="accent">em automações.</span>
</HeroTitle>
```

`--fs-28` Semibold, line 1 in `--text-primary`, line 2 in `--color-accent`. Reserved for hero moments — not a generic heading style.

### Prompt Starter Card (chat empty state)

**Role:** Suggestion below the composer.

`--bg-surface`, `--radius-md`, `--space-4` padding, hover lifts via `--shadow-sm`. Title in `--text-primary` Medium, body in `--text-secondary`. Click pre-fills the textarea.

## Do's and Don'ts

### Do

- Use the **single accent** (`--color-accent`) for all primary actions. Lexflow does not have a Rich Black equivalent — accent is the CTA.
- Stack surfaces upward in luminance: `--bg-base` → `--bg-surface` → `--bg-elevated` → `--bg-input`.
- Use real shadows (`--shadow-sm` through `--shadow-xl`) on elevated surfaces — dark mode requires them.
- Use JetBrains Mono for code, IDs, paths, technical chips, command palette input. Use the `.mono` helper class for inline switches.
- Use the GitHub Primer status pairs (`--status-{ok|warning|danger}-fg` + `-bg`) for state communication.
- Reserve `DarkGradientCard` for chat hero/composer moments only. Standard cards use `--bg-card`.
- Use the two-line accent-split `<HeroTitle>` only for true hero moments (chat empty, onboarding) — not for generic page headings.
- Define motion using `--duration-*` and `--ease-*` tokens. The 100–300ms window is enforced by the principles, not by individual decisions.
- Use semantic CTA tokens (`--cta-primary-bg` etc.) in components — never hardcode the accent hex.
- Inherit Inspira's typography rules. Same Poppins, same three weights, same no-italics/no-allcaps.

### Don't

- Don't use Rich Black (`#070c21`) as a CTA fill. That's Inspira's primary, not Lexflow's. Lexflow CTAs are accent-filled.
- Don't introduce Tropical Indigo or Inspira-style gradient accents. Lexflow's idiom is single-accent + status pairs, not the Cornflower→Indigo gradient family.
- Don't use Inspira's radius scale (12 / 16 / 24). Lexflow's is tighter (8 / 10 / 14) — denser surfaces.
- Don't deepen the dark surface ladder beyond `--bg-input` (`#21262d`). Anything darker reads as "off" — go to a separate component (modal, drawer) instead.
- Don't use system grays. The slate palette (`#161b22`, `#1c2129`, `#21262d`, `#30363d`) is the only valid neutral set.
- Don't use Inspira's status colors (Madder, Saffron, Keppel) directly. Lexflow uses GitHub Primer's red/yellow/green (`#f85149`, `#d29922`, `#3fb950`).
- Don't apply `DarkGradientCard` to multiple surfaces per page. One per screen, max — it's a hero treatment.
- Don't redefine the principles. Sub-brands inherit `principles.md` from the parent, unmodified.
- Don't introduce a body font other than Poppins, or a mono other than JetBrains Mono.
- Don't use the legacy aliases at the bottom of `brisa.css` (the `--color-cool-gray-N`, `--color-rich-black-N` mappings) for new code. They exist only to keep legacy screens rendering during migration. New code references canonical tokens directly.

## Imagery

Lexflow's imagery is dominated by **product UI itself** — workflow nodes, execution timelines, chat threads, code-like surfaces. Photography is essentially absent.

- **Icons:** Lucide-style outlined, moderate stroke weight, rendered in `--text-secondary` or `--color-accent` (for active/selected states).
- **Illustrations:** flat, geometric, brand-tinted neutrals; rare.
- **Code surfaces:** mono font on `--bg-input` background, syntax highlighting subtle (no rainbow).
- **Avatars:** solid circles with initials, derived deterministically from name hash; no random color generators.

## Layout Principles

- **Shell:** persistent sidebar + topbar + content column.
- **Sidebar:** 248px, dark surface, never auto-collapsed below `--breakpoint-md` (1024px).
- **Topbar:** 56px, hosts breadcrumb (always present, named `team → app → screen`), search, user menu.
- **Content:** max width 1200px, padded `--space-6` to `--space-8` from the sidebar/topbar edges.
- **Drawers:** 480px, slide in from right with `--ease-out` over `--duration-normal`.
- **Modals:** 560px wide, centered, `--shadow-xl`, backdrop `rgba(0,0,0,0.6)`.

Hero sections (chat empty, onboarding) break the standard rhythm with the `DarkGradientCard` surface and centered hero title.

## Components — In Scope (v1)

These are what the Setup Skill provisions when scaffolding a Lexflow-flavored project.

- Button (Primary, Neutral, Ghost, Danger)
- Card (Default, with optional shadow)
- Modal / Dialog
- Drawer (right-side slide-in)
- HealthBadge / StatusBadge (ok / warning / danger / neutral)
- Text Input / Textarea
- Sidebar Nav (with active item treatment)
- Topbar (with breadcrumb)
- Composer (chat textarea + chip starters)
- Chat primitives — `UserBubble`, `AgentBubble`, `AgentHeader`, `ResumoBlock`, `ReferenceTag`, `ResourceCard`, `ContextSidebar`, `FileChip`, `HoverCard`
- HeroTitle (two-line accent-split)
- PromptStarter card
- Avatar (initials, deterministic color)
- Tag / Pill (status, category)

## Components — Out of Scope (for now)

- Data table primitives (Lexflow uses card/list patterns instead)
- Date picker
- Rich text editor
- Charts / data viz
- Drag-and-drop file upload
- Form complex (multi-step wizard, conditional fields)
- Toast / notification system

If a Lexflow-derived project needs these, the Setup Skill logs the gap.

## Open Questions / Known Gaps

- **Token migration.** Canonical Lexflow tokens currently live in `lexflow-full-uxpm/lexflow-merged/brisa.css` (Pencil-extracted). They need to migrate into `brand/lexflow/tokens/` (`primitives.css`, `semantic.css`, `dimensions.css`, `utilities.css`) following the same architecture as Inspira's `brand/tokens/`. Until then, this DESIGN.md is the source of truth.
- **Legacy alias removal.** `brisa.css` has a 130-line legacy alias section mapping Inspira primitive names (`--color-cool-gray-N`, `--color-rich-black-N`, `--color-cornflower-blue-N`) to dark Lexflow values. The note says "Lucas: remove these after migrating references to the canonical tokens above." Status: pending. New code must not depend on these aliases.
- **Motion tokens promotion.** Lexflow's motion tokens should bubble up to Inspira's parent layer so all sub-brands inherit them. Currently they live only in Lexflow.
- **Shadow tokens promotion.** Same question as motion — does Inspira want a shadow scale for dark surfaces it might define later, or stay shadowless on light?
- **Hero pattern reusability.** The two-line accent-split `<HeroTitle>` is a Lexflow signature. Is it Lexflow-only, or a Brisa hero pattern that other dark sub-brands could inherit?
- **Light-mode variant.** Lexflow is dark-only by design. If an embed/preview context ever needs a light-on-light render, there's no spec.
- **Dual accents.** Lexflow ships a single accent (`#6a96ea`). When workflows need an "AI moment" callout (rare), do we resurrect Tropical Indigo, or stay accent-only? Currently: stay accent-only; revisit if real surfaces demand the distinction.
- **Avatar color generation.** Spec says "deterministic from name hash" but the actual hash algorithm and palette aren't pinned down.
- **Command palette spec.** `⌘K` is referenced in HANDOFF.md as mocked but not wired. The visual spec for the picker (Pencil Tela 5) hasn't been ported.

## Quick Start

### CSS Custom Properties

```css
:root {
  /* Color — Canonical (Lexflow primitives) */
  --color-accent: #6a96ea;
  --color-accent-muted: #1f3a5f;
  --color-accent-subtle: #131d2f;

  --color-bg-base: #0e1117;
  --color-bg-surface: #161b22;
  --color-bg-elevated: #1c2129;
  --color-bg-input: #21262d;

  --color-border: #30363d;
  --color-border-emphasis: #484f58;

  --color-text-primary: #e6edf3;
  --color-text-secondary: #8b949e;
  --color-text-muted: #6e7681;

  --color-success: #3fb950;
  --color-success-muted: #1a2d1a;
  --color-warning: #d29922;
  --color-danger: #f85149;

  /* Color — Semantic aliases */
  --color-link: var(--color-accent);
  --color-focus-ring: var(--color-accent);
  --bg-page: var(--color-bg-base);
  --bg-card: var(--color-bg-surface);
  --bg-modal: var(--color-bg-elevated);
  --bg-code: var(--color-bg-input);
  --text-primary: var(--color-text-primary);
  --text-secondary: var(--color-text-secondary);
  --text-tertiary: var(--color-text-muted);
  --text-link: var(--color-accent);
  --border-default: var(--color-border);
  --border-subtle: color-mix(in srgb, var(--color-border) 60%, transparent);
  --border-strong: var(--color-border-emphasis);

  /* Status pairs */
  --status-ok-fg: var(--color-success);
  --status-ok-bg: var(--color-success-muted);
  --status-warning-fg: var(--color-warning);
  --status-warning-bg: color-mix(in srgb, var(--color-warning) 15%, var(--color-bg-base));
  --status-danger-fg: var(--color-danger);
  --status-danger-bg: color-mix(in srgb, var(--color-danger) 15%, var(--color-bg-base));
  --status-neutral-fg: var(--color-text-secondary);
  --status-neutral-bg: var(--color-bg-input);

  /* CTA */
  --cta-primary-bg: var(--color-accent);
  --cta-primary-fg: #ffffff;
  --cta-primary-hover: color-mix(in srgb, var(--color-accent) 85%, white);
  --cta-neutral-bg: var(--color-bg-input);
  --cta-neutral-fg: var(--color-text-primary);
  --cta-neutral-hover: var(--color-bg-elevated);
  --cta-ghost-fg: var(--color-text-secondary);
  --cta-ghost-hover: var(--color-bg-input);
  --cta-danger-bg: var(--color-danger);
  --cta-danger-fg: #ffffff;

  /* Typography */
  --font-sans:
    "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  --fs-10: 10.5px;
  --fs-11: 11px;
  --fs-12: 12px;
  --fs-13: 13px;
  --fs-14: 14px;
  --fs-15: 15px;
  --fs-17: 17px;
  --fs-22: 22px;
  --fs-28: 28px;

  --fw-regular: 400;
  --fw-medium: 500;
  --fw-semibold: 600;

  --lh-tight: 1.25;
  --lh-normal: 1.5;
  --lh-relaxed: 1.6;

  --tracking-tight: -0.02em;
  --tracking-mono: 0;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Radius */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-xl: 14px;
  --radius-pill: 999px;

  /* Shadow (dark-mode tuned) */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 48px rgba(0, 0, 0, 0.6);

  /* Motion */
  --duration-fast: 140ms;
  --duration-normal: 220ms;
  --duration-slow: 320ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Layout */
  --sidebar-width: 248px;
  --topbar-height: 56px;
  --content-max-width: 1200px;
  --drawer-width: 480px;
  --modal-width: 560px;
}

html,
body {
  margin: 0;
  padding: 0;
  font-family: var(--font-sans);
  background: var(--bg-page);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

.mono {
  font-family: var(--font-mono);
  font-size: var(--fs-12);
}
```

### Tailwind v4

```css
@theme {
  /* Inherit Inspira's parent @theme blocks first, then override below. */

  /* Color — overrides */
  --color-accent: #6a96ea;
  --color-bg-base: #0e1117;
  --color-bg-surface: #161b22;
  --color-bg-elevated: #1c2129;
  --color-bg-input: #21262d;
  --color-border: #30363d;
  --color-border-emphasis: #484f58;
  --color-text-primary: #e6edf3;
  --color-text-secondary: #8b949e;
  --color-text-muted: #6e7681;
  --color-success: #3fb950;
  --color-warning: #d29922;
  --color-danger: #f85149;

  /* Type — additions */
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Radius — overrides */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-xl: 14px;

  /* Shadow — additions */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 48px rgba(0, 0, 0, 0.6);

  /* Motion — additions */
  --duration-fast: 140ms;
  --duration-normal: 220ms;
  --duration-slow: 320ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Layout — additions */
  --sidebar-width: 248px;
  --topbar-height: 56px;
  --content-max-width: 1200px;
  --drawer-width: 480px;
  --modal-width: 560px;
}
```

## Sub-Brand Pattern Notes (for the Setup Skill)

When the Setup Skill provisions a Lexflow-flavored project:

1. **Inherit** Inspira's typography (`--font-poppins`, weights, type rules) from the parent `brand/` layer.
2. **Inherit** the principles file unchanged.
3. **Override** color tokens with Lexflow's dark palette (the entire color section above).
4. **Override** radius scale with Lexflow's tighter ladder.
5. **Add** `--font-mono`, motion tokens, shadow tokens, layout tokens.
6. **Drop in** the `DarkGradientCard` surface utility class for chat hero/composer.
7. **Provision** the chat primitives if the project's artifact target involves chat (signal: chat-related component selection in Phase 3 of the Setup interview).

The minimum surface override is **colors + radius + mono font addition**. Everything else can be added incrementally as the project's surface needs emerge.
