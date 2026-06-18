#!/usr/bin/env bash
# Claude Code statusLine script
# Receives JSON payload on stdin. Outputs a right-aligned bright-white status line.

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "Unknown"')

# Real context size = cache_read + cache_creation + input_tokens of current_usage.
# current_usage.input_tokens alone is only the new (non-cached) input of the last call.
raw_tokens=$(echo "$input" | jq -r '
  (.context_window.current_usage.cache_read_input_tokens // 0)
  + (.context_window.current_usage.cache_creation_input_tokens // 0)
  + (.context_window.current_usage.input_tokens // 0)
')

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Format token count as x.xk
if [ -n "$raw_tokens" ] && [ "$raw_tokens" -gt 0 ] 2>/dev/null; then
  token_k=$(awk "BEGIN { printf \"%.1fk\", $raw_tokens / 1000 }")
else
  token_k="0.0k"
fi

# Build percentage string
if [ -n "$used_pct" ]; then
  pct_int=$(printf "%.0f" "$used_pct")
  ctx_field="${token_k} (${pct_int}%)"
else
  ctx_field="${token_k}"
fi

# Assemble the status string (plain text, no color yet)
status_text="${model} | ${ctx_field}"

# Right-align: pad with spaces so the colored block sits at the right edge.
cols=$(tput cols 2>/dev/null || echo 80)
text_len=${#status_text}
# +1 for the trailing single space padding inside the colored block
padded_len=$(( text_len + 1 ))
pad=$(( cols - padded_len ))
if [ "$pad" -lt 0 ]; then
  pad=0
fi
spaces=$(printf '%*s' "$pad" '')

# ANSI bright white (97) — reset at the end so the cursor line stays clean.
WHITE='\033[97m'
RESET='\033[0m'

printf "%s${WHITE}%s ${RESET}\n" "$spaces" "$status_text"
