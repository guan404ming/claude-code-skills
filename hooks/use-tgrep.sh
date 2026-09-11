#!/bin/bash
command -v tgrep >/dev/null || exit 0
input=$(cat)
pattern=$(printf '%s' "$input" | jq -r '.tool_input.pattern // ""')
glob=$(printf '%s' "$input" | jq -r '.tool_input.glob // ""')
cmd="tgrep -- $(printf '%q' "$pattern") ."
[ -n "$glob" ] && cmd="$cmd -g $(printf '%q' "$glob")"
jq -n --arg c "$cmd" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("Grep is disabled. Run from the project root via Bash: " + $c + " . Add -F for literal strings, -t or -g to scope, --no-index when file freshness matters. Exit 1 means no match.")
  }
}'
