# Inspira — Brand Package

This folder is the canonical brand definition for **Inspira**, a legal tech platform positioned as the reference brand for AI in the Brazilian legal market. It is the single source of truth for how Inspira looks, sounds, and behaves.

Feed this folder to any AI design tool, hand it to any new team member, or use it as the input for generating on-brand work. Everything needed to produce authentic Inspira output lives here.

## What Inspira is

A legal tech platform. "Traditional discourse with focus on the future." The intersection of **Direito** and innovation — authoritative but never rigid, modern but never flippant.

Three brand outcomes guide every decision:
- **Consistência** — recognizable across every touchpoint
- **Autoridade** — the reference in legal innovation
- **Reconhecimento** — product value that compounds

## How to read this folder

| File | What it tells you |
|---|---|
| `principles.md` | How Inspira behaves. The 5 Brisa principles in priority order. |
| `tokens/tokens.json` | Source of truth for colors, spacing, radius, typography, motion. W3C Design Token Format. |
| `tokens/tokens-css.md` | The four generated CSS token files, inline (`primitives.css` palettes, `semantic.css` roles, `dimensions.css` spacing/radius, `utilities.css` font/motion/opacity/z-index). |
| `voice/pillars.md` | How Inspira sounds. Three tone pillars. |
| `voice/grammar.md` | Copy rules: gender, register, tense, inclusive language. |
| `voice/examples.md` | Do/don't copy examples. |
| `visual/color-meanings.md` | The emotional intent behind each color — what it signals beyond hue. |
| `visual/typography.md` | Poppins-only. Size roles and when to use each. |
| `visual/logos/usage.md` | Logo usage rules + SVG variants inline. |

## Quick facts

- **Language:** Portuguese (Brazilian). All copy is pt-BR.
- **Gender:** Inspira is feminine — "a ferramenta," "somos a Inspira."
- **Primary font:** Poppins. Nothing else.
- **Primary color:** Cornflower Blue (`#6a97eb`) — the welcoming face.
- **Authority color:** Rich Black (`#070c21`) — the anchor for CTAs and elegance.
- **Success color:** Keppel Green (`#26ba9d`).

## Architecture note

Tokens are organized in **two layers**:
1. **Brand primitives** — Inspira-specific names (cornflower-blue, rich-black, cool-gray). What the color *is*.
2. **Semantic aliases** — Abstract roles (bg-primary, text-inverse, interactive-primary). What the color *does*.

Components reference only the semantic layer. This keeps the system ready for sub-brands: future products override primitives, semantics stay the same, all components adapt automatically.
