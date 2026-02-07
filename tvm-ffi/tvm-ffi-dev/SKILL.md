---
name: tvm-ffi-dev
description: Develop and verify TVM FFI changes.
---

# TVM FFI Dev

## Usage
```
/tvm-ffi-dev                  # auto-run: pick next item or continue current work
/tvm-ffi-dev <GitHub issue URL>
/tvm-ffi-dev <text description>
```

## Instructions

1. **Understand the task:**
   - If given a GitHub issue URL, fetch with `gh issue view <URL>`
   - Write a minimal Python repro script and run it to confirm the error. If it can't be reproduced, stop and report.
   - If given text, use that as the requirement

2. Follow `/dev-autodev` loop with these project-specific details:

   - **If fixing an issue:** Re-run the repro script to verify it passes, then delete it.
   - **Verify:** Use `/tvm-ffi-build`, then `/tvm-ffi-test`.

## Code style

- C++: prefer `std::string_view`, `static_cast`, STL algorithms over manual loops
- C++: add move-qualified overloads (`&&`) for accessors returning owned values
- C++: align new APIs with C++ std equivalents (e.g. `std::expected`, `std::unexpected`), list deviations explicitly
- C++: use `std::move` on optionals (`*std::move(val)`), avoid double checking
- C++: fast path first (value before error), minimize branches
- C++: ban implicit conversions for error types, use explicit constructors (e.g. `Unexpected(Error(...))`)
- Python: reuse stdlib types (e.g. `dataclasses.KW_ONLY`) instead of redefining
- Tests: call actual registered FFI functions, not reimplement logic
- Tests: use `ASSERT_TRUE` for null checks before dereferencing
- Tests: no duplicate assertions, remove redundant checks
- Extract duplicated logic into helpers
- New user-facing APIs need documentation with usage examples
- Preserve original error info on rethrow, not generic messages
