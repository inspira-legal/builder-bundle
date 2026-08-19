---
name: code-deep-research
description: Pesquisa profunda em código. Encontra, clona e explora repositórios reais, e verifica adversarialmente os achados contra o source antes de reportar. Use quando o usuário disser "acha repos de", "como outros implementam", "pesquisa de código", "mergulha em como [projeto] funciona", "acha exemplos de", "clona e analisa", ou perguntar sobre padrões de implementação, comparação de bibliotecas ou arquitetura de codebases. Pra pesquisa de tópicos não-código, use a skill deep-research nativa.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.0.0
---

# Code deep research

Find, clone, and explore real repositories to understand implementation patterns and architectures, then **verify every load-bearing claim against the actual source** before it reaches the report. The depth comes from the loop: plan → fan out → verify → synthesize, repeated until the open questions run dry.

## How it works

Two query types, two entry paths:

| Query Type                                 | Example                                   | Path                              |
| ------------------------------------------ | ----------------------------------------- | --------------------------------- |
| **Discovery**: find repos for a topic      | "find react state management libs"        | Scout (script) → Select → Explore |
| **Targeted**: explore a known repo/project | "how does vscode handle WSL server build" | Skip scout → Explore directly     |

Both paths converge on the same verify-and-synthesize back half.

## Workflow

### 1. Plan the research

Before searching, turn the request into a concrete plan:

- **Query type**: discovery (find repos) or targeted (explore known repo/project)
- **Claims to answer**: the 2-5 specific questions the report must settle (e.g. "how does X handle concurrency?", "which approach scales to N?"). These become the verification checklist later.
- **What to find**: libraries, frameworks, implementations, patterns
- **Why**: comparing options, learning patterns, finding reference implementations
- **Constraints**: language, framework, license, activity level

### 2a. Discovery path: scout

Generate **2-3 search queries** from different angles, plus **1-2 GitHub topic slugs** (kebab-case tags like `state-management`, `orm`, `cli`), then run the bundled script (path relative to this skill's directory):

```
python scripts/search_repos.py "query 1" "query 2" --topic topic-slug-1 --topic topic-slug-2
```

Optional flags: `--limit 20`, `--language python`, `--min-stars 500`

Keyword queries match repo name/description. Topic searches find repos tagged with that topic (catches repos with creative names). Results are merged, deduped, and filtered to 100+ stars by default. Ordered by GitHub's relevance ranking.

Returns a JSON list with: `fullName`, `description`, `stargazersCount`, `updatedAt`, `language`, `url`.

### 2b. Targeted path: resolve the repo

The user is asking about a specific project. Resolve the repo:

- If the user names it explicitly (e.g. "vscode", "next.js") → map to the GitHub URL (e.g. `microsoft/vscode`, `vercel/next.js`)
- If ambiguous, run a quick search: `python scripts/search_repos.py "project name" --min-stars 0` and pick the top match
- Skip straight to **Step 4: Explore**

### 3. Evaluate and select (discovery path only)

From the script output:

- Review the ranked list against the plan's claims
- **Select 1-3 repos** for deep exploration (ask the user if unclear which to prioritize)

Present a quick summary:

```
Found [N] relevant repos. Top picks for deep dive:
1. **owner/repo** (⭐ N): [why relevant to the claims]
2. **owner/repo** (⭐ N): [why]

Cloning and exploring these now...
```

### 4. Explore (parallel)

Launch all agents in parallel:

- **1 explorer per repo** (`general-purpose` agent): clone and analyze the codebase
- **1 web researcher for all repos** (`general-purpose` agent): docs, blog posts, design discussions

Each explorer must back claims with **evidence** (`file:path:line` citations) so the verify step has something concrete to re-check.

**Explorer prompt** (one per repo):

```
Clone and analyze https://github.com/owner/repo to /tmp/research-repos/owner-repo (shallow, --depth 1).

Answer these claims: [the planned claims relevant to this repo]

Return: purpose, stack, directory layout, architecture pattern, and for each claim a finding
with a file:path:line citation as evidence. Keep under 600 words.
```

**Web researcher prompt** (single agent, all repos):

```
Research these repositories: owner/repo1, owner/repo2, ...

For each, find: official docs, blog posts, architecture discussions, design decisions.
Focus on: [the planned claims]. Return findings grouped by repo, with source URLs. Under 300 words per repo.
```

### 5. Verify (adversarial)

The explorers can be confidently wrong. For each **load-bearing claim** (one that drives a recommendation or comparison-table cell), spawn an independent verifier that **tries to refute it** against the cloned source it already has on disk:

**Verifier prompt** (one per claim, parallel):

```
Claim: "[claim]", cited at [file:path:line] in /tmp/research-repos/owner-repo.

Read that file and the surrounding code. Try to refute the claim. Report:
verdict (holds / partial / refuted), the code you actually read, and a corrected statement if wrong.
Default to "refuted" if the cited evidence doesn't support it.
```

Keep the claims that hold, rewrite the partial ones to what the code actually shows, drop the refuted ones. A refuted load-bearing claim sends you back to Step 4 (explore deeper) or Step 2 (scout a better repo). That's the loop.

### 6. Synthesize and report

Combine the **verified** findings. Every claim traces to `file:path:line` and carries a confidence:

```markdown
## Code Deep Research: [topic]

### Summary

[What was found and the key takeaway]

### Repositories Analyzed

#### 1. owner/repo

- **URL**: https://github.com/owner/repo
- **Stack**: [languages, frameworks]
- **Architecture**: [pattern description]
- **Key insight**: [most valuable finding], `path/to/file.ts:42` (verified)
- **Cloned to**: `/tmp/research-repos/owner-repo`

### Pattern Comparison

| Aspect       | repo-1 | repo-2 | repo-3 |
| ------------ | ------ | ------ | ------ |
| Architecture | ...    | ...    | ...    |
| State mgmt   | ...    | ...    | ...    |

### Recommendations

[Which approach fits the user's needs and why]

### Confidence & Open Questions

[Claims that only partially held, anything verification couldn't settle, conflicting evidence]

### Cloned Repos

- `/tmp/research-repos/owner-repo1`
- `/tmp/research-repos/owner-repo2`
```

### 7. Loop or offer next steps

If a planned claim is still unanswered or a load-bearing claim was refuted, run another round (scout more / explore deeper) until the open questions dry up. Once they do, offer:

- "Want me to read specific files in any of these repos?"
- "Should I extract [pattern] from [repo] into your project?"
- "Want a deeper comparison of [aspect]?"

## Guidelines

- **Plan the claims first**: the verify step is only as good as the claims it checks
- **Pick the right path**: discovery queries scout first, targeted queries go straight to explore
- **Parallel everywhere**: explorers and verifiers each fan out in parallel
- **Verify before asserting**: an unverified claim is an open question, not a finding
- **Cite to `file:line`**: every claim traces back to code or a source URL
- **Shallow clones** to `/tmp/research-repos/` (`--depth 1`): fast, easy cleanup, left in place for follow-up
- **Ask before exploring more than 3 repos**: each clone costs time
- **Compare when possible**: side-by-side beats isolated summaries
