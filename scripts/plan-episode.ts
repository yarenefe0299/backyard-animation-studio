import {mkdirSync, writeFileSync, appendFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {episodeById, totalFrames, validateEpisode} from '../src/story.ts';
import type {Episode} from '../src/story.ts';

export function createPlan(ep: Episode, limit = 210) {
  validateEpisode(ep);
  if (!Number.isInteger(limit) || limit < 1) throw new Error('Invalid chunk size');
  const chunks: {id: string; from: number; to: number; frames: number; shot: string}[] = [];
  const review: {frame: number; label: string}[] = [];
  let start = 0;
  for (const shot of ep.shots) {
    for (let local = 0; local < shot.frames; local += limit) {
      const from = start + local, to = Math.min(start + shot.frames - 1, from + limit - 1);
      chunks.push({id: String(chunks.length).padStart(3, '0'), from, to, frames: to - from + 1, shot: shot.id});
    }
    review.push({frame: start + Math.floor(shot.frames * .3), label: `${shot.id}-addition`},
      {frame: start + Math.floor(shot.frames * .82), label: `${shot.id}-result`});
    start += shot.frames;
  }
  return {episodeId: ep.id, title: ep.title, compositionId: ep.compositionId,
    video: {width: ep.width, height: ep.height, fps: ep.fps, frames: totalFrames(ep), seconds: totalFrames(ep) / ep.fps},
    shots: ep.shots, chunks, review};
}
export function srtTime(frame: number, fps: number) {
  const ms = Math.round(frame / fps * 1000);
  return [Math.floor(ms / 3600000), Math.floor(ms / 60000) % 60, Math.floor(ms / 1000) % 60]
    .map(v => String(v).padStart(2, '0')).join(':') + ',' + String(ms % 1000).padStart(3, '0');
}
export function subtitles(ep: Episode) {
  let frame = 0;
  return ep.shots.map((shot, index) => {
    const text = `${index + 1}\n${srtTime(frame, ep.fps)} --> ${srtTime(frame + shot.frames, ep.fps)}\n${shot.narration}\n`;
    frame += shot.frames; return text;
  }).join('\n');
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const ep = episodeById(process.argv[2] || 'flying-armor'), plan = createPlan(ep);
  mkdirSync('out', {recursive: true});
  writeFileSync('out/manifest.json', JSON.stringify(plan, null, 2));
  writeFileSync('out/story.srt', subtitles(ep));
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT,
    `matrix=${JSON.stringify({include: plan.chunks})}\ncomposition=${plan.compositionId}\nepisode=${plan.episodeId}\n`);
  console.log(`${plan.title}: ${plan.video.seconds}s, ${plan.video.frames} frames, ${plan.chunks.length} render jobs.`);
}
