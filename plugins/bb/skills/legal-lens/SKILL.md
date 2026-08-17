---
name: legal-lens
description: Passa uma lente jurídica sobre qualquer artefato — ideia, feature, fluxo ou documento — pra levantar implicações legais e regulatórias, gaps de compliance, risco e o que um advogado exigiria antes do lançamento. Default direito brasileiro (LGPD, CDC, Marco Civil…), sobrescrevível pra qualquer jurisdição. Grounded — cita a norma quando conhece, sinaliza incerteza em vez de inventar lei, e faz triagem pra revisão jurídica humana em vez de dar parecer. Reporta só o significativo, cada issue com mitigação; anexa `## Jurídico` à spec quando roda sobre uma. Use quando o usuário disser "revisão jurídica", "isso é legal?", "implicações legais", "checa compliance", "LGPD", "risco regulatório", ou "o que um advogado objetaria". NÃO use como substituto de um advogado qualificado.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.0.0
---

# Legal lens

A juridical pass over whatever you point it at — surfacing where it touches the
law, the risk that carries, and what a lawyer would require before it ships. It
**triages for human legal review; it is not legal advice** and does not replace
counsel. Default jurisdiction is **Brazilian law**; pass another to override.
All user-facing text — findings, the report, the `## Jurídico` section — is PT-BR.

## Input

Invoke on one of:

- a **slug** → resolve the spec per the spec-state contract (plugin-level
  `references/spec-state.md`: `.bb/<slug>/spec.md`) and review the framed
  work;
- a **file path** → review that document (a contract, policy, ToS, spec);
- a **free description** → review the idea as stated.

Resolve the jurisdiction first: use what the user passed, else default to Brazil
and say so. Then read the artifact in full before judging.

## What to look for

Scan where the artifact meets the law and, for each touchpoint, state the
implication and what it would take to be clear:

- **Data & privacy** — what personal data is collected, why, consent, retention,
  sharing (LGPD bases and rights, by default).
- **User-facing obligations** — claims made, disclosures owed, consumer
  protections, terms and consent flows (CDC, Marco Civil da Internet).
- **Third-party rights** — IP, licensing, scraping, content ownership.
- **Regulated activity** — anything sector-regulated (financial, health, legal
  practice) that needs a license, registration, or specific safeguard.
- **Liability & contract** — who's on the hook when it fails, and what clause or
  control limits that.

These are the common touchpoints, not a checklist to exhaust — follow the
artifact to where the real exposure is.

## Grounded — the load-bearing rule

A legal lens that fabricates law is worse than none. Cite the specific norm
(_lei_, _artigo_, regulation) when you know it; when you are unsure whether a
rule exists or applies, **say so explicitly and flag it for a qualified lawyer**
— never invent a statute, a precedent, or an article number. Confidence-tag
uncertain points. Where a fact would settle it (does this norm still apply, is
there a newer one), check before asserting.

## Editorial stance

Mirror a sharp design review: **significant issues only, no nitpicking.** Each
finding pairs the problem with a concrete mitigation — an issue with no suggested
fix is half a finding. Rank by severity:

- **blocker** — ships something unlawful or creates real, present liability;
  resolve before building or launching.
- **significant** — a genuine legal risk or compliance gap that needs a decision
  or a lawyer's review, though not necessarily blocking.
- **minor** — hygiene that lowers risk (wording, a disclosure, a best practice).

## Output

Always report the findings in the conversation, grouped by severity. **If the
artifact is a spec** (resolved via the spec-state contract), also append
or update a `## Jurídico` section so the spec carries the legal context
downstream; for an arbitrary document outside the spec folders, report only —
don't write into it. A spec that already carries a `## legal` section from before
the rename is read and updated under the name it has — and one line of the report
says the Portuguese name is `## Jurídico`, the same answer the lint's `W003` gives.

```
## Jurídico
jurisdiction: Brazil (default)
- [blocker] <issue> — <norm, cited or flagged as uncertain> — <mitigation>
- [significant] <issue> — <norm> — <mitigation>  [confidence: med]
- [minor] <issue> — <mitigation>
```

Close by naming what needs a real lawyer's sign-off before launch — the lens
narrows where counsel is needed; it doesn't stand in for it. No handoff gate:
report and stop.
