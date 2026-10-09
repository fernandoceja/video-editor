"""Silero ONNX voice detection and sample-accurate speech-aware local music mix."""
import json
import pathlib
import subprocess
import wave
import numpy as np
import onnxruntime as ort

BASE = pathlib.Path(__file__).resolve().parents[1]
V3 = BASE.parent/'maze-monsters-v3'
RATE = 48000
FRAMES = 1066
DURATION = FRAMES/30

def decode(path, rate=RATE, channels=2, fmt='f32le'):
    result = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn',
        '-ac',str(channels),'-ar',str(rate),'-f',fmt,'-'],check=True,capture_output=True)
    dtype = '<i2' if fmt == 's16le' else '<f4'
    return np.frombuffer(result.stdout,dtype=dtype).reshape(-1,channels)

original_path = V3/'remotion/public/source.mp4'
vad_audio = decode(original_path,16000,1).flatten()
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1
vad = ort.InferenceSession(str(BASE/'scripts/silero-vad.onnx'), sess_options=options,
                          providers=['CPUExecutionProvider'])
window = 512  # Silero's 32 ms inference window, with 64-sample streaming context.
state = np.zeros((2,1,128),dtype=np.float32)
context = np.zeros((1,64),dtype=np.float32)
labels = []
probabilities = []
active = False
for start in range(0,len(vad_audio),window):
    block = vad_audio[start:start+window]
    if len(block)<window:
        block = np.pad(block,(0,window-len(block)))
    input_block = np.concatenate([context,block.reshape(1,-1)],axis=1).astype(np.float32)
    output,state = vad.run(None,{'input':input_block,'state':state,'sr':np.array(16000,dtype=np.int64)})
    context = input_block[:,-64:]
    probability = float(output[0,0])
    probabilities.append(probability)
    # Hysteresis with lower thresholds to retain children's voices / vocal reactions.
    active = probability >= (.20 if active else .35)
    labels.append(active)
raw = []
begin = None
for i,voice in enumerate(labels+[False]):
    if voice and begin is None: begin = i*.032
    if not voice and begin is not None:
        raw.append([round(begin,3),round(min(i*.032,DURATION),3)]);begin=None
merged = []
for start,end in raw:
    if merged and start-merged[-1][1]<.25:
        merged[-1][1]=end
    else: merged.append([start,end])

source = decode(original_path)
total = round(DURATION*RATE)
source = np.pad(source,((0,max(0,total-len(source))),(0,0)))[:total]
v3mix = decode(V3/'remotion/public/draft-mix.wav')[:total]
times = np.arange(total)/RATE
# Recover the original locally synthesized accents, removing the v3 caption ducks.
old_gain = np.ones(total)
for hit in [0,2,6,11,15,19,24.8,26.4,28,32.6,34.8]:
    depth = 1 if hit in [0,2,6,15,24.8,32.6,34.8] else 2
    curve = np.interp(times,[hit-.03,hit,hit+.07,hit+.21],
                      [1,10**(-depth/20),10**(-depth/20),1])
    old_gain = np.minimum(old_gain,curve)
accents = v3mix-source*old_gain[:,None]
foreground = source+accents  # Original foreground at unity; music alone is ducked.

music = decode(BASE/'music/Scheming-Weasel.oga')
if len(music)<total: raise RuntimeError('Music track shorter than the finished video')
music = music[:total].copy()
music_rms = float(np.sqrt(np.mean(music**2)))
original_rms = float(np.sqrt(np.mean(source**2)))
base_music_db_below_original = 17
music_target_rms = original_rms*10**(-base_music_db_below_original/20)
music *= music_target_rms/max(music_rms,1e-9)
duck_db = 8
minimum = 10**(-duck_db/20)
attack = .08
release = .35
intervals = [(s,e,'voice') for s,e in merged]
intervals += [(26.4,26.68,'candy-cockroach-sting'),(34.5,34.66,'NOPE-sting')]
# Extra protection around strong source reaction cues, even if VAD misses a scream/laugh.
intervals += [(3.8,5.6,'reaction-safety'),(8.65,9.05,'reaction-safety'),(14.8,18.0,'reaction-safety')]
gain = np.ones(total)
duck_events = []
for start,end,kind in intervals:
    onset = max(0,start-attack)
    recovery = min(DURATION,end+release)
    if start<=0:
        curve = np.interp(times,[0,end,end+release],[minimum,minimum,1])
    else:
        # Anticipatory attack reaches full reduction exactly when the voice starts.
        curve = np.interp(times,[onset,start,end,end+release],[1,minimum,minimum,1])
    gain = np.minimum(gain,curve)
    duck_events.append({'kind':kind,'duck_on':round(onset,3),
      'full_duck':start,'release_start':end,'duck_off':round(recovery,3)})
