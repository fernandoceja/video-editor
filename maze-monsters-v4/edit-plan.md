# Maze Monsters v4 — approved visuals plus speech-aware Halloween music

All timestamps reference the finished source timeline. Preserve original footage
and stereo reactions. No generated replacement shots. User confirmed the unseen
gift was a candy cockroach; both reveal captions below are approved.

| Time | Footage | Caption and treatment | Purpose |
|---|---|---|---|
| 00:00.0–00:01.8 | Wide-eyed child | WHAT COULD GO WRONG?; animated pop and modest push-in | Hook |
| 00:02.0–00:05.5 | Walking into darkness / camera whip | WE SHOULD HAVE TURNED BACK; fog, vignette, glitch at 00:04.1 | Build |
| 00:06.0–00:10.8 | Child on shoulders; plaid monster | THEN THIS GUY SHOWED UP; short shake at 00:08.8 | First scare |
| 00:11.0–00:14.8 | Gate / monster lineup | PICK YOUR NIGHTMARE | Renew curiosity |
| 00:15.0–00:18.8 | Courtyard movement | KEEP WALKING. KEEP WALKING.; progressive words | Pace |
| 00:19.0–00:22.8 | Tall black-robed monster | WHY IS IT SO TALL?; subtle push-in | Escalate |
| 00:24.8–00:26.35 | Antlered creature / hands | WAIT… WHAT'S IN HIS HAND?; slight push-in | Curiosity |
| 00:26.4–00:27.8 | Same encounter | A CANDY COCKROACH.; small cartoon roach pop-in, short sting at 26.4 | Comic payoff |
| 00:28.0–00:32.5 | Shelter walk | JUST ACT NORMAL; light edge fog | Reset |
| 00:32.6–00:34.75 | Furry horned close-up | NOPE.; punch-in, short shake/hit near 34.5 | Final scare |
| 00:34.8–00:35.5 | Whip away | NEVER AGAIN…; ending returns to opening reaction on replay | Loop |

Original loudness cues (100 ms mono RMS windows, not confirmed musical beats):
00:04.1 −10.7 dBFS; 00:24.8 −14.2; 00:26.4 −12.9; 00:34.5 −15.6.
Keep captions within mobile-safe upper space, short and high-contrast. Avoid
obscuring faces and hands. Effects are brief and preserve night-footage visibility.
The caption-first draft retains the original duration and existing footage order;
local effects replace any optional AI enhancement. No new footage or paid assets.

## Music and license

Track: **Darkest Child**, Kevin MacLeod; duration 3:58.68; instrumental harp/celesta/low strings.
Source: https://commons.wikimedia.org/wiki/File:Darkest_Child_(ISRC_USUAN1100783).mp3

Original artist listing: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100783

Downloaded mirror license: **CC BY 3.0** — https://creativecommons.org/licenses/by/3.0/
Permits commercial/social-media use with attribution. Official current listing labels CC BY 4.0; this edition credits the downloaded mirror under CC BY 3.0.

Exact posting credit:

> “Darkest Child” — Kevin MacLeod, via Wikimedia Commons. Licensed under CC BY 3.0: https://creativecommons.org/licenses/by/3.0/. Trimmed, faded and mixed with original audio.

The name/license was disclosed in chat before downloading. No paid licenses or APIs used.

## Audio implementation

Silero ONNX VAD (MIT), run on original audio only at 16 kHz with 32 ms windows, hysteresis 0.35/0.20. Merge gaps under 250 ms. Music ducks 23 dB, attack 80 ms before onset, release 350 ms after voice. Caption stings at 26.4 and 34.5 also duck music. The v3 short foreground ducks are reversed; source foreground is unity before mastering. Existing synthesized stings are retained.

Use the first 35.533 s of music, base RMS −25 dBFS, fade in 80 ms and fade out over the final 1 s. This smooths the music boundary on replay; the source footage/reactions remain unchanged. Two-pass EBU R128 master targets −14 LUFS and limits true peaks, with −1.7 dBTP internal ceiling to allow AAC encoding headroom. Verify actual encoded output ≤−1 dBTP.

See `speech-duck-report.md` for each raw/merged segment and duck timestamps, `speech-duck-report.json` for machine-readable timing, and `voice-music-envelope.png` for the VAD probabilities and effective envelope.
