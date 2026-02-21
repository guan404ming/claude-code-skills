---
name: df-dev
description: Develop dialect features for datafusion-sqlparser-rs from the upstream contribution list or a description.
---

# DataFusion SQLParser Dev

## Usage
```
/df-dev                  # auto-pick next unchecked item from the TODO below
/df-dev <text description>
```

## TODO

### MSSQL (2 remaining)

- [x] `TRY/CATCH` — `BEGIN TRY...END TRY BEGIN CATCH...END CATCH`
- [x] `WHILE` — standalone statement and cursor loop support
- [x] `CURSOR` — `DECLARE CURSOR FOR`, `OPEN`, `FETCH`, `CLOSE`, `DEALLOCATE`
- [x] `THROW` statement
- [x] `WAITFOR` statement
- [ ] `OUTPUT` clause on `INSERT`/`UPDATE`/`DELETE`
- [x] `TRAN` shorthand for `TRANSACTION`
- [ ] Multiple statements without semicolons

### ClickHouse (8 remaining)

- [ ] `PARTITION BY` / `SAMPLE BY` / `TTL` in `CREATE TABLE`
- [ ] `ARRAY JOIN`
- [ ] Distributed table syntax
- [ ] Materialized views with `ENGINE` / `POPULATE`
- [ ] `CREATE DICTIONARY`
- [ ] `ALTER TABLE UPDATE` / `ALTER TABLE DELETE`
- [ ] `SYSTEM` commands
- [ ] ClickHouse-specific `WITH` clause

### Redshift (4 remaining)

- [ ] `DISTKEY` / `SORTKEY` / `DISTSTYLE` on `CREATE TABLE`
- [ ] `ENCODE` column compression
- [x] `COPY` with Redshift options
- [ ] `ANALYZE` statement
- [ ] `CREATE EXTERNAL SCHEMA`

### Hive (6 remaining)

- [ ] Complex types: `ARRAY<>`, `MAP<>`, `STRUCT<>`
- [ ] `TRANSFORM` clause
- [ ] `ADD COLUMNS` with parenthesized syntax
- [ ] `SET LOCATION` on `ALTER TABLE`
- [ ] Hive-style `CREATE INDEX`
- [ ] `DESCRIBE DATABASE`

### Snowflake (3 remaining)

- [ ] `PUT` / `GET` file staging
- [ ] `CREATE TASK` / `ALTER TASK`
- [ ] `CREATE STREAM`

### SQLite (4 remaining)

- [ ] `GLOB` operator
- [ ] `PRAGMA` statements
- [ ] `DETACH DATABASE`
- [ ] `ANALYZE`

### DuckDB (2 remaining)

- [x] Lambda functions (`list_filter(lambda x : x > 4)`)
- [ ] `SAMPLE` clause
- [ ] `ASOF JOIN`

### PostgreSQL (1 remaining)

- [x] `ANALYZE` with column specification
- [ ] `VACUUM` with options

### General (2 remaining)

- [ ] `UPDATE ... ORDER BY` (MySQL extension)
- [ ] `CREATE TABLE AS` with explicit column list

## Instructions

1. **Understand the task:** If no argument given, pick the next unchecked item from the TODO above. Otherwise, match the request to an item if applicable.

2. Follow `/dev-autodev` loop with these project-specific details:

   - **Implement:**
     - Add or modify relevant files under `src/`
     - Reuse existing parser infrastructure (e.g., `parse_begin_exception_end()`)
     - Add tests in `tests/sqlparser_<dialect>.rs`
     - For dialect-specific syntax, include a comment with the official doc link
     - **AST convention (issue #1204):** wrap new statements in a named struct, not inline enum fields.
       ```rust
       // Good: named struct
       pub struct Throw { pub error_number: Option<Expr>, ... }
       Statement::Throw(Throw)

       // Bad: inline fields
       Statement::Throw { error_number: Option<Expr>, ... }
       ```
     - **Parser convention:** parse functions should be standalone (parse the full statement including its keyword) and return the struct, not `Statement`. In the keyword dispatch, rewind the token first:
       ```rust
       Keyword::THROW => {
           self.prev_token();
           self.parse_throw().map(Into::into)
       },
       ```
     - **No early-return for empty input:** do not add short-circuit checks for semicolons or EOF at the start of parse functions. Let the function error naturally on incomplete input.

   - **Verify:**
     ```bash
     cargo test
     cargo clippy --all-targets --all-features -- -D warnings
     cargo fmt --all -- --check
     ```

   - **Update this skill's TODO:** Mark completed items with `[x]` and update the remaining count.

   - **PR title** must include the dialect name prefix (e.g., `MSSQL: Add support for ...`).
