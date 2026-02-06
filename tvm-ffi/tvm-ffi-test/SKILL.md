---
name: tvm-ffi-test
description: Run TVM FFI tests.
---

# TVM FFI Test

## Commands

| Test | Command |
|---|---|
| C++ tests | `ctest --test-dir build --output-on-failure` |
| Python tests | `.venv/bin/pytest tests/python/ -v` |
| Specific C++ | `ctest --test-dir build -R <test_name> --output-on-failure` |
| Specific Python | `.venv/bin/pytest tests/python/<file>::<test> -v` |
