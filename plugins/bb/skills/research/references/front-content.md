# The content front

Loaded by step 4 of `SKILL.md` when the plan picked the content front. Its evidence is a URL plus the passage that supports it, quoted.

**Content researcher prompt** (one per question cluster, or one for all when they are few):

```
Research: [the planned questions], in the context of [topic and constraints].

Search the web. Prefer official docs, source repositories, changelogs and design
discussions over secondary summaries. For each finding, return the claim, the source URL,
and the exact passage that supports it, quoted. Mark a claim with no quotable passage as
unsupported. Keep it under 500 words.
```
