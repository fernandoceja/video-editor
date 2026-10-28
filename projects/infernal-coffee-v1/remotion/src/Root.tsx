import React from 'react';
import {AbsoluteFill, Composition, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import '@fontsource/fredoka/700.css';
type Shot = {src: string; kind: 'video' | 'image'; frames: number; caption: string};
type Props = {shots: Shot[]};
const defaults: Props = {shots: [{src: 'placeholder.jpg', kind: 'image', frames: 90, caption: ''}]};
const ShotView: React.FC<{shot: Shot}> = ({shot}) => {
 const frame = useCurrentFrame();
 const zoom = shot.kind === 'image' ? interpolate(frame, [0, Math.max(shot.frames - 1, 1)], [1, 1.08], {extrapolateRight:'clamp'}) : 1;
 const style: React.CSSProperties = {width:'100%', height:'100%', objectFit:'cover', transform:`scale(${zoom})`};
 return <AbsoluteFill style={{backgroundColor:'#111', overflow:'hidden'}}>
  {shot.kind === 'image' ? <Img src={staticFile(shot.src)} style={style}/> : <OffthreadVideo src={staticFile(shot.src)} muted style={style}/>}
  {shot.caption && <div style={{position:'absolute', left:90, right:140, bottom:430, textAlign:'center', whiteSpace:'pre-line', fontFamily:'Fredoka, sans-serif', fontSize:68, lineHeight:1.08, color:'white', WebkitTextStroke:'6px #181018', paintOrder:'stroke fill', textShadow:'0 5px 12px #000'}}>{shot.caption}</div>}
 </AbsoluteFill>;
};
const Video: React.FC<Props> = ({shots}) => {let from = 0; return <AbsoluteFill>{shots.map((shot,i) => {const start = from; from += shot.frames; return <Sequence key={i} from={start} durationInFrames={shot.frames}><ShotView shot={shot}/></Sequence>;})}</AbsoluteFill>};
export const Root: React.FC = () => <Composition id="InfernalCoffee" component={Video} width={1080} height={1920} fps={30} durationInFrames={90} defaultProps={defaults} calculateMetadata={({props}) => ({durationInFrames:props.shots.reduce((n,s)=>n+s.frames,0)})}/>;
