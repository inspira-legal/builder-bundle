# Phase 3 — Scaffold (write real files)

This is the phase that delivers. Everything before was conversation; here you write files to disk. If something fails, surface the error — don't simulate success.

## When to run

- Coming out of Phase 2 with `gate.resolution: not-applicable` or `override`.
- OR coming from a subsequent /bb:brisar invocation resumed by Step 0.1 of SKILL.md after a `status: bootstrapped-to-discover` session (the builder ran /bb:discover and came back — the spec informs scope and fidelity here).

## Step 1 — Confirm slug and location

Phase 1 derived a slug (e.g. `lexflow-busca-semantica`). Before creating files, confirm:

```json
{
  "questions": [
    {
      "question": "Slug do projeto: '<slug>'. Vou criar a pasta `./<slug>/` aqui (`pwd`). OK?",
      "header": "Slug",
      "options": [
        { "label": "OK, criar aqui", "description": "Pasta vai ser ./<slug>/ no diretório atual" },
        {
          "label": "Quero ajustar o slug",
          "description": "Texto livre — me dá o nome que prefere"
        },
        {
          "label": "Quero criar em outra pasta",
          "description": "Texto livre — caminho relativo ou absoluto"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If the slug or path changed, update session.yaml.

Additional check: if the destination folder already exists and is not empty, ask if it's OK to overwrite or if they want another name.

## Step 2 — Directory structure

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
│       └── (empty for now — surfaces will populate)
├── design-context/
│   ├── tokens.md
│   └── components.md
└── .brisar/
    └── config.yaml
```

The visual direction does **not** live here — Phase 4 writes it into the task folder, `.bb/<slug>/`, next to the spec (plugin-level `references/spec-state.md`).

Command:

```bash
mkdir -p <slug>/src/components <slug>/design-context <slug>/.brisar
```

## Step 3 — File templates

