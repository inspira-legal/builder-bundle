# Phase 2 — Maturity gate

This phase only does one thing: decide whether it's worth running `/bb:discover` before going further. Costs one turn (or zero, if it doesn't fire). The target: prevent the builder from spending 6 weeks building the wrong thing because they skipped the framing.

**Not to be confused with the Research phase that follows it.** Different questions, and both matter:

- `/bb:discover` frames **the problem** — who hurts, how, is it worth solving, what do we cut.
- the Research phase maps **the solution space** — market, design system, what the product has.

The research does not replace the framing; it is what gets **tested against** it later (the brief's
reconciliation). Skipping the gate means the research runs with no hypothesis to check itself
against — which is exactly why the gate exists for production-shaped work.

## When the gate fires

```python
gate_fires = (
    artifact.fidelity == "production"
    or intent.scale_signal in {"will-scale", "commitment"}
)
```

**Does not fire** when the intent is clearly exploratory (`fidelity` ∈ low-fi/mid-fi/hi-fi AND scale_signal == exploration). For those cases, scaffold goes straight through.

## When the gate fires — the offer

Print diagnosis in plain text (informative, not interactive):

> **Heads up.** Você marcou [artefato] com [scale_signal]. Antes de scaffoldar, vale rodar `/bb:discover` (~10 minutos) para enquadrar: problema (com quem dói, como dói), fit, hipótese e apetite. O custo de pular essa etapa em produto-real é alto — descobre-se a falha de fundamentação só depois que código foi escrito.
>
> Se quiser pular, registro o override no session.yaml e sigo direto. Se quiser maturar, gravo bootstrap e você roda `/bb:discover` agora — quando voltar para `/bb:brisar`, ele continua da pesquisa com o enquadramento incorporado.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Maturar problema antes de scaffoldar?",
      "header": "Gate",
      "options": [
        {
          "label": "Sim — rodar /bb:discover primeiro",
          "description": "Gravo bootstrap; você roda /bb:discover, depois volta pro /bb:brisar e a pesquisa continua com o enquadramento pronto"
        },
        {
          "label": "Não — sigo direto",
          "description": "Registro override + razão, scaffolda agora; risco fica documentado"
        },
        {
          "label": "Não tenho certeza",
          "description": "Me dá mais contexto sobre o que /bb:discover faria que o brisar sozinho não faz"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

## Processing

### Yes — run /bb:discover first

Update `.brisar/session.yaml` to:

```yaml
status: bootstrapped-to-discover
gate:
  fired: true
  resolution: bootstrap-to-discover
```

(Keeps `intent`, `brand`, `artifact`, `surfaces_provisional` intact.)

Print to the user, seeding discover with the intake already collected:

> ✓ Bootstrap salvo em `.brisar/session.yaml`. Roda `/bb:discover <sua ideia em 1 frase>` agora — ele enquadra problema, fit e hipótese e grava o brief em `.bb/tasks/<slug>/spec.md`. Quando terminar, chama `/bb:brisar` de novo na mesma pasta — eu detecto o bootstrap, leio o brief e prossigo da pesquisa (o enquadramento é justamente o que a pesquisa vai testar).

**STOP.** Do not scaffold and do not invoke /bb:discover — the builder crosses on purpose. End the turn here. (On return, Step 0.1 of SKILL.md handles the resume: locate the brief, record `gate.discover_brief`, resume at the Research phase.)

### No — going straight

Ask ONE extra question to record the reason:

```json
{
  "questions": [
    {
      "question": "Razão do override (registro no session.yaml para você revisar depois):",
      "header": "Override",
      "options": [
        {
          "label": "Já fiz shaping antes em outro contexto",
          "description": "Trio existe na cabeça/Notion/Linear, não preciso re-fazer aqui"
        },
        {
          "label": "É baixo risco — tipo 'vai escalar' mas é experimento",
          "description": "Marquei 'vai escalar' por intuição, mas na real é exploratório"
        },
        {
          "label": "Tenho prazo apertado, vou shapear no caminho",
          "description": "Aceito o risco; rodo /bb:discover mais tarde se virar dor"
        },
        { "label": "Outro motivo", "description": "Texto livre" }
      ],
      "multiSelect": false
    }
  ]
}
```

Record in session.yaml:

```yaml
gate:
  fired: true
  resolution: override
  override_reason: "<label escolhido ou texto livre>"
```

Continue to the Research phase.

### Not sure

Print informative response (plain text):

> `/bb:discover` enquadra o problema antes do código: com quem dói e como dói, se vale resolver (fit), a hipótese (Se X, esperamos Y porque Z), a métrica de sucesso e o apetite (quanto vale investir, em estilo Shaping). Demora ~10 minutos e grava um brief em `.bb/tasks/`. Eu, brisar, capturo só os 3 dados que viram pasta de projeto. Sem o enquadramento, o scaffold sai pronto mas você não sabe o que conta como sucesso.
>
> Em produto-real ou commitment isso costuma valer. Em exploração descartável é overkill.

Repeat the original question (yes / no / additional free text). No infinite loop — max 2 times.

## When the gate does NOT fire

(`fidelity` ∈ low-fi/mid-fi/hi-fi AND scale_signal == exploration)

Update `.brisar/session.yaml`:

```yaml
gate:
  fired: false
  resolution: not-applicable
current_phase: phase-3
```

Print short echo: _"Apetite exploratório, scale=exploration — pulando o gate. Indo pra pesquisa."_ Continue to the Research phase.

## State at the end

Regardless of the path:

```yaml
gate:
  fired: true | false
  resolution: bootstrap-to-discover | override | not-applicable
  override_reason: <string or null>
  discover_brief: <path or null> # filled on the bootstrap return (Step 0.1)
current_phase: phase-3 # (unless it bootstrapped, which stops here)
```
