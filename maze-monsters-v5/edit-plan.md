# Maze Monsters v5 — continuous low music bed

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

## Music license and source

Track: **Scheming Weasel (faster version)** — Kevin MacLeod. Playful, sneaky instrumental; no vocals. Not an actual period rock-and-roll recording.
Source: https://commons.wikimedia.org/wiki/File:Scheming_Weasel_faster_version_(Kevin_MacLeod)_(ISRC_USUAN1100085).oga

Downloaded file license: **CC BY 3.0 US** (https://creativecommons.org/licenses/by/3.0/us/); free commercial/social-media use with attribution. Name and license were disclosed before download.

Exact posting credit:

> “Scheming Weasel (faster version)” — Kevin MacLeod (incompetech.com), via Wikimedia Commons. CC BY 3.0 US: https://creativecommons.org/licenses/by/3.0/us/. Trimmed, faded and mixed with original audio.

## Revised music mix

The whole-clip RMS of the original stereo audio is -21.37 dBFS. The music is calibrated to -38.37 dBFS RMS before fades/ducks, **17 dB below** original audio. This is a programme-wide calibration, not instant tracking of the source waveform.

Music plays throughout the 35.533-second timeline, with 80 ms fade-in and 1 second fade-out. Only music receives an additional **8 dB duck**, with 80 ms attack and 350 ms release. No pause/mute is applied to the music. VAD voice gaps shorter than 250 ms are merged. Extra reaction-safety windows: 03.8–05.6, 08.65–09.05, 14.8–18.0 seconds; these protect scream/laugh candidates without claiming speaker identity. Candy and NOPE stings get dedicated ducks at 26.4 and 34.5. All original voices and reactions remain at unity gain before common final loudness mastering.

Silero VAD runs on the original audio with the archived MIT-licensed ONNX model; same detector parameters as v4. See speech-duck-report.md for all raw/merged voice segments and duck on/off times.

Final file: **maze-monsters-v5-music-mastered.mp4**. A first candidate measured −14.58 LUFS / −1.57 dBTP; retained locally as maze-monsters-v5-music.mp4 but excluded from commit. Final mastering adds 0.30 dB after the two-pass R128 normalizer, then the AAC output is measured again. Target: approximately −14 LUFS, true peak ≤−1 dBTP. Video packets are copied from v4. v3/v4 and uploaded originals remain unchanged. No paid actions.
