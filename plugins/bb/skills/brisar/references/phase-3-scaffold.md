# Phase 3: scaffold (write real files)

This is the phase that delivers. Everything before was conversation; here you write files to disk. If something fails, surface the error. Don't simulate success.

## When to run

- Coming out of Phase 2 with `gate.resolution: not-applicable` or `override`.
- OR coming from a subsequent /bb:brisar invocation resumed by Step 0.1 of SKILL.md after a `status: bootstrapped-to-discover` session (the builder ran /bb:discover and came back. The spec informs scope and fidelity here).

## Step 1: confirm slug and location

Phase 1 derived a slug (e.g. `lexflow-semantic-search`). Before creating files, confirm:

```json
{
  "questions": [
    {
      "question": "Project slug: '<slug>'. I'll create the folder `./<slug>/` here (`pwd`). OK?",
      "header": "Slug",
      "options": [
        {
          "label": "OK, create it here",
          "description": "The folder will be ./<slug>/ in the current directory"
        },
        {
          "label": "I want to adjust the slug",
          "description": "Free text, give me the name you prefer"
        },
        {
          "label": "I want to create it in another folder",
          "description": "Free text, a relative or absolute path"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If the slug or path changed, rename the task folder and update the brief's `slug`.

Additional check: if the destination folder already exists and is not empty, ask if it's OK to overwrite or if they want another name.

## Step 2: directory structure

Create:

```
<slug>/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── README.md
├── .gitignore
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   └── components/
│       └── (empty for now; surfaces will populate)
└── design-context/
    ├── tokens.md
    └── components.md
```

The visual direction does **not** live here: Phase 4 writes it into the task folder, `.bb/<slug>/`, next to the spec (plugin-level `references/spec-state.md`).

Command:

```bash
mkdir -p <slug>/src/components <slug>/design-context
```

## Step 3: file templates

The templates below assume Vite + React + TS + Tailwind v4 stack (the stack BRISA DS V0 uses). For `Storybook only`, adjust. See subsection at the end.

### package.json

```json
{
  "name": "<slug>",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

### vite.config.ts

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src"]
}
```

### index.html

```html
<!doctype html>
<html lang="<locale>">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><slug></title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### src/main.tsx

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

### src/App.tsx

Content varies by brand. For Inspira (light theme):

```tsx
export default function App() {
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-3xl font-semibold mb-4">{`<slug>`}</h1>
        <p className="text-text-secondary">
          Scaffolded by /bb:brisar. <strong>Inspira</strong> brand tokens active. Next: the Develop
          phase builds each surface from the visual direction in <code>.bb/</code>.
        </p>
      </main>
    </div>
  );
}
```

For Lexflow (dark theme), swap to:

```tsx
export default function App() {
  return (
    <div
      className="min-h-screen"
      style={{ background: "var(--color-bg-base)", color: "var(--color-text-primary)" }}
    >
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-2xl font-semibold mb-4">{`<slug>`}</h1>
        <p style={{ color: "var(--color-text-secondary)" }}>
          Scaffolded by /bb:brisar. <strong>Lexflow</strong> brand tokens active (dark, GitHub
          Primer-inspired).
        </p>
      </main>
    </div>
  );
}
```

For custom-from-inspira / custom-from-lexflow, use the base with a note in the comment:

```tsx
// Initial tokens inherited from brand <base>; adjust in design-context/tokens.md.
```

### src/index.css

```css
@import "tailwindcss";

/* Brand tokens, copied from <design_md_path> on <date> */
@import "./tokens-brand.css";
```

### src/tokens-brand.css

**Content:** copy from `<DS_PATH>/<brand.design_md_path>` the entire "Quick Start: Tailwind v4" block (the `@theme { ... }` block). For Inspira, read `<DS_PATH>/brand/DESIGN.md`. For Lexflow, read `<DS_PATH>/brand/lexflow/DESIGN.md`. For custom-from-X, copy from brand-base + add comment at the top: `/* Custom: start here and adjust, inherited from <base brand>. */`.

