import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Vector3} from 'three';
import {createHumanRig} from '../src/human-rig.ts';
import {shotStart} from '../src/story.ts';
import data from '../src/assets/inventor.json' with {type: 'json'};

test('compiled human has valid topology, normalized skin weights and adult scale', () => {
  const count = data.position.length / 3;
  assert.ok(count > 10000);
  for (const index of data.index) assert.ok(index >= 0 && index < count);
  for (let i = 0; i < count; i++) {
    let sum = 0;
    for (let j = 0; j < 4; j++) {
      assert.ok(data.skinIndex[i * 4 + j] < data.bones.length);
      const w = data.skinWeight[i * 4 + j];
      assert.ok(w >= 0 && w <= 1);
      sum += w;
    }
    assert.ok(Math.abs(sum - 1) < 1e-5, 'unweighted or over-weighted skin vertex');
  }
  const ys = data.position.filter((_, i) => i % 3 === 1);
  assert.ok(Math.max(...ys) - Math.min(...ys) > 2.7);
});

test('deformed human stays finite and its soles remain grounded before actor lift', () => {
  const rig = createHumanRig(), v = new Vector3();
  try {
    for (const frame of [0, 120, 190, 330, 390, 510, 670, 750, 850, 1000, 1160, 1280, 1439]) {
      rig.setFrame(frame);
      let min = Infinity, max = -Infinity;
      for (let i = 0; i < rig.mesh.geometry.attributes.position.count; i++) {
        v.fromBufferAttribute(rig.mesh.geometry.attributes.position, i);
        rig.mesh.applyBoneTransform(i, v).applyMatrix4(rig.mesh.matrixWorld);
        assert.ok(v.toArray().every(Number.isFinite), `invalid skin pose at frame ${frame}`);
        min = Math.min(min, v.y); max = Math.max(max, v.y);
      }
      assert.ok(Math.abs(min) < .0001, `feet drifted from ground at frame ${frame}`);
      assert.ok(max > 2.5 && max < 3.1, 'skin collapsed or stretched');
    }
    rig.setFrame(shotStart('power') + 150);
    const first = rig.bones['wrist.R'].matrixWorld.elements.slice();
    rig.setFrame(0); rig.setFrame(1439); rig.setFrame(shotStart('power') + 150);
    assert.deepEqual(rig.bones['wrist.R'].matrixWorld.elements, first);
  } finally {rig.dispose();}
});

test('heated inventor raises a hand toward the forehead and cools back to rest', () => {
  const rig = createHumanRig();
  try {
    rig.setFrame(shotStart('power'));
    const rest = rig.bones['wrist.L'].getWorldPosition(new Vector3());
    rig.setFrame(shotStart('power') + 160);
    const hot = rig.bones['wrist.L'].getWorldPosition(new Vector3());
    assert.ok(hot.y > rest.y + .5);
    assert.ok(hot.distanceTo(new Vector3(.22, 2.54, .29)) < .18);
    rig.setFrame(shotStart('cooling') + 160);
    const cool = rig.bones['wrist.L'].getWorldPosition(new Vector3());
    assert.ok(cool.y < hot.y - .5);
  } finally {rig.dispose();}
});
test('finger skin is not painted with the trouser color', () => {
  let checked = 0;
  for (let i = 0; i < data.position.length / 3; i++) {
    let fingers = 0;
    for (let j = 0; j < 4; j++) if (data.bones[data.skinIndex[i * 4 + j]].name.startsWith('finger')) fingers += data.skinWeight[i * 4 + j];
    if (fingers > .8) {
      assert.ok(data.color[i * 3] > data.color[i * 3 + 2]); checked++;
    }
  }
  assert.ok(checked > 50);
});
