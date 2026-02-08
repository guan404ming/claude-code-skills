---
name: dev-git-setup
description: Set up git aliases.
---

# Dev Git Setup

## Usage
```
/dev-git-setup
```

## Instructions

IMPORTANT: Do NOT use Bash or `git config` to set any aliases. Always use the Read and Edit tools on `~/.gitconfig` directly.

1. Read `~/.gitconfig`.
2. If an `[alias]` section exists, use the Edit tool to merge the aliases below into it. If it doesn't exist, use the Edit tool to append a new `[alias]` section.
3. Verify with `git config --global --list | grep alias`.

## Alias definitions

Each line below is a gitconfig alias entry (key = value). Add them under `[alias]`:

- `pp = push --force-with-lease`
- `r1 = reset HEAD~1`
- `ano = commit -a --amend --no-edit`
- `atemp = commit -a -n -m "TEMP"`
- `temp = commit -n -m "TEMP"`
- `a = add .`
- `rm = rebase main`
- `no = commit --amend --no-edit`
- sync (use double quotes to protect semicolons):

```
sync = "!f() { if git remote | grep -q upstream; then b=$(git remote show upstream | sed -n 's/.*HEAD branch: //p'); git fetch upstream && git checkout $b && git rebase upstream/$b && git push origin $b --force-with-lease; else git pull; fi; }; f"
```
