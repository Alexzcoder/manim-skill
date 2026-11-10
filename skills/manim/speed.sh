#!/bin/bash
# Speed a finished video up, audio pitch preserved. Usage: speed.sh IN OUT [factor=1.75]  (factor 0.5-2.0)
set -eu
f="${3:-1.75}"
ffmpeg -v error -y -i "${1:?usage: speed.sh IN OUT [factor]}" -filter_complex "[0:v]setpts=PTS/$f[v];[0:a]atempo=$f[a]" \
  -map "[v]" -map "[a]" -r 60 -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 160k "${2:?}"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$2"
