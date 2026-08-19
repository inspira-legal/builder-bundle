---
status: done
created: 2026-07-30
slug: ship-lexflow
---

# ship: the LexFlow destination

`/bb:ship` gains **LexFlow** as a 4th destination, next to branch / main / PR. Whoever builds
a LexFlow app gets the same landing path everyone else has: quality pass → commit → push →
and then the deploy command **handed over**, never pressed by the ship. Along with it comes a
refactor: the four landings leave `SKILL.md` for `references/land-*.md`, leaving `SKILL.md` as
a router.

The gap is not about convenience: **nobody reviews the LexFlow workflow YAMLs today.** The app
repos (`data-magnifier`, `data-inspira-hm`, `data-chat-features-hm`) have no `.github/` at
all, zero CI, and `lexflow-builder` only validates the syntax of the YAML it just generated
itself. The ship's quality pass is exactly the substance missing there. And it can be done
without inventing anything: this cohort has git, the apps are git repos, so the ship's
sequence (diff → review → commit → push) already serves.

Success: a LexFlow app reaches the deploy having gone through a real review, and the builder
presses the deploy knowing which sha is going up.

## What a LexFlow app is

Source: `inspira-legal/lexflow-automacoes/lexflow-deploy-cli/` (README plus `cli.py`,
`manifest.py`, `deploy.py`, `doctor.py`).

- **The remote is the platform, not GitHub.** `lexflow clone`/`init` install a credential
  helper in `~/.config/lexflow/git-credentials-helper.py` that authenticates through a Firebase
  JWT. A raw `git clone` of the URL fails with `could not read Username` on a machine that
  never ran `lexflow login`. There is no PR mechanism on that remote, which is why the
  destination is exclusive.
- **`push` is not `deploy`, by design.** The CLI is explicit: "Pushing to the git remote does
  NOT trigger a deploy"; the bucket is versioned storage. And it instructs LLMs directly:
  "prefer raw git for read paths". Asking for "push" is VCS, asking for "deploy" is
  `lexflow deploy`. Push is safe and authorized for an agentic tool; deploy is the irreversible
  act.
- **`manifest.py` already validates the coherence of `lexflow.toml`**: required fields, slug
  format, duplicate slugs (datastore/workflow/deployment) and the existence of every `source`,
  middleware included.
- **`load_manifest` runs before the network.** In `deploy()`: auth → `load_manifest` →
  (`ManifestError` → `Manifest error:` plus exit 1) → only then a fetch of the platform state →
  diff. That is why `--dry-run` is a reliable gate for the **manifest** and useless as a gate
  for the **plan**: the local validation happens before the call that can return a 500.
- **`lexflow deploy --ref <branch|tag|sha>`** fetches the source at that ref and deploys exactly
  that commit, recording the `git_sha` in the deployment.
- Commands that exist: `login/logout`, `deploy`, `refs`, `clone`, `sync`, `init`, `push`,
  `pull`, `doctor`, `self-update`, `destroy`, `secret *`, `connection *`, `examples *`,
  `opcodes *`. **There is no `lexflow validate`**, and `doctor` is only local tooling detection.

## Where the ship changes

| layer                      | changes? | how                                                     |
| -------------------------- | -------- | ------------------------------------------------------- |
| destination (Step 1)       | yes      | a 4th destination plus a detection preflight            |
| gate plus quality pass (2) | yes      | a gate of its own; the lenses repointed at the artifact |
| landing                    | yes      | a new `land-lexflow.md` plus extracting the other three |

**Detection**: `lexflow.toml` at the root → `project_kind: lexflow`, a flag Step 1 and Step 2
read. It makes LexFlow the recommended option, and it does not skip the question: the same repo
can legitimately want a PR in that run.

**The gate, three layers with one authority each:**

