# Discovery — 5 parallel subagents, then rule extraction

Fire ALL 5 subagents in ONE message (parallel Agent tool calls). Discovery never
runs in the main context — subagents protect it. If the repo has more than 1000
files, tell each subagent to sample representative files per directory. If a
focus area was given, pass the constraint to every subagent.

Every subagent returns the same structure:

```
## Confirmed Patterns
- [patterns found consistently, with file-count evidence]

## Candidate Patterns
- [patterns probable but needing validation]

## Evidence
- [file paths and snippets supporting each finding]
```

## Subagent 1 — Stack & Structure

> You are a codebase structure analyst. Discover the technology stack and
> project structure. Investigate: (1) languages by extension distribution;
> (2) frameworks — package.json, pyproject.toml, go.mod, Cargo.toml, pom.xml,
> Gemfile…; (3) package manager (lock files); (4) directory layout (top ~50
> dirs, excluding node_modules/.git/venv); (5) entry points; (6) build system —
> Makefile, Dockerfile, docker-compose, bundler configs; (7) monorepo signals —
> workspaces, lerna.json, nx.json, turbo.json. Use Glob and Bash. Return the
> Confirmed/Candidate/Evidence structure.

## Subagent 2 — Patterns & Conventions

> You are a code patterns analyst. Sample 10–15 representative source files
> across directories and identify: (1) naming conventions (files, variables,
> functions); (2) layer organization — MVC, hexagonal, clean, feature-based;
> (3) design patterns — factories, repositories, DI, middleware chains;
> (4) module organization — barrel exports, path aliases, module boundaries;
> (5) error handling — try/catch, Result types, error middleware, custom error
> classes; (6) code style — check .editorconfig / formatter / linter configs.
> Confirmed = consistent across 80%+ of relevant files. Use Glob, Grep, Read.
> Return the Confirmed/Candidate/Evidence structure.

## Subagent 3 — Git History & PRs

> You are a git history and PR analyst. Investigate: (1) commit-message pattern
> over the last 50 commits (conventional? scopes? ticket refs?); (2) branch
> naming (`git branch -r`); (3) merged-PR patterns —
> `gh pr list --state merged --limit 10 --json title,body,labels,reviewDecision`;
> (4) recurring review feedback — `gh pr view <n> --json reviews,comments` on
> the 5 most recent merged PRs; (5) refactor trends in the last 100 commits;
> (6) top contributors (`git shortlog -sn --no-merges`). If a git/gh command
> fails, note it and continue. Return the Confirmed/Candidate/Evidence
> structure with exact commit messages / PR titles as evidence.

## Subagent 4 — CI/CD, Quality & Infra

> You are a CI/CD and quality infrastructure analyst. Investigate: (1) pipelines
> — read every workflow/pipeline file found (.github/workflows, GitLab CI,
> Jenkinsfile…); (2) linters & formatters and their configs; (3) test framework,
> config, and directory structure; (4) coverage config and thresholds in CI;
> (5) pre-commit hooks — .husky/, .pre-commit-config.yaml, lint-staged;
> (6) infra context (Dockerfile, terraform, serverless) for code-rule context,
> not infra rules; (7) quality gates — Sonar, CodeClimate. Use Glob, Read, Bash.
> Return the Confirmed/Candidate/Evidence structure.

## Subagent 5 — Security, Contracts & Dependencies

> You are a security and API contracts analyst. Investigate: (1) auth patterns —
> middleware, JWT, sessions, guards; (2) input validation libraries and where
> validation happens; (3) API error structure — codes, envelopes, global
> handlers; (4) API contracts — OpenAPI, GraphQL schemas, protobuf;
> (5) external integrations — HTTP clients, DB connections, queues, caches, and
> their error handling; (6) dependency management and injection patterns;
> (7) secret management — .env handling, .gitignore coverage; (8) CORS/security
> headers. Use Grep, Glob, Read, Bash. Return the Confirmed/Candidate/Evidence
> structure.

## Rule extraction (after all 5 return)

Consolidate the findings into candidate rules. Each rule gets:

| Field        | Meaning                                                                                                                                                           |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**       | `{DOMAIN}-{NUMBER}` — `CMT` commits, `PAT` patterns, `TST` tests, `SEC` security, `DEP` dependencies, `ERR` errors, `API` contracts, plus detected custom domains |
| **Title**    | short descriptive name, English                                                                                                                                   |
| **Severity** | suggested `HIGH` / `MEDIUM` / `LOW`                                                                                                                               |
| **Category** | the kind of concern the rule is: `logic-edges`, `async-state`, `contracts-security`, or `quality`                                                                 |
| **Evidence** | file paths / snippets supporting the rule                                                                                                                         |
| **Status**   | `Confirmed` (80%+ of relevant files) or `Candidate` (needs validation)                                                                                            |
| **Do/Don't** | real examples from the repo, correct and incorrect                                                                                                                |

Group by domain, order by severity (HIGH first). Cap candidates at ~15–20 —
merge near-duplicates rather than flooding the interview.
