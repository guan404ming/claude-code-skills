---
name: pr-summarize
description: Generate a concise PR changelog summary from the current branch diff.
---

# pr-summarize - PR Changelog Generator

Generate a clear, minimal changelog for the current branch.

## Instructions

1. Run `git log --oneline main..HEAD` to get commits on the branch
2. Run `git diff main...HEAD --stat` to see changed files
3. Run `git diff main...HEAD` to read the actual changes
4. Produce a changelog using the template below

## Template

```
## <Short imperative title describing the change>

## Why

<One sentence explaining the motivation or problem>

## How

- <Bullet points describing what was done, keep each line short>
- <Focus on what changed, not implementation details>
```

## Rules

- Title must be short and imperative (e.g. "Add X", "Fix Y")
- "Why" is one sentence max
- "How" bullets should be minimal and clear
- No fluff, no over-explanation
- Output only the changelog, nothing else
