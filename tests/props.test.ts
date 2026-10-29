import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Quaternion, Vector3} from 'three';
import {cardboardPose, paperPose} from '../src/prop-motion.ts';
import {propReleaseFrame} from '../src/story.ts';

test('drawing starts at the releasing hand and settles flat on the lawn', () => {
  const release = {position: new Vector3(-.2, 1.6, 1), quaternion: new Quaternion()};
  const first = paperPose(propReleaseFrame, release);
  assert.deepEqual(first.position, release.position.toArray());
  assert.ok(first.quaternion.angleTo(release.quaternion) < 1e-7);
  const last = paperPose(propReleaseFrame + 100, release);
  assert.ok(Math.abs(last.position[1] - (-.038)) < .0001);
  assert.ok(last.position[1] < first.position[1]);
  assert.deepEqual(last.position, paperPose(propReleaseFrame + 200, release).position);
});
test('cardboard descends continuously and stays put after ground contact', () => {
  let last = cardboardPose(propReleaseFrame).position[1];
  for (let i = 1; i <= 100; i++) {
    const y = cardboardPose(propReleaseFrame + i).position[1];
    assert.ok(y <= last + .0001);
    assert.ok(last - y < .22, 'a falling panel teleported');
    assert.ok(y >= -.028);
    last = y;
  }
  assert.deepEqual(cardboardPose(299).position, cardboardPose(298).position);
});
