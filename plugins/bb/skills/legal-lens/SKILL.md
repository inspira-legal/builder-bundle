---
name: legal-lens
description: Pass a juridical lens over any artifact — an idea, feature, flow, or document — to surface legal and regulatory implications, compliance gaps, risk, and what a lawyer would require before it ships. Defaults to Brazilian law (LGPD, CDC, Marco Civil…), overridable to any jurisdiction. Grounded — cites the norm when it can, flags uncertainty instead of inventing statutes, and triages for human legal review rather than giving legal advice. Reports significant issues only, each paired with a fix; appends `## legal` to a shape brief when run against one. Use when the user says "legal review", "is this legal", "legal implications", "compliance check", "LGPD", "regulatory risk", or "what would a lawyer object to". Do NOT use as a substitute for a qualified lawyer.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Legal lens

A juridical pass over whatever you point it at — surfacing where it touches the
law, the risk that carries, and what a lawyer would require before it ships. It
**triages for human legal review; it is not legal advice** and does not replace
counsel. Default jurisdiction is **Brazilian law**; pass another to override.

## Input

Invoke on one of:

- a **slug** → reads `.ofc/tasks/<slug>/shape.md` and reviews the framed work;
- a **file path** → reviews that document (a contract, policy, ToS, spec);
- a **free description** → reviews the idea as stated.

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
artifact is a shape** (`.ofc/tasks/<slug>/shape.md`), also append or update a
`## legal` section so the brief carries the legal context downstream; for an
arbitrary document outside `.ofc/`, report only — don't write into it.

```
## legal
jurisdiction: Brazil (default)
- [blocker] <issue> — <norm, cited or flagged as uncertain> — <mitigation>
- [significant] <issue> — <norm> — <mitigation>  [confidence: med]
- [minor] <issue> — <mitigation>
```

Close by naming what needs a real lawyer's sign-off before launch — the lens
narrows where counsel is needed; it doesn't stand in for it.
