---
name: dev-pr-review
description: Review code changes for consistency, best practices, and conventions.
---

# Dev Review

## Usage
```
/dev-pr-review                    # local branch vs main
/dev-pr-review <PR_URL>           # checkout and review PR
```

## Instructions

1. **Get changed files:**
   - PR: `gh pr checkout <URL>` then `gh pr diff --name-only`
   - Local: `git diff main --name-only`

2. **Read the changed files.** Only focus on the changes — do not review unchanged code.

3. **Review checklist:**
   - Consistency with existing patterns
   - Reuse existing utilities, components, and helpers
   - No duplication
   - Minimal and clear comments

4. **List issues** as polite suggestions. Only report real issues — do not pad the list.
   ```
   1. `src/Foo.ts:42` - Consider reusing existing `handleError` utility.
   2. `src/Bar.ts:15` - Duplicates logic from `src/utils/parse.ts`.
   ```

5. **Start** the verdict with a one-sentence summary of whether this change is valuable or unnecessary.

6. **End** with a verdict:
   - **Approved** — no issues found, good to merge.
   - **Approved with comments** — minor suggestions, but OK to merge as-is.
   - **Request changes** — blocking issues that should be fixed before merge.
