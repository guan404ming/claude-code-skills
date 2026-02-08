# Guan-Ming's Claude Code Skills

[![PyPI](https://img.shields.io/pypi/v/gmccc)](https://pypi.org/project/gmccc/)
[![npm](https://img.shields.io/npm/v/gmccc)](https://www.npmjs.com/package/gmccc)

Custom skills for Claude Code.

## Install Skills with npx

```bash
npx gmccc install
npx gmccc uninstall
```

## Scheduler (gmccc CLI)

```bash
uv tool install gmccc
gmccc --init       # Create ~/.config/gmccc/jobs.json
gmccc --list       # List jobs
gmccc -p <name>    # Run specific job
gmccc --dry-run    # Simulate execution
gmccc start        # Start scheduler daemon
gmccc stop         # Stop scheduler
```