If DS not-found, write a minimal `@theme` stub with Tailwind defaults + comment asking the builder to edit.

### .gitignore

```
node_modules
dist
.DS_Store
*.local
```

### README.md

````markdown
# <slug>

Scaffolded by /bb:brisar, <date>.

## Stack

- Vite + React 18 + TypeScript
- Tailwind v4 (with the <brand> brand tokens)

## How to run

```bash
pnpm install
pnpm dev
```
````

## What's here

- `src/`: React code. Still empty; the surfaces will fill it.
- `design-context/`: the source for /bb:brisar's Develop phase. Don't edit it by hand unless you know what you're doing.
  The Develop phase finds both by convention: `design-context/` at this folder's root, and the visual direction in the task folder.

The visual direction for each surface lives in `.bb/<slug>/`, next to the spec. Read it before designing.

## Next steps

Run `/bb:brisar` again in this folder. It detects the project and offers the Develop phase, which reads `design-context/tokens.md` and `design-context/components.md`, plus the surface's visual direction, and helps you build each surface.

For deeper shaping: `/bb:discover`.
For a formal spec: `/bb:spec`.

````

## Step 4: design-context/ (contract with the Develop phase)

### design-context/tokens.md

Short synthesis extracted from `<DS_PATH>/<brand.design_md_path>`. Don't copy the entire file, extract the essential. Structure:

```markdown
# Tokens: <brand>

> Source: <DS_PATH>/<brand.design_md_path>
> Synthesized by /bb:brisar on <date>.

## Color (semantic)

| Role            | Token                            | Value     |
| --------------- | -------------------------------- | --------- |
| Page background | `--color-bg-primary`             | `<value>` |
| Primary text    | `--color-text-primary`           | `<value>` |
| Primary CTA     | `--color-interactive-primary`    | `<value>` |
| Secondary CTA   | `--color-interactive-secondary`  | `<value>` |
| Border default  | `--color-border-default`         | `<value>` |
| Focus ring      | `--color-interactive-focus-ring` | `<value>` |
| Error           | `--color-feedback-critical-text` | `<value>` |
| Success         | `--color-feedback-success-text`  | `<value>` |

(Add more rows as the specific DESIGN.md carries them.)

## Typography

- Family: `<--font-poppins | --font-sans>`
- Weights: 400 / 500 / 600 only
- Default body: `<--text-body>` (`<size>`)
- Default heading: `<--text-title-sm>` (`<size>`)

## Radius / spacing

- Default radius: `<--radius-md>`
- Default control height: `<--size-md>`
- Spacing scale: 4pt base (`--space-1`...`--space-24`)

## Hard rules

- Use semantic tokens, not primitives.
- Never the secondary brand color as primary CTA fill (Inspira: Cornflower Blue is secondary; Rich Black is primary).
- (extracted from the "Don't" section of DESIGN.md)
````

For Lexflow, adapt the tokens to the dark equivalents.
For custom, copy from the base but add `> ⚠ Custom, adjust the values as the identity evolves.` at the top.

### design-context/components.md

Synthesis of the "Components: In Scope" and "Components: Out of Scope" sections of the brand's DESIGN.md:

```markdown
# Components: <brand>

> Source: <DS_PATH>/<brand.design_md_path>
> Synthesized by /bb:brisar on <date>.

## In scope (use these)

- Button (Primary, Secondary, Neutral, Ghost, Destructive)
- Text Input
- Card (Default, Brand-Tinted)
- Feedback Banner (info, success, warning, critical)
- (...the list from DESIGN.md...)

## Out of scope (not there yet: flag a gap if you need one)

- Data table
- Combobox / Multi-select
- Date picker
- (...the list from DESIGN.md...)

## When you need something out of scope

