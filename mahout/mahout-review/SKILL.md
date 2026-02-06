---
name: mahout-review
description: Review Apache Mahout PRs for correctness and conventions.
---

# Mahout Review

## Usage
```
/mahout-review                    # local branch vs main
/mahout-review <PR_URL>           # checkout and review PR
```

## Stack
Python (qumat), Rust (qdp), uv, maturin, pytest

## Instructions

1. **Get changed files:** Use `/dev-review` flow.

2. **Review checklist:**
   - Consistency with existing patterns in `qumat/` and `qdp/`
   - Tests added in `testing/`
   - Version numbers unchanged (unless release PR)
   - No secrets or `.pypirc` included

3. **Run checks:** Use `/mahout-build`.

4. **Verdict:** Follow `/dev-review` format.
