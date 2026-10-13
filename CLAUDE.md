# video-editor: standing workflow for every session

Personal tool for editing the owner's own videos. Read `PRIVACY.md` first. Never print, log or commit secrets
or tokens. Never commit raw footage.

## Hard rules

- **No paid service or credits without asking first**, with the exact cost. Default is the free tier.
- **Never render or spend before the user approves the edit plan** (step 3).
- **Never overwrite an earlier version.** Each render goes in a new folder (`<project>-vN/`) or new filename.
- **Never modify the originals** (Drive files or `work/<batch>/raw/`).
- Financial/legal moves are the user's call. Do not quote prices or promise dates for the user's business.
- Pronouns: use they/them unless told otherwise.

## Where things live

- `work/` is git-ignored. Raw downloads, analysis, scratch renders and temp audio live there.
- `tools/` is the generic, reusable tooling (below). `tools/models/silero-vad.onnx` is the Silero VAD model (MIT, see `SILERO-LICENSE.txt`).
- Reference implementation (Remotion + ffmpeg + Silero ducking) lives on **branches `maze-monsters-v3` to `v6`**,
  not on `main`. Read it with `git show origin/maze-monsters-v6:<path>`:
  - `maze-monsters-v3/remotion/src/Root.tsx` and `README.md`: Remotion captions, push-ins, fog/glitch overlays, SVG art, local synthesized stings.
  - `maze-monsters-v4/scripts/mix_music.py`: Silero VAD + speech-aware music ducking (-23 dB under speech) with fade-out.
  - `maze-monsters-v4/scripts/render_master.py`: two-pass loudnorm to -14 LUFS / -1.7 dBTP and AAC remux, video copied without re-encode.
  - `maze-monsters-v4/scripts/verify.py`, `maze-monsters-v6/scripts/finalize.py`: delivery checks and stills.
  - `maze-monsters-v4/edit-plan.md`: the timestamp-table format for edit plans.
  - Those scripts hard-code the maze-monsters frame count and hit times. Copy and adapt them into a new project folder, do not import them.
  - Note: v3 to v6 committed raw `source.mp4` and music files to Git. That is history only; the rules here forbid it going forward.
- Environment: `python3.11`, `ffmpeg/ffprobe`, Node 22. Python venv: `python3.11 -m venv ~/.venvs/video && ~/.venvs/video/bin/pip install numpy==2.3.5 scipy==1.17.0 onnxruntime==1.31.0 gdown==6.4.2`.
  Remotion: `npm ci` inside the project's `remotion/` folder. Remotion's free individual/small-team license is assumed; flag it if use becomes commercial at team scale.

## Workflow (follow in order)

1. **Download.** The user shares a Drive folder or file link set to "Anyone with the link". Run
   `python tools/drive_download.py "<link>" --name <batch>`. Files land in `work/<batch>/raw/`. Never commit them.
   If the download fails, report the exact error; do not ask for credentials in chat.
2. **Analyze.** `python tools/analyze.py work/<batch>/raw/*.mp4` writes `work/<batch>/analysis/<stem>.json`: duration,
   resolution, fps, rotation, audio codec, integrated LUFS / true peak / LRA, and Silero VAD speech segments.
   Also pull a contact sheet or stills (ffmpeg) so the plan is based on what is actually on screen.
3. **Propose an edit plan, then stop and wait for approval.** Timestamp table (format as in v4 `edit-plan.md`): time, footage, caption and
   effect, purpose. Two tiers:
   - **Free tier (default):** local ffmpeg + Remotion captions, push-ins, overlays, locally synthesized stings, royalty-free music.
   - **Optional paid tier:** only things that cost money (e.g. generated shots via fal.ai or Higgsfield, stock, hosted render). Give the
     exact cost per item and total. Nothing paid runs without an explicit yes.
   Include the music proposal from step 4 in the plan.
4. **Music.** Royalty-free with a license that allows social **and commercial** use. Before using any track tell the user the track,
   artist, source URL, license (and version), and the exact attribution line if one is required. Save the track's `music/CREDIT.txt` and
   license evidence in the project folder. Prefer CC0 / CC BY. Avoid NC licenses. Check the license on the actual download page, not memory
   (v4 found a mirror at CC BY 3.0 while the official listing says 4.0; credit what you actually downloaded).
5. **Mix.** Original audio stays audible at original level. Duck music under speech using Silero VAD as in v4 (`mix_music.py`).
   Short stings must not mask speech. Fade the music out at the end.
6. **Render, verify, publish.** Render to a new folder. Run `python tools/verify_final.py <file.mp4>`. It must pass: 1080x1920,
   30 fps, stereo AAC, clean full decode, about -14 LUFS (-14.5 to -13.5), true peak at most -1 dBTP. Look at sampled frames before
   claiming captions are readable and say what was not reviewed (playback). Commit the project (scripts, plan, credits, verification, final
   MP4; **not** raw footage or secrets) and **push to a branch**. Tell the user the file names and the attribution line.
7. **Deliver.** Final results go to a Drive folder named `edited videos`. Until Drive write access exists in the environment (needs the
   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` secrets with a matching OAuth client), hand the files to the user in
   the session and say so. Never ask the user to paste secrets into chat. The `feat/drive-video-edit` branch has a create-only upload
   helper (`skills/drive-video-edit/scripts/drive.py`) for when credentials are ready.

## Branches

- Develop on the branch the session specifies. Push with `git push -u origin <branch>`. Do not open a pull request unless asked.
