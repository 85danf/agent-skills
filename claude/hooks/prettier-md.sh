#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[ -z "$file_path" ] && exit 0
[[ "$file_path" != *.md ]] && exit 0
[ ! -f "$file_path" ] && exit 0

prettier -w "$file_path" >/dev/null 2>&1
exit 0
