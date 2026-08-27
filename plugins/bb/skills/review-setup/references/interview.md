# Interview: the maintainer validates every rule

Every interaction goes through `AskUserQuestion`: rationale and the "Other"
convention in the plugin-root `references/handoff-gate.md`.

Processing each answer, always in this order:

1. Read the selected option from the tool result.
2. Confirm it in one printed line, `"Rule {ID}: you picked [{option}]."`, so the
   user sees it registered.
3. Apply the decision **before** presenting the next item. "Confirm as Sugestão"
   means the rule enters the guide as Sugestão; "Ignore" means it's gone.
4. Free-text via "Other" gets interpreted and applied (level change,
   rewording, merge, skip).

The two levels are the plugin-root `references/finding-levels.md`'s, and the interview
offers those two. A maintainer who asks in free text for a rung between them gets the
concrete-cost gate that file describes, applied to the Sugestão.

## Setup mode

### Confirmed rules: one batch

Print the confirmed rules as an informational table (ID, title, level,
category), context only, no questions in the text. Then immediately ask:

```
question: "You reviewed the confirmed rules above. Do I go with all of them, or adjust some?"
header: "Confirmed"
options:
  - "Confirm all": they enter the guide as listed.
  - "Adjust some": I want to change a level, remove one or reword one.
```

"Adjust some" (or free text) → interpret and apply; ask a follow-up
`AskUserQuestion` if the request is vague.

### Candidate rules: one at a time, never grouped

For EACH candidate: print the ID, the title, what was observed in the repo (with
paths), the proposed inference, the evidence and the suggested level, then
immediately ask:

```
question: "Rule {ID}, {Title} (suggested: {LEVEL}). Confirm, adjust or ignore?"
header: "{ID}"
options:
  - "Confirm {LEVEL}": accept it at the suggested level.
  - "Confirm as Bloqueante": mandatory, a change breaking it does not ship.
  - "Confirm as Sugestão": worth saying, and a judgment call.
  - "Ignore": not a valid rule for this repo.
```

The first option and one of the next two say the same thing, so drop whichever
duplicates the suggestion and offer three.

Only after confirming the answer does the next candidate appear.

## Update mode (incremental: only what changed)

Never re-ask about rules that didn't change. Three question shapes:

- **New pattern detected:** "New pattern detected: {description}. Create a rule?", options: "Yes, Bloqueante" / "Yes, Sugestão" / "No, ignore".
- **Drifted rule:** "Rule {ID} looks out of date: {evidence}. What do we do?",
  options: "Update it with the new pattern" / "Remove it from the guide" / "Keep
  it as it is".
- **Obsolete pattern:** "Rule {ID}'s pattern no longer appears in the codebase.
  Remove it?", options: "Remove" / "Keep it (it may come back)".

## Priorities

Validation order when time/attention is short: functional delivery > repo
patterns > best practices > security-hardening nits. Each question's
informational text must carry the repo evidence. The maintainer decides on
facts, not on trust.
