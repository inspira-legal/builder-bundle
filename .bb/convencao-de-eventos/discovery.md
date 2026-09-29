---
slug: convencao-de-eventos
created: 2026-09-10
phase: done
verdict: build-mvp
---

# the event convention outlives its app

## Problem

The convention that keeps Inspira's product data readable has no owner and no single
statement. Its written rule, the generator prompt inside the Tracking Automator (prefix
is the feature's first word cut at 12 letters, type abbreviations `ck` `ip` `id` `sc`
`er` `hv`, English element, snake_case), disagrees with its practice: the 190-event
catalog in the registry sheet and the typed event map in `inspira-legal/app`
(`apps/inspira/src/lib/events/types.ts`) use a team-chosen feature slug as prefix
(`ai_chat`, `trial_checkout`, `vault_folder`, `initial_tour`), the three error events
spell `erro` where the rule says `er`, and the 40 Tabular Review events spell `click`
and `impression` in full. The app that mediated between rule and practice is being
retired into a manual, and the data specialist who maintained both has left. Today the
person writing an event picks its name from memory, 21% of the catalog is already off
the grammar under a running generator, free text (the user's question, the AI's
response, the search term, the document name) enters payloads by design in code while
the cycle's own payload rule forbids it, and any tool that wants to hold a new event to
the convention (bb's instrumentation front) finds two contradictory sources to cite.
[confidence: high on the divergence facts, med on the size of the pain]

- who & impact: everyone who creates an event (the app's developers and every bb user),
  the readers of the data (the Health Metrics dashboards, Ray, CS) whose funnels and
  per-product filters depend on consistent prefixes like `ai_chat_%`, so an off-grammar
  event vanishes from the analysis silently, and the compliance side (LGPD, professional
  secrecy) for the free-text payloads. Sized: 40 of 190 events off the grammar; free
  text declared in at least four dictionary fields and in the whole feedback event
  family; the downstream breakage in dashboards, unsized. [confidence: med]
- appetite: one week for the manual v1, seeded from the extracted catalog and ratified
  as a pull request; the bb change stays outside this appetite, with its own spec
  (owner's pick: no preference stated, the recommendation stands)
- success signal: the share of new events, born after the manual, whose name matches
  the grammar and whose payload fields are all in the dictionary with no unplanned free
  text. [confidence: med]
- baseline: names, 150 of 190 on the grammar (79%); payload, unmeasured (the registry
  sheet as read on 2026-08-31, counted by pattern over the `Nome do Evento` column)
- target: 100% of the first 20 new events, within the first quarter after the manual
  lands (the operator's target, stated as such)

## Hypothesis

If the manual v1 (the reconciled grammar, a prefix registry, a payload policy with named
exceptions, a legacy allowlist and the metadata dictionary) lands in `inspira-legal/app`
as one machine-readable file ratified by pull request within one week, and bb becomes its
curator (proposing the events table from it at spec time, checking names and payloads
against it in the lint and the review, drafting the manual's own update when a spec needs
a new prefix or an exception), then 100% of the first 20 new events match the grammar and
carry no unplanned free text within the first quarter, because naming leaves individual
memory and becomes a checked contract at the moment the event is born, and the only
human decisions left are the exceptions, taken where the spec surfaces them. Ownership
is the team's as a whole (owner's call: no specialist, the agent as the focus), which is
why the ratification is a pull request review and not a session. Measured by the same
checker, run over the typed event map's additions. [confidence: med]

## Fit

Worth building. The demand is internal and evidenced from three sides: the cycle's
operator asked for it unprompted [evidence: high]; the Data Portal's own process document
admits in writing that event validation is skipped [evidence: high]; and the catalog shows
21% of events off the grammar under a running generator, with free text declared in the
app's typed event map, verified in source [evidence: high]. The downstream damage is the
weakest link: the dashboards filter product by name prefix and none of the portal's
listed patterns matches the 40 Tabular Review events, so they fall out of the product
distribution, but how much this has already distorted the readings is unmeasured
[evidence: med]. Team adherence beyond the operator is assumed, not measured [evidence:
none]: "everyone owns it" is the operator's stance, and it is the risk the pull-request
ratification has to cover. Without a stated approval rule (who ratifies, how many), a
convention everyone owns is a convention nobody approves.

- next_action: build-mvp
- confidence: med

The manual v1 is at once the MVP and the experiment: the pull request that carries it is
where the team either converges on one grammar and one payload policy or shows it cannot,
and the second outcome is worth knowing before bb enforces anything.

The bet is legal-sensitive: the payload policy touches free text of legal content (the
AI's response over legal material, the user's question, the search term) already flowing
into analytics events. `/bb:legal-lens` over this record is recommended before the build.

## Cuts

Cut:

- sanitizing the existing catalog (renaming off-grammar legacy events, separating the
  `Prioridade` column's status values from its priorities, deduplicating the dictionary),
  out-of-appetite and depends-on-other: renaming an event breaks the dashboards that read
  it, and the legacy allowlist buys the same effect for the checker. _revisit_
- moving the registry off the Google Sheet into the repository as the single source of
  truth (the inversion), depends-on-other and out-of-appetite: the manual v1 starts from
  an exported snapshot; the inversion is a later round once the file has proven itself.
  _revisit_
- deciding the fate of the feedback family's free-text fields (`response`, `question`,
  `content`) and of `search_term`, depends-on-other and low-confidence: a legal and
  product call, not a grammar one; the manual v1 records them as named exceptions under
  review, and `/bb:legal-lens` carries the question. _revisit_
- the bb change itself (the convention file's format, the checker, the spec proposing
  events from the file, the review citing it): not a cut, a dependency with its own spec,
  decoupled from the manual's values by design.
- an analytics page in the manifesto for greenfield products, depends-on-other,
  carried over from `metricas-no-ciclo`. _revisit_

Kept, in priority order:

1. the grammar reconciled with practice: `prefix_abbr_element` in English snake_case,
   the abbreviation from the closed list `ck` `ip` `id` `sc` `er` `hv`, the prefix a
   registered feature slug, plus the generator's granularity rule (8 to 12 events per
   feature, never one per form field) (ICE 8: high impact, low effort, high confidence)
2. the prefix registry: feature slug to its home (grupo, produto, feature), seeded from
   the 190 events (ICE 8: high impact, low effort, high confidence)
3. the payload policy: identifiers, enumerations, numbers and booleans by default; free
   text only as a named exception with its justification and retention, and the
   existing free-text fields listed as exceptions under review (ICE 6: high impact,
   medium effort, medium confidence)
4. the legacy allowlist: the current 190 names exempt from the grammar check, so the
   checker fires on what is born from here on and never on debt (ICE 7: medium impact,
   low effort, high confidence)
5. the metadata dictionary in machine-readable form (name, type, description, feature
   scope), from the sheet's 78 rows (ICE 6: medium impact, medium effort, high
   confidence)

The form for all five: one file in `inspira-legal/app`, prose for people and a structured
block for the checker, ratified by pull request under an approval rule the file itself
states.
