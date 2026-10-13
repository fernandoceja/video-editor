#!/usr/bin/env bash
# Render the four clips: silent Remotion video + processed audio, two-pass loudnorm to -14 LUFS / -1.5 dBTP, AAC mux.
# Run from repo root after prepare.py. Output goes to projects/zoe-dumpling-v1/final/ (never overwrites).
set -euo pipefail
P=projects/zoe-dumpling-v1
CH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
declare -A NAME=( [c1]=c1-purple-reveal [c2]=c2-glitter-reveal [c3]=c3-pretty-squishy [c4]=c4-squeeze-test )
mkdir -p $P/final
for c in c1 c2 c3 c4; do
  OUT=$P/final/zoe-dumpling-v1-${NAME[$c]}.mp4
  [ -e "$OUT" ] && { echo "exists, skipping $OUT"; continue; }
  (cd $P/remotion && npx remotion render src/index.ts Clip ../../../work/zv1/$c/video.mp4 --props=../../../work/zv1/$c/props.json \
     --public-dir=../../../work/zv1 --browser-executable=$CH --muted --codec=h264 --crf=19 --pixel-format=yuv420p --log=error)
  A=work/zv1/$c/audio_premaster.wav
  M=$(ffmpeg -hide_banner -nostats -i $A -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "import sys,re,json;print(json.dumps(json.loads(re.findall(r'\{[^{}]+\}',sys.stdin.read())[-1])))")
  F=$(python3 -c "import json;m=json.loads('$M');print(f\"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true\")")
  ffmpeg -v error -n -i work/zv1/$c/video.mp4 -i $A -map 0:v:0 -map 1:a:0 -c:v copy -af "$F" -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -shortest "$OUT"
  echo "done $OUT"
done
