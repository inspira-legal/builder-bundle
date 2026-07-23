# Typography

## The rule

**Poppins only.** One family, used with discipline, across every Inspira surface.

No serif companions. No display fonts. No exceptions in v1.

(Instrument Serif is mentioned in the brand guidelines as a potential future accent font. It is **not in scope** for this version. Ignore it until explicitly added.)

## Weights

Only three weights are used:

| Weight       | CSS   | Use for                                                   |
| ------------ | ----- | --------------------------------------------------------- |
| **Regular**  | `400` | Body text, field values, descriptions, most UI copy       |
| **Medium**   | `500` | Labels, button text, active nav items, subtle emphasis    |
| **Semibold** | `600` | Titles, headings, section headers, CTAs on heavy surfaces |

Never use Bold (700+). Never use Light (300 or below). The palette above covers every legitimate case.

## Size scale

Defined in `tokens/tokens.json` under `typography`. Each size has a semantic role — use the role, not the raw size.

### Display scale (for moments, not paragraphs)

| Token         | Size | Line height | Letter spacing | When to use                                     |
| ------------- | ---- | ----------- | -------------- | ----------------------------------------------- |
| `title`       | 32px | 150%        | -2%            | Page-level hero titles, major marketing moments |
| `title-sm`    | 24px | 160%        | -1%            | Section titles, modal headings                  |
| `subtitle`    | 20px | 160%        | 0%             | Subheadings inside long-form content            |
| `subtitle-sm` | 18px | 160%        | 0%             | Secondary subheadings, card titles              |

Tight letter-spacing (`-2%`, `-1%`) is intentional at larger sizes — it keeps display text feeling crafted, not default.

### Body scale (for reading)

| Token        | Size | Line height | When to use                                                 |
| ------------ | ---- | ----------- | ----------------------------------------------------------- |
| `body-lg`    | 16px | 160%        | Long-form reading content, primary article body             |
| `body`       | 14px | 160%        | **Default body text.** Product UI, descriptions, most copy. |
| `body-sm`    | 13px | 150%        | Dense tables, metadata, secondary descriptions              |
| `caption`    | 12px | 150%        | Timestamps, labels under icons, tertiary metadata           |
| `caption-sm` | 11px | 150%        | Legal fine print, badges, very dense contexts               |

### Action scale (for interactive elements)

| Token       | Size | Line height | Letter spacing | When to use                                    |
| ----------- | ---- | ----------- | -------------- | ---------------------------------------------- |
| `button-lg` | 14px | 100%        | 0.1%           | Large buttons (primary CTAs at the page level) |
| `button`    | 13px | 100%        | 0.1%           | **Default button size.** Most UI buttons.      |
| `button-sm` | 12px | 100%        | 0.1%           | Small buttons (dense toolbars, inline actions) |
| `button-xs` | 11px | 150%        | 0px            | Extra small buttons (chip-level, filters)      |

Button text uses **tight line-height (100%)** because buttons are single-line by rule. Use slight positive letter-spacing (`0.1%`) to preserve legibility at small sizes.

### Link scale

| Token     | Size | Line height | When to use                                     |
| --------- | ---- | ----------- | ----------------------------------------------- |
| `link`    | 13px | 150%        | Inline links inside body copy, navigation links |
| `link-sm` | 11px | 150%        | Footer links, tertiary navigation               |

## Hierarchy in practice

A typical Inspira screen uses **no more than 3 type roles**:

1. **One display size** (e.g., `title-sm` for the page heading)
2. **One body size** (usually `body` at 14px)
3. **One caption or metadata size** (e.g., `caption` for timestamps or labels)

Adding a fourth role should trigger the question: "Is this a hierarchy problem, or am I stacking too much on one screen?"

## Pairing with weight

| Role                                     | Weight         | Notes                                                        |
| ---------------------------------------- | -------------- | ------------------------------------------------------------ |
| Titles (`title`, `title-sm`, `subtitle`) | Semibold (600) | Weight gives the crafted feel Poppins needs at display sizes |
| Body text                                | Regular (400)  | Always. Medium body feels aggressive.                        |
| Labels (form fields, table headers)      | Medium (500)   | Distinguishes them from body without shouting                |
| Buttons                                  | Medium (500)   | Never Semibold — keeps CTAs from feeling heavy               |
| Captions / metadata                      | Regular (400)  | Even small text stays light                                  |

## What to avoid

- **Italic Poppins.** Inspira doesn't use italics for emphasis. Use semibold or color instead.
- **All caps.** No uppercase headings. No `text-transform: uppercase`.
- **Letter-spacing beyond the scale.** The scale defines the only valid tracking values.
- **Body copy below 13px.** Caption sizes (12, 11) are for metadata only, never running prose.
- **Line-heights under 100%.** Buttons at 100% are the minimum; everything else needs breathing room.

## Accessibility notes

- Body text minimum: **13px**. Anything smaller is metadata, never primary content.
- Line-height on body: **always ≥150%.** Reading at 160% is the default target.
- Color contrast: body text must pass **WCAG AA (4.5:1)**. See the `semantic.css` section of `tokens/tokens-css.md` for `text-primary`, `text-secondary`, `text-tertiary` — these are pre-validated pairings with their intended backgrounds.
