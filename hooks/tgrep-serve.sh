#!/bin/bash
command -v tgrep >/dev/null || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
[ -d .git ] && grep -qx '.tgrep/' .git/info/exclude 2>/dev/null || echo '.tgrep/' >> .git/info/exclude
tgrep status . 2>/dev/null | grep -q 'PID:' && exit 0
nohup tgrep serve . >/dev/null 2>&1 &
