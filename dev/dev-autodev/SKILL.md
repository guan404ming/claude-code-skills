---
name: dev-autodev
description: Common autodev loop for branch, implement, test, commit, and PR summary.
---

# Autodev Loop

Shared development workflow used by project-specific dev skills.

## Steps

1. **Create a branch** for the feature/fix.

2. **Implement** — follow existing coding style, keep changes minimal.

3. **Add tests** — parameterized, concise, following project conventions.

4. **Verify** — run the project's build and test commands.

5. **Commit** with `git commit -n -m "msg"` — no co-author tags.

6. **PR summary:** Use `/dev-pr-summarize` to generate a changelog.
