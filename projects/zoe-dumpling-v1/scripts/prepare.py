#!/usr/bin/env python3
"""Cut proxies, process voice audio, synthesize SFX, build caption/event JSON for each clip.
Run from repo root: python projects/zoe-dumpling-v1/scripts/prepare.py
Inputs: work/batch1/raw/*.MOV, work/batch1/transcript.json, work/zv1/clips_raw.json
Outputs: work/zv1/<clip>/{proxy.mp4,audio_premaster.wav,props.json}"""
import json
import pathlib
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT = pathlib.Path('work')
SRC = next((ROOT / 'batch1/raw').glob('*.MOV'))
SR = 48000
END_CARD = 2.0
SKIP_WORDS = {'rare', 'josie', 'bloober'}  # product claim / relative's name / uncertain brand word: never captioned
MIN_P = 0.40  # a segment is captioned only if EVERY word is at least this confident; otherwise leave a gap, never guess

CLIPS = {
    'c1': dict(start=189.5, end=222.0, hook='WAIT FOR THE PURPLE ONE',
               events=[(1.8, 'pop'), (7.7, 'pop'), (22.2, 'squish'), (30.2, 'pop')]),
    'c2': dict(start=123.8, end=158.0, hook="WHAT'S INSIDE?!",
               events=[(2.4, 'pop'), (17.2, 'pop'), (20.0, 'squish'), (28.7, 'pop')]),
    'c3': dict(start=445.62, end=479.7, hook='THIS ONE IS SO PRETTY',
               events=[(4.5, 'pop'), (14.7, 'squish'), (28.9, 'pop')]),
    'c4': dict(start=723.0, end=757.0, hook="DON'T THROW THIS AT ANYBODY",
               events=[(7.2, 'pop'), (20.6, 'squish'), (24.7, 'pop'), (28.4, 'pop')]),
}


def sh(*cmd):
    subprocess.run(cmd, check=True)


def pop(n=SR // 8):
    t = np.arange(n) / SR
    f = 700 * np.exp(-t * 14) + 180
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.16


def squish(n=int(SR * 0.28)):
    t = np.arange(n) / SR
    f = 420 * np.exp(-t * 7) + 90
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    rng = np.random.default_rng(7)
    noise = np.convolve(rng.standard_normal(n), np.ones(24) / 24, mode='same')
    return (tone * 0.5 + noise * 0.9) * np.exp(-t * 9) * np.minimum(1, t * 200) * 0.14


def chunks_for(words, dur):
    out, cur = [], []
    def flush():
        if not cur:
            return
        text = ' '.join(w[0] for w in cur)
        ok = all(w[3] >= MIN_P for w in cur)
        if ok:
            out.append(dict(text=text.upper(), start=cur[0][1], end=min(cur[-1][2] + 0.3, dur)))
        cur.clear()
    for i, w in enumerate(words):
        if cur and (w[1] - cur[-1][2] > 0.7 or w[4] != cur[-1][4]):
            flush()
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in '?.!':
            flush()
    flush()
    for a, b in zip(out, out[1:]):  # no overlap: one caption on screen at a time
        a['end'] = min(a['end'], b['start'])
    return [c for c in out if c['end'] - c['start'] >= 0.25]


segs = json.load(open(ROOT / 'batch1/transcript.json'))['segments']
# (word, start, end, prob, segment index); a segment containing a skip word is never captioned
allwords = [(w['word'], w['start'], w['end'], w['p'], i) for i, s in enumerate(segs) for w in s['words']
            if not any(x['word'].strip('?.!,').lower() in SKIP_WORDS for x in s['words'])
            and all(x['probability'] >= MIN_P if 'probability' in x else x['p'] >= MIN_P for x in s['words'])]
for name, c in CLIPS.items():
    d = round(c['end'] - c['start'], 3)
    out = ROOT / 'zv1' / name
    out.mkdir(parents=True, exist_ok=True)
    # 1080p30 H.264 working copy (the 60 fps HEVC original is never modified); autorotate fixes the upside-down flag
    sh('ffmpeg', '-v', 'error', '-y', '-ss', str(c['start']), '-i', str(SRC), '-t', str(d), '-map', '0:v:0', '-vf', 'fps=30',
       '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-an', str(out / 'proxy.mp4'))
    voice = out / 'voice.wav'
    sh('ffmpeg', '-v', 'error', '-y', '-ss', str(c['start']), '-i', str(SRC), '-t', str(d), '-map', '0:a:0', '-af',
       f'highpass=f=90,afftdn=nr=12:nf=-45,acompressor=threshold=0.03:ratio=4:attack=8:release=120:makeup=8,'
       f'alimiter=limit=0.8:level=disabled,afade=t=in:d=0.05,afade=t=out:st={d-0.2}:d=0.2', '-ar', str(SR), '-ac', '2', str(voice))
    _, v = wavfile.read(voice)
    v = v.astype(np.float32) / 32768
    total = int((d + END_CARD) * SR)
    mix = np.zeros((total, 2), np.float32)
    mix[:len(v)] += v
    for t, kind in c['events']:
        s = (pop() if kind == 'pop' else squish()).astype(np.float32)
        i = int(t * SR)
        mix[i:i + len(s), 0] += s[:total - i]
        mix[i:i + len(s), 1] += s[:total - i]
    wavfile.write(out / 'audio_premaster.wav', SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
    ws = [(w, s - c['start'], e - c['start'], p, g) for w, s, e, p, g in allwords if s >= c['start'] + 0.05 and s < c['end']]
    props = dict(video=f'{name}/proxy.mp4', duration=d, hook=c['hook'], chunks=chunks_for(ws, d),
                 zooms=[t for t, _ in c['events']], endCard=END_CARD)
    json.dump(props, open(out / 'props.json', 'w'), indent=1)
    print(name, d, 'chunks', len(props['chunks']), [x['text'] for x in props['chunks']])
