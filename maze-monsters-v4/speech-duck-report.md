# Voice detection and music ducking report

Silero ONNX VAD; 16 kHz mono original audio; 32 ms windows; onset 0.35 / offset 0.20.
Voice gaps shorter than 250 ms merged. Only music ducks, by 23 dB.
Attack: 80 ms before onset; release: 350 ms. Original input remains at 0 dB gain.
VAD labels are algorithmic voice estimates, not a transcript. No music was supplied to the detector.

## Detected speech segments (raw)

| Start | End |
|---|---|
| 00:01.088 | 00:02.016 |
| 00:02.336 | 00:02.432 |
| 00:02.496 | 00:03.040 |
| 00:03.104 | 00:05.568 |
| 00:05.824 | 00:05.888 |
| 00:05.920 | 00:07.680 |
| 00:09.632 | 00:10.112 |
| 00:11.104 | 00:13.280 |
| 00:13.920 | 00:14.336 |
| 00:24.672 | 00:25.248 |
| 00:26.208 | 00:26.784 |
| 00:27.648 | 00:28.384 |
| 00:34.400 | 00:34.624 |
| 00:34.976 | 00:35.533 |

## Merged voice segments

| Start | End |
|---|---|
| 00:01.088 | 00:02.016 |
| 00:02.336 | 00:05.568 |
| 00:05.824 | 00:07.680 |
| 00:09.632 | 00:10.112 |
| 00:11.104 | 00:13.280 |
| 00:13.920 | 00:14.336 |
| 00:24.672 | 00:25.248 |
| 00:26.208 | 00:26.784 |
| 00:27.648 | 00:28.384 |
| 00:34.400 | 00:34.624 |
| 00:34.976 | 00:35.533 |

## Duck events

| Trigger | Duck on | Full duck | Release starts | Duck off |
|---|---|---|---|---|
| voice | 00:01.008 | 00:01.088 | 00:02.016 | 00:02.366 |
| voice | 00:02.256 | 00:02.336 | 00:05.568 | 00:05.918 |
| voice | 00:05.744 | 00:05.824 | 00:07.680 | 00:08.030 |
| voice | 00:09.552 | 00:09.632 | 00:10.112 | 00:10.462 |
| voice | 00:11.024 | 00:11.104 | 00:13.280 | 00:13.630 |
| voice | 00:13.840 | 00:13.920 | 00:14.336 | 00:14.686 |
| voice | 00:24.592 | 00:24.672 | 00:25.248 | 00:25.598 |
| voice | 00:26.128 | 00:26.208 | 00:26.784 | 00:27.134 |
| candy-cockroach-sting | 00:26.320 | 00:26.400 | 00:26.680 | 00:27.030 |
| voice | 00:27.568 | 00:27.648 | 00:28.384 | 00:28.734 |
| voice | 00:34.320 | 00:34.400 | 00:34.624 | 00:34.974 |
| NOPE-sting | 00:34.420 | 00:34.500 | 00:34.660 | 00:35.010 |
| voice | 00:34.896 | 00:34.976 | 00:35.533 | 00:35.533 |

Overlapping events share one envelope; another event can hold the music down after an individual release.

## Effective music duck on/off intervals

| Duck on | Fully recovered |
|---|---|
| 00:01.008 | 00:08.030 |
| 00:09.552 | 00:10.462 |
| 00:11.024 | 00:13.630 |
| 00:13.840 | 00:14.686 |
| 00:24.592 | 00:25.598 |
| 00:26.128 | 00:27.134 |
| 00:27.568 | 00:28.734 |
| 00:34.320 | 00:35.533 |
