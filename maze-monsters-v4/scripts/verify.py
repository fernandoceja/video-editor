"""Verify media, encoded loudness, unchanged visuals/originals, and duck timing."""
import hashlib
import json
import pathlib
import subprocess
import numpy as np
from scipy.io import wavfile

BASE = pathlib.Path(__file__).resolve().parents[1]
V3 = BASE.parent/'maze-monsters-v3'
OUTPUT = BASE/'maze-monsters-v4-music.mp4'

def run(args):
    return subprocess.run(args,capture_output=True,text=True,check=True).stdout

data = json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams',
                      '-show_format','-of','json',str(OUTPUT)]))
video = next(s for s in data['streams'] if s['codec_type']=='video')
audio = next(s for s in data['streams'] if s['codec_type']=='audio')
decode = subprocess.run(['ffmpeg','-v','error','-i',str(OUTPUT),'-f','null','-'],
                        capture_output=True,text=True)
def video_hash(path):
    packets = run(['ffprobe','-v','error','-select_streams','v:0','-show_packets',
                   '-show_data_hash','sha256','-show_entries','packet=data_hash',
                   '-of','json',str(path)])
    hashes = [p['data_hash'] for p in json.loads(packets)['packets']]
    return hashlib.sha256('\n'.join(hashes).encode()).hexdigest()
provenance = json.loads((V3/'source-provenance.json').read_text())
v3tracked = subprocess.run(['git','-C',str(BASE.parent),'rev-parse',
   '248667f:maze-monsters-v3/maze-monsters-v3-draft.mp4'],capture_output=True,text=True,check=True).stdout.strip()
v3actual = subprocess.run(['git','-C',str(BASE.parent),'hash-object',
   'maze-monsters-v3/maze-monsters-v3-draft.mp4'],capture_output=True,text=True,check=True).stdout.strip()
report = json.loads((BASE/'speech-duck-report.json').read_text())
gain = np.load(BASE/'vad-envelope-data.npz')['music_gain']
timing_pass = True
for start,end in report['merged_speech_segments']+[[26.4,26.68],[34.5,34.66]]:
    i,j = int(np.ceil(start*100)),int(np.floor(end*100))
    if j>i and np.max(gain[i:j])>10**(-23/20)+1e-5:timing_pass=False
for i in range(1,len(report['merged_speech_segments'])):
    if report['merged_speech_segments'][i][0]-report['merged_speech_segments'][i-1][1]<.25:timing_pass=False
rate,music = wavfile.read(BASE/'ducked-music.wav')
last_music_rms = float(np.sqrt(np.mean(music[-480:]**2)))
master = json.loads((BASE/'loudness-final.json').read_text())
checks = {
 '1080x1920':video['width']==1080 and video['height']==1920,
 '30fps':video['r_frame_rate']=='30/1',
 '1066frames':int(video['nb_read_frames'])==1066,
 'stereo_aac_48khz':audio['codec_name']=='aac' and audio['channels']==2 and audio['sample_rate']=='48000',
 'clean_decode':decode.returncode==0 and not decode.stderr,
 'video_packets_identical_to_v3':video_hash(OUTPUT)==video_hash(V3/'maze-monsters-v3-draft.mp4'),
 'v3_draft_unchanged':v3actual==v3tracked,
 'uploaded_original_unchanged':hashlib.sha256(pathlib.Path(provenance['original']).read_bytes()).hexdigest()==provenance['sha256'],
 'integrated_loudness_about_minus14':-14.5<=float(master['input_i'])<=-13.5,
 'true_peak_at_most_minus1':float(master['input_tp'])<=-1,
 'speech_and_stings_duck_23db':timing_pass,
 'music_end_fades_to_near_silence':last_music_rms<.001,
 'foreground_premix_gain_unity':report['foreground_input_gain_db']==0,
}
result = {'checks':checks,'passed':all(checks.values()),'output':str(OUTPUT),
 'duration':data['format']['duration'],'integrated_lufs':float(master['input_i']),
 'true_peak_dbtp':float(master['input_tp']),'decode_errors':decode.stderr,
 'voice_segments_raw':len(report['raw_speech_segments']),
 'voice_segments_merged':len(report['merged_speech_segments']),
 'voice_seconds':report['vad_voice_seconds'],'music_last_10ms_rms':last_music_rms,
 'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],
 'paid_actions':False,'music_credit_file':'music/CREDIT.txt'}
(BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if not result['passed']:raise RuntimeError('Verification failed: '+', '.join(k for k,v in checks.items() if not v))
