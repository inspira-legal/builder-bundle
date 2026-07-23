# Pre-flight tooling — silent checks

Runs as part of Step 0 of SKILL.md, before the profile calibration (Phase 0). Prints nothing to the user — just observes and persists to `.brisar/session.yaml`.

Core principle: **never block due to missing tooling** — there is always a fallback. Surface the gap, offer to resolve it, and continue the path.

## What it checks

### 1. git + gh

```bash
git --version 2>/dev/null
gh --version 2>/dev/null
gh auth status 2>/dev/null
```

Captures:

```yaml
preflight:
  tooling:
    git_installed: true | false
    gh_installed: true | false
    gh_authed: true | false
    gh_user: "<username or null>"
```

### 2. Available MCPs

Reads `~/.claude.json` (or `.claude/settings.local.json` in project scope) and extracts keys from `mcpServers`.

```bash
test -f ~/.claude.json && \
  cat ~/.claude.json | python3 -c "import json, sys; d=json.load(sys.stdin); print('\n'.join(d.get('mcpServers', {}).keys()))" 2>/dev/null
```

(Use `python3` if available — fall back to `grep` if not.)

```bash
# grep fallback
grep -oE '"[a-zA-Z0-9_-]+":\s*\{' ~/.claude.json 2>/dev/null | head -30
```

Maps to known flags:

```yaml
preflight:
  mcps:
    unframer: bool       # mcp-unframer-co — needed for Framer path with canvas
    figma: bool          # mcp__figma — optional, improves design-to-code
    atlassian: bool      # optional
    google_drive: bool   # optional
    raw_list: [<all keys found>]
```

### 3. Detected product (cross-ref with product-registry)

Already done in Step 0.5 of SKILL.md. Persists:

```yaml
preflight:
  product:
    detected: <product_id or unknown>
    detection_basis: <list of markers that matched>
```

## Full persistence

Goes to `.brisar/session.yaml` in Step 0:

```yaml
preflight:
  ran_at: <ISO>
  cwd: <absolute path>

  tooling:
    git_installed: bool
    gh_installed: bool
    gh_authed: bool
    gh_user: <string or null>

  mcps:
    unframer: bool
    figma: bool
    atlassian: bool
    google_drive: bool
    raw_list: [<keys>]

  product:
    detected: <id or unknown>
    detection_basis: [<markers>]
```

Does not re-run if filled within the last 24h AND the session is active. Re-runs when:
- New session
- Phase 0 changed the profile (e.g., senior → content — needs to re-check MCPs)
- Builder explicitly requested a refresh

## How each brisar piece uses the preflight

### Phase 0 (profile calibration)

To validate the answer by cross-referencing with tooling. See `phase-0-calibration.md` section "Cross-validation with preflight".

### Phase 1 (lightning intake)

If product detected: skips the brand question (already known via `product.brand`). Skips the hosting question (already known: embed).

### Phase 3 (scaffold) — NOT called for content persona

If persona = `executive` AND `tooling.git_installed: false`: goes to `prototype-hosted` instead of local scaffold.

If persona = `builder-senior` AND product detected AND `tooling.gh_authed: false`: offers to authenticate before trying to clone the private repo.

### Phase Framer (content path)

If `mcps.unframer: false`: falls back to the product's `fallback_path: framer-handoff-no-mcp` — generates `harpa-handoff-<slug>-<date>.md` in cwd, without depending on MCP. Mention that the builder can add the `mcp-unframer-co` MCP to their Claude config (`~/.claude.json`, `mcpServers` block) for the live-canvas path next time. brisar never edits `~/.claude.json` itself.

## When the preflight detects inconsistency

Common cases and what to do:

| Detected | Response |
|---|---|
| `gh_authed: false` but builder is in a folder of an Inspira product (private) | Warn: "esse produto é privado. Quer autenticar?" |
| MCP unframer present but builder didn't choose Framer | Don't mention it — only used when relevant |
| Multiple matches in the product registry | Silent log (debug). Take the first one from the registry. |
| `git_installed: false` AND persona = builder-senior | "Você marcou senior mas git não tá aqui. Atualizar perfil ou instalar git?" |
| `git_installed: false` AND persona = executive | Don't mention it — the executive path doesn't require git. |

Detected product and profile calibration stay independent: product = "where I am", profile = "who I am" — a senior embedding into an Inspira product and an executive prototyping something new can sit in the same folder.

## Minimum acceptable state

brisar can run WITHOUT:
- gh / authentication (falls back to fallbacks)
- MCPs (falls back to manual path)

brisar needs:
- Bash (comes with any macOS/Linux)
- Filesystem write in the cwd (for scaffold/session)

Without these two, surface a clear error in Step 0 and STOP. Don't try to continue.
