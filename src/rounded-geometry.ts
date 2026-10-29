import {BoxGeometry, Vector3} from 'three';

// Build in unit space, then place each corner with a physical (uniform) radius.
// Scaling a beveled cube afterward turns thin roof boards into swollen pillows.
export function roundedGeometry(size: [number, number, number], radius: number) {
  const r = Math.max(.0001, Math.min(...size.map(v => v / 2), radius));
  const segments = 5;
  const indexed = new BoxGeometry(1, 1, 1, segments, segments, segments);
  const geometry = indexed.toNonIndexed(); indexed.dispose();
  const positions = geometry.attributes.position, normals = geometry.attributes.normal;
  const p = new Vector3(), n = new Vector3();
  for (let i = 0; i < positions.count; i++) {
    p.fromBufferAttribute(positions, i);
    n.set(p.x - Math.sign(p.x) * .1, p.y - Math.sign(p.y) * .1, p.z - Math.sign(p.z) * .1).normalize();
    positions.setXYZ(i,
      (size[0] / 2 - r) * Math.sign(p.x) + n.x * r,
      (size[1] / 2 - r) * Math.sign(p.y) + n.y * r,
      (size[2] / 2 - r) * Math.sign(p.z) + n.z * r);
    normals.setXYZ(i, n.x, n.y, n.z);
  }
  positions.needsUpdate = normals.needsUpdate = true;
  return geometry;
}
