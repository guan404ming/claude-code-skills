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
