"""Copy v5 audio unchanged, verify the export and extract the requested stills."""
import hashlib
import json
import pathlib
import subprocess
from PIL import Image, ImageDraw

BASE = pathlib.Path(__file__).resolve().parents[1]
V5 = BASE.parent/'maze-monsters-v5/maze-monsters-v5-music-mastered.mp4'
OUTPUT = BASE/'maze-monsters-v6-caption-fix.mp4'

def run(args):
    return subprocess.run(args,capture_output=True,text=True,check=True).stdout

run(['ffmpeg','-v','error','-n','-i',str(BASE/'maze-monsters-v6-picture.mp4'),
     '-i',str(V5),'-map','0:v:0','-map','1:a:0','-c','copy',
     '-movflags','+faststart',str(OUTPUT)])
probe = json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams',
                       '-show_format','-of','json',str(OUTPUT)]))
video = next(s for s in probe['streams'] if s['codec_type']=='video')
audio = next(s for s in probe['streams'] if s['codec_type']=='audio')
def audio_hash(path):
    result = json.loads(run(['ffprobe','-v','error','-select_streams','a:0',
       '-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash',
       '-of','json',str(path)]))
    return hashlib.sha256('\n'.join(p['data_hash'] for p in result['packets']).encode()).hexdigest()
decode = subprocess.run(['ffmpeg','-v','error','-i',str(OUTPUT),'-f','null','-'],
                        capture_output=True,text=True)
old_provenance = json.loads((BASE.parent/'maze-monsters-v3/source-provenance.json').read_text())
checks = {
 '1080x1920':video['width']==1080 and video['height']==1920,
 '30fps':video['r_frame_rate']=='30/1',
 '1066frames':int(video['nb_read_frames'])==1066,
 'stereo_aac_48khz':audio['codec_name']=='aac' and audio['channels']==2 and audio['sample_rate']=='48000',
 'audio_packets_identical_to_v5':audio_hash(OUTPUT)==audio_hash(V5),
 'clean_decode':decode.returncode==0 and not decode.stderr,
 'single_caption_layer_all_frames':json.loads((BASE/'caption-report.json').read_text())['maximum_simultaneous_caption_layers']==1,
 'uploaded_original_unchanged':hashlib.sha256(pathlib.Path(old_provenance['original']).read_bytes()).hexdigest()==old_provenance['sha256'],
}
for version,commit,name in [('v3','248667f','maze-monsters-v3-draft.mp4'),('v4','13d1090','maze-monsters-v4-music.mp4'),('v5','cf0675f','maze-monsters-v5-music-mastered.mp4')]:
    path=f'maze-monsters-{version}/{name}'
    checks[version+'_unchanged'] = run(['git','-C',str(BASE.parent),'hash-object',path]).strip()==run(['git','-C',str(BASE.parent),'rev-parse',f'{commit}:{path}']).strip()
result = {'output':str(OUTPUT),'checks':checks,'passed':all(checks.values()),
          'duration':probe['format']['duration'],'audio':'Bit-identical v5 AAC packets, no processing',
          'inherited_loudness_lufs':-14.28,'inherited_true_peak_dbtp':-1.26,
          'decode_errors':decode.stderr,'paid_actions':False}
(BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not result['passed']:raise RuntimeError('Verification failed: '+', '.join(k for k,v in checks.items() if not v))
stills=[]
for time,label in [(1,'01-0'),(3.3,'03-3'),(3.6,'03-6'),(6,'06-0')]:
    path=BASE/f'still-{label}s.png'
    run(['ffmpeg','-v','error','-n','-ss',str(time),'-i',str(OUTPUT),'-frames:v','1',str(path)])
    stills.append((time,path))
sheet=Image.new('RGB',(720,1320),(22,22,22))
draw=ImageDraw.Draw(sheet)
for i,(time,path) in enumerate(stills):
    im=Image.open(path).resize((360,640))
    x=i%2*360;y=i//2*660
    sheet.paste(im,(x,y));draw.text((x+10,y+643),f'{time:.1f} seconds',fill='white')
sheet.save(BASE/'requested-stills.jpg')
print('Exported all four full-resolution requested stills.')
