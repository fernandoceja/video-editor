#!/usr/bin/env python3
"""Normalize audio to about -14 LUFS (video stream copied). Compressor + gain + limiter; searches the gain
until integrated loudness is within +/-0.2 LU of -14 and true peak <= -1.2 dBTP.
Usage: loud_cut.py in.mp4 out.mp4"""
import re, subprocess, sys
IN, OUT = sys.argv[1:3]

def run(gain):
    af = (f"acompressor=threshold=-32dB:ratio=3:attack=8:release=180:makeup=1,volume={gain}dB,"
          "alimiter=limit=0.72:level=false:attack=3:release=50")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', IN, '-c:v', 'copy', '-af', af, '-c:a', 'aac', '-b:a', '192k',
                    '-ar', '48000', '-ac', '2', '-movflags', '+faststart', OUT], check=True)
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', OUT, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    summ = o[o.rfind('Summary:'):]
    i = float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1))
    p = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1))
    return i, p

g = 21.0
for _ in range(8):
    i, p = run(g)
    print(f'gain {g:.1f} dB -> {i} LUFS, peak {p} dBTP')
    if abs(i + 14) <= 0.2 and p <= -1.2:
        break
    g += (-14 - i)
