#!/usr/bin/env bash
# Render one v2 clip: silent Remotion video + processed audio, two-pass loudnorm to -14 LUFS / -1.5 dBTP, AAC mux.
# Usage (repo root, after prepare_v2.py): render_v2.sh c1 purple-reveal. Output: projects/zoe-dumpling-v1/final-v2/ (git-ignored, never overwrites).
set -euo pipefail
c=$1; name=$2
P=projects/zoe-dumpling-v1
CH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
PUB=work/zv2pub
mkdir -p $PUB/v2_$c $P/final-v2
ln -f work/zv2/$c/proxy.mp4 $PUB/v2_$c/proxy.mp4
cp -n work/zv1/logo.png $PUB/logo.png
OUT=$P/final-v2/zoe-dumpling-v2-$c-$name.mp4
[ -e "$OUT" ] && { echo "exists: $OUT"; exit 1; }
(cd $P/remotion && npx remotion render src/index.ts Clip ../../../work/zv2/$c/video.mp4 --props=../../../work/zv2/$c/props.json \
   --public-dir=../../../$PUB --browser-executable=$CH --muted --codec=h264 --crf=20 --pixel-format=yuv420p --log=error)
A=work/zv2/$c/audio_premaster.wav
M=$(ffmpeg -hide_banner -nostats -i $A -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "import sys,re,json;print(json.dumps(json.loads(re.findall(r'\{[^{}]+\}',sys.stdin.read())[-1])))")
F=$(python3 -c "import json;m=json.loads('$M');print(f\"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true\")")
ffmpeg -v error -n -i work/zv2/$c/video.mp4 -i $A -map 0:v:0 -map 1:a:0 -c:v copy -af "$F" -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -shortest "$OUT"
echo "done $OUT"
