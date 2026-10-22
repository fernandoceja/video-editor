#!/usr/bin/env python3
"""Infinity-Gauntlet-short-v2 from the popcorn-bucket MOV (gauntlet + Endgame TV).
Usage: render_v2.py stabilized_video_only.mp4 out.mp4 original.mov
Original audio at normal level (unity) + synthesized snap/pop SFX. (v2 muted it; v3 restores it by request.)"""
import subprocess, sys

SRC, OUT, ORIG = sys.argv[1], sys.argv[2], sys.argv[3]
LOGO = 'projects/infinity-gauntlet-short-v1/assets/logo-80s-obsession.png'
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
# (src_start, src_end, crop_x_start, crop_x_end) in the 1920-wide frame; 608x1080 strip, panned linearly
SEGS = [(76.0, 79.0, 520, 520), (24.5, 27.5, 500, 500), (38.5, 46.5, 400, 1000),
        (46.5, 54.5, 500, 1100), (84.0, 90.0, 450, 450)]
durs = [e - s for s, e, _, _ in SEGS]
st = [sum(durs[:i]) for i in range(len(durs))]
body = sum(durs)
END = 2.0
PUNCH = [0.0, 0.95, st[2] + 0.2, st[3] + 0.2, st[4] + 0.3]
SNAP_T = 0.95
POPS = [st[2] + 0.2, st[3] + 0.2, st[4] + 0.3]
z = '+'.join(f"if(gte(t,{p:.2f}),0.10*max(0,1-(t-{p:.2f})/0.3),0)" for p in PUNCH)
cap_on, cap_off = st[4] + 0.4, body - 0.2

f = []
for i, (s, e, xa, xb) in enumerate(SEGS):
    d = e - s
    f.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,crop=608:1080:'{xa}+({xb}-{xa})*t/{d}':0,"
             f"scale=1080:1920:flags=lanczos,setsar=1,fps=30[v{i}]")
for i, (s, e, xa, xb) in enumerate(SEGS):
    f.append(f"[2:a:0]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[oa{i}]")
f.append(''.join(f'[oa{i}]' for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=0:a=1[oac]")
f.append(''.join(f'[v{i}]' for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0[vc]")
f.append(f"[vc]scale=w='trunc(1080*(1+{z})/2)*2':h='trunc(1920*(1+{z})/2)*2':eval=frame,crop=1080:1920,setsar=1[vz]")
f.append(f"[vz]drawtext=fontfile={FONT}:text='Snap!':fontsize=190:fontcolor=white:borderw=10:bordercolor=black:"
         f"x=(w-text_w)/2:y=1000:enable='between(t,0.1,2.0)'[vh]")
f.append(f"[vh]drawtext=fontfile={FONT}:text='Perfectly balanced,':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1290:enable='between(t,{cap_on:.2f},{cap_off:.2f})',"
         f"drawtext=fontfile={FONT}:text='as all things should be.':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1395:enable='between(t,{cap_on:.2f},{cap_off:.2f})',format=yuv420p[vb]")
f.append(f"color=c=black:s=1080x1920:r=30:d={END}[bk]")
f.append(f"[1:v]scale=820:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[lg]")
f.append(f"[bk][lg]overlay=(W-w)/2:(H-h)/2-80:shortest=1,format=yuv420p[ve]")
f.append(f"[vb][ve]concat=n=2:v=1:a=0[vout]")
# audio: synthesized only
f.append("anoisesrc=d=0.18:c=white:a=0.9:r=48000,highpass=f=2500,afade=t=out:st=0.02:d=0.16,volume=0.3,aformat=channel_layouts=stereo[sn1]")
f.append("aevalsrc='0.4*sin(2*PI*180*t)*exp(-t*90)':d=0.06:s=48000,aformat=channel_layouts=stereo[sn2]")
f.append("[sn1][sn2]amix=inputs=2:normalize=0,asplit=1[snap]")
f.append(f"[snap]adelay={int(SNAP_T*1000)}|{int(SNAP_T*1000)}[sd]")
f.append("aevalsrc='0.2*sin(2*PI*(500+1800*t)*t)*exp(-t*28)':d=0.18:s=48000,aformat=channel_layouts=stereo,"
         f"asplit={len(POPS)}" + ''.join(f'[p{i}]' for i in range(len(POPS))))
labs = ['[sd]']
for i, p in enumerate(POPS):
    ms = int(p * 1000)
    f.append(f"[p{i}]adelay={ms}|{ms}[pd{i}]")
    labs.append(f'[pd{i}]')
f.append(f"[oac]apad=whole_dur={body+END}[sil]")
f.append(f"[sil]{''.join(labs)}amix=inputs={1+len(labs)}:normalize=0:duration=first,alimiter=limit=0.89[aout]")
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-loop', '1', '-t', str(END), '-i', LOGO, '-i', ORIG,
       '-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]', '-t', str(body + END),
       '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', OUT]
print('total', body + END)
subprocess.run(cmd, check=True)
