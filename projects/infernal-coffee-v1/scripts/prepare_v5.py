#!/usr/bin/env python3
"""Prepare approved timeline assets, without touching raw sources. Run only after plan approval.
JSON: {"shots":[{"source":"filename", "kind":"video"|"image", "seconds":4,
"start":0, "caption":"..."}]}. Source names are relative to the raw directory.
"""
import json, pathlib, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[3]
raw = root / 'work/infernal-coffee-v1/raw'
out = root / 'work/infernal-coffee-v5/prepared'
if out.exists():
    raise SystemExit('Prepared directory already exists; choose a new version before running.')
spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
shots = spec['shots']
if not shots:
    raise SystemExit('Timeline is empty')
for shot in shots:
    src = (root / shot['source']).resolve() if shot['kind']=='logo' else (root / shot.get('sourceRoot','work/infernal-coffee-v1/raw') / shot['source']).resolve()
    if root not in src.parents or not src.is_file() or shot['kind'] not in ('image', 'video', 'logo') or float(shot['seconds']) <= 0:
        raise SystemExit('Invalid source, kind, or duration')
out.mkdir(parents=True)
props, audio = [], []
for i, shot in enumerate(shots):
    src = root / shot['source'] if shot['kind']=='logo' else root / shot.get('sourceRoot','work/infernal-coffee-v1/raw') / shot['source']
    frames = round(float(shot['seconds']) * 30)
    seconds = frames / 30
    name = f'shot-{i:02d}'
    wav = out / (name + '.wav')
    if shot['kind'] in ('image','logo'):
        cmd=['magick',str(src)+'[0]','-auto-orient']
        if 'crop' in shot:
            x,y,w,h=shot['crop']; cmd += ['-crop',f'{w}x{h}+{x}+{y}','+repage']
        subprocess.run(cmd+[str(out/(name+'.png'))],check=True)
        media = name + '.png'
        subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',str(seconds),str(wav)], check=True)
    else:
        media = name + '.mp4'
        start = str(shot.get('start', 0))
        subprocess.run(['ffmpeg','-v','error','-n','-ss',start,'-i',str(src),'-t',str(seconds),'-an','-vf','fps=30','-c:v','libx264','-pix_fmt','yuv420p',str(out / media)], check=True)
        subprocess.run(['ffmpeg','-v','error','-n','-ss',start,'-i',str(src),'-t',str(seconds),'-vn','-ar','48000','-ac','2',str(wav)], check=True)
    props.append({'src':media,'kind':shot['kind'],'frames':frames,'caption':shot.get('caption','')})
    for key in ('fit','zoomBase','anchor'):
        if key in shot: props[-1][key]=shot[key]
    audio.append(wav)
(out / 'props.json').write_text(json.dumps({'shots':props},indent=2)+'\n')
(out / 'audio-list.txt').write_text(''.join("file '" + p.name + "'\n" for p in audio))
print('Prepared',len(props),'shots. Video rendering and final audio mixing are separate steps.')
