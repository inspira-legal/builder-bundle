# Tokens CSS — arquivos inline

Os quatro arquivos CSS de tokens da marca, inline neste markdown porque a Loja de Skills só aceita `.md/.yaml/.yml/.json/.txt`. **Fonte da verdade continua sendo `tokens.json`** (W3C Design Token Format) — estes CSS são gerados a partir dele.

Pra usar num projeto: escreva cada bloco abaixo como arquivo `.css` no projeto de destino (ex.: `src/brand/primitives.css`) e importe no `app.css`, na ordem em que aparecem aqui.

## primitives.css

```css
/* ==========================================================================
 * AUTO-GENERATED from tokens.json — DO NOT EDIT MANUALLY
 * Run: pnpm tokens:build
 * ========================================================================== */

@theme {
  /* — Color Primitives — */
  --color-white: #ffffff;
  --color-black: #000000;
  --color-cool-gray-50: #f4f7f9;
  --color-cool-gray-100: #ecf0f3;
  --color-cool-gray-200: #dce3e9;
  --color-cool-gray-300: #c6d1db;
  --color-cool-gray-400: #aebccb;
  --color-cool-gray-500: #98a7bc;
  --color-cool-gray-600: #8995ae;
  --color-cool-gray-700: #6f7a93;
  --color-cool-gray-800: #5b6478;
  --color-cool-gray-900: #4d5462;
  --color-cool-gray-950: #2d3139;
  --color-rich-black-50: #ebf5ff;
  --color-rich-black-100: #daedff;
  --color-rich-black-200: #bdddff;
  --color-rich-black-300: #94c4ff;
  --color-rich-black-400: #6aa0ff;
  --color-rich-black-500: #487bff;
  --color-rich-black-600: #2853ff;
  --color-rich-black-700: #1c40e6;
  --color-rich-black-800: #1a39b9;
  --color-rich-black-900: #1e3791;
  --color-rich-black-950: #070c21;
  --color-cornflower-blue-50: #f0f5fe;
  --color-cornflower-blue-100: #dee7fb;
  --color-cornflower-blue-200: #c5d7f8;
  --color-cornflower-blue-300: #9dbdf3;
  --color-cornflower-blue-400: #6a97eb;
  --color-cornflower-blue-500: #4c77e5;
  --color-cornflower-blue-600: #385ad8;
  --color-cornflower-blue-700: #2e47c7;
  --color-cornflower-blue-800: #2c3ba1;
  --color-cornflower-blue-900: #283680;
  --color-cornflower-blue-950: #1d234e;
  --color-tropical-indigo-50: #f5f2ff;
  --color-tropical-indigo-100: #ede8ff;
  --color-tropical-indigo-200: #ddd4ff;
  --color-tropical-indigo-300: #c5b2ff;
  --color-tropical-indigo-400: #9970ff;
  --color-tropical-indigo-500: #8e55fd;
  --color-tropical-indigo-600: #8132f5;
  --color-tropical-indigo-700: #7220e1;
  --color-tropical-indigo-800: #601abd;
  --color-tropical-indigo-900: #4f189a;
  --color-tropical-indigo-950: #300c69;
  --color-keppel-green-50: #f1fcf8;
  --color-keppel-green-100: #d0f7ec;
  --color-keppel-green-200: #a1eed8;
  --color-keppel-green-300: #6adec1;
  --color-keppel-green-400: #3cc5a8;
  --color-keppel-green-500: #26ba9d;
  --color-keppel-green-600: #198874;
  --color-keppel-green-700: #186d5f;
  --color-keppel-green-800: #18574e;
  --color-keppel-green-900: #184941;
  --color-keppel-green-950: #082b27;
  --color-madder-50: #fef2f3;
  --color-madder-100: #fde3e6;
  --color-madder-200: #fcccd1;
  --color-madder-300: #f9a8b0;
  --color-madder-400: #f37683;
  --color-madder-500: #e94a5a;
  --color-madder-600: #d62c3d;
  --color-madder-700: #b32231;
  --color-madder-800: #97202c;
  --color-madder-900: #7c2029;
  --color-madder-950: #430c12;
  --color-saffron-50: #fdf9ed;
  --color-saffron-100: #f8eccd;
  --color-saffron-200: #f1d796;
  --color-saffron-300: #ebc26a;
  --color-saffron-400: #e4a73b;
  --color-saffron-500: #dc8924;
  --color-saffron-600: #c3671c;
  --color-saffron-700: #a24a1b;
  --color-saffron-800: #843a1c;
  --color-saffron-900: #6d311a;
  --color-saffron-950: #3e180a;
  --color-blue-50: #e0f5ff;
  --color-blue-100: #d4f1ff;
  --color-blue-200: #b6e5fc;
  --color-blue-300: #6acaf9;
  --color-blue-400: #3dbaf7;
  --color-blue-500: #13abf5;
  --color-blue-600: #1091d0;
  --color-blue-700: #0d79ae;
  --color-blue-800: #0b618c;
  --color-blue-900: #094d6e;
  --color-cyan-50: #e9fcfc;
  --color-cyan-100: #cbf9f7;
  --color-cyan-200: #a2f3f0;
  --color-cyan-300: #77eeea;
  --color-cyan-400: #4ee9e3;
  --color-cyan-500: #27e4dd;
  --color-cyan-600: #21c2bc;
  --color-cyan-700: #1ca29d;
  --color-cyan-800: #16827e;
  --color-cyan-900: #126763;
}
```

