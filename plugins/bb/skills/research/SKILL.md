---
name: research
description: Researches a topic across code, content and visual references, verifies every load-bearing claim against its evidence, and writes the report to the spec folder of the slug. Runs to the end without questions, so an agent can call it. Use when the user says "research this", "find repos that", "how do others implement", "code research", "dig into how [project] works", "find examples of", "clone and analyze", "look up the docs for", "compare libraries", "find design references", "how do apps do [pattern]", "show me screens of", "pesquisa isso", "pesquise como", "como os outros implementam", "acha repos que", "procura exemplos de", "compara bibliotecas", "referências visuais de", "como os apps fazem", or asks about implementation patterns, library comparisons, codebase architecture, or UI patterns. /bb:spec calls it before a draft that depends on outside facts.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 3.0.0
---

# Research

Research a topic and write a verified report to `.bb/<slug>/research.md`. The research
picks the fronts the topic needs (code, content, visual), gathers findings with evidence,
and passes every load-bearing claim through an independent verifier that tries to refute
it. The depth comes from the loop: plan, fan out, verify, synthesize, repeated within a
fixed cap.

## How it runs

The research is often called by an agent with nobody watching: `/bb:spec` runs it before
a draft, and `/bb:orchestrate` side sessions run `/bb:spec`. Four rules follow from that.

- **No questions.** Every choice below has a default. Make it, write it in the report, and
  keep going.
- **A fixed cap.** At most three repositories cloned, at most three verify rounds (the
  first pass plus two reruns), at most six images per page and 30 per run. What the cap
  leaves out goes in the report's open section.
- **No commit.** The research writes `research.md` and leaves it uncommitted. Called by
  `/bb:spec`, it is committed with `spec.md`. Called alone, the caller decides.
- **No gate.** It ends by returning a short summary and the path, and stops. Called by
  `/bb:spec`, the spec continues into the draft.

## The three fronts

A topic takes one or more fronts, and they combine. "How do apps do onboarding with a
paywall" takes visual and content; "how does vscode build its WSL server" takes code and
content.

| front   | when it fits                                        | evidence                                | tools it needs                          |
| ------- | --------------------------------------------------- | --------------------------------------- | --------------------------------------- |
| code    | reading real code settles the question              | `file:line` in a cloned repo            | `git`, plus `gh` to search repositories |
| content | docs, articles, discussions, changelogs settle it   | a URL plus the passage that supports it | web search and web fetch                |
| visual  | the question is how a screen, flow or pattern looks | the page URL and the image it shows     | web search and `python3`                |

The visual front works from the open web with no account: public design galleries and the
real products' own sites. A browser screenshot is optional and covers only pages the image
script cannot read.

## Workflow

### 1. Resolve the slug and the report path

- **Called by `/bb:spec`**: use the slug it passes, as given. The report goes to `.bb/<slug>/research.md`,
  beside `spec.md`.
- **Called alone**: derive a kebab slug from the topic, two to five lowercase ASCII words
  joined by hyphens (`onboarding-paywall`, `vscode-wsl-server`). A later `/bb:spec` on the
  same idea then finds the report.
- **Called alone, and `.bb/<slug>/` already holds another idea's work** (its `spec.md` or another record):
  append `-research` to the slug, and keep appending a number until the folder is free or
  holds this topic's earlier report.

A rerun on the same slug rewrites `research.md` whole. The previous version lives in git.
A folder that holds only `research.md` is fine: the spec selection lists slugs by
`.bb/*/spec.md` and pass over it.

### 2. Plan the research

Turn the topic into a plan before searching:

- **Questions**: the 2 to 5 questions the report must settle ("how does X handle concurrency?",
  "which approach scales to N?"). They become the verify checklist.
- **Fronts**: which of code, content and visual the questions need.
- **Constraints**: language, framework, license, platform, activity level, from the topic
  or the caller's context.

Then check the tools for each chosen front. A front with no tool to run it (no web search,
no `gh` and no named repo, no `python3`) is skipped and named in the open section, and the
research continues on the fronts it has. When no chosen front can run, write the report
anyway: it states that nothing could be researched and lists what each front needed.

### 3. Set up the work folder

Clones and images go outside the worktree, so they never land in a commit. Get the
platform's temp folder (Windows has no `/tmp`):

```
python3 -c "import tempfile; print(tempfile.gettempdir())"
```

Use `TEMP/bb-research/SLUG/` as the work folder, with clones under
`TEMP/bb-research/SLUG/repos/OWNER-REPO`. The image script makes its own new folder.

### 4. Fan out per front

Run one agent per unit of work below, all in parallel, with `general-purpose` agents. When
the session has no Agent tool, run the same prompts inline, one at a time, in the same
order. Each finding carries its evidence, so the verify step has something concrete to
re-check.

Load only the reference of each front the plan picked:

| front   | reference                     |
| ------- | ----------------------------- |
| code    | `references/front-code.md`    |
| content | `references/front-content.md` |
| visual  | `references/front-visual.md`  |

### 5. Verify (adversarial)

Findings can be confidently wrong. For each **load-bearing claim** (one that drives the
recommendation or a comparison cell), run an independent verifier that tries to refute it
against its own evidence. One verifier per claim, in parallel, or inline one at a time
with no Agent tool.

**Verifier prompt**:

```
Claim: "[claim]"
Evidence: [file:path:line in WORKDIR/repos/OWNER-REPO | URL and the quoted passage | page URL and local image path]

Open the evidence yourself: read the cited code and the code around it, fetch the page
and find the passage, or open the image with Read. Try to refute the claim.
Report: verdict (holds / partial / refuted), what you actually read or saw, and a
corrected statement when it is wrong. Default to "refuted" when the evidence does not
support the claim.
```

Keep the claims that hold. Rewrite the partial ones to what the evidence shows. Drop the
refuted ones. A claim with no verdict is an open question, never a finding.

### 6. Loop within the cap

A refuted load-bearing claim, or a planned question still unanswered, sends the research
back for another round: explore deeper in the repositories already cloned, scout a better
one while under three clones, search new sources or reference pages. Run at most three
verify rounds in total. After the last round, what is still open goes to the open section.
When every load-bearing claim ends refuted, the report says nothing was verified and lists
what each round tried.

### 7. Write the report

Write `.bb/<slug>/research.md` in the shape of `references/report.md`, replacing any
earlier version whole.

### 8. Return the summary

Return three to five lines: the recommendation in one sentence, how many claims held, what
stayed open, and the path `.bb/<slug>/research.md`. Leave the file uncommitted, and stop.

## Guidelines

- **Plan the questions first**: the verify step is only as good as the claims it checks.
- **Fan out in parallel**: explorers, researchers and verifiers each run side by side.
- **Verify before asserting**: an unverified claim is an open question, not a finding.
- **Cite every claim**: `file:line`, a URL with its passage, or a page with its image.
- **Shallow clones** (`--depth 1`) in the temp work folder, left in place for follow-up.
- **Compare when possible**: side by side beats isolated summaries.
