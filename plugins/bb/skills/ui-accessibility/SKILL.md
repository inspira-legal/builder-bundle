---
name: ui-accessibility
description: Analisa interfaces web para conformidade WCAG AA. Valida contraste de cores, navegação por teclado, compatibilidade com leitores de tela e gera relatório de acessibilidade priorizado por impacto. Use quando o usuário disser "auditoria de acessibilidade", "checa acessibilidade", "WCAG", "a11y", "contraste", "leitor de tela", ou quando a fase Deliver do /bb:brisar sugerir profundidade.
license: MIT
metadata:
  author: rafael (skill original da loja inspira-skills)
  version: 2.0.0
---

# UI Accessibility Auditor

You audit web interfaces for WCAG AA compliance. Point it at a folder, a set of
files, or a running page; it walks the checklist below and produces a
prioritized report. All user-facing output is PT-BR.

Scope split with `/bb:review`: its `a11y` front covers what a diff can prove from
source alone, scoped to the changed elements. This skill is the whole surface —
including what only a rendered page shows: computed contrast, real focus order,
live-region announcements. Same checklist, same priority matrix, so the two
reports read as one.

## Audit Checklist

- Color contrast (4.5:1 text, 3:1 UI elements)
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader compatibility
- Focus indicators visible
- Alt text on images
- Form labels associated
- Error messages connected via aria-describedby

## Priority Matrix

Every finding gets exactly one priority:

1. **Critical** — Blocks access entirely
2. **Major** — Significantly impacts experience
3. **Minor** — Inconvenient but workable
4. **Enhancement** — Better but not required

## Report

Group findings by priority (Critical first), each with: where (file/element),
what fails (the WCAG criterion), and a concrete fix. Close with a one-line
verdict: `WCAG AA: pass | fail | partial` plus the count per priority. Report
and stop — this skill has no handoff gate.
