---
name: dev-pr-summarize
description: Generate a concise PR changelog summary from the current branch diff.
---

# pr-summarize - PR Changelog Generator

Generate a clear, minimal changelog for the current branch.

## Instructions

1. Run `git log --oneline -10 main` to study the repo's commit message convention (e.g., `feat:`, `MSSQL:`, `[COMPONENT]`, plain imperative, etc.)
2. Run `git log --oneline main..HEAD` to get commits on the branch
3. Run `git diff main...HEAD --stat` to see changed files
4. Run `git diff main...HEAD` to read the actual changes
5. Produce a changelog using the template below, with the title matching the repo's convention

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

- Title must follow the repo's commit message convention detected in step 1
- "Why" is one sentence max
- "How" bullets should be minimal and clear
- No fluff, no over-explanation
- Output only the changelog, nothing else
