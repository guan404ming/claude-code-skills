# gmccc

[![PyPI](https://img.shields.io/pypi/v/gmccc)](https://pypi.org/project/gmccc/)
[![npm](https://img.shields.io/npm/v/gmccc)](https://www.npmjs.com/package/gmccc)

CLI to install Guan-Ming's Claude Code Skills.

## Install Skills

```bash
npx gmccc install
npx gmccc uninstall
```

## Scheduler

```bash
uv tool install gmccc
gmccc --init       # Create ~/.config/gmccc/jobs.json
gmccc --list       # List jobs
gmccc -p <name>    # Run specific job
gmccc --dry-run    # Simulate execution
gmccc start        # Start scheduler daemon
gmccc stop         # Stop scheduler
```
