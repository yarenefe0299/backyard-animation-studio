import {test} from 'node:test';
import assert from 'node:assert/strict';
import {poseAt} from '../src/motion.ts';
import {preview, shotAt, totalFrames} from '../src/story.ts';

test('storyboard composes exactly ten seconds with no shot gaps', () => {
  assert.equal(totalFrames, 300);
  assert.equal(preview.width / preview.height, 9 / 16);
  assert.deepEqual([0, 71, 72, 155, 156, 221, 222, 299].map(f => shotAt(f).id),
    ['idea', 'idea', 'collapse', 'collapse', 'upgrade', 'upgrade', 'hover', 'hover']);
});
test('all rendered poses are finite and grounded debris never penetrates the lawn', () => {
  for (let f = 0; f < totalFrames; f++) {
    const p = poseAt(f);
    for (const v of Object.values(p)) if (typeof v === 'number') assert.ok(Number.isFinite(v));
    assert.ok(p.debrisY >= .07);
    assert.ok(p.lift >= 0 && p.lift <= .85);
  }
});
test('cardboard fails, metal assembles, hover rises and settles', () => {
  assert.equal(poseAt(72).fail, 0);
  assert.equal(poseAt(155).fail, 1);
  assert.ok(poseAt(156).panelSpread > poseAt(210).panelSpread);
  assert.ok(poseAt(262).lift > .8);
  assert.ok(poseAt(299).lift < .001);
  assert.equal(poseAt(299).metal, true);
});
test('rendering frames out of order cannot change motion state', () => {
  const expected = poseAt(265);
  [299, 4, 200, 72, 0, 112].forEach(poseAt);
  assert.deepEqual(poseAt(265), expected);
});
