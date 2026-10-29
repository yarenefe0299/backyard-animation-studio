import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Quaternion, Vector3} from 'three';
import {paperPose} from '../src/prop-motion.ts';
import {paperReleaseFrame} from '../src/story.ts';

test('drawing leaves the actual hand and remains on the lawn for the full story', () => {
  const release = {position: new Vector3(-.2, 1.6, 1), quaternion: new Quaternion()};
  const first = paperPose(paperReleaseFrame(), release);
  assert.deepEqual(first.position, release.position.toArray());
  assert.ok(first.quaternion.angleTo(release.quaternion) < 1e-7);
  const last = paperPose(paperReleaseFrame() + 100, release);
  assert.ok(Math.abs(last.position[1] - (-.038)) < .0001);
  assert.deepEqual(last.position, paperPose(1439, release).position);
});
