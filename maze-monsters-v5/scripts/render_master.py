"""Two-pass EBU R128 mastering and AAC remux; copy v3 video without re-encoding."""
import json
import pathlib
import subprocess
import re

BASE = pathlib.Path(__file__).resolve().parents[1]
mix = BASE/'premaster-mix.wav'
output = BASE/'maze-monsters-v5-music-mastered.mp4'

def measure(path):
    result = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn',
       '-af','loudnorm=I=-14:TP=-1.7:LRA=11:print_format=json','-f','null','-'],
       capture_output=True,text=True,check=True)
    return json.loads(re.findall(r'\{[^{}]+\}',result.stderr)[-1])

measured = measure(mix)
(BASE/'loudness-premaster.json').write_text(json.dumps(measured,indent=2)+'\n')
filt = (f"loudnorm=I=-14:TP=-1.7:LRA=11:measured_I={measured['input_i']}:"
        f"measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:"
        f"measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:"
        'linear=false:print_format=json,volume=0.30dB')
result = subprocess.run(['ffmpeg','-hide_banner','-nostats','-n',
   '-i',str(BASE.parent/'maze-monsters-v4/maze-monsters-v4-music.mp4'),
   '-i',str(mix),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',filt,
   '-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-t',str(1066/30),
   '-movflags','+faststart',str(output)],capture_output=True,text=True,check=True)
(BASE/'loudness-mastering.json').write_text(json.dumps(json.loads(re.findall(r'\{[^{}]+\}',result.stderr)[-1]),indent=2)+'\n')
encoded = measure(output)
(BASE/'loudness-final.json').write_text(json.dumps(encoded,indent=2)+'\n')
print('Encoded final:',json.dumps(encoded))
if not (-14.5 <= float(encoded['input_i']) <= -13.5 and float(encoded['input_tp']) <= -1):
    raise RuntimeError(f"Encoded loudness outside target: {encoded['input_i']} LUFS, {encoded['input_tp']} dBTP")
