# Maze Monsters v6 — remove overlapping captions

Latest deliverable: maze-monsters-v6-caption-fix.mp4.
Hook: 0.0–3.4 seconds (end exclusive). Gap: 3.4–3.5. Payoff: 3.5–6.5,
with 0.15-second fade-in, fully visible before the 4-second scream.
Later captions resume at 6.5 seconds, per the user's clarification; their copy
and remaining timings are retained. The hook is smaller (46px / weight700);
payoff uses the current dark rounded box, white 58px bold type and unchanged
border/shadow. Both share top=285, left=70, right=120 at 1080x1920.
The upper 12% and lower 20% are clear of caption text.

Two existing captions were burned into the original footage: the corn-maze
hook and Then we met the monsters. A local working copy removes these only
from the upper text region during the first 11 seconds using ffmpeg delogo.
The generated rounded title box covers that region during captions; the
uploaded original and v3–v5 are unchanged. All original v3 local effects,
later captions and the candy cockroach graphic are retained.

The single caption array renders at most one text layer for every frame.
The hook is removed before the payoff fade begins; this is not a crossfade.
See caption-report.json for every transition frame and the issues fixed.

## Reproduce

Run scripts/prepare_source.sh from this folder, then:

```sh
cd remotion
npm ci --no-audit --no-fund
npx tsc --noEmit
npm run render
cd ..
python scripts/finalize.py
```

The finalizer copies the v5 AAC audio packets without re-encoding and exports
four full-resolution PNGs from the delivered MP4: 1.0, 3.3, 3.6 and 6.0 seconds.
Remotion initially creates the silent picture MP4. Its temporary node_modules
symlink is local only and ignored by Git; npm ci supports a fresh checkout.
No paid services, credits, or music downloads are used.

The unchanged v5 music retains its attribution requirement; see ../maze-monsters-v5/music/CREDIT.txt.
