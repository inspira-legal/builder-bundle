---
name: research-code
description: Code-focused research that finds, clones, and explores relevant repositories. Use when user says "find repos for", "how do others implement", "code research", "find examples of", "explore how [project] works", "clone and analyze", or asks about implementation patterns, library comparisons, or codebase architecture. Do NOT use for general topic research (use /ofc:research-topic instead).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Code Research

Find, clone, and explore relevant repositories to understand implementation patterns, architectures, and real-world code.

## How It Works

Two query types, two paths:

| Query Type                                  | Example                                   | Path                              |
| ------------------------------------------- | ----------------------------------------- | --------------------------------- |
| **Discovery** — find repos for a topic      | "find react state management libs"        | Scout (script) → Select → Explore |
| **Targeted** — explore a known repo/project | "how does vscode handle WSL server build" | Skip scout → Explore directly     |

## Workflow

### 1. Understand the Research Goal

Parse the user's request and identify:

- **Query type** — discovery (find repos) or targeted (explore known repo/project)
- **What to find** — libraries, frameworks, implementations, patterns
- **Why** — comparing options, learning patterns, finding reference implementations
- **Constraints** — language, framework, license, activity level preferences

### 2a. Discovery Path: Scout

Generate **2-3 search queries** from different angles, plus **1-2 GitHub topic slugs** (kebab-case tags like `state-management`, `orm`, `cli`), then run the bundled script (path relative to this skill's directory):

```
python scripts/search_repos.py "query 1" "query 2" --topic topic-slug-1 --topic topic-slug-2
```

Optional flags: `--limit 20`, `--language python`, `--min-stars 500`

Keyword queries match repo name/description. Topic searches find repos tagged with that topic (catches repos with creative names). Results are merged, deduped, and filtered to 100+ stars by default. Ordered by GitHub's relevance ranking.

Returns a JSON list with: `fullName`, `description`, `stargazersCount`, `updatedAt`, `language`, `url`.

### 2b. Targeted Path: Resolve Repo

The user is asking about a specific project. Resolve the repo:

- If the user names it explicitly (e.g. "vscode", "next.js") → map to the GitHub URL (e.g. `microsoft/vscode`, `vercel/next.js`)
- If ambiguous, run a quick search: `python scripts/search_repos.py "project name" --min-stars 0` and pick the top match
- Skip straight to **Step 4: Explore**

### 3. Evaluate & Select (discovery path only)

From the script output:

- Review the ranked list against the user's goal
- **Select 1-3 repos** for deep exploration (ask user if unclear which to prioritize)

Present a quick summary:

```
Found [N] relevant repos. Top picks for deep dive:
1. **owner/repo** (⭐ N) — [why relevant to user's question]
2. **owner/repo** (⭐ N) — [why]
3. **owner/repo** (⭐ N) — [why]

Cloning and exploring these now...
```

### 4. Explore (Parallel)

Launch all agents in parallel:

- **1 explorer per repo** (`research:repo-explorer`) — clone and analyze codebase
- **1 web researcher for all repos** (`research:web-researcher`) — search for docs, blog posts, discussions

**Explorer prompt** (one per repo):

```
Clone and analyze https://github.com/owner/repo to /tmp/research-repos/owner-repo

Focus on: [specific aspect user cares about]

Return: purpose, stack, directory layout, architecture pattern, key files, notable techniques.
Keep under 600 words.
```

**Web researcher prompt** (single agent, all repos):

```
Research these repositories:
- owner/repo1
- owner/repo2
- owner/repo3

For each, find: official docs, blog posts, architecture discussions, design decisions.
Focus on: [specific aspect user cares about]

Return findings grouped by repo. Keep under 300 words per repo.
```

### 5. Synthesize & Report

Combine all explorer findings:

```markdown
## Code Research: [topic]

### Summary

[What was found and the key takeaway]

### Repositories Analyzed

#### 1. owner/repo

- **URL**: https://github.com/owner/repo
- **Stack**: [languages, frameworks]
- **Architecture**: [pattern description]
- **Key insight**: [most valuable finding]
- **Cloned to**: `/tmp/research-repos/owner-repo`

#### 2. owner/repo

...

### Pattern Comparison

| Aspect       | repo-1 | repo-2 | repo-3 |
| ------------ | ------ | ------ | ------ |
| Architecture | ...    | ...    | ...    |
| State mgmt   | ...    | ...    | ...    |
| Testing      | ...    | ...    | ...    |

### Recommendations

[Which approach fits the user's needs and why]

### Cloned Repos

All repos are available locally for further exploration:

- `/tmp/research-repos/owner-repo1`
- `/tmp/research-repos/owner-repo2`
```

### 6. Offer Next Steps

- "Want me to read specific files in any of these repos?"
- "Should I extract [specific pattern] from [repo] into your project?"
- "Want a deeper comparison of [aspect]?"

## Guidelines

- **Pick the right path** — discovery queries scout first, targeted queries go straight to explore
- **Parallel explorers** — explorer agents run in parallel
- **Shallow clones** — always `--depth 1` to save time and space
- **Clone to `/tmp/research-repos/`** — consistent location, easy cleanup
- **Ask before exploring more than 3 repos** — each clone costs time
- **Focus on architecture** — the user wants patterns and structure, not to read every line
- **Compare when possible** — side-by-side comparisons are more valuable than isolated summaries
- **Leave repos cloned** — the user may want to explore further after the report
