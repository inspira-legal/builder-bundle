---
name: research-topic
description: Deep research on any topic using parallel agents. Use when user says "research", "investigate", "deep dive into", "what do we know about", "explore the topic of", or asks a broad question requiring multi-source investigation. Do NOT use for code-specific research or finding repos (use /ofc:research-code instead).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Research

Deep, multi-angle research using parallel agents to investigate a topic and synthesize findings.

## How It Works

This skill spawns parallel research agents that each tackle a different angle of the question, then synthesizes their findings into a unified report.

## Workflow

### 1. Understand the Question

Parse the user's research request and identify:

- **Core question** — what specifically needs answering
- **Angles** — 2-4 distinct research angles to explore in parallel
- **Scope** — breadth vs depth preference

### 2. Spawn Parallel Research Agents

Launch **2-4 agents in parallel** using the Agent tool. Each agent gets a focused sub-question:

**Standard research pattern** (adapt angles to the topic):

| Agent   | Focus                                                                | Subagent Type           |
| ------- | -------------------------------------------------------------------- | ----------------------- |
| Agent 1 | Core question — direct search for the primary answer                 | research:web-researcher |
| Agent 2 | Context & background — history, ecosystem, alternatives              | research:web-researcher |
| Agent 3 | Technical details — specs, docs, APIs, implementation details        | research:doc-analyst    |
| Agent 4 | Community perspective — discussions, opinions, real-world experience | research:web-researcher |

**Each agent prompt MUST include:**

- The specific sub-question to research
- A reminder to be concise (under 500 words)

### 3. Synthesize Findings

After all agents return, combine their findings into a single report:

```markdown
## Research: [topic]

### Summary

[2-3 sentence executive summary answering the core question]

### Key Findings

- [Finding 1 — synthesized from multiple agents]
- [Finding 2]
- [Finding 3]

### Details

[Organized narrative combining all agent findings, grouped by theme]

### Sources

[Deduplicated list of all sources cited, numbered]

### Open Questions

[What couldn't be answered, conflicting info, areas needing deeper research]
```

### 4. Offer Next Steps

After presenting the report, offer:

- "Want me to dig deeper into any of these findings?"
- "Should I research [related topic] next?"
- "Want me to switch to `/ofc:research-code` to find implementations?"

## Guidelines

- **Always use parallel agents** — never do sequential research when angles are independent
- **Minimum 2 agents, maximum 4** — more than 4 rarely adds value
- **Tailor angles to the topic** — don't force a template that doesn't fit
- **Deduplicate** — agents may find the same sources; merge, don't repeat
- **Cite everything** — every claim should trace back to a source
- **Flag uncertainty** — if agents disagree, present both sides
- **Be concise** — the synthesis should be shorter than the sum of agent outputs
