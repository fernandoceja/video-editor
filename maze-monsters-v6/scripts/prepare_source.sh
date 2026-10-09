#!/usr/bin/env bash
set -euo pipefail
ffmpeg -v error -n -i ../maze-monsters-v3/remotion/public/source.mp4 -vf "delogo=x=150:y=252:w=790:h=140:enable='lt(t,11)',fps=30" -an -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p remotion/public/source.mp4