The templates below assume Vite + React + TS + Tailwind v4 stack (the stack BRISA DS V0 uses). For `Storybook only`, adjust — see subsection at the end.

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
<html lang="pt-BR">
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
          Scaffolded by /bb:brisar. Tokens da marca <strong>Inspira</strong> ativos. Próximo: a fase
          Develop constrói cada surface a partir da direção visual em <code>.bb/</code>.
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
          Scaffolded by /bb:brisar. Tokens da marca <strong>Lexflow</strong> ativos (dark, GitHub
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

/* Brand tokens — copied from <design_md_path> on <date> */
@import "./tokens-brand.css";
```

### src/tokens-brand.css

**Content:** copy from `<DS_PATH>/<brand.design_md_path>` the entire "Quick Start — Tailwind v4" block (the `@theme { ... }` block). For Inspira, read `<DS_PATH>/brand/DESIGN.md`. For Lexflow, read `<DS_PATH>/brand/lexflow/DESIGN.md`. For custom-from-X, copy from brand-base + add comment at the top: `/* Custom: start here and adjust — inherited from <base brand>. */`.

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

Scaffolded by /bb:brisar — <data>.

## Stack

- Vite + React 18 + TypeScript
- Tailwind v4 (com tokens da marca <brand>)

## Como rodar

```bash
pnpm install
pnpm dev
```
````

## O que está aqui

- `src/` — código React. Ainda vazio; surfaces vão preencher.
- `design-context/` — fonte para a fase Develop do /bb:brisar. Não edite à mão a menos que saiba o que está fazendo.
- `.brisar/config.yaml` — config do brisar. A fase Develop lê esse arquivo para saber onde estão os tokens e a direção visual.

A direção visual de cada surface fica em `.bb/<slug>/`, junto do brief. Leia antes de desenhar.

## Próximos passos

Rode `/bb:brisar` de novo nesta pasta — ele detecta o projeto e oferece a fase Develop, que lê `design-context/tokens.md` e `design-context/components.md`, mais a direção visual da surface, e te ajuda a construir cada surface.

Para shaping mais profundo: `/bb:discover`.
Para spec formal: `/bb:spec`.

````

## Step 4 — design-context/ (contract with the Develop phase)

### design-context/tokens.md

Short synthesis extracted from `<DS_PATH>/<brand.design_md_path>`. Don't copy the entire file — extract the essential. Structure:

```markdown
# Tokens — <brand>

> Fonte: <DS_PATH>/<brand.design_md_path>
> Sintetizado por /bb:brisar em <data>.

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

(Adicione mais linhas conforme o DESIGN.md específico tem.)

## Typography

- Family: `<--font-poppins | --font-sans>`
- Weights: 400 / 500 / 600 only
- Default body: `<--text-body>` (`<size>`)
- Default heading: `<--text-title-sm>` (`<size>`)

## Radius / Spacing

- Default radius: `<--radius-md>`
- Default control height: `<--size-md>`
- Spacing scale: 4pt base (`--space-1`...`--space-24`)

## Hard rules

- Use semantic tokens, not primitives.
- Never the secondary brand color as primary CTA fill (Inspira: Cornflower Blue is secondary; Rich Black is primary).
- (extraídas do "Don't" do DESIGN.md)
````

For Lexflow, adapt the tokens to the dark equivalents.
For custom, copy from the base but add `> ⚠ Custom — ajuste valores conforme a identidade evolui.` at the top.

### design-context/components.md

Synthesis of the "Components — In Scope" and "Components — Out of Scope" sections of the brand's DESIGN.md:

```markdown
# Components — <brand>

> Fonte: <DS_PATH>/<brand.design_md_path>
> Sintetizado por /bb:brisar em <data>.

## In scope (use estes)

- Button (Primary, Secondary, Neutral, Ghost, Destructive)
- Text Input
- Card (Default, Brand-Tinted)
- Feedback Banner (info, success, warning, critical)
- (...lista da DESIGN.md...)

## Out of scope (não tem ainda — sinalize gap se precisar)

- Data table
- Combobox / Multi-select
- Date picker
- (...lista da DESIGN.md...)

## Quando precisar de algo out-of-scope

Edite este arquivo adicionando `## Custom adicionado neste projeto` com o componente.
Quando rodar `/bb:brisar` em modo feedback (futuro), os adicionais viram seeds para o DS.
```

## Step 5 — .brisar/config.yaml

```yaml
version: 1
brisar_version: "2.0.0"
slug: "<slug>"
created_at: <ISO>

ds_path: "<absolute path of the DS, or null if not-found>"
brand:
  name: "<brand.name>"
  source: "<brand.source>"
  design_md_path: "<brand.design_md_path absolute, or null>"

# Path of design-context — THIS IS WHERE THE DEVELOP PHASE WILL LOOK.
design_context_path: "<slug>/design-context/"

# Task folder (.bb/<slug>/) — Phase 4 fills it in when it writes the direction.
design_path: null

# Surface tracking — one entry per surface file generated in Phase 4.
surfaces: []
```

## Step 6 — Update .brisar/session.yaml

Move from `current_phase: phase-3` to `current_phase: phase-4` (which will generate design directions). Don't mark `completed` yet — only after Phase 4.

## Stack variants

### Storybook only

Instead of Vite + App.tsx, use:

- `package.json` with `@storybook/react-vite` and `storybook` scripts
- `.storybook/main.ts` and `.storybook/preview.ts`
- `src/components/Button.stories.tsx` as starter

### Embedded (inside existing app)

Don't create a new folder. Instead:

- Ask which folder of the app is the entry point.
- Create only `design-context/` and `.brisar/` at the root of the existing app (the design direction goes to `.bb/<slug>/` as usual).
- Create `src/components/<slug>/` for the feature's components.
- Don't touch existing `package.json`, `vite.config`, `index.html`.

Warning: embedded is riskier. Confirm with the builder before touching any file of the existing app.

### Prototype-hosted (static HTML — executive persona)

**When to run:** `profile.persona_id == executive` OR `artifact.fidelity == prototype-hosted`. Output is HTML + CSS without a build step. Builder opens the file directly in the browser (`file://` or drag-and-drop).

**Why HTML, not Vite?** Executive doesn't have an npm/node/git environment. Vite requires `pnpm install && pnpm dev` running locally — friction that blocks the path. Static HTML opens in any browser, any machine, without dependencies. When the eng team picks it up, they can rewrite it in Vite/React by reading the `HANDOFF-DEV.md`.

**DON'T confuse with Framer.** Framer is the specific path for the institutional site (persona `content`). Static HTML is the path for the executive building a new internal tool.

#### Directory structure (variant)

```
<slug>/
├── index.html                       ← prototype landing (links to each surface)
├── <surface-1>.html                 ← one page per surface
├── <surface-2>.html
├── <surface-3>.html
├── styles.css                       ← brand tokens in :root + inline components
├── HANDOFF-DEV.md                   ← instructions for the technical team to continue
├── README.md                        ← executive language — how to open, how to show
└── .brisar/
    ├── config.yaml
    └── session.yaml
```

The written direction for each screen lands in `.bb/<slug>/` (Phase 4), same as the standard variant.

DO NOT create: `package.json`, `vite.config.ts`, `tsconfig.json`, `src/`, `node_modules/`.

#### Step 1 — Confirm slug (same as normal variant)

Same Step 1 as the standard scaffold. Confirms slug and where to create the folder.

#### Step 2 — Create directories

```bash
mkdir -p <slug>/.brisar
```

#### Step 3 — HTML templates

##### `<slug>/index.html` — landing

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><slug> — Protótipo</title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <main class="landing">
      <header>
        <h1><slug></h1>
        <p class="subtitle">Protótipo clicável — gerado por /bb:brisar em <data>.</p>
      </header>

      <section class="surfaces">
        <h2>Telas</h2>
        <ul>
          <li><a href="<surface-1>.html"><surface-1 — descrição curta></a></li>
          <li><a href="<surface-2>.html"><surface-2 — descrição curta></a></li>
          <!-- one <li> per surface -->
        </ul>
      </section>

      <footer class="meta">
        <p>Marca: <strong><brand></strong> · Audiência: <audience> · Apetite: <appetite></p>
        <p class="hint">Pra time técnico: ver <code>HANDOFF-DEV.md</code> na raiz da pasta.</p>
      </footer>
    </main>
  </body>
</html>
```

##### `<slug>/<surface>.html` — one per surface (generated in Phase 4 + scaffold base here)

Phase 3 creates empty stubs; Phase 4 populates with content from the visual direction. Stub:

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><surface> — <slug></title>
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <nav class="back"><a href="index.html">← Voltar</a></nav>
    <main class="surface" id="<surface-id>">
      <h1><surface — título></h1>
      <!-- Phase 4 will populate this block with the visual direction of the surface -->
      <p class="placeholder">Conteúdo desta tela vai aqui (gerado em Phase 4 do /bb:brisar).</p>
    </main>
  </body>
</html>
```

##### `<slug>/styles.css`

Brand tokens in `:root` (extracted from DESIGN.md, same as the standard scaffold extracts for Tailwind), BUT here they are pure CSS vars (no Tailwind):

```css
/* Brand tokens — copied from <design_md_path> on <date> */
:root {
  /* Extract from the "Quick Start — Tailwind v4" block of DESIGN.md, mapping @theme → :root */
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

##### `<slug>/HANDOFF-DEV.md` — delivery for the technical team

```markdown
# HANDOFF — <slug>

**Status:** protótipo HTML estático. Foi gerado por `/bb:brisar` em <data> pra <pessoa> (perfil executive) validar a ideia com stakeholders.

**Esta pasta NÃO é o produto.** É um clicável pra mostrar a direção. Pegue o conceito, NÃO o código — re-escreva no stack apropriado.

---

## Contexto da ideia

- **O que é:** <intent.raw_prompt>
- **Quem usa:** <intent.audience>
- **Problema que resolve:** <intent.problem_statement>
- **Marca:** <brand.name> (tokens em [styles.css](styles.css))
- **Apetite original:** <shaping.appetite>
- **Continua como produto?:** <intent.scale_signal == will-scale ? "sim — virar produto de verdade" : "não — só validação">

## Telas / surfaces

| Tela        | Arquivo                              | Direção visual                        |
| ----------- | ------------------------------------ | ------------------------------------- |
| <surface-1> | [<surface-1>.html](<surface-1>.html) | `../.bb/<slug>/design/<surface-1>.md` |
| <surface-2> | [<surface-2>.html](<surface-2>.html) | `../.bb/<slug>/design/<surface-2>.md` |

A direção visual de cada tela mora em `.bb/<slug>/`, junto do brief — leia ANTES do HTML. O HTML é mockado; o brief tem a intenção.

## Stack recomendada pra produção

Esta ferramenta é candidata a virar app interno. Stack alinhada com o resto da Inspira:

- **Framework:** Vite + React 18 + TypeScript
- **Estilo:** Tailwind v4 com tokens da marca <brand>
- **Design system:** Brisa DS (tokens em `BRISA DS V0/brand/<brand>/DESIGN.md`)
- **Para iniciar a versão real:**
  1. Rode `/bb:brisar` na pasta-raiz da Inspira (não nesta pasta — esta é só protótipo).
  2. Quando perguntar perfil, marque "Sei mexer em código".
  3. Quando perguntar produto/marca: marque <brand>.
  4. /bb:brisar scaffolda Vite. Use a direção visual em `.bb/<slug>/` como input pra fase Develop no projeto novo.

## O que NÃO fazer

- Não copie HTML/CSS direto. Re-escreva como componentes React tipados, usando o DS.
- Não use as cores hardcoded em `styles.css` — use os tokens semânticos do Tailwind v4 do scaffold real.
- Não precise pedir aprovação a cada tela — a direção visual já tá em `.bb/<slug>/`.

## Quem fez o protótipo

<pessoa> (executive). Use <pessoa> como stakeholder de validação — não como cliente final do código.
```

Fill the "Direção visual" column from what Phase 4 recorded (`design_path` + `surfaces[].file`), one row per surface — with a single surface that path is `../.bb/<slug>/design.md`.

##### `<slug>/README.md` — executive language

```markdown
# <slug>

Protótipo clicável da sua ideia. Gerado por /bb:brisar em <data>.

## Como abrir

1. Abra a pasta `<slug>/` no Finder.
2. Dê dois cliques em `index.html`.
3. Vai abrir no seu navegador (Chrome/Safari/Edge — qualquer um).
4. Os links levam pra cada tela do protótipo.

Não precisa instalar nada. Funciona offline.

## Como mostrar pro time

Opção 1 — Compartilhar a pasta inteira: zipe `<slug>/` e mande. Cada pessoa abre o `index.html`.

Opção 2 — Hospedar pra link: jogue a pasta no Vercel/Netlify (ou peça pro time de eng). Aí vira um link normal.

## E o produto de verdade?

Esse protótipo é pra validar a ideia. **Não é o produto final.** O time técnico precisa pegar o `HANDOFF-DEV.md` (na raiz da pasta) pra construir a versão real.

## O que tem em cada pasta

- `index.html` — tela inicial (lista todas as telas)
- `<surface>.html` — uma por tela do protótipo
- `styles.css` — visual (cores, fontes, espaçamentos da marca <brand>)
- `HANDOFF-DEV.md` — pacote pro time técnico (não precisa abrir, mas se for passar adiante, manda esse arquivo)

O brief de cada tela (texto explicando o que ela faz) fica em `.bb/<slug>/`, uma pasta acima.
```

#### Step 4 — `.brisar/config.yaml` (variant)

```yaml
version: 1
brisar_version: "2.0.0"
slug: "<slug>"
created_at: <ISO>
mode: prototype-hosted # <-- differentiates from the normal variant

ds_path: "<absolute path of the DS, or null>"
brand:
  name: "<brand.name>"
  source: "<brand.source>"
  design_md_path: "<absolute path, or null>"

# The Develop phase is NOT used on this path — no canonical design_context_path needed.
# But we keep it for compatibility in case the builder regenerates later in Vite mode.
design_context_path: null

# Task folder — filled by Phase 4, same as the standard variant.
design_path: null

surfaces:
  - name: <surface-1>
    file: null # filled by Phase 4 — it decides design.md vs design/<name>.md
    html: <surface-1>.html # relative to the prototype folder
    state: drafted
```

#### Step 5 — Update session.yaml

Add:

```yaml
artifact:
  fidelity: prototype-hosted
  hosting: prototype-hosted
profile:
  persona_id: executive
  needs_instructions: true
  can_clone_repo: false
```

`current_phase: phase-4` (same transition as the standard variant).

#### DO NOT use in this variant

- `pnpm install`, `pnpm dev`, or any build command
- `package.json`, `vite.config.ts`, `tsconfig.json`
- `src/` or React structure
- Tailwind (use pure CSS vars)
- The Develop phase (no React code to orchestrate — design goes straight to HTML in Phase 4)

#### Phase 4 in this variant

Phase 4 populates the `<surface>.html` stubs with HTML markup aligned to the surface's direction file in `.bb/<slug>/`. Not with React components, but with sections/divs styled via classes in `styles.css`. Result: builder opens `index.html`, clicks on a surface, sees a layout close to the brief.

#### Phase 5 in this variant

Terminal handoff varies: does NOT suggest `pnpm dev` — suggests opening `index.html`. Does NOT offer the Develop phase. See `phase-5-handoff.md` prototype-hosted variant.

## How to surface errors

If `mkdir`, `Write`, or any operation fails:

1. STOP immediately.
2. Print the exact error and the problematic path to the user.
3. Ask if they want to (a) try another path, (b) archive the session and abort, (c) resume manually from the current state.

Don't simulate success. Don't try to "fix" silently paths with `:` or other special characters — surface the problem.
