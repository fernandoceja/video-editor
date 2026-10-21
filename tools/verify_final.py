#!/usr/bin/env python3
"""Verify a delivery render: 1080x1920, 30 fps, stereo AAC, clean full decode, ~-14 LUFS, TP <= -1 dBTP.
Writes <file>.verification.json and exits non-zero on failure."""
import json
import pathlib
import re
import subprocess
import sys

path = pathlib.Path(sys.argv[1])
probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)],
                                  capture_output=True, text=True, check=True).stdout)
v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
a = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), {})
dec = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-'], capture_output=True, text=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-vn', '-af',
                    'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, check=True)
j = json.loads(re.findall(r'\{[^{}]+\}', r.stderr)[-1])
lufs, tp = float(j['input_i']), float(j['input_tp'])
checks = {
    '1080x1920': v['width'] == 1080 and v['height'] == 1920,
    '30fps': v['r_frame_rate'] == '30/1',
    'stereo_aac': a.get('codec_name') == 'aac' and a.get('channels') == 2,
    'clean_decode': dec.returncode == 0 and not dec.stderr.strip(),
    'lufs_about_minus14': -14.5 <= lufs <= -13.5,
    'true_peak_le_minus1': tp <= -1.0,
}
res = {'file': path.name, 'checks': checks, 'passed': all(checks.values()), 'duration_s': float(probe['format']['duration']),
       'frames': int(v['nb_read_frames']), 'integrated_lufs': lufs, 'true_peak_dbtp': tp,
       'audio_sample_rate': a.get('sample_rate'), 'decode_errors': dec.stderr.strip()}
path.with_suffix('.verification.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
sys.exit(0 if res['passed'] else 1)