## semantic.css

```css
/* ==========================================================================
 * AUTO-GENERATED from tokens.json — DO NOT EDIT MANUALLY
 * Run: pnpm tokens:build
 * ========================================================================== */

/* This file shows the semantic layer derived from tokens.json.
 * It uses var() references to the new primitive names (from primitives.css).
 *
 * STATUS: Reference only — not imported yet.
 * The hand-written semantic.css still uses old primitive names (navy, sky, neutral).
 * When ready to migrate, swap the hand-written file for this one. */

@theme {
  /* — Background — */
  --color-bg-primary: var(--color-white);
  --color-bg-secondary: var(--color-cool-gray-50);
  --color-bg-tertiary: var(--color-cool-gray-100);
  --color-bg-inverse: var(--color-rich-black-900);
  --color-bg-brand-subtle: var(--color-cornflower-blue-50);
  --color-bg-highlight: var(--color-cornflower-blue-100);
  --color-bg-selected: var(--color-cornflower-blue-200);

  /* — Text — */
  --color-text-primary: var(--color-cool-gray-950);
  --color-text-secondary: var(--color-cool-gray-800);
  --color-text-tertiary: var(--color-cool-gray-600);
  --color-text-disabled: var(--color-cool-gray-300);
  --color-text-inverse: var(--color-white);
  --color-text-brand: var(--color-rich-black-900);
  --color-text-link: var(--color-rich-black-900);
  --color-text-link-hover: var(--color-rich-black-950);
  --color-text-on-color: var(--color-white);

  /* — Border — */
  --color-border-default: var(--color-cool-gray-200);
  --color-border-subtle: var(--color-cool-gray-100);
  --color-border-strong: var(--color-cool-gray-300);
  --color-border-focus: var(--color-cornflower-blue-300);
  --color-border-brand: var(--color-rich-black-900);
  --color-border-error: var(--color-madder-500);

  /* — Interactive — */
  --color-interactive-primary: var(--color-rich-black-950);
  --color-interactive-primary-hover: var(--color-rich-black-900);
  --color-interactive-primary-active: var(--color-rich-black-800);
  --color-interactive-primary-text: var(--color-white);
  --color-interactive-secondary: var(--color-cornflower-blue-400);
  --color-interactive-secondary-hover: var(--color-cornflower-blue-300);
  --color-interactive-secondary-active: var(--color-cornflower-blue-500);
  --color-interactive-secondary-text: var(--color-white);
  --color-interactive-neutral: var(--color-cool-gray-200);
  --color-interactive-neutral-hover: var(--color-cool-gray-300);
  --color-interactive-neutral-active: var(--color-cool-gray-400);
  --color-interactive-neutral-text: var(--color-cool-gray-950);
  --color-interactive-destructive: var(--color-madder-600);
  --color-interactive-destructive-hover: var(--color-madder-700);
  --color-interactive-destructive-text: var(--color-white);
  --color-interactive-ghost: transparent;
  --color-interactive-ghost-hover: var(--color-cool-gray-50);
  --color-interactive-ghost-active: var(--color-cool-gray-100);
  --color-interactive-ghost-text: var(--color-cool-gray-950);
  --color-interactive-accent-from: var(--color-cornflower-blue-400);
  --color-interactive-accent-to: var(--color-tropical-indigo-400);
  --color-interactive-accent-text: var(--color-white);
  --color-interactive-inverse: var(--color-white);
  --color-interactive-inverse-hover: var(--color-cool-gray-50);
  --color-interactive-inverse-text: var(--color-rich-black-950);
  --color-interactive-focus-ring: var(--color-cornflower-blue-300);

  /* — Gradient — */
  --color-gradient-primary-from: var(--color-cornflower-blue-400);
  --color-gradient-primary-to: var(--color-cornflower-blue-800);
  --color-gradient-blue-purple-from: var(--color-cornflower-blue-400);
  --color-gradient-blue-purple-to: var(--color-tropical-indigo-400);
  --color-gradient-blue-green-from: var(--color-cornflower-blue-400);
  --color-gradient-blue-green-to: var(--color-keppel-green-500);
  --color-gradient-blue-purple-fade-from: var(--color-cornflower-blue-400);
  --color-gradient-blue-purple-fade-via: var(--color-tropical-indigo-400);
  --color-gradient-blue-purple-fade-to: var(--color-cornflower-blue-100);
  --color-gradient-blue-green-fade-from: var(--color-cornflower-blue-400);
  --color-gradient-blue-green-fade-via: var(--color-keppel-green-500);
  --color-gradient-blue-green-fade-to: var(--color-cornflower-blue-100);
  --color-gradient-spectrum-stop-1: var(--color-cornflower-blue-100);
  --color-gradient-spectrum-stop-2: var(--color-cornflower-blue-400);
  --color-gradient-spectrum-stop-3: var(--color-tropical-indigo-400);
  --color-gradient-spectrum-stop-4: var(--color-rich-black-950);
  --color-gradient-spectrum-green-stop-1: var(--color-cornflower-blue-100);
  --color-gradient-spectrum-green-stop-2: var(--color-cornflower-blue-400);
  --color-gradient-spectrum-green-stop-3: var(--color-keppel-green-500);
  --color-gradient-spectrum-green-stop-4: var(--color-rich-black-950);
  --color-gradient-subtle-primary-from: var(--color-cornflower-blue-50);
  --color-gradient-subtle-primary-to: var(--color-cornflower-blue-100);
  --color-gradient-subtle-blue-purple-from: var(--color-cornflower-blue-50);
  --color-gradient-subtle-blue-purple-to: var(--color-tropical-indigo-100);
  --color-gradient-subtle-blue-green-from: var(--color-cornflower-blue-50);
  --color-gradient-subtle-blue-green-to: var(--color-keppel-green-50);

  /* — Feedback — */
  --color-feedback-critical-bg: var(--color-madder-50);
  --color-feedback-critical-text: var(--color-madder-700);
  --color-feedback-critical-border: var(--color-madder-200);
  --color-feedback-critical-icon: var(--color-madder-500);
  --color-feedback-warning-bg: var(--color-saffron-50);
  --color-feedback-warning-text: var(--color-saffron-950);
  --color-feedback-warning-border: var(--color-saffron-200);
  --color-feedback-warning-icon: var(--color-saffron-500);
  --color-feedback-success-bg: var(--color-keppel-green-50);
  --color-feedback-success-text: var(--color-keppel-green-700);
  --color-feedback-success-border: var(--color-keppel-green-200);
  --color-feedback-success-icon: var(--color-keppel-green-500);
  --color-feedback-info-bg: var(--color-cornflower-blue-50);
  --color-feedback-info-text: var(--color-rich-black-900);
  --color-feedback-info-border: var(--color-cornflower-blue-200);
  --color-feedback-info-icon: var(--color-cornflower-blue-500);

  /* — Icon — */
  --color-icon-default: var(--color-cool-gray-950);
  --color-icon-secondary: var(--color-cool-gray-600);
  --color-icon-disabled: var(--color-cool-gray-400);
  --color-icon-success: var(--color-keppel-green-600);
  --color-icon-warning: var(--color-saffron-400);
  --color-icon-critical: var(--color-madder-500);
  --color-icon-brand: var(--color-rich-black-900);
}
```

