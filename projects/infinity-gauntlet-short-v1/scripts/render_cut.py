#!/usr/bin/env python3
"""Re-cut of the Endgame gauntlet clip with Fernando's exact segment order; original audio kept.
Usage: render_cut.py long|short stabilized_video_only.mp4 original.mov out.mp4
Audio is rendered at unity here; loud_cut.py then normalizes to about -14 LUFS."""
import subprocess, sys

MODE, SRC, ORIG, OUT = sys.argv[1:5]
LOGO = 'projects/infinity-gauntlet-short-v1/assets/logo-80s-obsession.png'
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
# (src_start, src_end, crop_x_start, crop_x_end) in the 1920 wide frame; 608x1080 strip panned linearly
SNAP_SRC = 77.0   # TV snap flash in the source
if MODE == 'long':
    SEGS = [(2, 8, 1000, 1000), (22, 25, 1000, 1000), (30, 38, 850, 850), (48, 52, 800, 900), (59, 61, 1100, 1100),
            (65, 69.4, 750, 750), (75.2, 89.0, 520, 700), (89.0, 91, 750, 750)]  # 7th cut now runs to 89.0 so the sentence finishes
    END = 2.0
else:
    SEGS = [(22, 25, 1000, 1000), (33, 38, 800, 800), (48, 52, 800, 900), (65, 69.4, 750, 750), (75.2, 80.3, 520, 700)]
    END = 1.5
durs = [e - s for s, e, _, _ in SEGS]
st = [sum(durs[:i]) for i in range(len(durs))]
body = sum(durs)
i6 = [i for i, (s, e, _, _) in enumerate(SEGS) if s == 75.2][0]
snap_out = st[i6] + (SNAP_SRC - 75.2)
if MODE == 'long':
    PUNCH = [st[1], st[2], st[3], snap_out, st[7]]
    POPS = [st[3], st[7]]
    cap_on, cap_off = body - 6.2, body - 0.2      # caption over the glowing-stones shots
else:
    PUNCH = [st[0], st[1], st[2], snap_out]
    POPS = [st[2]]
    cap_on, cap_off = body - 3.2, body - 0.2
z = '+'.join(f"if(gte(t,{p:.2f}),0.10*max(0,1-(t-{p:.2f})/0.3),0)" for p in PUNCH)

f = []
for i, (s, e, xa, xb) in enumerate(SEGS):
    d = e - s
    f.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,crop=608:1080:'{xa}+({xb}-{xa})*t/{d}':0,"
             f"scale=1080:1920:flags=lanczos,setsar=1,fps=30[v{i}]")
AUD = []
for s, e, _, _ in SEGS:
    if AUD and abs(AUD[-1][1] - s) < 1e-6:
        AUD[-1] = (AUD[-1][0], e)
    else:
        AUD.append((s, e))
for i, (s, e) in enumerate(AUD):
    d = e - s
    f.append(f"[2:a:0]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
             f"afade=t=in:d=0.03,afade=t=out:st={d-0.03:.3f}:d=0.03[a{i}]")
n = len(SEGS)
f.append(''.join(f'[v{i}]' for i in range(n)) + f"concat=n={n}:v=1:a=0[vc]")
f.append(''.join(f'[a{i}]' for i in range(len(AUD))) + f"concat=n={len(AUD)}:v=0:a=1[ac]")
f.append(f"[vc]scale=w='trunc(1080*(1+{z})/2)*2':h='trunc(1920*(1+{z})/2)*2':eval=frame,crop=1080:1920,setsar=1[vz]")
f.append(f"[vz]drawtext=fontfile={FONT}:text='Snap!':fontsize=190:fontcolor=white:borderw=10:bordercolor=black:"
         f"x=(w-text_w)/2:y=1000:enable='between(t,{snap_out-0.1:.2f},{snap_out+1.4:.2f})'[vh]")
f.append(f"[vh]drawtext=fontfile={FONT}:text='Perfectly balanced,':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1290:enable='between(t,{cap_on:.2f},{cap_off:.2f})',"
         f"drawtext=fontfile={FONT}:text='as all things should be.':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1395:enable='between(t,{cap_on:.2f},{cap_off:.2f})',format=yuv420p[vb]")
f.append(f"color=c=black:s=1080x1920:r=30:d={END}[bk]")
f.append(f"[1:v]scale=820:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[lg]")
f.append(f"[bk][lg]overlay=(W-w)/2:(H-h)/2-80:shortest=1,format=yuv420p[ve]")
f.append(f"[vb][ve]concat=n=2:v=1:a=0[vout]")
# light pops only (the real snap is in the original audio)
labs = []
f.append("aevalsrc='0.2*sin(2*PI*(500+1800*t)*t)*exp(-t*28)':d=0.18:s=48000,aformat=channel_layouts=stereo,"
         f"asplit={len(POPS)}" + ''.join(f'[p{i}]' for i in range(len(POPS))))
for i, p in enumerate(POPS):
    ms = int(p * 1000)
    f.append(f"[p{i}]adelay={ms}|{ms}[pd{i}]")
    labs.append(f'[pd{i}]')
f.append(f"[ac]apad=whole_dur={body+END}[base]")
f.append(f"[base]{''.join(labs)}amix=inputs={1+len(labs)}:normalize=0:duration=first[aout]")
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-loop', '1', '-t', str(END), '-i', LOGO, '-i', ORIG,
       '-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]', '-t', str(body + END),
       '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', OUT]
print(MODE, 'total', body + END)
subprocess.run(cmd, check=True)
