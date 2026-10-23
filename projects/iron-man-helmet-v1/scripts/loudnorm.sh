#!/bin/sh
# Two-pass loudnorm to -14 LUFS, true peak -1.5 dBTP; video copied. usage: loudnorm.sh in.mp4 out.mp4
M=$(ffmpeg -hide_banner -nostats -i "$1" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -v error -y -i "$1" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.84:level=false" -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$2"
