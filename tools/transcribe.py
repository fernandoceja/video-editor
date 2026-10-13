#!/usr/bin/env python3
"""Local transcription (faster-whisper, free, no upload). Usage: transcribe.py audio.wav out.json [start end]"""
import json
import sys

from faster_whisper import WhisperModel

audio, out = sys.argv[1], sys.argv[2]
m = WhisperModel("small", device="cpu", compute_type="int8", download_root="work/models")
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=True, language="en")
res = {"language": info.language, "segments": []}
for s in segs:
    res["segments"].append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                            "words": [{"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2),
                                       "p": round(w.probability, 2)} for w in s.words]})
    print(res["segments"][-1]["start"], flush=True)
json.dump(res, open(out, "w"), indent=1)
