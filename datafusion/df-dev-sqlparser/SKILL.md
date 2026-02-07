---
name: df-dev-sqlparser
description: Develop dialect features for datafusion-sqlparser-rs from the upstream contribution list or a description.
---

# DataFusion SQLParser Dev

## Usage
```
/df-dev-sqlparser <dialect> <feature>
/df-dev-sqlparser <text description>
```

## Instructions

1. **Understand the task:** Check `target/NOTE.md` for the upstream contribution list. Match the request to an unchecked item if applicable.

2. **Implement:**
   - Add or modify relevant files under `src/`
   - Reuse existing parser infrastructure (e.g., `parse_begin_exception_end()`)
   - Add tests in `tests/sqlparser_<dialect>.rs`
   - For dialect-specific syntax, include a comment with the official doc link

3. **Run checks:**
   ```bash
   cargo test
   cargo clippy --all-targets --all-features -- -D warnings
   cargo fmt --all -- --check
   ```

4. **Update `target/NOTE.md`:** Mark completed items with `[x]`.

5. **PR summary:** Use `/dev-pr-summarize` to generate a changelog for the changes. PR title must include the dialect name prefix (e.g., `MSSQL: Add support for ...`).