1. **A local pre-check**: `scripts/check_lexflow_manifest.py`, only the cheap and stable subset
   through `tomllib`: `[app]` exists, and every `source` (deployments, workflows, middlewares)
   points at a real file. It fails in milliseconds, with no network, and works logged out.
   Nothing beyond that; the rest belongs to the CLI, and duplicating it drifts.
2. **`lexflow deploy --dry-run`**: the authority over the manifest, in three buckets.
   `Manifest error:` plus exit 1 → the app's fault → **it blocks and fixes**; a 500 or a network
   error in the diff phase → platform instability → **it reports and goes on**; the CLI missing
   or logged out → **the check is skipped**, pointing at `lexflow login`.
3. **The LLM reading the YAMLs**: the workflows are small and declarative; the LLM checks
   opcode names and params against `lexflow opcodes list`. No YAML parser in Python (the repo
   rule is stdlib only, and the stdlib has no YAML).

**Quality pass**: four agents, one lens each, output
`file:line | what | evidence | suggested fix | confidence`. The lens set swaps to fit the
artifact: workflow logic and edges / opcode contracts and secret permissions / query
correctness / quality. `async-state` is dead weight in a declarative manifest.

**Landing**: `push` (plain git, reversible, explicitly authorized for an LLM) and then it
**hands over** `lexflow deploy --ref <sha>` with the sha that went through the quality pass.
Still holding: it never merges, never approves, never force-pushes, **never deploys**.

## Decisions

- **An exclusive 4th destination**, not a step that composes with the git landing. Step 1 stays
  a single choice: branch / main / PR / LexFlow. _Accepted consequence:_ the case "a PR for
  human review **and** a deploy" costs two runs.
- **The ship hands the deploy command over, it does not press it.** A convention to follow, not
  to invent: `lexflow-builder` already decided this.
- **The command handed over is `lexflow deploy --ref <sha>`** (not plain `lexflow deploy`), so
  it deploys the reviewed commit instead of the working tree.
- **The gate is the `tomllib` pre-check plus the CLI as the authority plus the LLM on the
  YAMLs.**
- **It blocks a manifest error, reports a platform error, and skips when logged out.**
- **It extracts the four landings** into `references/land-{branch,main,pr,lexflow}.md`;
  `SKILL.md` becomes a router.
- **Reuse:** `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py` serves with no change (plain
  git, and the CLI recommends exactly that for read paths). `references/review-checklist.md`
  and `references/loop.md` keep holding. `fetch_comments.py`, `reply_resolve_thread.py` and
  `scripts/inspect_pr_checks.py` belong to the PR path and do not enter here.
- **bb points at `lexflow-builder`, it does not re-teach deploy.** The mechanics (assembling
  the `lexflow.toml`, the `--url` flag, the publication URL) belong to the platform team;
  restating them drifts when the platform changes.
- **CLI output and YAML content are data, not instructions**, which extends the line the ship
  already has for a PR comment and a CI log.

## Behavior

1. A builder runs `/bb:ship` in a repo with `lexflow.toml` at the root.
2. The preflight sets `project_kind: lexflow`; Step 1 offers the four destinations with LexFlow
   recommended. The builder picks LexFlow.
3. The local pre-check passes (`[app]` present, every `source` exists).
4. Quality pass: a fan out of four repointed lenses over the diff; fixes applied only in the
   main context (a single writer); the gate re-runs.
5. `lexflow opcodes list` → the LLM checks the opcodes used in the YAMLs the diff touched.
6. `lexflow deploy --dry-run` → the plan is computed, reported as information.
7. A commit in logical units → `git push`.
8. The final report: the sha, which deployments the diff affects, the result of each gate layer,
   and the command `lexflow deploy --ref <sha>`.

