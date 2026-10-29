import {test} from 'node:test';
import assert from 'node:assert/strict';
import {roundedGeometry} from '../src/rounded-geometry.ts';

test('thin non-cubic armor panels have outward, unpinched corner normals', () => {
  for (const size of [[.24, .34, .07], [.18, .38, .065], [.02, .18, .008]] as [number, number, number][]) {
    const g = roundedGeometry(size, .025);
    const position = g.attributes.position, normal = g.attributes.normal;
    for (let i = 0; i < position.count; i++) for (let axis = 0; axis < 3; axis++) {
      const p = position.array[i * 3 + axis], n = normal.array[i * 3 + axis];
      assert.ok(p * n >= -1e-7, 'corner normal points toward the box center');
      assert.ok(Math.abs(p) <= size[axis] / 2 + 1e-6, 'geometry exceeds the requested panel');
    }
    g.dispose();
  }
});
