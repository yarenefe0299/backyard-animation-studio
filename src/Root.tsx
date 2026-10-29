// Composition/ThreeCanvas integration adapted from remotion-dev/template-three.
import {Composition} from 'remotion';
import {BackyardFilm} from './Scene';
import {episodes, totalFrames, validateEpisode} from './story';

export const RemotionRoot = () => <>{episodes.map(ep => {
  validateEpisode(ep);
  return <Composition key={ep.id} id={ep.compositionId} component={BackyardFilm}
    fps={ep.fps} durationInFrames={totalFrames(ep)} width={ep.width} height={ep.height}
    defaultProps={{episodeId: ep.id}}/>;
})}</>;
