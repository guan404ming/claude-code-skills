# Guan-Ming's Claude Code Skill CLI

[![PyPI](https://img.shields.io/pypi/v/gmccc)](https://pypi.org/project/gmccc/)
[![npm](https://img.shields.io/npm/v/gmccc)](https://www.npmjs.com/package/gmccc)

CLI to install, run, and schedule Claude Code skills.

## Install

```bash
npx gmccc install          # npm (gmccc install/uninstall only)
uv tool install gmccc      # PyPI (full CLI)
```

## Commands

| Command | Alias | Description |
|---|---|---|
| `gmccc install` | `gmccc i` | Install skills via openskills |
| `gmccc uninstall` | `gmccc u` | Remove skills and config |
| `gmccc run <name>` | `gmccc r <name>` | Run a specific job |
| `gmccc config` | `gmccc c` | Create default config file |
| `gmccc config <path>` | `gmccc c <path>` | Create config at custom path |
| `gmccc start` | | Start scheduler daemon |
| `gmccc stop` | | Stop scheduler daemon |
| `gmccc info` | | Show status, jobs, and logs |
| `gmccc test` | `gmccc t` | Simulate execution |