Edit this file, adding `## Custom added in this project` with the component.
When you run `/bb:brisar` in feedback mode (future), the additions become seeds for the DS.
```

## Step 5: record the scaffold in the brief

No config file: the paths are derived. `design-context/` is at the root of the folder
this phase just created, and the visual direction is `.bb/<slug>/design.md`, from the
slug. The brand and the DS path stay in context for this session, and the brief records
which brand the scaffold was built on.

Set the brief's frontmatter `phase: design-direction`. Don't mark `status: completed`
yet, only after Phase 4.

## Stack variants

### Storybook only

Instead of Vite + App.tsx, use:

- `package.json` with `@storybook/react-vite` and `storybook` scripts
- `.storybook/main.ts` and `.storybook/preview.ts`
- `src/components/Button.stories.tsx` as starter

### Embedded (inside existing app)

Don't create a new folder. Instead:

- Ask which folder of the app is the entry point.
- Create only `design-context/` at the root of the existing app (the design direction goes to `.bb/<slug>/` as usual).
- Create `src/components/<slug>/` for the feature's components.
- Don't touch existing `package.json`, `vite.config`, `index.html`.

Warning: embedded is riskier. Confirm with the builder before touching any file of the existing app.

### Prototype-hosted (static HTML, when `uses_terminal` is false)

**When to run:** `uses_terminal` is false OR `artifact.fidelity == prototype-hosted`. Output is HTML + CSS without a build step. Builder opens the file directly in the browser (`file://` or drag-and-drop).

**Why HTML, not Vite?** Someone who doesn't run commands doesn't have an npm/node/git environment. Vite requires `pnpm install && pnpm dev` running locally: friction that blocks the path. Static HTML opens in any browser, any machine, without dependencies. When the eng team picks it up, they can rewrite it in Vite/React by reading the `HANDOFF-DEV.md`.

**DON'T confuse with Framer.** Framer is the specific path for the institutional site (`brand.workflow == framer-harpa`). Static HTML is the path for a new internal tool built without a terminal.

#### Directory structure (variant)

```
<slug>/
├── index.html                       ← prototype landing (links to each surface)
├── <surface-1>.html                 ← one page per surface
├── <surface-2>.html
├── <surface-3>.html
├── styles.css                       ← brand tokens in :root + inline components
├── HANDOFF-DEV.md                   ← instructions for the technical team to continue
└── README.md                        ← everyday language. How to open, how to show
```

The written direction for each screen lands in `.bb/<slug>/` (Phase 4), same as the standard variant.

DO NOT create: `package.json`, `vite.config.ts`, `tsconfig.json`, `src/`, `node_modules/`.

#### Step 1: confirm slug (same as normal variant)

Same Step 1 as the standard scaffold. Confirms slug and where to create the folder.

#### Step 2: create the folder

```bash
mkdir -p <slug>
```

#### Step 3: HTML templates

##### `<slug>/index.html`: landing

```html
<!doctype html>
<html lang="<locale>">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><slug>, Prototype</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <main class="landing">
      <header>
        <h1><slug></h1>
        <p class="subtitle">Clickable prototype, generated by /bb:brisar on <date>.</p>
      </header>

      <section class="surfaces">
        <h2>Screens</h2>
        <ul>
          <li><a href="<surface-1>.html"><surface-1, short description></a></li>
          <li><a href="<surface-2>.html"><surface-2, short description></a></li>
          <!-- one <li> per surface -->
        </ul>
      </section>

      <footer class="meta">
        <p>Brand: <strong><brand></strong> · Audience: <audience> · Appetite: <appetite></p>
        <p class="hint">For the technical team: see <code>HANDOFF-DEV.md</code> at the root of the folder.</p>
      </footer>
    </main>
  </body>
</html>
```

##### `<slug>/<surface>.html`: one per surface (generated in Phase 4 + scaffold base here)

Phase 3 creates empty stubs; Phase 4 populates with content from the visual direction. Stub:

