# video-editor
Project for creating and editing videos

## Skills

- [drive-video-edit](skills/drive-video-edit/SKILL.md): download an accessible Google
  Drive video, apply requested local edits, and upload a new result. Includes a
  standard-library Python transfer helper. This repo currently has no bundled
  video editor; the skill documents a local FFmpeg fallback and review requirements.

Run the offline transfer tests with:

```bash
python3 -m unittest discover -s skills/drive-video-edit/scripts -v
```
