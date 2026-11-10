#!/bin/bash
# Live progress bar for a running render. Run it in a second terminal.
# Usage: watch_render.sh LOG TOTAL
#   LOG   = file the render's output is redirected to (manim ... > render.log 2>&1)
#   TOTAL = animation count, from: manim -ql --dry_run scene.py Scene | grep -o "Played [0-9]* animations"
#           (use the same NARRATION_AUDIO_DIR as the real render)
set -u
log="${1:?usage: watch_render.sh LOG TOTAL}"; total="${2:?usage: watch_render.sh LOG TOTAL}"
count() { grep -c -E "movie file written|Using cached data" "$log" 2>/dev/null || true; }
t0=$(date +%s); n0=$(count)
while :; do
  n=$(count); [ "$n" -gt "$total" ] && n=$total
  pct=$((100 * n / total)); fill=$((40 * n / total))
  eta="--:--"
  if [ "$n" -gt "$n0" ]; then
    s=$(( ($(date +%s) - t0) * (total - n) / (n - n0) )); eta=$(printf "%d:%02d" $((s / 60)) $((s % 60)))
  fi
  printf "\r[%-40s] %3d%%  %d/%d animations  about %s left " "$(printf '#%.0s' $(seq 1 $fill))" "$pct" "$n" "$total" "$eta"
  if grep -q -E "Rendered |Traceback" "$log" 2>/dev/null; then
    grep -q Traceback "$log" && printf "\nRender failed, see %s\n" "$log" || printf "\nRender finished.\n"
    exit 0
  fi
  [ "${WATCH_ONCE:-0}" = 1 ] && { echo; exit 0; }
  sleep 2
done