```html
<!doctype html>
<html lang="<locale>">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><surface>, <slug></title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <nav class="back"><a href="index.html">← Back</a></nav>
    <main class="surface" id="<surface-id>">
      <h1><surface, title></h1>
      <!-- Phase 4 will populate this block with the visual direction of the surface -->
      <p class="placeholder">The content of this screen goes here (generated in Phase 4 of /bb:brisar).</p>
    </main>
  </body>
</html>
```

##### `<slug>/styles.css`

Brand tokens in `:root` (extracted from DESIGN.md, same as the standard scaffold extracts for Tailwind), BUT here they are pure CSS vars (no Tailwind):

```css
/* Brand tokens, copied from <design_md_path> on <date> */
:root {
  /* Extract from the "Quick Start: Tailwind v4" block of DESIGN.md, mapping @theme → :root */
  --color-bg-primary: <value>;
  --color-bg-secondary: <value>;
  --color-text-primary: <value>;
  --color-text-secondary: <value>;
  --color-interactive-primary: <value>;
  --color-interactive-secondary: <value>;
  --color-border-default: <value>;
  --color-feedback-critical-text: <value>;
  --color-feedback-success-text: <value>;

  --font-sans: <font-stack>;

  --radius-sm: <value>;
  --radius-md: <value>;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
}

/* Minimal reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: var(--font-sans);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.5;
}
a {
  color: var(--color-interactive-primary);
}

/* Layout primitives */
.landing,
.surface {
  max-width: 768px;
  margin: 0 auto;
  padding: var(--space-12) var(--space-6);
}

.landing header h1 {
  font-size: 2rem;
  margin: 0 0 var(--space-2);
}
.landing .subtitle {
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-8);
}
.surfaces ul {
  list-style: none;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}
.surfaces li {
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}
.surfaces li a {
  text-decoration: none;
  font-weight: 500;
}
.meta {
  margin-top: var(--space-12);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-default);
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}
.meta .hint code {
  background: var(--color-bg-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}
.back {
  max-width: 768px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-6) 0;
}
.back a {
  text-decoration: none;
  font-size: 0.875rem;
}
.placeholder {
  color: var(--color-text-secondary);
  font-style: italic;
}
```

##### `<slug>/HANDOFF-DEV.md`: delivery for the technical team

```markdown
# HANDOFF: <slug>

**Status:** static HTML prototype. Generated by `/bb:brisar` on <date> for <person>, who doesn't run it locally, to validate the idea with stakeholders.

**This folder is NOT the product.** It's a clickable to show the direction. Take the concept, NOT the code, and rewrite it in the appropriate stack.

---

## Context of the idea

- **What it is:** <intent.raw_prompt>
- **Who uses it:** <intent.audience>
- **Problem it solves:** <intent.problem_statement>
- **Brand:** <brand.name> (tokens in [styles.css](styles.css))
- **Original appetite:** <shaping.appetite>
- **Does it continue as a product?:** <intent.scale_signal == will-scale ? "yes, it becomes a real product" : "no, validation only">

## Screens / surfaces

| Screen      | File                                 | Visual direction                      |
| ----------- | ------------------------------------ | ------------------------------------- |
| <surface-1> | [<surface-1>.html](<surface-1>.html) | `../.bb/<slug>/design/<surface-1>.md` |
| <surface-2> | [<surface-2>.html](<surface-2>.html) | `../.bb/<slug>/design/<surface-2>.md` |

The visual direction for each screen lives in `.bb/<slug>/`, next to the spec. Read it BEFORE the HTML. The HTML is mocked; the spec carries the intent.

## Recommended stack for production

This tool is a candidate to become an internal app. A stack aligned with the rest of Inspira:

- **Framework:** Vite + React 18 + TypeScript
- **Styling:** Tailwind v4 with the <brand> brand tokens
- **Design system:** Brisa DS (tokens in `BRISA DS V0/brand/<brand>/DESIGN.md`)
- **To start the real version:**
  1. Run `/bb:brisar` in Inspira's root folder (not in this folder. This one is only a prototype).
  2. When it asks for the profile, pick "I can work in code".
  3. When it asks about product/brand: pick <brand>.
  4. /bb:brisar scaffolds Vite. Use the visual direction in `.bb/<slug>/` as the input for the Develop phase in the new project.

## What to avoid

- Don't copy the HTML/CSS directly. Rewrite it as typed React components, using the DS.
- Don't use the hardcoded colors in `styles.css`. Use the semantic Tailwind v4 tokens of the real scaffold.
- Don't ask for approval on every screen. The visual direction is already in `.bb/<slug>/`.

## Who made the prototype

<person>. Use <person> as the validation stakeholder. Not as the end client of the code.
```

