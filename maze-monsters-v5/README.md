# Maze Monsters v5

Final output: **maze-monsters-v5-music-mastered.mp4**.
Audio-only change from v4; original footage/captions are copied without re-encoding.
Music: Scheming Weasel (faster version), Kevin MacLeod, CC BY 3.0 US.
Include the exact attribution in music/CREDIT.txt when posting.

Base music is 17 dB below the original whole-clip stereo RMS. Additional music-only
voice/sting duck is 8 dB, attack 80 ms, release 350 ms, gaps <250 ms merged.
Music is not muted; it has an 80 ms fade-in and 1-second fade-out. Source voices,
reactions and existing stings remain at unity in the premix. Common final mastering
sets loudness and peak levels. Extra reaction guards are listed in the timing report.

Reproduce (free local tools):

```sh
python -m pip install -r scripts/requirements.txt
python scripts/mix_music.py
python scripts/render_master.py
python scripts/verify.py
```

Requires ffmpeg. Scripts refuse to overwrite the output MP4. The dependencies
on ../maze-monsters-v3 are the original source copy and original sting mix; v4
supplies the copied video. No originals or earlier renders are modified.

The first local candidate maze-monsters-v5-music.mp4 failed the tight loudness
check and is excluded from version control; the mastered filename is the final.
Full source/license, mix settings, raw and merged VAD segments, every duck,
and measured encoded loudness are recorded in this folder.
