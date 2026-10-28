#!/usr/bin/env bash
# Run only after explicit edit-plan and external-music approval.
set -euo pipefail
cd "$(dirname "$0")/../../.."
P=projects/infernal-coffee-v1
W=work/infernal-coffee-v1
PY=$PWD/$W/../.venv/bin/python
[ -f "$P/music/Darkest-Child.mp3" ] || { echo 'STOP: approved music file missing'; exit 1; }
[ -f "$P/music/CREDIT.txt" ] || { echo 'STOP: music credit missing'; exit 1; }
[ ! -e "$P/final/infernal-coffee-v1.mp4" ] || { echo 'STOP: output exists'; exit 1; }
"$PY" "$P/scripts/prepare.py" "$1"
ffmpeg -v error -n -f concat -safe 0 -i "$W/prepared/audio-list.txt" -c:a pcm_s16le "$W/prepared/original.wav"
"$PY" "$P/scripts/mix.py" "$W/prepared/original.wav" "$P/music/Darkest-Child.mp3" "$W/prepared/mix.wav"
(cd "$P/remotion" && ./node_modules/.bin/remotion render src/index.ts InfernalCoffee "../../../$W/prepared/video.mp4" --props="../../../$W/prepared/props.json" --public-dir="../../../$W/prepared" --browser-executable=/usr/bin/chromium --muted --codec=h264 --crf=19 --pixel-format=yuv420p)
mkdir -p "$P/final"
M=$(ffmpeg -hide_banner -nostats -i "$W/prepared/mix.wav" -af loudnorm=I=-14:TP=-1.7:LRA=11:print_format=json -f null - 2>&1 | "$PY" -c 'import sys,re,json; print(json.dumps(json.loads(re.findall(r"\{[^{}]+\}",sys.stdin.read())[-1])))')
F=$("$PY" -c 'import json,sys; m=json.loads(sys.argv[1]); print("loudnorm=I=-14:TP=-1.7:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true".format(**m))' "$M")
ffmpeg -v error -n -i "$W/prepared/video.mp4" -i "$W/prepared/mix.wav" -map 0:v:0 -map 1:a:0 -c:v copy -af "$F" -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -shortest "$P/final/infernal-coffee-v1.mp4"
"$PY" tools/verify_final.py "$P/final/infernal-coffee-v1.mp4"
