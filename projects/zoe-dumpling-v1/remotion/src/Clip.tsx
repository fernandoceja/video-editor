import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import '@fontsource/fredoka/700.css';

export type Chunk = { text: string; start: number; end: number };
export type ClipProps = { video: string; duration: number; hook: string; chunks: Chunk[]; zooms: number[]; endCard: number; layout?: 'letterbox' | 'full' };

const W = 1080;
const BOX_H = 608; // 1080 x 608 keeps the full 16:9 wide shot
const BOX_Y = 656; // centered vertically in 1920
const FONT = 'Fredoka, Arial Rounded MT Bold, sans-serif';
const COLORS = ['#FF5FA8', '#FFD93B', '#4DD9FF', '#B58CFF'];

// Safe zones: nothing below y=1536 (bottom 20%) or right of x=960 (right edge)
const SAFE_RIGHT = 960;

const zoomAt = (t: number, zooms: number[]) => {
  let s = 1;
  for (const z of zooms) {
    const up = interpolate(t, [z - 0.1, z + 0.3], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
    const down = interpolate(t, [z + 1.2, z + 1.8], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
    s = Math.max(s, 1 + 0.22 * Math.min(up, down < 1 && t > z + 1.2 ? down : up));
  }
  return s;
};

const Pop: React.FC<{ children: React.ReactNode; start: number; end: number; color: string; size: number; y: number; align?: 'center' }> = ({ children, start, end, color, size, y }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < start || t >= end) return null;
  const sc = spring({ frame: frame - Math.round(start * fps), fps, config: { damping: 9, stiffness: 220, mass: 0.6 } });
  const rot = Math.sin((t - start) * 9) * 2.5 * Math.max(0, 1 - (t - start) * 3);
  return (
    <div style={{ position: 'absolute', top: y, left: 60, width: SAFE_RIGHT - 60, display: 'flex', justifyContent: 'center' }}>
      <div style={{
        fontFamily: FONT, fontWeight: 700, fontSize: size, lineHeight: 1.05, textAlign: 'center', color,
        transform: `scale(${0.4 + 0.6 * sc}) rotate(${rot}deg)`, WebkitTextStroke: '10px #2B1055', paintOrder: 'stroke fill',
        textShadow: '0 8px 0 #2B1055, 0 14px 24px rgba(0,0,0,.45)', letterSpacing: 1,
      }}>{children}</div>
    </div>
  );
};

export const Clip: React.FC<ClipProps> = ({ video, duration, hook, chunks, zooms, endCard, layout = 'letterbox' }) => {
  const full = layout === 'full'; // already-vertical footage: fill the frame, no blurred bars
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const z = zoomAt(t, zooms);
  const endStart = duration;
  const fade = interpolate(t, [endStart, endStart + 0.25], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      <Sequence from={0} durationInFrames={Math.round(duration * fps)}>
        {!full && <AbsoluteFill style={{ overflow: 'hidden' }}>
          <OffthreadVideo src={staticFile(video)} muted style={{ position: 'absolute', width: 1920 * (1920 / 1080) * 0.5625 * 1.0, height: 1920, left: -(1920 * (1920 / 1080) * 0.5625 - W) / 2, top: 0, objectFit: 'cover', filter: 'blur(38px) brightness(0.62) saturate(1.2)', transform: 'scale(1.15)' }} />
        </AbsoluteFill>}
        <div style={full
          ? { position: 'absolute', left: 0, top: 0, width: W, height: 1920, overflow: 'hidden' }
          : { position: 'absolute', left: 0, top: BOX_Y, width: W, height: BOX_H, overflow: 'hidden', boxShadow: '0 0 60px rgba(0,0,0,.5)' }}>
          <OffthreadVideo src={staticFile(video)} muted style={{ width: W, height: full ? 1920 : BOX_H, objectFit: 'cover', transform: `scale(${z})`, transformOrigin: full ? '50% 60%' : '45% 55%' }} />
        </div>
        <Pop start={0.15} end={2.7} color="#FFD93B" size={112} y={full ? 960 : 250}>{hook}</Pop>
        {chunks.map((c, i) => (
          <Pop key={i} start={c.start} end={c.end} color={COLORS[i % COLORS.length]} size={full && c.text.length > 26 ? 74 : 86} y={full ? 1240 : 1330}>{c.text}</Pop>
        ))}
      </Sequence>
      {fade > 0 && (
        <AbsoluteFill style={{ backgroundColor: '#000', opacity: fade, alignItems: 'center', justifyContent: 'center' }}>
          <Img src={staticFile('logo.png')} style={{ width: 800, marginTop: -60 }} />
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
