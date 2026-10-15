#!/usr/bin/env python3
"""High-accuracy local transcription of one short clip's cleaned voice track (free, nothing uploaded).
Usage: transcribe_clip.py voice.wav out.json [--model large-v3] [--prompt "context words"]
Loudness-normalises the cleaned voice to -14 LUFS first, keeps word timestamps and a probability for every word."""
import argparse
import json
import subprocess
import tempfile

from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument('audio')
ap.add_argument('out')
ap.add_argument('--model', default='large-v3')
ap.add_argument('--prompt', default='Squishy, squishies, dumpling, the dumpling lights up, glitter, purple, countdown, Zoe.')
a = ap.parse_args()
with tempfile.NamedTemporaryFile(suffix='.wav') as t:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.audio, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ac', '1', '-ar', '16000', t.name], check=True)
    m = WhisperModel(a.model, device='cpu', compute_type='int8', download_root='work/models')
    segs, info = m.transcribe(t.name, language='en', word_timestamps=True, beam_size=5, initial_prompt=a.prompt,
                              condition_on_previous_text=False, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=300),
                              hotwords='squishy squishies dumpling glitter purple Zoe')
    res = {'model': a.model, 'prompt': a.prompt, 'segments': []}
    for s in segs:
        res['segments'].append({'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip(),
                                'words': [{'word': w.word.strip(), 'start': round(w.start, 2), 'end': round(w.end, 2), 'p': round(w.probability, 2)} for w in s.words]})
json.dump(res, open(a.out, 'w'), indent=1)
print('segments', len(res['segments']))
