// Composition/ThreeCanvas integration adapted from remotion-dev/template-three.
import {Composition} from 'remotion';
import {BackyardFilm} from './Scene';
import {preview, totalFrames} from './story';

export const RemotionRoot = () => <Composition id={preview.id}
  component={BackyardFilm} fps={preview.fps} durationInFrames={totalFrames}
  width={preview.width} height={preview.height} />;
