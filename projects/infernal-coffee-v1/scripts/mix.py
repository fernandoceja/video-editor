#!/usr/bin/env python3
"""Mix stitched original audio and licensed music, with Silero speech ducking."""
import pathlib, subprocess, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'tools'))
from analyze import speech_segments
src, music, out = sys.argv[1:]
def decode(path, rate, channels):
    b = subprocess.run(['ffmpeg','-v','error','-i',path,'-vn','-ar',str(rate),'-ac',str(channels),'-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(b,dtype='<f4').reshape(-1,channels).copy()
voice = decode(src,48000,2)
track = decode(music,48000,2)
if len(track) < len(voice): raise SystemExit('Music shorter than timeline')
track = track[:len(voice)]
rms = float(np.sqrt(np.mean(track**2)))
if not rms: raise SystemExit('Music is silent')
track *= 10**(-25/20)/rms
segments = speech_segments(decode(src,16000,1).ravel())
t = np.arange(len(voice))/48000
gain = np.ones(len(t))
low = 10**(-23/20)
for start,end in segments:
    curve = np.interp(t,[start-.15,start-.05,end+.15,end+.45],[1,low,low,1])
    gain = np.minimum(gain,curve)
gain *= np.clip((len(voice)/48000-t)/1.5,0,1)
mix = voice + track * gain[:,None]
subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','-','-c:a','pcm_f32le',out],input=mix.astype('<f4').tobytes(),check=True)
print('VAD speech segments:',segments)
