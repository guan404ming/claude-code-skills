---
name: tvm-build
description: Build TVM C++ project.
---

# TVM Build

## When to run
Run if any `*.cc`, `*.h`, `*.cpp` files changed.

## Command
```bash
make -C build -j8

# or
cd tvm/build && ninja -j8
```