# Fade music at both boundaries: 80 ms in, last 1 second out.
fade = np.minimum(np.clip(times/.08,0,1),np.clip((DURATION-times)/1.0,0,1))
bed = music*(gain*fade)[:,None]
mix = foreground+bed
for name,samples in [('foreground-full-level.wav',foreground),('ducked-music.wav',bed),('premaster-mix.wav',mix)]:
    # Float WAV keeps the premaster unattenuated even when summation exceeds 0 dBFS.
    from scipy.io import wavfile
    wavfile.write(BASE/name,RATE,samples.astype(np.float32))

effective = []
for event in sorted(duck_events,key=lambda x:x['duck_on']):
    start,end = event['duck_on'],event['duck_off']
    if effective and start <= effective[-1][1]: effective[-1][1]=max(effective[-1][1],end)
    else: effective.append([start,end])
report = {'detector':'Silero VAD (ONNX CPU)','package':'onnxruntime',
 'model_source':'https://github.com/snakers4/silero-vad','model_license':'MIT',
 'onset_probability':.35,'offset_probability':.20,'sample_rate':16000,'frame_ms':32,'music_in_detector':False,
 'raw_speech_segments':raw,'merged_speech_segments':merged,'merge_gap_seconds':.25,
 'music_duck_db':duck_db,'attack_seconds':attack,'release_seconds':release,
 'music_base_rms_dbfs':float(20*np.log10(music_target_rms)),
 'original_rms_dbfs':float(20*np.log10(original_rms)),
 'base_music_db_below_original':base_music_db_below_original,'music_fade_out_seconds':1,'music_fade_in_seconds':.08,
 'foreground_input_gain_db':0,'v3_caption_ducks_removed':True,
 'caption_accents_preserved':True,'duck_events':sorted(duck_events,key=lambda x:x['duck_on']),
 'effective_duck_on_off_intervals':effective,
 'vad_voice_seconds':round(sum(e-s for s,e in merged),3),'duration':DURATION}
(BASE/'speech-duck-report.json').write_text(json.dumps(report,indent=2)+'\n')
def stamp(t): return f'{int(t//60):02d}:{t%60:06.3f}'
lines=['# Voice detection and music ducking report','',
 'Silero ONNX VAD; 16 kHz mono original audio; 32 ms windows; onset 0.35 / offset 0.20.',
 'Voice gaps shorter than 250 ms merged. Only music ducks, by 8 dB. Base music is 17 dB below original-audio whole-clip RMS.',
 'Attack: 80 ms before onset; release: 350 ms. Original input remains at 0 dB gain.',
 'VAD labels are algorithmic voice estimates, not a transcript. No music was supplied to the detector.','',
 'Base is measured before fades/ducks; foreground remains at unity before final mastering.',
 'Extra reaction-safety windows protect strong scream/laugh candidates independently of VAD.',
 '## Detected speech segments (raw)','', '| Start | End |','|---|---|']
lines += [f'| {stamp(s)} | {stamp(e)} |' for s,e in raw]
lines += ['', '## Merged voice segments','', '| Start | End |','|---|---|']
lines += [f'| {stamp(s)} | {stamp(e)} |' for s,e in merged]
lines += ['', '## Duck events','', '| Trigger | Duck on | Full duck | Release starts | Duck off |', '|---|---|---|---|---|']
lines += [f"| {d['kind']} | {stamp(d['duck_on'])} | {stamp(d['full_duck'])} | {stamp(d['release_start'])} | {stamp(d['duck_off'])} |" for d in report['duck_events']]
lines += ['', 'Overlapping events share one envelope; another event can hold the music down after an individual release.']
lines += ['', '## Effective music duck on/off intervals','', '| Duck on | Fully recovered |','|---|---|']
lines += [f'| {stamp(s)} | {stamp(e)} |' for s,e in effective]
(BASE/'speech-duck-report.md').write_text('\n'.join(lines)+'\n')
np.savez_compressed(BASE/'vad-envelope-data.npz',voice_probability=np.array(probabilities),music_gain=gain[::480],music_fade=fade[::480])
print(json.dumps({'raw_segments':len(raw),'merged_segments':merged,'vad_voice_seconds':report['vad_voice_seconds'],'premaster_peak':float(np.max(np.abs(mix)))},indent=2))
