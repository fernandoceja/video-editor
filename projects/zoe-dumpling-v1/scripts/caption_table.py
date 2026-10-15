#!/usr/bin/env python3
"""Build the caption-approval table from the large-model transcripts (work/zv2/<clip>_large.json).
LINES picks which words form each on-screen caption (indices into the clip's words, after dropping a leading
t=0 artefact). 'skip' rows are never rendered. Writes v2/caption-table.md and work/zv2/<clip>_proposed.json."""
import json
import pathlib

FLAG = 0.8
LINES = {
    'c1': [(0, 1), (2, 5), ('skip', 6, 7, 'SET IT: low confidence (0.41/0.76), unclear what was said'), (8, 8), (9, 9), (10, 10), (11, 14), (15, 19),
           (20, 23), (24, 26), (27, 28), ('skip', 29, 32, "THIS ONE'S ALSO RARE: product claim, not captioned"), (33, 36)],
    'c3': [('skip', 0, 2, 'DO YOU WANT: repeated start, first "Do" 0.37, looks like a stutter'), (3, 7), (8, 9), (10, 13), (14, 17), (18, 20), (21, 23), (24, 26),
           (27, 30), ('skip', 31, 37, "MY SISTER JOSIE GAVE ME THIS ONE: relative's name, not captioned unless you say so"),
           (38, 41), (42, 44), (45, 48), (49, 52), (53, 55), (56, 59)],
}

def conf(p):
    return 'high' if p >= 0.8 else 'medium' if p >= 0.5 else 'low'

md = ['# zoe-dumpling-v2 caption approval table (C1 and C3)', '',
      'Times are clip seconds (0 = first frame, before the 2 s end card). Source: faster-whisper large-v3 on the cleaned, loudness-normalised',
      'voice track, with context words as a prompt. Any word under 0.80 confidence is listed as word(0.xx). Confidence = lowest word in the line.', '']
for clip, spec in LINES.items():
    d = json.load(open(f'work/zv2/{clip}_large.json'))
    words = [w for s in d['segments'] for w in s['words']]
    if clip == 'c1':
        words = [w for w in words if not (w['word'].lower() == 'and' and w['start'] == 0.0)]
    rows, out, prev_end = [], [], 0.0
    for i, item in enumerate(spec):
        skip = item[0] == 'skip'
        a, b = (item[1], item[2]) if skip else item
        ws = words[a:b + 1]
        start = ws[0]['start']
        if len(ws) > 1 and ws[1]['start'] - start > 1.0:  # a long pause after the first word: show the line when the speech resumes
            start = ws[1]['start'] - 0.3
        end = ws[-1]['end'] + 0.3
        text = ' '.join(w['word'] for w in ws).upper()
        flags = ', '.join(f"{w['word'].strip('?.!,')}({w['p']:.2f})" for w in ws if w['p'] < FLAG) or '-'
        minp = min(w['p'] for w in ws)
        if start - prev_end > 1.5 and not skip:
            rows.append((f'{prev_end:.1f}-{start:.1f}', '(gap)', '-', 'no caption: silence or non-speech'))
        if skip:
            rows.append((f'{start:.1f}-{end:.1f}', f'~~{text}~~', conf(minp), 'SKIP: ' + item[3]))
        else:
            nxt = next((words[x[0]]['start'] for x in spec[i + 1:] if x[0] != 'skip'), 99)
            end = min(end, nxt - 0.04)
            rows.append((f'{start:.1f}-{end:.1f}', text, conf(minp), flags))
            out.append(dict(text=text.rstrip(',.'), start=round(start, 2), end=round(end, 2)))
            prev_end = end
    md += [f'## {clip.upper()}', '', '| Clip | Start-end (s) | Caption text | Confidence | Flagged words / note |', '|---|---|---|---|---|']
    md += [f'| {clip.upper()} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |' for r in rows] + ['']
    json.dump(out, open(f'work/zv2/{clip}_proposed.json', 'w'), indent=1)
p = pathlib.Path('projects/zoe-dumpling-v1/v2')
p.mkdir(parents=True, exist_ok=True)
(p / 'caption-table.md').write_text('\n'.join(md))
print('\n'.join(md))
