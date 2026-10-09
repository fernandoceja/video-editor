# Maze Monsters v3 — Tier A draft

Local ffmpeg + Remotion edit; no Higgsfield generation, hosted render, stock purchases, or credit use.
The candy cockroach is confirmed by the user, even though the candy is not identifiable on screen.
The animated cockroach is original SVG artwork in `remotion/src/Root.tsx`.

Output: 1080 × 1920, 30 fps, 1066 frames (35.533 seconds), H.264 / stereo AAC.
The original timeline is retained. Short push-ins, restrained fog/vignette/glitch overlays,
animated captions and locally synthesized accents are added. The last camera whip and
opening reaction support replay; this is a narrative loop, not a seamless matched cut.
The source's pre-existing captions remain part of the supplied footage.

## Reproduce

Requires Node.js, ffmpeg, Chromium, Python and NumPy. No paid service is required.

```sh
python scripts/prepare_audio.py
cd remotion
npm ci --no-audit --no-fund
npx tsc --noEmit
npm run render
```

`public/source.mp4` is a byte-identical working copy, documented by SHA-256 in
`source-provenance.json`. The uploaded originals are never modified.
Remotion dependencies are pinned and locked. Remotion's individual/small-team free
license is assumed for this personal edit; hosted services are not used.

## Mix

The original stereo track remains at its original timing. Brief 1–2 dB ducks around
caption hits leave reactions audible. The 26.4-second candy reveal has a short,
quiet synthesized sting on the existing loudness peak. `audio-mix-report.json`
documents the mix, and `audio-loudness-analysis.png` describes the original track.

## Contents

- `edit-plan.md`: approved timestamp plan
- `audio-loudness-analysis.png`: original audio chart
- `still-00-24.png`, `still-00-26.png`: requested original-source frames
- `remotion/`: editable project, lockfile, source copy and stereo mix
- `maze-monsters-v3-draft.mp4`: draft render
- `verification.json`: stream, decode and source-integrity results

