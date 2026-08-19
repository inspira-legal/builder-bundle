# Phase 2: maturity gate

This phase only does one thing: decide whether it's worth running `/bb:discover` before going further. Costs one turn (or zero, if it doesn't fire). The target: prevent the builder from spending 6 weeks building the wrong thing because they skipped the framing.

**Not to be confused with the Research phase that follows it.** Different questions, and both matter:

- `/bb:discover` frames **the problem**: who hurts, how, is it worth solving, what do we cut.
- the Research phase maps **the solution space**: market, design system, what the product has.

The research does not replace the framing; it is what gets **tested against** it later (the brief's
reconciliation). Skipping the gate means the research runs with no hypothesis to check itself
against, which is exactly why the gate exists for production-shaped work.

## When the gate fires

```python
gate_fires = (
    artifact.fidelity == "production"
    or intent.scale_signal in {"will-scale", "commitment"}
)
```

**Does not fire** when the intent is clearly exploratory (`fidelity` ∈ low-fi/mid-fi/hi-fi AND scale_signal == exploration). For those cases, scaffold goes straight through.

## When the gate fires: the offer

Print diagnosis in plain text (informative, not interactive):

> **Heads up.** You marked [artifact] as [scale_signal]. Before scaffolding, it is worth running `/bb:discover` (~10 minutes) to frame it: the problem (who it hurts, how it hurts), the fit, the hypothesis and the appetite. Skipping this step on a real product is expensive: the grounding failure only shows up after the code is written.
>
> If you want to skip it, I record the override in session.yaml and go straight through. If you want to frame it first, I save the bootstrap and you run `/bb:discover` now. When you come back to `/bb:brisar`, it continues from the research with the framing folded in.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Frame the problem before scaffolding?",
      "header": "Gate",
      "options": [
        {
          "label": "Yes, run /bb:discover first",
          "description": "I save the bootstrap; you run /bb:discover, then come back to /bb:brisar and the research continues with the framing ready"
        },
        {
          "label": "No, go straight through",
          "description": "I record the override + the reason and scaffold now; the risk stays documented"
        },
        {
          "label": "Not sure",
          "description": "Tell me more about what /bb:discover would do that brisar alone does not"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

## Processing

### Yes: run /bb:discover first

Update `.brisar/session.yaml` to:

```yaml
status: bootstrapped-to-discover
gate:
  fired: true
  resolution: bootstrap-to-discover
```

(Keeps `intent`, `brand`, `artifact`, `surfaces_provisional` intact.)

Print to the user, seeding discover with the intake already collected:

> ✓ Bootstrap saved at `.brisar/session.yaml`. Run `/bb:discover <your idea in 1 sentence>` now. It frames the problem, the fit and the hypothesis, and writes the spec at `.bb/<slug>/spec.md`. When it finishes, call `/bb:brisar` again in the same folder. I detect the bootstrap, read the spec and carry on from the research (the framing is exactly what the research is going to test).

**STOP.** Do not scaffold and do not invoke /bb:discover: the builder crosses on purpose. End the turn here. (On return, Step 0.1 of SKILL.md handles the resume: locate the spec, record `gate.discover_brief`, resume at the Research phase.)

### No: going straight

Ask ONE extra question to record the reason:

```json
{
  "questions": [
    {
      "question": "Reason for the override (recorded in session.yaml for you to review later):",
      "header": "Override",
      "options": [
        {
          "label": "I already framed the problem elsewhere",
          "description": "The trio exists in my head, in Notion or in Linear, no need to redo it here"
        },
        {
          "label": "Low risk, marked 'will scale' but it is an experiment",
          "description": "I marked 'will scale' on instinct, but it is really exploratory"
        },
        {
          "label": "Tight deadline, I will frame it along the way",
          "description": "I accept the risk; I run /bb:discover later if it starts to hurt"
        },
        { "label": "Another reason", "description": "Free text" }
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
  override_reason: "<the chosen label, or the free text>"
```

Continue to the Research phase.

### Not sure

Print informative response (plain text):

> `/bb:discover` frames the problem before the code: who it hurts and how it hurts, whether it is worth solving (the fit), the hypothesis (If X, we expect Y because Z), the success metric and the appetite (how much it is worth investing, in Shaping style). It takes ~10 minutes and writes a spec at `.bb/`. I, brisar, capture only the 3 pieces of data that become a project folder. Without the framing, the scaffold comes out ready but you do not know what counts as success.
>
> On a real product or a commitment it usually pays off. On a throwaway exploration it is overkill.

Repeat the original question (yes / no / additional free text). No infinite loop, max 2 times.

## When the gate does NOT fire

(`fidelity` ∈ low-fi/mid-fi/hi-fi AND scale_signal == exploration)

Update `.brisar/session.yaml`:

```yaml
gate:
  fired: false
  resolution: not-applicable
current_phase: phase-3
```

Print short echo: _"Exploratory appetite, scale=exploration, skipping the gate. Going to the research."_ Continue to the Research phase.

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
