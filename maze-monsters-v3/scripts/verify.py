"""Verify actual rendered streams, decode, audio continuity and original integrity."""
import hashlib
import json
import pathlib
import subprocess
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = BASE / 'maze-monsters-v3-draft.mp4'
provenance = json.loads((BASE/'source-provenance.json').read_text())
probe = subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams',
                        '-show_format','-of','json',str(OUTPUT)],
                       capture_output=True,text=True,check=True)
data = json.loads(probe.stdout)
video = next(s for s in data['streams'] if s['codec_type']=='video')
audio = next(s for s in data['streams'] if s['codec_type']=='audio')
decode = subprocess.run(['ffmpeg','-v','error','-i',str(OUTPUT),'-f','null','-'],
                        capture_output=True,text=True)
def audio_samples(path):
    r = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','2',
                        '-ar','48000','-f','f32le','-'],check=True,capture_output=True)
    return np.frombuffer(r.stdout,dtype='<f4').reshape(-1,2)
original = pathlib.Path(provenance['original'])
source = audio_samples(original)
rendered = audio_samples(OUTPUT)
correlations = []
for start,end in [(0.25,1.75),(3,5.5),(15,18.5),(24.2,26.2),(33,34.4)]:
    a = source[round(start*48000):round(end*48000)].flatten()
    b = rendered[round(start*48000):round(end*48000)].flatten()
    correlations.append({'start':start,'end':end,'correlation':float(np.corrcoef(a,b)[0,1])})
checks = {
 'dimensions':video['width']==1080 and video['height']==1920,
 'fps':video['r_frame_rate']=='30/1',
 'frames':int(video['nb_read_frames'])==1066,
 'audio_stream':audio['codec_name']=='aac' and audio['channels']==2,
 'decode':decode.returncode==0 and not decode.stderr,
 'original_unchanged':hashlib.sha256(original.read_bytes()).hexdigest()==provenance['sha256'],
 'working_copy_identical':hashlib.sha256((BASE/'remotion/public/source.mp4').read_bytes()).hexdigest()==provenance['sha256'],
 'reaction_audio_continuity':all(c['correlation']>.95 for c in correlations),
 'audio_not_silent':float(np.sqrt(np.mean(rendered**2)))>.001,
}
report = {'output':str(OUTPUT),'checks':checks,'passed':all(checks.values()),
          'streams':[{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate','channels','sample_rate','duration','nb_read_frames']} for s in data['streams']],
          'format_duration':data['format']['duration'],'decode_errors':decode.stderr,
          'reaction_audio_correlations':correlations,'audio_peak':float(np.max(np.abs(rendered))),
          'paid_actions':False,'higgsfield_generation':False}
(BASE/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not report['passed']:
    raise RuntimeError('Render verification failed: '+', '.join(k for k,v in checks.items() if not v))
