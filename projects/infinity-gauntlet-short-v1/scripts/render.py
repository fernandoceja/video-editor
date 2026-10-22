#!/usr/bin/env python3
"""Render Infinity-Gauntlet-short. Usage: render.py stabilized.mp4 out.mp4
Cuts the stabilized glove clip into 5 segments, crops each to 9:16, adds zoom punches, a hook flash,
approved caption, synthesized snap/pop SFX, low original audio and a logo end card."""
import subprocess, sys

SRC, OUT = sys.argv[1], sys.argv[2]
LOGO = 'projects/infinity-gauntlet-short-v1/assets/logo-80s-obsession.png'
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
# (src_start, src_end, crop_x in 1920 wide frame)
SEGS = [(40.5, 42.0, 350), (0.8, 5.3, 800), (20.0, 27.5, 450), (28.6, 35.0, 450), (37.3, 46.0, 450)]
durs = [e - s for s, e, _ in SEGS]
starts = [sum(durs[:i]) for i in range(len(durs))]
body = sum(durs)               # 28.6 s
END = 2.0
PUNCH_T = [0.0, starts[2] + 1.8, starts[3] + 2.5, starts[4] + 1.2]   # out times of zoom punches
z = '+'.join(f"if(gte(t,{p:.2f}),0.10*max(0,1-(t-{p:.2f})/0.3),0)" for p in PUNCH_T)
cap_on, cap_off = starts[4] + 0.6, body - 0.2

f = []
for i, (s, e, x) in enumerate(SEGS):
    f.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,crop=608:1080:{x}:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30[v{i}]")
    f.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000[a{i}]")
cat_in = ''.join(f'[v{i}][a{i}]' for i in range(len(SEGS)))
f.append(f"{cat_in}concat=n={len(SEGS)}:v=1:a=1[vc][ac]")
# zoom punches, hook flash, hook text, approved caption
f.append(f"[vc]scale=w='trunc(1080*(1+{z})/2)*2':h='trunc(1920*(1+{z})/2)*2':eval=frame,crop=1080:1920,setsar=1,"
         f"fade=t=in:st=0:d=0.3:color=white[vz]")
f.append(f"[vz]drawtext=fontfile={FONT}:text='Snap!':fontsize=190:fontcolor=white:borderw=10:bordercolor=black:"
         f"x=(w-text_w)/2:y=420:enable='between(t,0.1,1.5)'[vh]")
f.append(f"[vh]drawtext=fontfile={FONT}:text='Perfectly balanced,':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1290:enable='between(t,{cap_on:.2f},{cap_off:.2f})',"
         f"drawtext=fontfile={FONT}:text='as all things should be.':fontsize=82:fontcolor=white:borderw=6:bordercolor=black:"
         f"x=(w-text_w)/2-40:y=1395:enable='between(t,{cap_on:.2f},{cap_off:.2f})'[vb]")
# end card: black with logo, fade in
f.append(f"color=c=black:s=1080x1920:r=30:d={END}[bk]")
f.append(f"[1:v]scale=820:-1,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[lg]")
f.append(f"[bk][lg]overlay=(W-w)/2:(H-h)/2-80:shortest=1,format=yuv420p[ve]")
f.append(f"[vb]format=yuv420p[vb2]")
f.append(f"[vb2][ve]concat=n=2:v=1:a=0[vout]")
# audio: original low (-12 dB), snap + pops synthesized, end card silence
f.append(f"[ac]volume=-12dB[al]")
f.append("anoisesrc=d=0.18:c=white:a=0.9:r=48000,highpass=f=2500,afade=t=out:st=0.02:d=0.16,volume=0.3[sn1]")
f.append("aevalsrc='0.4*sin(2*PI*180*t)*exp(-t*90)':d=0.06:s=48000[sn2]")
f.append("[sn1][sn2]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo[snap]")
f.append("aevalsrc='0.2*sin(2*PI*(500+1800*t)*t)*exp(-t*28)':d=0.18:s=48000,aformat=channel_layouts=stereo[pop]")
f.append("[snap]asplit=1[sn]")
pops = [starts[2] + 1.8, starts[3] + 2.5, starts[4] + 1.2]
f.append(f"[pop]asplit={len(pops)}" + ''.join(f'[p{i}]' for i in range(len(pops))))
mix_in = "[al]"
labels = ["[sn_d]"]
f.append("[sn]adelay=0|0[sn_d]")
for i, p in enumerate(pops):
    ms = int(p * 1000)
    f.append(f"[p{i}]adelay={ms}|{ms}[pd{i}]")
    labels.append(f"[pd{i}]")
f.append(f"[al]aformat=channel_layouts=stereo{''.join(labels) and ''}[alst]")
f.append(f"[alst]{''.join(labels)}amix=inputs={1+len(labels)}:normalize=0:duration=first,apad=whole_dur={body+END},alimiter=limit=0.7[aout]")
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-loop', '1', '-t', str(END), '-i', LOGO,
       '-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]', '-t', str(body + END),
       '-c:v', 'libx264', '-crf', '17', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-r', '30',
       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', OUT]
print(' '.join(cmd[:6]), '... total', body + END)
subprocess.run(cmd, check=True)
