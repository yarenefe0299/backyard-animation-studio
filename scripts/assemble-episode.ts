// This script runs only in the GitHub assembly job. It joins existing renders;
// there is no 3D renderer or external media source in this process.
import {readFile, writeFile, mkdir, copyFile, appendFile} from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import path from 'node:path';
import {probeVideo, verifyVideo} from './video.ts';
import type {createPlan} from './plan-episode.ts';
const exec = promisify(execFile);
const plan: ReturnType<typeof createPlan> = JSON.parse(await readFile('plan/manifest.json', 'utf8'));
await mkdir('out/frames', {recursive: true});
const inputs: string[] = [];
for (const chunk of plan.chunks) {
  const file = path.resolve(`segments/episode-chunk-${chunk.id}/chunk.mp4`);
  verifyVideo(await probeVideo(file), {...plan.video, frames: chunk.frames});
  inputs.push(`file '${file.replaceAll("'", "'\\''")}'`);
}
await mkdir('work', {recursive: true});
await writeFile('work/concat.txt', inputs.join('\n') + '\n');
const output = `out/${plan.episodeId}.mp4`;
await exec('ffmpeg', ['-nostdin', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/concat.txt', '-c', 'copy', '-movflags', '+faststart', output]);
const probe = await probeVideo(output); verifyVideo(probe, plan.video);
await writeFile('out/probe.json', JSON.stringify(probe, null, 2));
const filter = plan.review.map(item => `eq(n,${item.frame})`).join('+');
await exec('ffmpeg', ['-nostdin', '-y', '-v', 'error', '-i', output, '-vf', `select='${filter}'`, '-fps_mode', 'vfr', '-frames:v', String(plan.review.length), 'out/frames/frame-%02d.png']);
const review = plan.review.map((item, i) => ({...item, file: `frames/frame-${String(i + 1).padStart(2, '0')}.png`}));
await writeFile('out/manifest.json', JSON.stringify({...plan, review, render: {
  commit: process.env.GITHUB_SHA, branch: process.env.GITHUB_REF_NAME, run: process.env.GITHUB_RUN_ID,
}}, null, 2));
await copyFile('plan/story.srt', 'out/story.srt');
console.log(`Verified full episode: ${plan.video.seconds}s, ${plan.video.frames} frames, ${plan.chunks.length} joined chunks.`);
if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY,
  `# Full episode complete\n\n${plan.title}\n\nVerified ${plan.video.seconds} seconds, 1080×1920, 30 fps.\n\nThe final artifact includes the MP4, ${review.length} review frames, story subtitles, encoding probe, render manifest and license notices.\n`);
