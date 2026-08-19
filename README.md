<div align="center">

# builder-bundle

[![github](https://img.shields.io/badge/github-inspira--legal%2Fbuilder--bundle-111111?style=flat-square&logo=github)](https://github.com/inspira-legal/builder-bundle)

_Builder Bundle (`bb`): the unified skill set for Inspira builders, 15 skills across 6 trilhas, from the problem to the PR._

</div>

add the marketplace and install the single plugin:

```bash
claude plugin marketplace add inspira-legal/builder-bundle
claude plugin install bb@inspira-legal
```

it ships a `SessionStart` operating-context hook, auto-active on install, which also carries the profile set by `/bb:config`, and two read-only agents (`bb-review-finder`, `bb-review-verifier`) that review dispatches in parallel: internal pipeline roles, not entry points. skills are invoked as `/bb:<skill>` (e.g. `/bb:discover`, `/bb:spec`, `/bb:ship`). every skill with a natural next step ends at a gate that **suggests** the next trilha, and never auto-invokes.

## what is inside

one plugin, `bb`; 15 skills in 6 trilhas, plus `/bb:config`.

### configurar: who is on the other side

| skill        | description                                                                                                                                       |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:config` | asks four questions once (do you read the code, do you run commands, do you want the technical parts step by step, does technical vocabulary read fine) and writes `~/.claude/bb.config.json`. the hook carries the answers into every session, so no skill asks again |

### pensar: frame and decide before building

| skill            | description                                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/bb:discover`   | from the itch to a bet you can spec: frames the problem, presses the fit (is it worth building, what to cut) and closes hypothesis plus appetite |
| `/bb:challenge`  | adversarial pre-mortem of a thesis: tries to break it before reality does                                                                        |
| `/bb:think`      | thinks with you and takes a position: an honest, decisive recommendation that names the tension you have not seen, with no flattery              |
| `/bb:legal-lens` | a legal pass over an idea, a flow or a document: legal and compliance risk, grounded in cited rules (Brazil by default)                          |

### desenhar: agree on the shape of what gets built

| skill      | description                                                                                                                           |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:spec` | align on the idea before the code: develops the draft, iterates the gray areas as questions, validates a spec at `.bb/<slug>/spec.md` |

### construir: write and land code

| skill                       | description                                                                                                                                                                                                             |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:implement`             | builds a validated spec: builds the tasks, keeps the project's checks green, then offers to land it                                                                                                                     |
| `/bb:ship`                  | takes the branch to landed, your way. it does not review: it greens the project's checks, commits, then pushes, preps main, opens a PR and tends it, or preps the LexFlow deploy. after landing, it offers `/bb:review` |
| `/bb:delegate`              | runs a spec end to end: selects it, builds every task and lands it (implement then ship), tracking the `status`                                                                                                         |
| `/bb:gather-branch-context` | summarizes every change on the branch against main                                                                                                                                                                      |

### revisar: quality and maintenance

| skill               | description                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:review`        | you pick the fronts (correctness, quality, project rules, the spec contract, UI accessibility, PR threads, CI), it runs them in parallel and verifies every finding; it fixes, replies and resolves whatever you approve. runs at cheap standard depth (agents on Sonnet); `/bb:review deep` turns on the whole angle set, the closing sweep and agents on Opus. the accessibility front also runs alone, as a WCAG AA audit of a folder or a live page |
| `/bb:maintain-repo` | triages PRs plus Dependabot and outdated deps, and reports what is safe to merge (it never merges)                                                                                                                                                                                                                                                                                                                                                      |
| `/bb:review-setup`  | sets up Inspira's code-review workflow in the repo and writes the `CODE_REVIEW_GUIDE.md`                                                                                                                                                                                                                                                                                                                                                                |

### design: from the idea to a high-fidelity surface

| skill        | description                                                                                                                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:brisar` | end-to-end design journey: scaffolds with the brand DS, writes a visual direction per surface, then builds (Develop) and reviews or hands off (Deliver) as internal phases |

### pesquisar and document

| skill                    | description                                                                               |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| `/bb:code-deep-research` | finds, clones and explores repos, then verifies the findings adversarially against source |
| `/bb:write-readme`       | generates a minimal centered-header README out of the repo's own facts                    |

## migrating from ofc?

see the [CHANGELOG](CHANGELOG.md): the full mapping from the 28 old skills to the new ones, the coexistence notice, and how to swap the plugin.

develop locally:

```bash
git clone git@github.com:inspira-legal/builder-bundle.git
claude --plugin-dir ./builder-bundle/plugins/bb    # loads the plugin off disk to test it
```

<sub>the quality pass in `/bb:review` is adapted from Claude Code's `/simplify`, its angle and verification architecture from `/code-review` (Anthropic, Apache-2.0), and the accessibility front absorbs rafael's skill in the inspira-skills store. `/bb:brisar` incorporates the skills of the brisa-ds bundle. individual components keep their original licenses.</sub>
