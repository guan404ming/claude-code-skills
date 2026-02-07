---
name: tvm-dev
description: Resolve a TODO or fix an issue in the TVM relax folder.
---

# TVM Dev

## Usage
```
/tvm-dev                    # pick a TODO from relax/
/tvm-dev <GitHub issue URL> # fix a reported issue
```

## Instructions

### If no argument (TODO mode):
1. **Checkout main** and find a TODO in the `relax/` folder. Skip items with existing PRs or branches.

### If given an issue URL:
1. Fetch with `gh issue view <URL>` to get the problem description.
2. Write a minimal Python repro script and run it to confirm the error. If it can't be reproduced, stop and report.

### Common steps:

Follow `/dev-autodev` loop with these project-specific details:

- **If fixing an issue:** Re-run the repro script to verify it passes, then delete it.
- **Verify:** Use `/tvm-build` if C/C++ changed, then `/tvm-test`.
