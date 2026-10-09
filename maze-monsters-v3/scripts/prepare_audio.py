"""Retain stereo source audio; short gentle ducks and original synthesized accents."""
import json
import pathlib
import subprocess
import wave
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[1]
PUBLIC = BASE / 'remotion' / 'public'
RATE = 48000
result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(PUBLIC/'source.mp4'),
                         '-vn', '-ac', '2', '-ar', str(RATE), '-f', 'f32le', '-'],
                        check=True, capture_output=True)
source = np.frombuffer(result.stdout, dtype='<f4').reshape(-1, 2).copy()
target_samples = round(1066 / 30 * RATE)
source = np.pad(source, ((0, max(0, target_samples-len(source))), (0, 0)))[:target_samples]
times = np.arange(len(source)) / RATE
gain = np.ones(len(source))
caption_hits = [0, 2, 6, 11, 15, 19, 24.8, 26.4, 28, 32.6, 34.8]
for hit in caption_hits:
    # 30 ms attack / 70 ms hold / 140 ms release. Reactions only dip 1 dB.
    depth = 1 if hit in [0, 2, 6, 15, 24.8, 32.6, 34.8] else 2
    envelope = np.interp(times, [hit-.03, hit, hit+.07, hit+.21], [1, 10**(-depth/20), 10**(-depth/20), 1])
    gain = np.minimum(gain, envelope)
mix = source * gain[:, None]
accents = []
for hit, duration, frequency, amplitude in [(19,1.4,55,.012), (28.1,.13,75,.018), (29.1,.13,75,.018), (30.1,.13,75,.018), (31.1,.13,75,.018)]:
    n = round(duration*RATE)
    t = np.arange(n)/RATE
    env = np.sin(np.pi*np.arange(n)/n)**2 if duration>1 else (1-np.exp(-t*700))*np.exp(-t*35)
    begin = round(hit*RATE)
    mix[begin:begin+n] += (amplitude*np.sin(2*np.pi*frequency*t)*env)[:,None]
    accents.append({'time':hit,'duration':duration,'kind':'rumble' if duration>1 else 'heartbeat'})
for hit, duration, amplitude, kind in [(4.1,.08,.025,'glitch'), (8.8,.10,.025,'bump'), (26.4,.28,.07,'candy-sting'), (34.5,.16,.04,'scare')]:
    n = round(duration*RATE)
    t = np.arange(n)/RATE
    env = (1-np.exp(-t*800))*np.exp(-t*22)
    if kind == 'candy-sting':
        tone = (np.sin(2*np.pi*(620*t+900*t*t)) + .4*np.sin(2*np.pi*930*t))*env
    else:
        tone = np.sin(2*np.pi*(110*t+200*t*t))*env
    begin = round(hit*RATE)
    stop = min(begin+n, len(mix))
    mix[begin:stop] += (amplitude*tone[:stop-begin])[:,None]
    accents.append({'time':hit,'duration':duration,'kind':kind})
peak = float(np.max(np.abs(mix)))
if peak > .98:
    mix *= .98/peak
with wave.open(str(PUBLIC/'draft-mix.wav'), 'wb') as wav:
    wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(RATE)
    wav.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
(BASE/'audio-mix-report.json').write_text(json.dumps({'sample_rate':RATE,'channels':2,
 'caption_hit_times':caption_hits,'duck_db':[1,2],'duck_duration_seconds':.24,
 'accents':accents,'peak_before_safety_gain':peak,'peak_after':float(np.max(np.abs(mix))),
 'original_audio_preserved':True,'no_external_audio_assets':True},indent=2)+'\n')
print('Stereo mix prepared; peak:', float(np.max(np.abs(mix))))
