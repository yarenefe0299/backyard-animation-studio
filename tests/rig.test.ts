import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Vector3} from 'three';
import {createHumanRig} from '../src/human-rig.ts';
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
    for (const frame of [0, 90, 92, 150, 180, 222, 235, 262, 290, 299]) {
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
    rig.setFrame(180);
    const first = rig.bones['wrist.R'].matrixWorld.elements.slice();
    rig.setFrame(0); rig.setFrame(299); rig.setFrame(180);
    assert.deepEqual(rig.bones['wrist.R'].matrixWorld.elements, first);
  } finally {rig.dispose();}
});