## dimensions.css

```css
/* ==========================================================================
 * AUTO-GENERATED from tokens.json — DO NOT EDIT MANUALLY
 * Run: pnpm tokens:build
 * ========================================================================== */

@theme {
  /* — Spacing — */
  --space-0: 0px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 28px;
  --space-8: 32px;
  --space-9: 36px;
  --space-10: 40px;
  --space-12: 48px;
  --space-14: 56px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
  --space-px: 1px;
  --space-0-5: 2px;
  --space-1-5: 6px;
  --space-2-5: 10px;
  --space-3-5: 14px;

  /* — Size — */
  --size-xs: 20px;
  --size-sm: 24px;
  --size-md: 32px;
  --size-lg: 40px;
  --size-xl: 48px;

  /* — Radius — */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* — Breakpoints — */
  --breakpoint-xs: 640px;
  --breakpoint-sm: 768px;
  --breakpoint-md: 1024px;
  --breakpoint-lg: 1366px;
  --breakpoint-xl: 1440px;

  /* — Border Width — */
  --border-width-none: 0px;
  --border-width-thin: 1px;
  --border-width-medium: 2px;
  --border-width-thick: 3px;
}
```

## utilities.css

```css
/* ==========================================================================
 * AUTO-GENERATED from tokens.json — DO NOT EDIT MANUALLY
 * Run: pnpm tokens:build
 * ========================================================================== */

@theme {
  /* — Font — */
  --font-sans: 'Poppins', sans-serif;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  /* — Motion — */
  --duration-instant: 0ms;
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-moderate: 300ms;
  --duration-slow: 500ms;
  --ease-out: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in: cubic-bezier(0.5, 0, 0.75, 0);
  --ease-in-out: cubic-bezier(0.45, 0, 0.55, 1);
  --stagger-delay: 30ms;

  /* — Opacity — */
  --opacity-disabled: 0.4;
  --opacity-overlay: 0.5;
  --opacity-hover: 0.08;
  --opacity-pressed: 0.12;

  /* — Z-Index — */
  --z-sidebar: 1100;
  --z-app-bar: 1100;
  --z-drawer: 1200;
  --z-dialog: 1310;
  --z-menu: 1400;
  --z-toast: 1400;
  --z-tooltip: 1500;
}
```
