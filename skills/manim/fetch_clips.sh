#!/bin/bash
# Download narration clips. Usage: fetch_clips.sh AUDIO_DIR < lines of "NN URL"
# (NN = two-digit position of the line in narration order; URL = signed content_url from ElevenLabs.)
set -u
dir="${1:?usage: fetch_clips.sh AUDIO_DIR < 'NN URL' lines}"
mkdir -p "$dir"
while read -r i url; do
  [ -z "$i" ] && continue
  code=$(curl -s -o "$dir/$i.mp3" -w "%{http_code}" "$url")
  echo "$i $code $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$dir/$i.mp3" 2>/dev/null)"
done
