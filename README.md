# Guan-Ming's Claude Code and Codex Skill CLI

[![PyPI](https://img.shields.io/pypi/v/gmccc)](https://pypi.org/project/gmccc/)
[![npm](https://img.shields.io/npm/v/gmccc)](https://www.npmjs.com/package/gmccc)

CLI to install skills for Claude Code and Codex, and run or schedule Claude
Code skills.

## Install

```bash
npx gmccc i                # npm installer
uv tool install gmccc      # PyPI full CLI
gmccc i
```

One install places the same skills in `~/.claude/skills` for Claude Code and
`~/.agents/skills` for Codex. It preserves skills from other sources.

## Invoke a skill

```text
Claude Code: /dev-pr-review
Codex:      $dev-pr-review
```

## Commands

| Command | Alias | Description |
|---|---|---|
| `gmccc install` | `gmccc i` | Install skills for Claude Code and Codex |
| `gmccc uninstall` | `gmccc u` | Remove gmccc skills and config |
| `gmccc run <name>` | `gmccc r <name>` | Run a specific job |
| `gmccc config` | `gmccc c` | Create default config file |
| `gmccc config <path>` | `gmccc c <path>` | Create config at custom path |
| `gmccc start` | | Start scheduler daemon |
| `gmccc stop` | | Stop scheduler daemon |
| `gmccc restart` | | Restart scheduler daemon |
| `gmccc info` | | Show status, jobs, and logs |
| `gmccc test` | `gmccc t` | Simulate execution |
