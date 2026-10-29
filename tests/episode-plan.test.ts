import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createPlan, subtitles} from '../scripts/plan-episode.ts';
import {episode, totalFrames} from '../src/story.ts';
import {verifyVideo} from '../scripts/video.ts';

test('render chunks cover the full timeline exactly once and stay within seven seconds', () => {
  for (const ep of [episode, {...episode, shots: episode.shots.map((s, i) => i === 0 ? {...s, frames: 421} : s)}]) {
    const plan = createPlan(ep);
    let next = 0;
    for (const chunk of plan.chunks) {
      assert.equal(chunk.from, next); assert.equal(chunk.frames, chunk.to - chunk.from + 1);
      assert.ok(chunk.frames <= 210); next = chunk.to + 1;
    }
    assert.equal(next, totalFrames(ep));
    assert.equal(plan.review.length, ep.shots.length * 2);
  }
  assert.match(subtitles(episode), /00:00:48,000/);
});
test('assembled encoding validation rejects missing frames and the wrong frame rate', () => {
  const probe = {streams: [{codec_name: 'h264', width: 1080, height: 1920, r_frame_rate: '30/1', nb_frames: '1440', pix_fmt: 'yuv420p'}], format: {duration: '48'}};
  const expected = {width: 1080, height: 1920, fps: 30, frames: 1440};
  verifyVideo(probe, expected);
  assert.throws(() => verifyVideo({...probe, streams: [{...probe.streams[0], nb_frames: '1439'}]}, expected));
  assert.throws(() => verifyVideo({...probe, streams: [{...probe.streams[0], r_frame_rate: '24/1'}]}, expected));
});
