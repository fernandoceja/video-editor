# Infinity-Gauntlet-short (v1)
Source: Infinity-Gauntlet-REAL.mp4 (wearable glove clip, 60s, 1080p). Caption option 2 approved by Fernando 2026-10-22.
Post copy: "Perfectly balanced, as all things should be. #infinitygauntlet #infinitystones #marvelfan #collector #80sobsession"

| Out time | Source | Effect |
|---|---|---|
| 0.0-1.5 | 40.5-42.0 | white flash, zoom punch, synthesized snap SFX, text "Snap!" |
| 1.5-6.0 | 0.8-5.3 | intro |
| 6.0-13.5 | 20.0-27.5 | zoom punch + pop |
| 13.5-19.9 | 28.6-35.0 | zoom punch + pop |
| 19.9-28.6 | 37.3-46.0 | glow punch + pop, on-screen caption "Perfectly balanced, as all things should be." |
| 28.6-30.6 | none | logo end card |

Stabilized with vidstab (smoothing 20), cropped 608x1080 -> 1080x1920. Original audio -12 dB; no music, no movie audio.
Deliberate: integrated loudness about -30 LUFS (fails the usual -14 LUFS check) so a trending sound can be added on top. Peak -3.8 dBTP.
Not verified: playback timing, audio content (not transcribed).
Render: python3.11 scripts/render.py <stabilized.mp4> <out.mp4>. Video files are not committed.

## v2 (popcorn-bucket MOV, 95.9s HEVC; caption 3 and muted original audio approved 2026-10-22)
Cut list: 76.0-79.0 (TV snap + flash, "Snap!"), 24.5-27.5 (gauntlet on shelf), 38.5-46.5 (pick-up), 46.5-54.5 (turn to camera), 84.0-90.0 (stones glowing + caption 3), 2s logo end card. 30.0s.
Pipeline: MOV -> constant 30 fps h264 (needed: stabilizing the HEVC directly gave blocky frames) -> vidstab -> scripts/render_v2.py. Original audio dropped; only synthesized snap/pop SFX.
Copyright: Endgame footage is visible on the TV (visuals may be flagged); no TV audio in the file.
Not verified: playback.

## v3 / glove v2 (2026-10-22): original audio restored at normal level by request
Same cuts, captions and effects as before. render_v2.py now takes the original MOV as a third argument and mixes its audio at unity under the synthesized SFX; render.py (glove) no longer lowers the original by 12 dB. Limiter ceiling -1 dBFS.
Outputs: Infinity-Gauntlet-short-v3.mp4 (Endgame clip, caption 3), Infinity-Gauntlet-glove-short-v2.mp4 (glove clip, caption 2), plus under-30MB copies. Video files not committed.
Copyright: v3 now carries the TV's Endgame dialogue/music at original level, so audio and visuals may be flagged or muted.

## v4 (2026-10-22): Endgame v3 audio raised to about -14 LUFS
scripts/loud_v4.sh: gentle compressor + 21 dB gain + limiter (ceiling about -3 dBFS). Result -14.04 LUFS, true peak -1.83 dBTP, video unchanged. The recording was quiet, so room noise and the TV are louder too.
Copyright: audio is loud and includes the TV's movie audio.

## Re-cut (2026-10-22): Fernando's exact segment order, original audio, about -14 LUFS
Source 1:36 MOV. Long (40.2s): 0:02-0:08, 0:22-0:25, 0:30-0:38, 0:48-0:52, 0:59-1:01, 1:05-1:09.4 + 1:15.2-1:24 (silent wait before the snap cut from about 8.9s to about 3s; reaction at 1:19-1:20 kept, so cut 6 runs straight into cut 7), 1:29-1:31, 2s logo card.
Short (22.7s): 0:22-0:25, 0:33-0:38, 0:48-0:52, 1:05-1:09.4 + 1:15.2-1:20, 1.5s logo card.
Caption 3 on screen over the stones/ending; "Snap!" text on the TV snap flash; zoom punches; two light pops (long) / one (short). Synthesized snap SFX dropped (the real snap is in the original audio).
Scripts: render_cut.py (long|short), loud_cut.py (compressor + gain + limiter). Video files not committed.

## Re-cut v2 (2026-10-22): finish the sentence
Cut 7 ended at 1:24 mid-sentence (speech runs 1:23.8-1:28.9, then a 1 s pause). Long now plays 1:15.2-1:29.0 continuously, then 1:29-1:31 as listed: 45.2s incl. 2s logo card. Short: cut 6 ends 1:20.3 instead of 1:20.0 so the reaction is not clipped: 23.0s incl. 1.5s card. Caption 3 now shows for the last 6 s of the long. Audio -14 LUFS again.
