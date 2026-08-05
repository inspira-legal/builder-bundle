# Phase 0 — Calibration (1 question)

Before the lightning intake (Phase 1), brisar needs to understand WHO is building. A 1-question calibration determines:

1. **Depth of questions in Phase 1.** Executive → more questions in operational language. Senior dev → fewer questions, technical vocabulary OK.
2. **Default output path.** Executive → prototype + written handoff to dev. Senior dev → embed into real codebase. Junior → embed with step-by-step narration. Content → Framer.
3. **Conversation language.** Executive never receives "scaffold", "embed", "MCP" vocabulary. Senior receives it directly.

## When to run

Right after the Step 0 pre-flight (session, DS, tooling, detected product), before Phase 1.

**Skip if** session.yaml already has `profile.persona_id` filled (re-runs inherit the profile until the builder asks for a change).

## The question

Print a short intro before:

> **/bb:brisar** — antes de começar, me ajuda a calibrar pra te atender melhor.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Como você vai trabalhar nesse projeto?",
      "header": "Perfil",
      "options": [
        {
          "label": "Não tenho repertório técnico — quero protótipo",
          "description": "Não conheço git/npm. Quero algo clicável pra validar com stakeholders. Outro time pega o código depois."
        },
        {
          "label": "Sei mexer em código — vou direto",
          "description": "Tenho git, ambiente configurado, conheço o stack. Quero o mínimo de fricção."
        },
        {
          "label": "Tenho noção, mas vou precisar de instruções",
          "description": "Tenho git + ambiente, mas siga me explicando cada passo."
        },
        {
          "label": "Vou mexer em conteúdo/site (Framer)",
          "description": "Site institucional, copy, design — não código. Não importa se tenho git ou não."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

## Mapping

| Answer                                  | persona_id       | needs_instructions | can_clone_repo         | Default path                                           |
| --------------------------------------- | ---------------- | ------------------ | ---------------------- | ------------------------------------------------------ |
| Não tenho repertório técnico            | `executive`      | true               | false                  | `prototype-hosted`                                     |
| Sei mexer em código                     | `builder-senior` | false              | true                   | `embed` if product detected, else `scaffold`           |
| Tenho noção, vou precisar de instruções | `builder-junior` | true               | true                   | `embed` with narration, else `scaffold` with narration |
| Vou mexer em conteúdo/site              | `content`        | true               | false (doesn't matter) | `framer-handoff`                                       |

## Persistence

Writes to `.brisar/session.yaml`:

```yaml
profile:
  persona_id: executive | builder-senior | builder-junior | content
  needs_instructions: bool
  can_clone_repo: bool
  calibrated_at: <ISO>
```

## Implications for the rest of the flow

### `executive`

- **Phase 1 turns into 5-6 questions in operational language.** Doesn't ask "hosting" / "fidelity" / "Shaping appetite". Asks:
  - "Quem vai usar essa coisa? (advogado interno, cliente, gestor...)"
  - "Qual problema resolve? (1 frase)"
  - "Quando precisa estar pronto?"
  - "Você tem noção do visual (Inspira / Lexflow / outro / não sei)?"
  - "Você precisa que o time técnico continue depois? (sim/não)"
- **Phase 2 (gate) skipped.** Executive doesn't decide on shaping — brisar can SUGGEST /bb:discover as a next step, but doesn't block.
- **Phase 3 does NOT scaffold locally with `pnpm install`.** Goes to `prototype-hosted` (generates folder + HANDOFF-DEV.md, makes it explicit that dev picks up later).
- **Terminal handoff** always includes instruction to pass the prototype + handoff markdown to someone in engineering.
- **Banned vocabulary in messages:** scaffold, embed, npm, MCP, repo, branch, slug. Use: "pasta", "projeto", "instalar", "ambiente", "nome do projeto".
  - **This binds on every phase that prints, not only the intake.** The first diamond adds its own
    method names to the list — `divergência`/`divergir`, `reconciliação`, `piso` da pesquisa,
    `pocket`/`full` — and they get replaced by what they mean ("os caminhos que montei", "a pesquisa
    mínima"), never annotated. `references/brief.md` carries the mechanical self-check.

### `builder-senior`

- **Phase 1 reduces to 2 questions:** intent + (product OR brand, depending on whether Step 0.5 detected the product).
- **Skips hosting/appetite calibration** when product is detected (it's already known: embed into existing codebase).
- **Direct embed** if product known by the registry. If greenfield, minimal scaffold.
- **Maturity gate runs normally.** Senior can do a conscious override.
- **Vocabulary:** technical ok. No narration of each `cd <folder>`.

### `builder-junior`

- **Standard Phase 1 (3 questions).**
- **Each handoff becomes narrated instruction.** Instead of "run `pnpm install && pnpm dev`", prints:
  > 1. Abra o terminal nessa pasta: `cd <slug>`
  > 2. Instale dependências (vai demorar 1-2min): `pnpm install`
  > 3. Espere terminar — vai aparecer "done" no final.
  > 4. Inicie o dev server: `pnpm dev`
  > 5. Abra http://localhost:5173 no navegador.
- **Maturity gate runs normally.**
- **Vocabulary:** technical OK but always explains the term on first occurrence.

### `content`

- **Forces Framer path.** Regardless of detected product, if calibration = content, goes to `references/phase-framer-handoff.md`.
- **Step 0.4 should have already detected** whether the unframer MCP is present. If missing: falls into `fallback_path: framer-handoff-no-mcp` — generates markdown in cwd that the dev/designer picks up (and mention the builder can add the MCP to their Claude config for the canvas path next time).
- **Visual direction is GIVEN, not asked.** Content persona does not formulate design — brisar proposes based on product/brand.
- **Vocabulary:** marketing/design, not dev. Use: "página", "seção", "bloco", "publicar". Avoid: "deploy", "merge", "branch".

## Cross-validation with preflight

After the answer, brisar cross-references with what `preflight-tooling.md` detected silently:

| Answer           | Detected tooling     | What brisar does                                                                                                       |
| ---------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `builder-senior` | git missing          | "Você marcou que sabe mexer em código mas git não tá instalado aqui. Quer que eu instale, ou prefere outro caminho?"   |
| `builder-senior` | gh without auth      | "Repos da Inspira são privados — você precisa de `gh auth login`. Faço junto?"                                         |
| `content`        | unframer MCP missing | Notes it silently; the Framer phase uses the markdown fallback and tells the builder how to add the MCP for next time. |
| `executive`      | (any state)          | Doesn't check anything git/MCP — path doesn't require it.                                                              |

## Fallback

If builder doesn't respond clearly OR free response is ambiguous:

1. Temporary default to `builder-junior` (more robust path for uncertainty).
2. Asks ONCE again, simpler:
   > "Pra calibrar: você vai mexer no código direto, ou só em conteúdo/protótipo?"
3. If still uncertain: persists as `builder-junior` and continues. Builder can ask to recalibrate at any time.

One sharp caution: **never guess the persona from the initial prompt** — an executive may write "preciso de uma plataforma X" exactly like a senior. Always run the calibration (ONE question; a second one turns it into a form).