Fill the "Visual direction" column from what Phase 4 recorded (`design_path` + `surfaces[].file`), one row per surface, with a single surface that path is `../.bb/<slug>/design.md`.

##### `<slug>/README.md`: everyday language

```markdown
# <slug>

A clickable prototype of your idea. Generated by /bb:brisar on <date>.

## How to open it

1. Open the `<slug>/` folder in Finder.
2. Double-click `index.html`.
3. It opens in your browser (Chrome/Safari/Edge, any of them).
4. The links take you to each screen of the prototype.

You don't need to install anything. It works offline.

## How to show it to the team

Option 1. Share the whole folder: zip `<slug>/` and send it. Each person opens the `index.html`.

Option 2. Host it for a link: drop the folder on Vercel/Netlify (or ask the eng team). Then it becomes a normal link.

## And the real product?

This prototype is for validating the idea. **It is not the final product.** The technical team needs to take the `HANDOFF-DEV.md` (at the root of the folder) to build the real version.

## What's in each folder

- `index.html`: the opening screen (lists every screen)
- `<surface>.html`: one per screen of the prototype
- `styles.css`: the visuals (colors, fonts, spacing of the <brand> brand)
- `HANDOFF-DEV.md`: the package for the technical team (you don't need to open it, but if you pass this on, send this file)

The spec for each screen (the text explaining what it does) lives in `.bb/<slug>/`, one folder up.
```

#### Step 4: record the prototype in the brief

Same as the standard variant, with one difference to state in prose: this is a
prototype-hosted artifact, so there is no `design-context/` and the Develop phase is not
used on this path. Which HTML file each surface landed in is Phase 4's business, and it
goes into `design.md`'s own frontmatter beside the direction it describes.

Set the brief's frontmatter `phase: design-direction` (same transition as the standard
variant).

#### DO NOT use in this variant

- `pnpm install`, `pnpm dev`, or any build command
- `package.json`, `vite.config.ts`, `tsconfig.json`
- `src/` or React structure
- Tailwind (use pure CSS vars)
- The Develop phase (no React code to orchestrate. Design goes straight to HTML in Phase 4)

#### Phase 4 in this variant

Phase 4 populates the `<surface>.html` stubs with HTML markup aligned to the surface's direction file in `.bb/<slug>/`. Not with React components, but with sections/divs styled via classes in `styles.css`. Result: builder opens `index.html`, clicks on a surface, sees a layout close to the brief.

#### Phase 5 in this variant

Terminal handoff varies: does NOT suggest `pnpm dev`. Suggests opening `index.html`. Does NOT offer the Develop phase. See `phase-5-handoff.md` prototype-hosted variant.

## How to surface errors

If `mkdir`, `Write`, or any operation fails:

1. STOP immediately.
2. Print the exact error and the problematic path to the user.
3. Ask if they want to (a) try another path, (b) archive the session and abort, (c) resume manually from the current state.

Don't simulate success. Don't try to "fix" silently paths with `:` or other special characters, surface the problem.
