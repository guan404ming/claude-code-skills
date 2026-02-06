---
name: af-review-ui
description: Review Airflow UI code for consistency, best practices, and conventions.
---

# Review Airflow UI

## Usage
```
/review-airflow-ui                    # local branch vs main
/review-airflow-ui <PR_URL>           # checkout and review PR
```

## Stack
React 19, Chakra UI v3, React Query, TypeScript, Vite, pnpm

## Review Checklist
- Consistency with existing patterns
- Reuse components from `src/components/ui/`
- Use types from `openapi-gen/` (never hand-write API types)
- Props with `readonly`: `type Props = { readonly x: T }`
- Return `undefined` not `null`

## Instructions

1. Get changed files:
   - PR: `gh pr checkout <URL>` then `gh pr diff --name-only`
   - Local: `git diff main --name-only`

2. If backend API changed, remind to run:
   ```bash
   prek airflow-core:generate-openapi-spec
   cd airflow-core/src/airflow/ui && pnpm codegen
   ```

3. Run `prek airflow-core:ts-compile-lint-ui`

4. Only focus on the changes made in this PR. Do not review unchanged code.

5. List issues as polite GitHub comment suggestions (do NOT post). Only report real issues — if there are fewer than 5, that's fine. Do not pad the list.
   ```
   1. `src/Foo.tsx:42` - Consider using existing `ErrorAlert` component.
   2. `src/Bar.tsx:15` - Type should come from `openapi-gen/`.
   ```

6. Start the verdict with a one-sentence summary of whether this PR's change is valuable or unnecessary.

7. End with a verdict:
   - **Approved** — no issues found, good to merge.
   - **Approved with comments** — minor suggestions, but OK to merge as-is.
   - **Request changes** — blocking issues that should be fixed before merge.
