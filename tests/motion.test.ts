import {test} from 'node:test';
import assert from 'node:assert/strict';
import {poseAt} from '../src/motion.ts';
import {episode, totalFrames, shotStart, validateEpisode, captionAt} from '../src/story.ts';
import type {Feature} from '../src/story.ts';

test('full story has eight cumulative beats and 48 seconds of valid delivery', () => {
  validateEpisode(episode);
  assert.equal(totalFrames(), 1440);
  assert.equal(episode.shots.length, 8);
  assert.equal(episode.width / episode.height, 9 / 16);
  for (const shot of episode.shots) assert.ok(shot.narration.length > 30);
});
test('every upgrade remains installed and no flight happens before hover modules', () => {
  const previous: Record<string, number> = {};
  for (let f = 0; f < totalFrames(); f++) {
    const p = poseAt(f);
    for (const [name, progress] of Object.entries(p.progress)) {
      assert.ok(progress >= 0 && progress <= 1);
      assert.ok(progress >= (previous[name] || 0), `${name} was removed`);
      previous[name] = progress;
    }
    for (const v of Object.values(p)) if (typeof v === 'number') assert.ok(Number.isFinite(v));
    if (f < shotStart('hover-test')) assert.equal(p.lift, 0);
    assert.ok(p.lift >= 0 && p.lift <= 3);
    assert.ok(captionAt(f).word.length > 0);
  }
  assert.deepEqual(Object.values(poseAt(1439).progress), [1, 1, 1, 1, 1, 1, 1]);
});
test('power causes heat, cooling resolves it, and stabilization resolves wobble', () => {
  assert.equal(poseAt(shotStart('power')).heat, 0);
  assert.ok(poseAt(shotStart('cooling') - 1).heat > .99);
  assert.equal(poseAt(shotStart('cooling')).heat, 1);
  assert.equal(poseAt(shotStart('cooling') + 140).heat, 0);
  assert.equal(poseAt(shotStart('flight') - 1).wobble, 0);
  assert.equal(poseAt(shotStart('flight')).lift, poseAt(shotStart('flight') - 1).lift);
});
test('invalid upgrade dependencies fail before rendering', () => {
  const bad = {...episode, shots: episode.shots.map((shot, i) => i === 1 ? {...shot, add: ['hover'] as Feature[]} : shot)};
  assert.throws(() => validateEpisode(bad), /Hover requires/);
});
test('frames rendered out of order retain the same state', () => {
  const frame = shotStart('power') + 145, expected = poseAt(frame);
  [1439, 4, 990, 180, 0, 610].forEach(f => poseAt(f));
  assert.deepEqual(poseAt(frame), expected);
});