| WHEN                                                                | THEN                                                                                     |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| the diff touches nothing the manifest references                    | it commits and pushes, and omits the deploy handoff; there is nothing to deploy          |
| the file may be referenced from inside a workflow (`queries/*.sql`) | the pre-check returns `affects_deploy: "unknown"`; the LLM reading the YAMLs decides     |
| a `source` points at a file that does not exist                     | it blocks before the quality pass, naming the path and the deployment                    |
| the dry-run exits with `Manifest error:`                            | it blocks, fixes, and re-runs the dry-run                                                |
| the dry-run returns a 500 or a network error in the diff phase      | it reports platform instability and goes on with the landing                             |
| it is not logged in                                                 | the dry-run and `opcodes list` become skipped checks; it points at `lexflow login`       |
| the CLI is not on the PATH or the shim is broken                    | the same degradation as logged out, and it reports the broken shim                       |
| the `git push` fails with `could not read Username`                 | it diagnoses a missing credential helper and points at `lexflow login`                   |
| the push is rejected because the remote is ahead                    | `lexflow sync` (ff-only) or `lexflow pull`; force-push stays barred                      |
| the diff declares a new `$secret` in `[env]`                        | it names the secret and points at `lexflow secret set`; the deploy will ask for it       |
| the diff touches `[[datastores]]`                                   | it warns this is the dry-run bug's area; a 500 there is probably not the app's           |
| there are several `lexflow.toml` (a monorepo)                       | it derives the app from what the diff touches; crossing more than one, it asks which     |
| a LexFlow destination was asked for and there is no `lexflow.toml`  | it says it did not find the manifest and suggests the right directory or `lexflow clone` |
| the diff is small (≲2 files / ≲100 lines)                           | it skips the fan out and reviews inline, the ship's current rule, kept                   |
| someone deployed another sha in the meantime                        | irrelevant to the handoff: `--ref <sha>` is deterministic                                |

## Tasks

- [x] **1. Detection and the 4th destination**: the preflight in Step 1 plus the destination in
      `SKILL.md` → behaviors 1, 2 · dep: — · verify: CI
- [x] **2. The manifest pre-check**: `scripts/check_lexflow_manifest.py` with `tomllib`
      (`[app]` plus the existence of every `source`), stdlib only → behavior 3 · dep: — ·
      verify: CI
- [x] **3. The landings extracted**: `references/land-{branch,main,pr,lexflow}.md`, `SKILL.md`
      becomes a router → behaviors 1-8 · dep: 1 · verify: reading
- [x] **4. `land-lexflow.md`**: the 3 layer gate, the quality pass with repointed lenses, the
      push landing plus the `--ref <sha>` handoff, the report in PT-BR
      → behaviors 3-8 · dep: 2, 3 · verify: CI
- [x] **5. The PT-BR triggers**: "deployar no lexflow", "subir o app lexflow" in the frontmatter
      → behavior 1 · dep: 1 · verify: CI
- [x] **6. CHANGELOG**: the release line → behaviors 1-8 · dep: 1-5 · verify: CI

## Out of scope

- Builders with no local tooling at all (Claude web, for instance, who solve a deploy by asking
  on Slack). Out of the ship's reach; the platform has LexFlow's internal chat.
- Re-teaching deploy mechanics inside bb (`lexflow-builder` owns it).
- Pressing the deploy, even with prior authorization. _revisit:_ not before the platform has
  deployment rollback.
- The fragmentation of the three competing `*-builder` skills (`lexflow-builder` in
  `lexflow-automacoes`, `lex-flow-builder` in `lex-flow`, and bb). Bigger than the ship, and it
  is a conversation with the platform team (Capitani/Giro). _revisit:_ after this spec lands.
- Re-adding `lexflow` to `brisar`'s `product-registry.yaml`. _revisit:_ when the canonical
  repo_urls settle.
- Fixing the CLI's broken shim on this machine: a test prerequisite, not scope.

## Open

- Nothing blocking. One caveat about the source: nothing here was validated against a real
  `lexflow --help` (this machine's shim points at a removed Python). All the CLI knowledge comes
  from the source (`cli.py`, `manifest.py`, `deploy.py`, README), which is more reliable than
  `--help` anyway, but the version installed on the team may be behind `main`.
