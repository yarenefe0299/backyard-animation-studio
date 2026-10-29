import {RoundedBoxGeometry} from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';

export function roundedGeometry(size: [number, number, number], radius: number) {
  // r178's corner normals assume unit-cube coordinates. Scale after construction.
  const r = Math.max(.001, Math.min(.48, radius / Math.min(...size)));
  return new RoundedBoxGeometry(1, 1, 1, 3, r).scale(...size);
}
