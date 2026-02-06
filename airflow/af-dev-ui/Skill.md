---
name: af-dev-ui
description: Develop Airflow UI features from an issue link or text description.
---

# Airflow UI Dev

## Usage
```
/af-dev-ui <GitHub issue URL>
/af-dev-ui <text description>
```

## Stack
React 19, Chakra UI v3, React Query, TypeScript, Vite, pnpm

## Conventions
- Minimal changes — reuse, don't rebuild
- Reuse from existing `src/` folders before creating new files:
  - `components/ui/` — shared UI components
  - `constants/` — app-wide constants
  - `utils/` — utility functions
  - `hooks/` — custom React hooks
  - `queries/` — React Query hooks
  - `context/` — React context providers
  - `layouts/` — page layouts
- Use types from `openapi-gen/` (never hand-write API types)
- Props with `readonly`: `type Props = { readonly x: T }`
- Return `undefined` not `null`
- Prevent duplication
- Keep comments simple and clear

## Instructions

1. **Understand the task:**
   - If given a GitHub issue URL, fetch it with `gh issue view <URL>` to get requirements
   - If given text, use that as the requirement

2. **Read before writing:** Study existing code and patterns in the area you're changing. Reuse what's there.

3. **If backend endpoint code changed:**
   ```bash
   prek airflow-core:generate-openapi-spec
   cd airflow-core/src/airflow/ui && pnpm codegen
   ```
   Then run `prek airflow-core:ts-compile-lint-ui`

4. **Implement** the minimal change needed. Follow existing patterns.

5. **Verify with Playwright:** Use `browser_snapshot` (accessibility snapshot) to inspect your changes in the browser. Do NOT use `browser_take_screenshot`. Navigate to the relevant page and verify the UI behaves correctly.

6. **Lint check:** Run `prek airflow-core:ts-compile-lint-ui` before finishing.

7. **PR summary:** Use `/dev-pr-summarize` to generate a changelog for the changes.
