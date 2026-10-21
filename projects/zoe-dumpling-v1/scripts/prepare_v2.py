#!/usr/bin/env python3
"""Prepare one clip from OWNER-APPROVED caption text (never the raw transcript).
Usage (repo root): python projects/zoe-dumpling-v1/scripts/prepare_v2.py <approved.json> <name>
Spec fields: source_start, source_end, hook, captions[{text,start,end}], events[[t,'pop'|'squish']], optional source (default: the Zoe MOV
in work/batch1/raw) and layout ('letterbox' default, or 'full' for already-vertical footage).
Writes work/zv2/<name>/{proxy.mp4,audio_premaster.wav,props.json}. Same voice chain, SFX and end card as v1."""
import json
import pathlib
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

spec_path, clip = sys.argv[1], sys.argv[2]
SR, END_CARD = 48000, 2.0
spec = json.load(open(spec_path))
SRC = pathlib.Path(spec['source']) if 'source' in spec else next(pathlib.Path('work/batch1/raw').glob('*.MOV'))
out = pathlib.Path('work/zv2') / clip
out.mkdir(parents=True, exist_ok=True)
d = round(spec['source_end'] - spec['source_start'], 3)


def pop(n=SR // 8):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(700 * np.exp(-t * 14) + 180) / SR) * np.exp(-t * 30) * 0.16


def squish(n=int(SR * 0.28)):
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(420 * np.exp(-t * 7) + 90) / SR)
    noise = np.convolve(np.random.default_rng(7).standard_normal(n), np.ones(24) / 24, mode='same')
    return (tone * 0.5 + noise * 0.9) * np.exp(-t * 9) * np.minimum(1, t * 200) * 0.14


def sh(*cmd):
    subprocess.run(cmd, check=True)


sh('ffmpeg', '-v', 'error', '-y', '-ss', str(spec['source_start']), '-i', str(SRC), '-t', str(d), '-map', '0:v:0', '-vf', 'fps=30',
   '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-an', str(out / 'proxy.mp4'))
sh('ffmpeg', '-v', 'error', '-y', '-ss', str(spec['source_start']), '-i', str(SRC), '-t', str(d), '-map', '0:a:0', '-af',
   f'highpass=f=90,afftdn=nr=12:nf=-45,acompressor=threshold=0.03:ratio=4:attack=8:release=120:makeup=8,'
   f'alimiter=limit=0.8:level=disabled,afade=t=in:d=0.05,afade=t=out:st={d-0.2}:d=0.2', '-ar', str(SR), '-ac', '2', str(out / 'voice.wav'))
_, v = wavfile.read(out / 'voice.wav')
v = v.astype(np.float32) / 32768
total = int((d + END_CARD) * SR)
mix = np.zeros((total, 2), np.float32)
mix[:len(v)] += v
for t, kind in spec['events']:
    s = (pop() if kind == 'pop' else squish()).astype(np.float32)
    i = int(t * SR)
    mix[i:i + len(s), 0] += s[:total - i]
    mix[i:i + len(s), 1] += s[:total - i]
wavfile.write(out / 'audio_premaster.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
props = dict(video=f'v2_{clip}/proxy.mp4', duration=d, hook=spec['hook'],
             chunks=[dict(text=c['text'], start=c['start'], end=c['end']) for c in spec['captions']],
             zooms=[t for t, _ in spec['events']], endCard=END_CARD, layout=spec.get('layout', 'letterbox'))
json.dump(props, open(out / 'props.json', 'w'), indent=1)
print(clip, 'duration', d, 'captions', len(props['chunks']))
