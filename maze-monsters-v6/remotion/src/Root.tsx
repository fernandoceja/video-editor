import React from 'react';
import {AbsoluteFill, Composition, Freeze, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';

const FPS = 30;
const captions = [
  {start: 0, end: 3.4, text: 'We thought the corn maze\nwas scary...', color: '#fff', setup: true},
  {start: 3.5, end: 6.5, text: 'WE SHOULD HAVE\nTURNED BACK', color: '#fff', setup: false},
  {start: 6.5, end: 10.8, text: 'THEN THIS GUY\nSHOWED UP', color: '#ffbd59', setup: false},
  {start: 11, end: 14.8, text: 'PICK YOUR NIGHTMARE', color: '#fff', setup: false},
  {start: 15, end: 18.8, text: 'KEEP WALKING.\nKEEP WALKING.', color: '#fff', setup: false},
  {start: 19, end: 22.8, text: 'WHY IS IT SO TALL?', color: '#ffbd59', setup: false},
  {start: 24.8, end: 26.35, text: "WAIT… WHAT'S\nIN HIS HAND?", color: '#fff', setup: false},
  {start: 26.4, end: 27.8, text: 'A CANDY COCKROACH.', color: '#ffbd59', setup: false},
  {start: 28, end: 32.5, text: 'JUST ACT NORMAL', color: '#fff', setup: false},
  {start: 32.6, end: 34.75, text: 'NOPE.', color: '#ff745c', setup: false},
  {start: 34.8, end: 35.534, text: 'NEVER AGAIN…', color: '#fff', setup: false},
];

// Original vector art: no stock asset, download, or generation service.
const Cockroach: React.FC = () => <svg viewBox="0 0 220 260" width="190" height="224" aria-label="cartoon candy cockroach">
  <g stroke="#24130a" strokeWidth="9" strokeLinecap="round" fill="none">
    <path d="M85 62 Q25 8 24 23 M135 62 Q190 5 200 23"/>
    <path d="M78 102 L38 82 L13 94 M75 139 L28 143 L13 168 M79 177 L36 207 L28 237 M142 102 L182 82 L207 94 M145 139 L192 143 L207 168 M141 177 L184 207 L192 237"/>
  </g>
  <ellipse cx="110" cy="146" rx="49" ry="87" fill="#a45122" stroke="#24130a" strokeWidth="8"/>
  <ellipse cx="110" cy="77" rx="36" ry="31" fill="#67381f" stroke="#24130a" strokeWidth="7"/>
  <path d="M110 111 V220 M69 139 H151 M69 168 H151 M78 193 H142" stroke="#50240e" strokeWidth="6"/>
  <ellipse cx="97" cy="69" rx="7" ry="10" fill="#fff2c0"/><ellipse cx="124" cy="69" rx="7" ry="10" fill="#fff2c0"/>
  <circle cx="99" cy="72" r="3"/><circle cx="122" cy="72" r="3"/>
</svg>;

const Movie: React.FC = () => {
  const frame = useCurrentFrame();
  const time = frame / FPS;
  const cap = captions.find(c => time >= c.start && time < c.end);
  const local = cap ? frame - Math.round(cap.start * FPS) : 0;
  const pop = spring({frame: local, fps: FPS, config: {damping: 15, stiffness: 230, mass: .65}});
  let zoom = 1;
  if (time < 1.8) zoom = 1.03;
  if (time >= 19 && time < 22.8) zoom = interpolate(time, [19,22.8], [1,1.035]);
  if (time >= 24.8 && time < 26.4) zoom = interpolate(time, [24.8,25.25,26.4], [1,1.045,1.045], {extrapolateRight:'clamp'});
  if (time >= 32.6 && time < 34.75) zoom = interpolate(time,[32.6,32.85,34.75],[1,1.07,1.07]);
  const shakes = [4.1,8.8,34.5];
  const shake = shakes.some(t => time >= t && time < t+.12);
  const dx = shake ? Math.sin(frame * 3.1)*8 : 0;
  const fog = (time >= 2 && time < 5.5) || (time >= 28 && time < 32.5);
  const roach = time >= 26.4 && time < 27.8;
  const roachSpring = spring({frame: frame-792, fps:FPS, config:{damping:12,stiffness:190}});
  const walk = time >= 15 && time < 18.8 ? (time<16.4?1:time<17.5?2:time<17.8?3:4) : 0;
  const actualText = walk ? ['KEEP','KEEP WALKING.','KEEP WALKING.\nKEEP','KEEP WALKING.\nKEEP WALKING.'][walk-1] : cap?.text;

  return <AbsoluteFill style={{backgroundColor:'#080707'}}>
    <AbsoluteFill style={{transform:`translateX(${dx}px) scale(${zoom})`,transformOrigin:'70% 55%'}}>
      <Freeze frame={990} active={time>=33 && time<33.167}>
        <OffthreadVideo src={staticFile('source.mp4')} muted style={{width:'100%',height:'100%',objectFit:'cover'}} />
      </Freeze>
    </AbsoluteFill>
    <AbsoluteFill style={{pointerEvents:'none',background:'radial-gradient(ellipse at 50% 48%, transparent 48%, rgba(14,3,23,0.22) 100%)'}}/>
    {fog && <AbsoluteFill style={{opacity:.15,transform:`translateX(${Math.sin(frame/40)*35}px)`,background:'radial-gradient(ellipse at 0% 68%, #d8d0ef 0%, transparent 38%), radial-gradient(ellipse at 100% 80%, #bbb7ca 0%, transparent 32%)'}}/>}
    {shake && <AbsoluteFill style={{opacity:.09,background:'linear-gradient(transparent 30%, #ac8fff 31%, transparent 32%, transparent 67%, #dcac7a 68%, transparent 69%)',mixBlendMode:'screen'}}/>}
    {cap && <div style={{position:'absolute',top:285,left:70,right:120,textAlign:'center',transform:cap.start<=3.5?'none':`translateY(${(1-pop)*16}px) scale(${.94+.06*pop})`,opacity:cap.setup ? 1 : cap.start===3.5 ? Math.min(1,(time-3.5)/.15) : Math.min(1,local/3+.25),padding:'22px 18px',borderRadius:24,background:'rgba(10,7,17,0.88)',border:'2px solid rgba(255,189,89,0.3)',boxShadow:'0 8px 28px rgba(0,0,0,.4)',fontFamily:'DejaVu Sans, Arial, sans-serif',fontSize:cap.setup?46:cap.text==='NOPE.'?106:58,fontWeight:cap.setup?700:900,lineHeight:1.15,letterSpacing:1.5,color:cap.color,whiteSpace:'pre-line',textShadow:'0 4px 4px #000'}}>{actualText}</div>}
    {roach && <div style={{position:'absolute',top:465,left:115,transform:`scale(${roachSpring}) rotate(${Math.sin(frame/3)*4}deg)`,background:'rgba(255,216,137,.95)',borderRadius:'50%',padding:'14px 22px',boxShadow:'0 12px 30px #0008'}}><Cockroach/></div>}
  </AbsoluteFill>;
};

export const Root: React.FC = () => <Composition id="MazeMonsters" component={Movie} durationInFrames={1066} fps={FPS} width={1080} height={1920}/>;
