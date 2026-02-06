---
name: dev-git-setup
description: Set up git aliases.
---

# Dev Git Setup

## Usage
```
/dev-git-setup
```

## Aliases

```bash
git config --global alias.sync '!f() { git fetch upstream && git checkout main && git rebase upstream/main && git push origin main --force-with-lease; }; f'
git config --global alias.pp 'push --force-with-lease'
git config --global alias.r1 'reset HEAD~1'
git config --global alias.ano 'commit -a --amend --no-edit'
```

## Instructions

1. Run each alias command above.
2. Verify with `git config --global --list | grep alias`.
