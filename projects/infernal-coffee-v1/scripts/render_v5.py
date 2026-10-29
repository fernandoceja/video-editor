#!/usr/bin/env python3
"""Approved v5 render with v4 proven mastering recipe. Stops on any failure."""
import json,pathlib,re,subprocess,sys
R=pathlib.Path(__file__).resolve().parents[3]; P=R/'projects/infernal-coffee-v1'; W=R/'work/infernal-coffee-v5/prepared'; PY=R/'work/.venv/bin/python'
OUT=P/'final/infernal-coffee-v1-v5.mp4'
def run(args,**kw): return subprocess.run(list(map(str,args)),check=True,**kw)
def measure(path):
 r=run(['ffmpeg','-hide_banner','-nostats','-i',path,'-af','loudnorm=I=-14:TP=-2.9:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True)
 return json.loads(re.findall(r'\{[^{}]+\}',r.stderr)[-1])
if OUT.exists(): sys.exit('STOP: v5 output already exists')
run(['ffmpeg','-v','error','-n','-f','concat','-safe','0','-i',W/'audio-list.txt','-c:a','pcm_s16le',W/'original.wav'])
run([PY,P/'scripts/mix.py',W/'original.wav',P/'music/Darkest-Child.mp3',W/'mix.wav'])
run([P/'remotion/node_modules/.bin/remotion','render','src/index.ts','InfernalCoffee',W/'video.mp4','--props='+str(W/'props.json'),'--public-dir='+str(W),'--browser-executable=/usr/bin/chromium','--muted','--codec=h264','--crf=19','--pixel-format=yuv420p'],cwd=P/'remotion')
run(['ffmpeg','-v','error','-n','-i',W/'mix.wav','-af','loudnorm=I=-14:TP=-2.9:LRA=11','-ar','48000',W/'mix_norm.wav'])
m=measure(W/'mix_norm.wav'); print('Stage 2:',json.dumps(m),flush=True)
(W/'stage2.json').write_text(json.dumps(m,indent=2)+'\n')
i,tp=float(m['input_i']),float(m['input_tp'])
if not (-15<=i<=-13 and tp<=-2.6): sys.exit('STOP: stage 2 threshold failure')
g=min(-14-i,-2.5-tp)
run(['ffmpeg','-v','error','-n','-i',W/'mix_norm.wav','-af',f'volume={g:.8f}dB','-c:a','pcm_f32le',W/'mix_final.wav'])
post=measure(W/'mix_final.wav'); print('Trim gain:',g,'Post-trim:',json.dumps(post),flush=True)
if float(post['input_tp'])>-2.5: sys.exit('STOP: post-trim peak failure')
run(['ffmpeg','-v','error','-n','-i',W/'video.mp4','-i',W/'mix_final.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-movflags','+faststart','-shortest',OUT])
run([PY,R/'tools/verify_final.py',OUT])
report=json.loads(OUT.with_suffix('.verification.json').read_text())
if abs(report['duration_s']-38.5)>.001: sys.exit('STOP: duration must equal 38.5 seconds')
(P/'final/infernal-coffee-v1-v5.mastering.json').write_text(json.dumps({'stage2':m,'trim_gain_db':g,'post_trim':post},indent=2)+'\n')
