# Consult the manifesto — stack decisions come from one place

`inspira-legal/manifesto` is the company's source of truth for stack and tooling
choices. The skills that make stack decisions — `implement`, `ship`, `review`,
`review-setup` — consult it **at runtime** when (and only when) a decision of that
kind comes up: picking a framework, a package manager, a test runner, a deploy
target, or judging whether code under review uses an approved tool.

## How to consult

1. Fetch the relevant document from the repo via `gh` (no clone):
   - `gh api repos/inspira-legal/manifesto/readme --jq .content | base64 -d` for
     the index; follow its pointers with
     `gh api repos/inspira-legal/manifesto/contents/<path> --jq .content | base64 -d`.
2. Read only what the decision at hand needs — the manifesto is consulted per
   decision, not loaded wholesale into context.
3. Apply its levels: **Obrigatório** (use it, no debate) · **Padrão** (default;
   deviating needs a stated reason) · **Alternativa** (acceptable when the default
   doesn't fit) · **Proibido** (never; flag it in review).

## Fallback — never invent a stack

If the manifesto is unreachable (offline, `gh` unauthenticated, repo access
denied): follow the current repo's existing patterns and dependencies, and **say
explicitly in the output that the manifesto was not consulted**. A warning plus
repo convention beats a guessed standard; never present an invented stack choice
as manifesto-backed.
