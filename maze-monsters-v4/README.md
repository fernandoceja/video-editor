# Maze Monsters v4 — music draft

No paid actions. v3 video packets are copied unchanged; only the audio mix changes.
Music is Kevin MacLeod's Darkest Child, downloaded from Wikimedia Commons under CC BY 3.0.
See music/CREDIT.txt for the exact credit to include when posting, and music/license.json for source/license URLs.

Original source audio remains at unity in the premix, with v3's caption ducks reversed.
Local Silero VAD drives a 23 dB music-only duck, 80 ms attack, 350 ms release, gaps <250 ms merged.
The candy and NOPE stings are preserved and trigger independent music ducks.
Final mastering changes the combined mix's loudness and limits peaks; it does not sidechain the original voices.

Reproduce from this repository with ffmpeg, Python and the pinned packages:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/mix_music.py
python scripts/render_master.py
python scripts/verify.py
```

Rendering refuses to overwrite the MP4. A rerender must use a new filename or directory.
The local archived Silero model is MIT-licensed; its license is in scripts/SILERO-LICENSE.txt.
The music starts at source time zero, runs for the video's 35.533 seconds, and fades at the end.
The original uploads and v3 are unchanged. The source video and v3 audio assets are dependencies in ../maze-monsters-v3/.

Files:
- maze-monsters-v4-music.mp4 — new music draft
- speech-duck-report.md / .json — voice and duck timings
- voice-music-envelope.png — voice detector and duck envelope chart
- foreground-full-level.wav — original audio plus existing stings, before mastering
- ducked-music.wav — isolated faded/ducked music
- premaster-mix.wav — unity foreground summed with music
- loudness-final.json / verification.json — encoded-output checks
- music/CREDIT.txt — required posting attribution
