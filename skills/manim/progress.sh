#!/bin/bash
# Burn a thin progress bar along the bottom edge (a personal review copy; keep the clean file for sharing).
# Usage: progress.sh IN OUT [color=yellow] [height_px=8]
set -eu
in="${1:?usage: progress.sh IN OUT [color] [height]}"; out="${2:?}"; col="${3:-yellow}"; h="${4:-8}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
w=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$in")
ffmpeg -v error -y -i "$in" -f lavfi -i "color=c=$col:s=${w}x${h}" \
  -filter_complex "[0:v][1:v]overlay=x='-W+W*t/$dur':y=H-h:shortest=1[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a copy "$out"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"
