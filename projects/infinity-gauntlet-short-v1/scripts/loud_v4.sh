#!/bin/sh
# Raise v3 audio to about -14 LUFS (video stream copied, not re-encoded).
# usage: loud_v4.sh in.mp4 out.mp4
ffmpeg -y -i "$1" -c:v copy \
  -af "acompressor=threshold=-32dB:ratio=3:attack=8:release=180:makeup=1,volume=21dB,alimiter=limit=0.72:level=false:attack=3:release=50" \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$2"
