#!/usr/bin/env python3
"""Iron Man helmet popcorn bucket edit. Usage: render.py full|short out_base.mp4 original.mov
Picture: source is portrait 1080x1920 after rotation, so no crop (bucket stays where it was filmed); zoom punches only.
Audio: original (Fernando + TV bleed), 15 ms edge fades, light synthesized pops. Loudness is set afterwards by loudnorm.sh."""
import subprocess, sys

MODE, OUT, ORIG = sys.argv[1], sys.argv[2], sys.argv[3]
LOGO = 'projects/iron-man-helmet-v1/assets/logo-80s-obsession.png'
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
HOOK = ("This helmet has", "a secret...")
PAY = ("I love you", "3,000")
# (src_start, src_end, tag) tags: punch at segment start for 'p', caption payoff for 'c'
SEGS = {
 'short': [(23.05, 25.35, 'p'), (50.45, 56.75, 'p'), (62.25, 67.35, 'p'), (68.5, 72.45, ''), (74.25, 76.15, 'c')],
 'full': None,
}
if MODE == 'full':
    # speech-led cuts from Silero VAD: dead gaps trimmed, lines kept in order, ends padded 0.25 s so no word is clipped
    import json
    sp = json.load(open('work/ih/analysis/Ironman-Helmet.json'))['speech_segments']
    sp = [s for s in sp if s[0] >= 5.9]
    m = []
    for s, e in sp:
        if m and s - m[-1][1] < 0.7: m[-1][1] = e
        else: m.append([s, e])
    segs = []
    for s, e in m:
        s2, e2 = max(0, s - 0.15), min(87.0, e + 0.25)
        if segs and s2 < segs[-1][1]: segs[-1][1] = e2
        else: segs.append([s2, e2])
    SEGS['full'] = [(round(s, 2), round(e, 2), '') for s, e in segs]
    # punches: helmet reveal, eyes light, projector reveal
    FORCE = [23.0, 52.3, 62.2, 66.0]
S = SEGS[MODE]
durs = [e - s for s, e, _ in S]
st = [sum(durs[:i]) for i in range(len(S))]
body = sum(durs)
END = 2.0
PUNCH = [st[i] + 0.05 for i, (_, _, t) in enumerate(S) if t == 'p']
if MODE == 'full':
    PUNCH = [0.05]  # also punch exactly on the beats inside long segments
    for f in FORCE:
        for i, (s, e, _) in enumerate(S):
            if s <= f < e: PUNCH.append(st[i] + (f - s))
    PUNCH = sorted(set(round(p, 2) for p in PUNCH))
z = '+'.join(f"if(gte(t,{p:.2f}),0.09*max(0,1-(t-{p:.2f})/0.3),0)" for p in PUNCH)
HOOK_END = 2.2
if MODE == 'short':
    pay_on, pay_off = st[4] + 0.1, body - 0.1
else:
    pay_on, pay_off = None, None
    for i, (s, e, _) in enumerate(S):
        if s <= 74.3 < e: pay_on = st[i] + (74.3 - s)
    pay_off = pay_on + 2.0
f = []
for i, (s, e, _) in enumerate(S):
    f.append(f"[{i+2}:v]setpts=PTS-STARTPTS,scale=1080:1920,setsar=1,fps=30[v{i}]")
    f.append(f"[{i+2}:a:0]asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
             f"afade=t=in:st=0:d=0.015,afade=t=out:st={e-s-0.015:.3f}:d=0.015[a{i}]")
f.append(''.join(f'[a{i}]' for i in range(len(S))) + f"concat=n={len(S)}:v=0:a=1[ac]")
f.append(''.join(f'[v{i}]' for i in range(len(S))) + f"concat=n={len(S)}:v=1:a=0[vc]")
f.append(f"[vc]scale=w='trunc(1080*(1+{z})/2)*2':h='trunc(1920*(1+{z})/2)*2':eval=frame,crop=1080:1920,setsar=1[vz]")
def dt(l1, l2, on, off, sz):
    return (f"drawtext=fontfile={FONT}:text='{l1}':fontsize={sz}:fontcolor=white:borderw=8:bordercolor=black:"
            f"x=(w-text_w)/2-30:y=250:enable='between(t,{on:.2f},{off:.2f})',"
            f"drawtext=fontfile={FONT}:text='{l2}':fontsize={sz}:fontcolor=white:borderw=8:bordercolor=black:"
            f"x=(w-text_w)/2-30:y=250+{int(sz*1.2)}:enable='between(t,{on:.2f},{off:.2f})'")
f.append(f"[vz]{dt(*HOOK, 0.1, HOOK_END, 96)},{dt(*PAY, pay_on, pay_off, 110)},format=yuv420p[vb]")
f.append(f"color=c=black:s=1080x1920:r=30:d={END}[bk]")
f.append(f"[0:v]scale=820:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[lg]")
f.append(f"[bk][lg]overlay=(W-w)/2:(H-h)/2-80:shortest=1,format=yuv420p[ve]")
f.append(f"[vb][ve]concat=n=2:v=1:a=0[vout]")
POPS = PUNCH
f.append("aevalsrc='0.12*sin(2*PI*(500+1800*t)*t)*exp(-t*28)':d=0.18:s=48000,aformat=channel_layouts=stereo,"
         f"asplit={len(POPS)}" + ''.join(f'[p{i}]' for i in range(len(POPS))))
labs = []
for i, p in enumerate(POPS):
    ms = int(p * 1000)
    f.append(f"[p{i}]adelay={ms}|{ms}[pd{i}]")
    labs.append(f'[pd{i}]')
f.append(f"[ac]apad=whole_dur={body+END}[sil]")
f.append(f"[sil]{''.join(labs)}amix=inputs={1+len(labs)}:normalize=0:duration=first[aout]")
# one seeked input per segment keeps ffmpeg from buffering the whole file (an earlier single-input version was OOM-killed)
cmd = ['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', str(END), '-i', LOGO, '-f', 'lavfi', '-i', 'anullsrc=d=0.1',
       *[x for s_, e_, _ in S for x in ('-ss', str(s_), '-t', str(round(e_ - s_, 3)), '-i', ORIG)],
       '-filter_complex_threads', '1', '-threads', '2', '-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]', '-t', str(body + END),
       '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', OUT]
print(MODE, 'segments', [(s, e) for s, e, _ in S], 'punches', PUNCH, 'total', round(body + END, 2))
subprocess.run(cmd, check=True)
