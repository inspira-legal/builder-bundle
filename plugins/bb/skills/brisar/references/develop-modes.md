# Develop modes — templates for the 3 build modes

Load lazily: only read the section of the mode chosen in Step 1 of `phase-develop.md`.

---

## Mode 1: Full surface (`full-surface`)

**Why it exists:** building 1 screen end-to-end is the most common case. It reads the contract (tokens + components + visual direction) and produces React/HTML code applying everything.

### Inputs

- `.brisar/config.yaml` — `design_context_path`, `brand.name`, `surfaces[]`
- `<design_context_path>/tokens.md` — colors, spacing, type-scale
- `<design_context_path>/components.md` — components available in the DS
- `<design_context_path>/design/<surface>.md` — visual direction written by brisar Phase 4 (hierarchy, components, states, sketch)
- `.brisar/session.yaml` — gate.discover_brief (cuts, hypothesis, appetite live in the brief)

### Target decision (silent before building)

Read `artifact.hosting` from session.yaml:

| Hosting            | Target                                                                             |
| ------------------ | ---------------------------------------------------------------------------------- |
| `standalone`       | React + Tailwind in `src/<surface>.tsx`                                            |
| `embedded`         | React + Tailwind in `src/pages/<surface>.tsx` (or convention of the embedded repo) |
| `prototype-hosted` | Plain static HTML in `<surface>.html` (no Vite, no build)                          |
| `storybook-only`   | Story in `src/stories/<Component>.stories.tsx`                                     |

### Per-surface checklist

For each surface chosen in Step 1:

**1. Screen header**

- Read visual direction: top-to-bottom hierarchy
- Identify the primary CTA (the most salient element)
- Identify navigation/breadcrumb if applicable

**2. Main content**

- A DS component for each block (Card, List, Form, Dialog, ...)
- Custom only if justifiable + record in `notes.md`
- Tokens applied to every element (color, spacing, type)

**3. CTA / primary action**

- Visually dominant
- Clear destination (route, modal, action)
- Disabled state if there is a pre-condition

**4. States (always)**

- `default` — the happy state
- `loading` — skeleton or spinner aligned with the DS
- `empty` — when there is no data to show, with a CTA to fill in
- `error` — recoverable (message + retry) and non-recoverable (message + support)

**5. Responsiveness (if hosting != storybook)**

- DS breakpoints (mobile/tablet/desktop)
- Tabs/menus collapse correctly on mobile

**6. Basic accessibility (does not replace the Deliver phase)**

- Buttons are `<button>`, links are `<a>`
- Form fields have `<label>`
- Headings in order
- Icon-only have `aria-label`

### React + Tailwind template

```tsx
// src/<surface>.tsx
import { Button, Card } from "@/components"; // adjust the import path to the DS
import { useState } from "react";

type Status = "default" | "loading" | "empty" | "error";

export default function <SurfaceName>() {
  const [status, setStatus] = useState<Status>("default");

  if (status === "loading") return <LoadingSkeleton />;
  if (status === "empty") return <EmptyState onCTA={...} />;
  if (status === "error") return <ErrorState onRetry={...} />;

  return (
    <main className="<tokens-applied>">
      <header className="<tokens-applied>">
        {/* hierarchy + primary CTA */}
      </header>
      <section className="<tokens-applied>">
        {/* main content using DS components */}
      </section>
    </main>
  );
}
```

### Static HTML template (prototype-hosted)

```html
<!-- <surface>.html -->
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><Brand> — <surface></title>
    <link rel="stylesheet" href="design-context/tokens.css" />
    <link rel="stylesheet" href="design-context/components.css" />
  </head>
  <body>
    <main>
      <!-- structure applying tokens via the DS CSS classes -->
    </main>
  </body>
</html>
```

### Expected output

- Surface file at the correct path (per the target decision above)
- Update in `.brisar/session.yaml`:

```yaml
tarsila:
  surfaces:
    - name: <surface>
      file: src/<surface>.tsx
      status: built
      custom_components: []
      missing_tokens: []
      states_covered: [default, loading, empty, error]
```

- If there were custom_components or missing_tokens: write `.brisar/tarsila/notes.md`:

```markdown
# Develop phase — build notes

> Generated on <ISO date>

## Custom components (created outside the DS)

- <Name> in <surface> — reason: <brief> — suggestion: <add to DS | keep local>

## Missing tokens

- <token_name> needed in <surface> — used fallback: <value> — flag for a DS-update round on tokens.md? (TODO)
```

---

## Mode 2: Isolated component (`component`)

**Why it exists:** sometimes it is not a surface — it is a component that goes to the DS or to the project. A lean mode to build 1 component in isolation.

### Minimum inputs

- `components.md` (to check whether an equivalent already exists)
- Tokens (always applied)

### Questions (1 turn)

```json
{
  "questions": [
    {
      "question": "Como esse componente se encaixa?",
      "header": "Encaixe",
      "options": [
        {
          "label": "Adicionar ao DS",
          "description": "Vai virar parte do Brisa DS — output em <DS_path>/components/. Sugere PR ao DS."
        },
        {
          "label": "Custom local",
          "description": "Vive no projeto, fora do DS. Output em src/components/."
        },
        {
          "label": "Variant de existente",
          "description": "Variação de um componente do DS (ex: Button variant=destructive). Atualiza no DS."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Minimum structure

- The component itself (.tsx)
- 1 story (Storybook or MDX) — optional if hosting != storybook
- Props documented with TypeScript
- States (minimum: default, hover, focus, disabled — when applicable)

### Output

- `<path>/<Name>.tsx`
- (if DS) `<DS_path>/components/<Name>.tsx` + entry in `components.md`
- Update in session.yaml (`tarsila.custom_components` if it was local)

---

## Mode 3: Iteration on existing (`iteration`)

**Why it exists:** a second pass on code that already exists. Read first, propose diff, apply with consent.

### Flow

**1. Read the current file**

```bash
test -f <path> && cat <path>
```

**2. Identify what is going to change**

Ask:

```json
{
  "questions": [
    {
      "question": "O que precisa mudar?",
      "header": "Mudança",
      "options": [
        { "label": "Hierarquia visual", "description": "CTA, ordem, prominência" },
        {
          "label": "Aplicar tokens corretos",
          "description": "Trocar hex hardcoded por tokens do DS"
        },
        { "label": "Adicionar estado", "description": "Falta loading/empty/error" },
        { "label": "Outro", "description": "Descreve em texto livre" }
      ],
      "multiSelect": true
    }
  ]
}
```

**3. Show the diff before applying**

Use the Edit tool with specific `old_string`/`new_string`. DO NOT overwrite the whole file — only the blocks that change.

**4. Short echo after applying**

> "Atualizei <surface>: <resumo de 1 linha do que mudou>. Loading/empty/error já estavam — não toquei."

**5. Update session.yaml**

```yaml
tarsila:
  surfaces:
    - name: <surface>
      file: <path>
      status: iterated # changed from "built" to "iterated"
      last_iteration: <ISO date>
      iteration_reason: <short summary>
```

One sharp caution for iteration: touching `tokens.md`/`components.md` "in passing" during a surface iteration is a separate decision — record it in `.brisar/tarsila/notes.md` and leave the DS files alone.

---

**Mental recap before closing any mode:**

- Always update `session.yaml` `tarsila:` section.
- If there were custom or missing_tokens, write `.brisar/tarsila/notes.md`.
- End at the Step 3 gate of `phase-develop.md` (Deliver / another surface / stop) — suggest, never invoke.
