---
name: prek
description: Run pre-commit checks using prek. Fuzzy matches check names.
---

# prek - Pre-commit Runner

Run pre-commit checks easily with fuzzy matching.

## Usage

The user invokes this skill with `/prek <query>` where query can be:
- A partial check name: `/prek compile-ui` matches `airflow-core:compile-ui-assets`
- A project name: `/prek airflow-core` runs all airflow-core checks
- `list` to show all available checks

## Instructions

1. If the argument is `list` or empty, run `prek list` and show the output
2. Otherwise, run `prek list` to get available checks, then fuzzy match the argument against check names
3. If exactly one match, run it with `prek <project>:<check>`
4. If multiple matches, show them and ask user to be more specific
5. If no matches, show similar options

## Examples

- `/prek compile-ui` → runs `prek airflow-core:compile-ui-assets`
- `/prek mypy-airflow` → runs `prek airflow-core:mypy-airflow-core`
- `/prek providers` → runs all providers checks
- `/prek list` → shows all available checks
