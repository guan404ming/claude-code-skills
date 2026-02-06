---
name: tvm-dev-relax
description: Resolve a TODO or fix an issue in the TVM relax folder.
---

# TVM Dev Relax

## Usage
```
/tvm-dev-relax                    # pick a TODO from relax/
/tvm-dev-relax <GitHub issue URL> # fix a reported issue
```

## Instructions

### If no argument (TODO mode):
1. **Checkout main** and find a TODO in the `relax/` folder. Skip items with existing PRs or branches.

### If given an issue URL:
1. Fetch with `gh issue view <URL>` to get the problem description.
2. Write a minimal Python repro script and run it to confirm the error. If it can't be reproduced, stop and report.

### Common steps:

2. **Create a branch** for the feature/fix.

3. **Implement** — follow existing coding style, keep comments minimal.

4. **Add tests** — parameterized, concise, in the right place following conventions.

5. **If fixing an issue:** Re-run the repro script to verify it passes, then delete it.

6. **Verify:**

   | Trigger | Command |
   |---|---|
   | `*.cc`, `*.h`, `*.cpp` changed | `make -C build -j8` |
   | `*.py` changed | `bash docker/lint.sh -i python_format pylint` |
   | `*.cc`, `*.h` changed | `bash docker/lint.sh -i clang_format cpplint` |
   | `*.java`, `*_jni.cc` changed | `bash docker/lint.sh jnilint` |
   | Any file | `bash docker/lint.sh asf` |
   | Python tests | `pytest tests/python -xv` |

7. **Commit** with `git commit -n -m "msg"` — no co-author tags.

8. **PR summary:** Use `/dev-pr-summarize` to generate a changelog.
