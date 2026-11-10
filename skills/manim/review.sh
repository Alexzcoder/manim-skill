#!/bin/bash
# Contact sheets for layout review. Usage: review.sh VIDEO OUT_DIR [seconds_between_frames=6]
set -eu
v="${1:?usage: review.sh VIDEO OUT_DIR [step]}"; out="${2:?}"; step="${3:-6}"
mkdir -p "$out"
ffmpeg -v error -y -i "$v" -vf "fps=1/$step,scale=640:-1,tile=4x4" "$out/sheet_%02d.png"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$v"
ffmpeg -hide_banner -nostats -i "$v" -vn -af "volumedetect,silencedetect=noise=-35dB:d=1.2" -f null - 2>&1 |
  awk '/mean_volume/{print "mean_volume", $5, "dB"} /silence_end/{n++; if($8>m)m=$8} END{print "pauses>1.2s:", n+0, "longest:", m+0}'
ls "$out"
