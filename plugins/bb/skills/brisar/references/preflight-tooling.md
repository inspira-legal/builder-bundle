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

Reads `~/.claude.json` and extracts keys from `mcpServers`. **Read both scopes** — global and
project — because a server configured for the current directory does not appear at the top level,
and treating it as absent silently removes a medium the builder actually has:

```bash
test -f ~/.claude.json && python3 - "$PWD" <<'PY' 2>/dev/null
import json, os, sys
cwd = sys.argv[1]
d = json.load(open(os.path.expanduser("~/.claude.json")))
keys = set(d.get("mcpServers", {}))
for proj, v in (d.get("projects") or {}).items():
    if cwd == proj or cwd.startswith(proj.rstrip("/") + "/"):
        keys |= set(v.get("mcpServers") or {})
print("\n".join(sorted(keys)))
PY
```

(Use `python3` when available — fall back to `grep` if not. The fallback loses project scope; say
so rather than reporting a clean absence.)

```bash
# grep fallback — global scope only
grep -oE '"[a-zA-Z0-9_-]+":\s*\{' ~/.claude.json 2>/dev/null | head -30
```

Matching is **by substring, case-insensitive** — server keys are user-chosen and are sometimes
opaque ids instead of product names. Match `paper` inside `paper-mcp`, `figma` inside
`figma-dev-mode`. When a key is an opaque id matching nothing known, keep it in `raw_list` and
treat the capability as absent.

Maps to known flags:

```yaml
preflight:
  mcps:
    # design mediums — feed the medium question (references/phase-medium.md)
    paper: bool # Paper — canvas design tool
    figma: bool # Figma — canvas design tool, also improves design-to-code
    pencil: bool # Pencil — .pen design files
    # research
    mobbin: bool # Mobbin — market bench; the research floor degrades without it
    # other paths
    unframer: bool # mcp-unframer-co — Framer path with live canvas
    atlassian: bool # optional
    google_drive: bool # optional
    raw_list: [<all keys found, both scopes>]
    scope_read: both | global-only # global-only when the python3 path was unavailable
```

**Two consumers care about these beyond the classic paths:**

- **The medium question** (`references/phase-medium.md`) offers a canvas medium **only** when its
  MCP is present, and **names** the missing ones instead of hiding them. Code and Claude design
  need no MCP and are always offered.
- **The research floor** (`references/phase-research.md`, Front A) uses Mobbin. Without it the
  market bench degrades to web search — a **declared** degradation, never a silent skip.

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

### Research phase (market bench)

`mcps.mobbin` gates Front A of the research floor. Present → bench via Mobbin. Absent → degrade
to web search and **say so in the mode line**: the floor never scales down silently, so a
degraded front is announced, not omitted.

### Medium question (`references/phase-medium.md`)

`mcps.paper` / `mcps.figma` / `mcps.pencil` decide which canvas mediums are **offered**. Code and
Claude design require no MCP and are always available, so there is always at least one path — the
question can never dead-end.

Missing mediums are **named, not hidden**: "não detectei o MCP do Figma aqui" tells the builder
something actionable. Silently offering three options where they expected four reads as the tool
deciding for them. brisar never edits `~/.claude.json` — it says what would enable the path.

## When the preflight detects inconsistency

Common cases and what to do:

| Detected                                                                      | Response                                                                                                                                                         |
| ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gh_authed: false` but builder is in a folder of an Inspira product (private) | Warn: "esse produto é privado. Quer autenticar?"                                                                                                                 |
| MCP unframer present but builder didn't choose Framer                         | Don't mention it — only used when relevant                                                                                                                       |
| Multiple matches in the product registry                                      | Silent log (debug). Take the first one from the registry.                                                                                                        |
| `git_installed: false` AND persona = builder-senior                           | "Você marcou senior mas git não tá aqui. Atualizar perfil ou instalar git?"                                                                                      |
| `git_installed: false` AND persona = executive                                | Don't mention it — the executive path doesn't require git.                                                                                                       |
| `scope_read: global-only` (no python3)                                        | A project-scoped MCP may exist and be invisible. Before naming a medium as missing, say the check was partial — never report a clean absence you did not verify. |
| No canvas MCP at all                                                          | Don't treat it as a gap. Code and Claude design cover the medium question; mention the canvas paths once, without nagging.                                       |
| `mobbin: false`                                                               | Declare the degraded bench in the research mode line. Do not drop Front A.                                                                                       |

Detected product and profile calibration stay independent: product = "where I am", profile = "who I am" — a senior embedding into an Inspira product and an executive prototyping something new can sit in the same folder.

## Minimum acceptable state

brisar can run WITHOUT:

- gh / authentication (falls back to fallbacks)
- MCPs (falls back to manual path)

brisar needs:

- Bash (comes with any macOS/Linux)
- Filesystem write in the cwd (for scaffold/session)

Without these two, surface a clear error in Step 0 and STOP. Don't try to continue.
