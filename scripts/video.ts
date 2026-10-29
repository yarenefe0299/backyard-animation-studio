import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import assert from 'node:assert/strict';
const exec = promisify(execFile);
export type Probe = {streams: {codec_name: string; width?: number; height?: number; r_frame_rate?: string; nb_frames?: string; pix_fmt?: string}[]; format: {duration: string}};
export async function probeVideo(path: string): Promise<Probe> {
  const {stdout} = await exec('ffprobe', ['-v', 'error', '-show_entries',
    'stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt', '-show_entries', 'format=duration', '-of', 'json', path]);
  return JSON.parse(stdout);
}
export function verifyVideo(probe: Probe, expected: {width: number; height: number; fps: number; frames: number}) {
  const stream = probe.streams.find(s => s.codec_name === 'h264');
  assert.ok(stream, 'H.264 video required');
  assert.equal(stream.width, expected.width); assert.equal(stream.height, expected.height);
  assert.equal(stream.r_frame_rate, `${expected.fps}/1`); assert.equal(Number(stream.nb_frames), expected.frames);
  assert.equal(stream.pix_fmt, 'yuv420p');
  assert.ok(Math.abs(Number(probe.format.duration) - expected.frames / expected.fps) < .05, 'Unexpected video duration');
}
