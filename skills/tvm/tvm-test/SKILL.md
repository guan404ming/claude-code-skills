---
name: tvm-test
description: Run TVM lint and tests.
---

# TVM Test

## Commands

| Trigger | Command |
|---|---|
| `*.py` changed | `bash docker/lint.sh -i python_format pylint` |
| `*.cc`, `*.h` changed | `bash docker/lint.sh -i clang_format cpplint` |
| `*.java`, `*_jni.cc` changed | `bash docker/lint.sh jnilint` |
| Any file | `bash docker/lint.sh asf` |
| Python tests | `pytest tests/python -xv` |

## Local Lint (without Docker)

```bash
# clang-format (check)
uv tool run clang-format --dry-run --Werror <files>

# clang-format (fix in place)
uv tool run clang-format -i <files>

# cpplint
uv run cpplint --linelength=100 <files>
```
