# Brisa Design Principles

Brisa is the design system that governs every Inspira surface. These five principles are ranked. **When two principles conflict, the higher-ranked one wins** — always.

Before producing any UI, scan against this list in order. If your design breaks a principle, fix it at that principle before worrying about the ones below.

---

## 1. Dar Pé — Give footing

Accessibility and predictability first. The user must always feel where they are, what they can do, and what will happen next.

- Keyboard navigation works everywhere. Tab order is logical.
- Screen readers get meaningful labels. Icon-only buttons have `aria-label`.
- Focus states are always visible. Focus never disappears.
- Color contrast meets WCAG AA minimum (AAA where practical).
- Loading and error states have clear recovery paths.
- No surprises. The interface behaves the same way every time.

## 2. Clareza — Clarity

Every element has one direct purpose. Zero ambiguity.

- Error messages explain the problem AND the next step.
- Labels say exactly what will happen: "Apagar conversa" not "OK."
- No generic errors ("Algo deu errado"). Name the problem.
- One primary action per screen. Secondary actions are visually secondary.
- Empty states teach the next action, never leave the user stuck.
- If a user has to ask "what does this do?", the design has failed.

## 3. Ritmo e Fluidez — Rhythm and flow

Motion serves understanding, never decoration. Transitions answer the question: "what changed, and where did it come from?"

- Interactions: 100–300ms. Never exceed 500ms.
- `ease-out` for entrances (fast start, gentle land).
- `ease-in` for exits (gentle start, decisive leave).
- `ease-in-out` for state changes.
- Stagger sibling animations by 30ms for sense of sequence.
- Motion must answer: "what does this help the user understand?" If it doesn't, remove it.

## 4. Segurança e Transparência — Safety and transparency

Destructive actions require confirmation. Confirmations name what's being destroyed. Compliance is visible.

- "Apagar 3 documentos?" not "Tem certeza?"
- Sensitive data (PII, passwords, regulated fields) gets visual distinction.
- Actions that can't be undone say so.
- Data handling is made explicit where relevant.
- Trust is engineered, not assumed.

## 5. Leveza — Lightness

Visual breathing. Generous spacing. Show essential first; complexity on demand.

- Every element earns its place. Remove before adding.
- Whitespace is a feature, not empty space.
- Progressive disclosure: the 80% case is simple, the 20% case is reachable.
- Rounder corners feel lighter. Use the radius scale to signal weight.
- When in doubt, remove.

---

## Applying the scan

Before shipping any UI:

1. **Dar Pé:** Can I operate this with only a keyboard? Does every interactive element have an accessible name?
2. **Clareza:** If I show this to someone who has never used Inspira, will they know what to do?
3. **Ritmo:** Do transitions help me understand what changed? Is anything over 500ms?
4. **Segurança:** Can any destructive action be triggered without an intentional confirmation?
5. **Leveza:** What can I remove and still ship the same value?

If any answer is "no," fix it before moving on.
