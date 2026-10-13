#!/usr/bin/env python3
"""Probe a video: duration, resolution, fps, loudness (EBU R128) and Silero VAD speech segments.
Writes work/<name>/analysis/<stem>.json and prints a summary."""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import numpy as np
import onnxruntime as ort

MODEL = pathlib.Path(__file__).parent / 'models' / 'silero-vad.onnx'


def run(cmd):
    return subprocess.run(cmd, capture_output=True, check=True)


def decode_mono16k(path):
    out = run(['ffmpeg', '-v', 'error', '-i', str(path), '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']).stdout
    return np.frombuffer(out, dtype='<f4')


def speech_segments(audio):
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = opts.inter_op_num_threads = 1
    vad = ort.InferenceSession(str(MODEL), sess_options=opts, providers=['CPUExecutionProvider'])
    window = 512  # 32 ms at 16 kHz, same settings as v4 (hysteresis keeps children's voices and reactions)
    state = np.zeros((2, 1, 128), dtype=np.float32)
    context = np.zeros((1, 64), dtype=np.float32)
    active, labels = False, []
    for start in range(0, len(audio), window):
        block = audio[start:start + window]
        if len(block) < window:
            block = np.pad(block, (0, window - len(block)))
        x = np.concatenate([context, block.reshape(1, -1)], axis=1).astype(np.float32)
        out, state = vad.run(None, {'input': x, 'state': state, 'sr': np.array(16000, dtype=np.int64)})
        context = x[:, -64:]
        active = float(out[0, 0]) >= (0.20 if active else 0.35)
        labels.append(active)
    raw, begin = [], None
    for i, v in enumerate(labels + [False]):
        if v and begin is None:
            begin = i * 0.032
        if not v and begin is not None:
            raw.append([round(begin, 3), round(i * 0.032, 3)])
            begin = None
    merged = []
    for s, e in raw:
        if merged and s - merged[-1][1] < 0.25:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    return merged


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-vn', '-af',
                        'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True, check=True)
    j = json.loads(re.findall(r'\{[^{}]+\}', r.stderr)[-1])
    return {'integrated_lufs': float(j['input_i']), 'true_peak_dbtp': float(j['input_tp']), 'lra': float(j['input_lra'])}


def analyze(path):
    p = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)
    v = next((s for s in p['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in p['streams'] if s['codec_type'] == 'audio'), None)
    res = {'file': str(path), 'duration_s': float(p['format']['duration']), 'size_bytes': int(p['format']['size'])}
    if v:
        num, den = v['r_frame_rate'].split('/')
        res['video'] = {'codec': v['codec_name'], 'width': v['width'], 'height': v['height'],
                        'fps': round(int(num) / int(den), 3), 'rotation': (v.get('side_data_list') or [{}])[0].get('rotation', 0)}
    if a:
        res['audio'] = {'codec': a['codec_name'], 'channels': a['channels'], 'sample_rate': int(a['sample_rate'])}
        res['loudness'] = loudness(path)
        seg = speech_segments(decode_mono16k(path))
        res['speech_segments'] = seg
        res['speech_seconds'] = round(sum(e - s for s, e in seg), 2)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('videos', nargs='+')
    ap.add_argument('--out', help='output folder (default: alongside raw/, in analysis/)')
    a = ap.parse_args()
    for f in map(pathlib.Path, a.videos):
        out = pathlib.Path(a.out) if a.out else f.parent.parent / 'analysis'
        out.mkdir(parents=True, exist_ok=True)
        r = analyze(f)
        (out / (f.stem + '.json')).write_text(json.dumps(r, indent=2) + '\n')
        v = r.get('video', {})
        print(f"{f.name}: {r['duration_s']:.1f}s {v.get('width')}x{v.get('height')} {v.get('fps')}fps "
              f"{r.get('loudness', {}).get('integrated_lufs')} LUFS speech {r.get('speech_seconds')}s", file=sys.stderr)
