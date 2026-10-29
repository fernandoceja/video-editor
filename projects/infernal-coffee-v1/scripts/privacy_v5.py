import json,pathlib,subprocess
from PIL import Image,ImageOps,ImageDraw
R=pathlib.Path('/workspace/video-editor'); P=R/'projects/infernal-coffee-v1'; W=R/'work/infernal-coffee-v5'; out=W/'privacy-v5'
out.mkdir(exist_ok=True)
s=json.loads((P/'timeline-with-cynthia.json').read_text())
s['shots']=[x for x in s['shots'] if x['source'] not in ['Cyndi about to enjoy Kreuger Latte.MOV','Silly Cyndi with Kreuger Latte.HEIC']]
new='Kreuger&Jason Latte w_Infernal Coffee signage_1322.HEIC'
s['shots'][5].update(source=new,sourceRoot='work/infernal-coffee-v5/raw',crop=[650,1450,850,1400])
s['shots'].insert(6,dict(source=new,sourceRoot='work/infernal-coffee-v5/raw',kind='image',seconds=4,caption='WE LOVED OUR VISIT',fit='contain',zoomBase=.90,anchor='45% 50%'))
s['shots'].append(dict(source='projects/_brand/logo-80s-obsession-company.png',kind='logo',seconds=2.5,caption=''))
assert sum(x['seconds'] for x in s['shots'])==38.5
(P/'timeline-v5.json').write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n')
for i,x in enumerate(s['shots']):
 if x['kind']=='logo': continue
 src=R/x.get('sourceRoot','work/infernal-coffee-v1/raw')/x['source']
 if x['kind']=='image':
  png=out/f'{i:02d}-original.png'
  subprocess.run(['magick',str(src)+'[0]','-auto-orient',str(png)],check=True)
  original=Image.open(png).convert('RGB')
  if 'crop' in x:
   a,b,w,h=x['crop']; original=original.crop((a,b,a+w,b+h))
 for label,frac in [('start',0),('mid',.5),('end',1)]:
  if x['kind']=='video':
   time=x['start']+frac*(x['seconds']-1/30)
   png=out/f'{i:02d}-{label}-raw.png'
   subprocess.run(['ffmpeg','-v','error','-n','-ss',str(time),'-i',str(src),'-frames:v','1',str(png)],check=True)
   im=Image.open(png).convert('RGB'); im=ImageOps.fit(im,(1080,1920))
  else:
   im=original.copy()
   if x.get('fit')=='contain':
    im=ImageOps.contain(im,(1080,1920)); canvas=Image.new('RGB',(1080,1920)); canvas.paste(im,((1080-im.width)//2,(1920-im.height)//2)); im=canvas
   else: im=ImageOps.fit(im,(1080,1920))
   z=x.get('zoomBase',1)*(1+.08*frac)
   scaled=im.resize((round(1080*z),round(1920*z)))
   canvas=Image.new('RGB',(1080,1920)); ax=.45 if 'anchor' in x else .5
   canvas.paste(scaled,(round((1080-scaled.width)*ax),round((1920-scaled.height)*.5))); im=canvas
  im.save(out/f'{i:02d}-{label}.jpg')
 sheet=Image.new('RGB',(810,510),'#222')
 for k,label in enumerate(['start','mid','end']):
  im=Image.open(out/f'{i:02d}-{label}.jpg'); im.thumbnail((270,480)); sheet.paste(im,(k*270,30))
  ImageDraw.Draw(sheet).text((k*270+8,8),f'{i:02d} {label}',fill='white')
 sheet.save(out/f'{i:02d}-sheet.jpg')
print('Proofs generated; no final video rendered.')
