# Color Meanings

Colors are not just hues — each Inspira color carries a specific emotional role. When choosing a color, the *intent* matters as much as the *scale position*. Use this file to decide **which color** to use; use the `primitives.css` section of `tokens/tokens-css.md` to decide **which shade**.

Hex values shown are the brand base for each scale (the "face" of the color). The full 50-950 range lives in the `primitives.css` section of `tokens/tokens-css.md`.

## Brand colors

### Cornflower Blue — `#6a97eb`

> **Calmos e tecnológicos** — welcoming + serious.

The primary face of Inspira. Technology presented with warmth. Signals trust without distance.

**Use for:**
- Primary brand moments (hero surfaces, key illustrations)
- Secondary interactive elements (supporting CTAs)
- Informational feedback (info banners, hints)
- Links and navigational brand touches

**Avoid:**
- Destructive or urgent contexts — Madder belongs there.

---

### Rich Black — `#070c21`

> **Sérios, seguros e elegantes** — extreme elegance, authority, sophistication.

The anchor. When you need gravity, weight, or authoritative presence.

**Use for:**
- Primary CTAs (the main "do this" button)
- Dark surfaces (inverse backgrounds, hero dark modes)
- Elegance moments (premium contexts, serious legal content)
- Brand text, strong borders

**Note:** Rich Black is deceptively blue — `950` is a near-black indigo (`#070c21`). The deeper tones in this scale are what carry Inspira's authority.

---

### Tropical Indigo — `#9970ff`

> **Criativos e futurista** — bold, unconventional for legal tech.

Signals modernity and daring. Rare in the legal market — that's the point.

**Use for:**
- AI / accent moments (gradient end points, innovation markers)
- Forward-looking features (when introducing new capability)
- Premium surfaces that need more personality than Cornflower Blue allows

**Avoid:**
- Overuse. Tropical Indigo earns its impact by scarcity. Using it on every screen dulls its signal.

---

### Keppel Green — `#26ba9d`

> **Inovadores e revitalizantes** — disruptive yet wellness-oriented, positive transformation.

Also serves as the **success semantic role**.

**Use for:**
- Success states (checkmarks, completion feedback, positive confirmations)
- Growth / positive metrics
- Moments of relief or progress (task done, document saved)

---

## Functional colors

### Madder — `#d62c3d`

**Urgency, danger, attention required.**

**Use for:**
- Error states and messages
- Destructive action buttons (after a confirmation — never as the default path)
- Critical alerts that interrupt the user

**Avoid:**
- Decorative use. Madder should always signal something requires attention.

---

### Saffron — `#ebc26a`

**Caution, non-critical alerts.**

**Use for:**
- Warning states (something worth knowing, not yet blocking)
- Limits and quota notifications
- Pending-state feedback

**Avoid:**
- Confusing Saffron with Madder. If the user must act right now, use Madder. If they should be aware, use Saffron.

---

### Cool Gray — `#8995ae`

**Calm, supportive neutral.**

The workhorse. Covers all neutral UI: backgrounds, text, borders, dividers, disabled states.

**Use for:**
- Body text, secondary text, disabled text
- Page and surface backgrounds
- Borders, dividers, inactive states

**Note:** Cool Gray is **blue-tinted**, not pure gray. This keeps the UI harmonious with Inspira's blue-forward palette — pure grays would feel cold and disconnected.

---

## Choosing between colors

| If the element is... | Use... |
|---|---|
| The primary CTA | **Rich Black** (`interactive-primary`) |
| A supporting action | **Cornflower Blue** (`interactive-secondary`) |
| An AI-powered or forward-looking feature | **Cornflower Blue → Tropical Indigo gradient** |
| A success confirmation | **Keppel Green** |
| An error or destructive action | **Madder** |
| A warning or caution | **Saffron** |
| Neutral UI (text, bg, border) | **Cool Gray** scale |
| A brand moment (hero, marketing) | **Rich Black** on **Cornflower Blue**, or a gradient |

## Gradients

Inspira has a defined gradient system (see `tokens/tokens.json` under `color.gradient`). Use gradients for:

- **Accent gradient** (Cornflower Blue → Tropical Indigo): AI / innovation moments, accent button variant.
- **Positive gradient** (Cornflower Blue → Keppel Green): transformation, wellness, positive milestones.
- **Primary gradient** (Cornflower Blue 400 → 800): default brand gradient, hero depth.
- **Spectrum gradients** (4-stop dramatic): flagship brand moments only.

Gradients should be **rare and intentional**. If a gradient appears on every screen, none of them feel special.
