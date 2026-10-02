---
name: drive-video-edit
description: Find a Google Drive video by exact name or ID, download it privately, apply requested edits locally, and create a new Drive video with a viewing link.
---

Use for a user-authorized Drive video edit. Read the repository README, PRIVACY.md,
and any AGENTS.md first. Respect Google's Limited Use policy. Do not send footage
or transcripts to third-party services without the user's authorization.

## Repository capabilities

At introduction, this repository has only README.md and PRIVACY.md: there is no
existing editor, timeline format, caption generator, or render tool. Do not claim
otherwise or silently depend on a neighboring checkout. Recheck the repository
on each invocation and use its editor and documented checks if one is added.
Until then, use installed FFmpeg/FFprobe for explicitly requested local edits.
If required tools or transcription capability are missing, report the exact
failure and ask for the missing tool or a supplied transcript; never invent captions.
The helper requires Python 3.9+ and uses only the standard library.

## Workflow

1. Resolve the exact file name or file ID and requested changes. Ask about material
   ambiguity. Preserve dimensions, frame rate, voice, content and audio unless the
   requested edit requires changing them. Never add music, crops, speed changes,
   or editorial omissions merely as an enhancement.
2. Use `scripts/drive.py` relative to this skill. It exchanges the three environment
   network secrets `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and
   `GOOGLE_REFRESH_TOKEN` at `https://oauth2.googleapis.com/token`. Credentials and
   access tokens stay in memory. Never print, log, serialize, or write them to a
   file; never use shell tracing, environment dumps, HTTP debug logs, or put tokens
   in command arguments. OAuth must already have `drive.file` authorization; the
   refresh exchange cannot broaden the scope.
3. The helper queries Drive v3 by exact escaped name, or gets metadata by ID.
   Duplicate names require an ID. An empty search or a 404 means the file likely
   needs to be opened with the app or uploaded by it to be visible to `drive.file`.
   Report Google's exact error body when present and this explanation; do not guess
   IDs, switch scopes, or select a different file. Download using `alt=media` into
   a private temporary folder; the original is never an upload target.
4. Prepare a local editor command, passing `{input}` and `{output}` as separate
   command arguments (no shell expansion). Use a new output file and FFmpeg `-n`.
   For captions, obtain accurate text and timestamps, align them to the trimmed
   output, and inspect readability. Keep caption assets in a temporary directory
   managed by a context manager or `trap` so they are removed on failure as well.
   Never fabricate speech or omit requested edits because a dependency is missing.
5. Before uploading, probe the output and fully decode it; compare requested
   duration, streams, dimensions, and edits. Inspect caption frames and review
   playback where available. State any review limitation. Implement a wrapper
   editor command to perform these checks before returning success if needed.
   The helper pauses with the temp output available for review. If any change goes
   beyond the request, explain it and **ask the user before uploading**; a helper
   confirmation is not a substitute for that approval. Do not answer `y` until
   required review and approval are complete. User-requested uploads within scope
   need no additional user permission; the agent may confirm the helper prompt.
6. The helper always creates a new Drive file via a resumable upload, in 8 MiB
   chunks. It names the result `<original-stem>-edited.<output-extension>` (for
   example `tour.mp4` → `tour-edited.mp4`). It never updates, deletes, or replaces
   an existing file, even with a matching name. Do not alter sharing permissions.
   It refreshes OAuth after editing, checks the returned size, and returns
   `webViewLink`. Interrupted uploads fail rather than blindly creating duplicates;
   a lost final response can mean the new file exists. Do not retry blindly.
7. Return the file name, byte size, clickable `webViewLink`, and a concise account
   of the actual changes and validation limits. On failure, report the exact
   error text, with secret/token values redacted if echoed. Temp files are cleaned
   on success, cancellation, and ordinary exceptions. Forced process termination
   may require removing the specific leftover temp folder after checking it.
   Never perform destructive actions without asking the user first. Routine
   cleanup of this workflow's own temporary files is authorized by this skill.

## Usage

“Take `collection-tour-review.mp4` from my Drive, trim the first 5 seconds,
add captions, and save it back.”

For that request, first obtain/verify the transcript and caption timing, then
render both the trim and captions. The following command demonstrates **trim only**;
it does not fulfill the caption example by itself:

```bash
python3 skills/drive-video-edit/scripts/drive.py \
  --name collection-tour-review.mp4 --ext mp4 --mime video/mp4 -- \
  ffmpeg -nostdin -n -ss 5 -i '{input}' -map 0:v:0 -map '0:a?' \
  -c:v libx264 -crf 18 -c:a aac -movflags +faststart '{output}'
```

Use `--id FILE_ID` instead of `--name` for an unambiguous ID. Run interactively
so the agent can inspect the printed temp output path before confirming upload.
Do not run this example during installation or testing against live Drive.
