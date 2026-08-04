# Medium question — where the exploration happens

Loaded after the Diverge phase, before Phase 3 (scaffold) and Develop. One question, and it
decides the shape of everything downstream: whether a scaffold runs at all, what Develop
produces, and what Deliver has to be able to read.

## Why it is a question and not an assumption

The first diamond is medium-agnostic on purpose. Research, brief and directions serve a Figma
file, a Paper canvas, a React app and an HTML preview equally — **the brief does not care where
the pixels land.** What changes is the second diamond.

Assuming the medium gets it wrong in both directions: it scaffolds a Vite project for someone
who wanted to sketch on a canvas, and it opens a canvas for someone who was going to ship code
today. The cost of asking is one turn.

**Detect, then ask.** The preflight already knows which canvas tools are reachable
(`preflight.mcps`). Offer what exists, name what does not, and never dead-end — code and Claude
design need no MCP, so there is always a path.

## Step 0 — Build the option list

Read `preflight.mcps` and `preflight.product`:

| Option            | Offered when  | Needs                                      |
| ----------------- | ------------- | ------------------------------------------ |
| **Código**        | always        | the repo (embed) or a scaffold             |
| **Claude design** | always        | nothing — rendered preview, no local setup |
| **Paper**         | `mcps.paper`  | Paper MCP                                  |
| **Figma**         | `mcps.figma`  | Figma MCP                                  |
| **Pencil**        | `mcps.pencil` | Pencil MCP                                 |

Cap the list at four options (the question tool's limit). When more than four qualify, keep
**Código** and **Claude design** and the canvas tools in registry order, and mention the
remainder in the intro line rather than dropping them silently.

If `preflight.mcps.scope_read` is `global-only`, the check was partial: a project-scoped server
may exist and be invisible. Say the check was partial instead of asserting a clean absence.

## Step 1 — Ask

Print one intro line naming the chosen direction and what is missing, if anything:

> **Direção escolhida: <nome>.** Onde você quer explorar? _(Não detectei o MCP do Figma aqui —
> se quiser esse caminho, é só configurar e eu ofereço na próxima.)_

```json
{
  "questions": [
    {
      "question": "Onde você quer explorar a direção <nome>?",
      "header": "Meio",
      "options": [
        {
          "label": "Paper",
          "description": "Desenho as pranchas no Paper via MCP. Melhor pra comparar composições lado a lado e iterar rápido antes de existir código."
        },
        {
          "label": "Código",
          "description": "Construo a surface no projeto (React + Tailwind, ou HTML se for protótipo). Melhor quando o destino já é produção."
        },
        {
          "label": "Claude design",
          "description": "Monto um preview renderizado aqui, sem setup local e sem MCP. Melhor pra ver de pé rápido e mostrar pra alguém."
        },
        {
          "label": "Figma",
          "description": "Desenho no Figma via MCP. Melhor quando a revisão é assíncrona com stakeholders ou o arquivo tem a biblioteca do time."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

Order the options by fit, not alphabetically, and put the best fit first. Signals: a detected
product with a real repo leans **Código**; an unresolved visual direction with several
compositions to compare leans a **canvas**; a builder with no local toolchain leans **Claude
design**.

Do **not** add an "Outro" option — the tool provides free text.

## Step 2 — What each medium changes downstream

| Medium            | Phase 3 (scaffold)                                         | Develop builds                           | Deliver reads via                           |
| ----------------- | ---------------------------------------------------------- | ---------------------------------------- | ------------------------------------------- |
| **Código**        | yes — embed into the repo, or Vite scaffold for greenfield | `.tsx` / `.html` in the project          | the files on disk                           |
| **Claude design** | no                                                         | a rendered preview (self-contained HTML) | the preview file on disk                    |
| **Paper**         | no                                                         | artboards in a Paper file                | the Paper MCP (structure + computed values) |
| **Figma**         | no                                                         | frames in a Figma file                   | the Figma MCP (design context + variables)  |
| **Pencil**        | no                                                         | nodes in a `.pen` file                   | the Pencil MCP                              |

Three consequences worth stating explicitly:

1. **A canvas medium skips the scaffold.** No `<slug>/` folder, no `package.json`, no
   `design-context/` generated from Phase 3. The design system still has to be _read_ — that
   already happened in the research (Front B), and the token values from there are what the
   canvas gets. Record `scaffold: skipped` with the reason so a later re-entry does not think
   the scaffold failed.
2. **Deliver must be able to open what Develop produced.** This is not optional: a review that
   cannot read the artifact is not a review. The reader per medium is in the table above, and
   `references/deliver-modes.md` implements it.
3. **Values come from the source, never from a screenshot.** On a canvas medium, spacing, tokens
   and copy are read through the MCP. A screenshot is for looking at, not for measuring — and
   handoff numbers taken off an image are wrong in a way nobody catches until implementation.

## Step 3 — The medium is not one-way

The most common real path is **canvas first, code after**: explore compositions where iteration
is cheap, converge, then implement. Support it as a first-class flow rather than a restart.

- **Record the medium per round**, not per session. `mediums: [paper, código]` is a normal
  history, not a conflict.
- When the exploration converges on a canvas and the work is going to production, the Deliver
  gate offers **"construir em código a partir daqui"** — carrying the brief, the chosen
  direction and the design decisions forward. The canvas becomes the design source of truth and
  the handoff names it as such, including which values the implementer must read from the MCP.
- When switching medium, **do not re-run the first diamond.** Research, brief and directions are
  already settled; changing medium is a build decision, not a reopening. Say that out loud so
  nobody expects a fresh interview.

## Step 4 — Persistence

```yaml
medium:
  chosen: código | claude-design | paper | figma | pencil
  offered: [<options presented>]
  unavailable: [<medium>: <missing mcp>]
  reason: <one line — why this one fits>
  history: [<medium per round, in order>]
  scaffold: required | skipped
  deliver_reader: files | preview | paper-mcp | figma-mcp | pencil-mcp
```

No gate here — the medium question is a step inside the flow, not a stopping point. Continue
straight to Phase 3 when `scaffold: required`, or to Develop when it is skipped.

## Persona — expected behaviors

1. **Offer only what exists, and name what doesn't.** A silently shortened list reads as the tool
   deciding for the builder.
2. **Never dead-end.** Code and Claude design always work. If every canvas MCP is missing, that is
   not a blocker and should not be presented as one.
3. **Recommend by fit, and say why in one line.** "Paper porque há três composições pra comparar
   e nenhuma decidida" is useful; a bare recommendation is not.
4. **The brief does not change with the medium.** If you find yourself re-running the research
   because the medium changed, stop — that is the first diamond and it is done.
5. **Read values from the source.** Never measure a canvas from a screenshot.
6. **brisar never edits the MCP config.** Say what would enable the path and move on.

One sharp caution: **do not let the medium decide the design.** A canvas tempts toward polish
before structure, and code tempts toward what is easy to implement over what the direction asked
for. The chosen direction is the contract in every medium — the medium changes how it is
expressed, never what it is.

## Cooperation contract

| Artifact                                                       | Produced by                       | Consumed by                                            |
| -------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------ |
| `preflight.mcps`                                               | Step 0.4 (`preflight-tooling.md`) | Step 0 here — the option list                          |
| `.brisar/session.yaml` (`diverge.directions[].status: chosen`) | Diverge                           | Step 1 — what is being built                           |
| `.brisar/session.yaml` (`medium:` section)                     | this step                         | Phase 3, Develop, Deliver, re-entry                    |
| Token values read from source                                  | Research (Front B)                | Develop on canvas mediums (no `design-context/` there) |
