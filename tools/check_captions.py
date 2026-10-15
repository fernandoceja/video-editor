#!/usr/bin/env python3
"""Check the captions ACTUALLY ON SCREEN in a rendered video against the owner-approved caption file.
Samples the video at 10 fps, OCRs the caption band (and the hook band), judges each approved caption on settled frames,
and flags any word that differs from the approved text, any approved caption never seen, and any caption text on screen where none was approved.
Usage: check_captions.py video.mp4 approved.json [--out report.md]   (exit 1 on any mismatch)
Needs: rapidocr-onnxruntime. Reads only the video; nothing is uploaded."""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR

ap = argparse.ArgumentParser()
ap.add_argument('video')
ap.add_argument('approved')
ap.add_argument('--out')
ap.add_argument('--fps', type=float, default=10)
a = ap.parse_args()
spec = json.load(open(a.approved))
approved = spec['captions']
norm = lambda s: re.sub(r"[^A-Z0-9' ]", ' ', s.upper().replace('’', "'")).split()
ocr = RapidOCR()
BANDS = {'caption': (1290, 280), 'hook': (200, 420)}  # y, height


def read(img):
    res, _ = ocr(str(img))
    return ' '.join(r[1] for r in (res or [])).upper()


def read_enhanced(img):
    # second reading on a grayscale, auto-contrasted, 1.5x upscaled copy (coloured stylised text on a dark blur can fool the first pass)
    im = ImageOps.autocontrast(Image.open(img).convert('L'), cutoff=2)
    im = im.resize((int(im.width * 1.5), int(im.height * 1.5)))
    tmp = str(img) + '.enh.png'
    im.save(tmp)
    return read(tmp)


frames = {k: [] for k in BANDS}  # (t, text) per sampled frame
with tempfile.TemporaryDirectory() as td:
    for band, (y, h) in BANDS.items():
        subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'fps={a.fps},crop=1080:{h}:0:{y}', f'{td}/{band}_%04d.png'], check=True)
        for i, f in enumerate(sorted(pathlib.Path(td).glob(f'{band}_*.png'))):
            frames[band].append((i / a.fps, ' '.join(norm(read(f))), ' '.join(norm(read_enhanced(f)))))
SETTLE = 0.35  # the pop-in animation (spring + wobble) is over by then; earlier frames can be mid-bounce and unreadable
letters = lambda t: re.sub(r'[^A-Z0-9]', '', t)
bad = []
rows = ['| On screen (s) | OCR text (settled frames) | Approved text | Result |', '|---|---|---|---|']
active = lambda t, pad=0.0: any(c['start'] - pad <= t < c['end'] + pad for c in approved)
for c in approved:
    lo = c['start'] + SETTLE
    win = [x for x in frames['caption'] if lo <= x[0] < c['end']] or [x for x in frames['caption'] if c['start'] + 0.1 <= x[0] < c['end']]
    reads = [x[1] for x in win if x[1]]
    reads2 = [x[2] for x in win if x[2]]
    want = norm(c['text'])
    if not reads and not reads2:
        rows.append(f"| {c['start']:.1f}-{c['end']:.1f} | (nothing readable) | {' '.join(want)} | MISSING |")
        bad.append('missing: ' + c['text'])
        continue
    got = max(set(reads), key=reads.count) if reads else ''
    got2 = max(set(reads2), key=reads2.count) if reads2 else ''
    if letters(got) == letters(' '.join(want)) or letters(got2) == letters(' '.join(want)):
        res = 'OK' if letters(got) == letters(' '.join(want)) else 'OK (second, contrast-enhanced reading)'
        got = got if letters(got) == letters(' '.join(want)) else got2
    else:
        diff = [w for w in got.split() if w not in want] + [f'(missing {w})' for w in want if w not in got.split()]
        res = 'DIFF: ' + ', '.join(diff)
        bad.append(res)
    rows.append(f"| {c['start']:.1f}-{c['end']:.1f} | {got} | {' '.join(want)} | {res} |")
extra = [x for x in frames['caption'] if x[1] and not active(x[0], 0.2)]
for t, txt, _ in extra:
    rows.append(f"| {t:.1f} | {txt} | (no caption approved here) | UNAPPROVED TEXT ON SCREEN |")
    bad.append('unapproved: ' + txt)
hk = [x[1] for x in frames['hook'] if x[1]] + [x[2] for x in frames['hook'] if x[2]]
hook_ok = any(letters(x) == letters(' '.join(norm(spec['hook']))) for x in hk)
rows.append(f"| hook | {max(set(hk), key=hk.count) if hk else ''} | {' '.join(norm(spec['hook']))} | {'OK' if hook_ok else 'DIFF'} |")
if not hook_ok:
    bad.append('hook differs')
rep = '\n'.join(['# Caption check (OCR of the rendered video vs approved text)', '', *rows, '',
                 f"Result: {'PASS' if not bad else 'FAIL'} ({len(bad)} problem(s)). OCR can misread stylised text, so also review the proof stills."])
print(rep)
if a.out:
    pathlib.Path(a.out).write_text(rep + '\n')
sys.exit(1 if bad else 0)
