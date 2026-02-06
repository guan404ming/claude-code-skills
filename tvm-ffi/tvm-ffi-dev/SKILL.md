---
name: tvm-ffi-dev
description: Develop and verify TVM FFI changes.
---

# TVM FFI Dev

## Usage
```
/tvm-ffi-dev <GitHub issue URL>
/tvm-ffi-dev <text description>
```

## Instructions

1. **Understand the task:**
   - If given a GitHub issue URL, fetch with `gh issue view <URL>`
   - Write a minimal Python repro script and run it to confirm the error. If it can't be reproduced, stop and report.
   - If given text, use that as the requirement

2. **Implement** — follow existing coding style, keep comments minimal.

3. **Build and test:** Use `/tvm-ffi-build`, then `/tvm-ffi-test`.

5. **If fixing an issue:** Re-run the repro script to verify it passes, then delete it.

6. **PR summary:** Use `/dev-pr-summarize` to generate a changelog.
