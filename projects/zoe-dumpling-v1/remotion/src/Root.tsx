import React from 'react';
import { Composition } from 'remotion';
import { Clip, ClipProps } from './Clip';

const FPS = 30;
const defaults: ClipProps = { video: 'c1/proxy.mp4', duration: 10, hook: 'HOOK', chunks: [], zooms: [], endCard: 2 };

export const Root: React.FC = () => (
  <Composition
    id="Clip"
    component={Clip}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={Math.round((defaults.duration + defaults.endCard) * FPS)}
    defaultProps={defaults}
    calculateMetadata={({ props }) => ({ durationInFrames: Math.round((props.duration + props.endCard) * FPS) })}
  />
);
