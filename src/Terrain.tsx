import {useLayoutEffect, useMemo, useRef} from 'react';
import {DataTexture, RGBAFormat, RepeatWrapping, SRGBColorSpace, InstancedMesh,
  Object3D, BackSide} from 'three';

function hash(x: number, y: number) {
  const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
  return n - Math.floor(n);
}
function noise(x: number, y: number) {
  const ix = Math.floor(x), iy = Math.floor(y);
  let fx = x - ix, fy = y - iy;
  fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
  const a = hash(ix, iy), b = hash(ix + 1, iy), c = hash(ix, iy + 1), d = hash(ix + 1, iy + 1);
  return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy;
}
function fbm(x: number, y: number) {
  return noise(x, y) * .55 + noise(x * 3, y * 3) * .28 + noise(x * 9, y * 9) * .17;
}
function texture(kind: 'soil' | 'grass' | 'sky') {
  const width = kind === 'sky' ? 512 : 256, height = 256;
  const bytes = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const n = fbm(x / 22, y / 30), grain = hash(x, y);
    let rgb: number[];
    if (kind === 'soil') {
      const strata = noise(x / 75, y / 6) * .25;
      const crevice = Math.pow(Math.max(0, 1 - Math.abs(noise(x / 35, y / 80) - .5) * 10), 4) * .18;
      const a = .6 + n * .65 + strata - crevice + grain * .09;
      rgb = [111 * a, 77 * a, 49 * a];
    } else if (kind === 'grass') {
      const a = .7 + n * .45 + grain * .16;
      const earth = Math.max(0, noise(x / 40, y / 40) - .56) * 2;
      rgb = [100 * a + earth * 30, 111 * a - earth * 4, 76 * a - earth * 5];
    } else {
      const haze = y / height;
      const cloud = Math.max(0, fbm(x / 48, y / 24) - .48) * 1.7 * (1 - haze);
      rgb = [143 + haze * 46 + cloud * 52, 161 + haze * 30 + cloud * 42, 178 + haze * 15 + cloud * 29];
    }
    const i = (y * width + x) * 4;
    for (let c = 0; c < 3; c++) bytes[i + c] = rgb[c];
    bytes[i + 3] = 255;
  }
  const map = new DataTexture(bytes, width, height, RGBAFormat);
  map.colorSpace = SRGBColorSpace;
  map.wrapS = map.wrapT = RepeatWrapping;
  if (kind !== 'sky') map.repeat.set(3, 2);
  map.needsUpdate = true;
  return map;
}

export function Terrain() {
  const maps = useMemo(() => ({soil: texture('soil'), grass: texture('grass'), sky: texture('sky')}), []);
  useLayoutEffect(() => () => Object.values(maps).forEach(map => map.dispose()), [maps]);
  return <group>
    {/* An exposed soil section, rather than a rounded toy display platform. */}
    <mesh position={[0, -1.2, -1.4]} castShadow receiveShadow>
      <boxGeometry args={[12.6, 2.3, 9.6]}/>
      <meshStandardMaterial map={maps.soil} bumpMap={maps.soil} bumpScale={.11} roughness={1}/>
    </mesh>
    <mesh position={[0, -.045, -1.4]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[12.6, 9.6]}/>
      <meshStandardMaterial map={maps.grass} bumpMap={maps.grass} bumpScale={.025} roughness={1}/>
    </mesh>
    <mesh position={[0, 0, 0]}>
      <sphereGeometry args={[75, 40, 24]}/><meshBasicMaterial map={maps.sky} side={BackSide}/>
    </mesh>
  </group>;
}

export function Leaves({frame}: {frame: number}) {
  const ref = useRef<InstancedMesh>(null);
  useLayoutEffect(() => {
    const m = new Object3D();
    for (let i = 0; i < 240; i++) {
      const angle = i * 2.39996, radius = .3 + Math.sqrt(hash(i, 3)) * 1.3;
      m.position.set(Math.cos(angle) * radius, .3 + hash(i, 4) * 1.3, Math.sin(angle) * radius * .8);
      m.rotation.set(hash(i, 5) * 2, angle + Math.sin(frame * .035 + i) * .045, hash(i, 6));
      m.scale.set(.12 + hash(i, 8) * .12, .045, .07);
      m.updateMatrix(); ref.current?.setMatrixAt(i, m.matrix);
    }
    if (ref.current) ref.current.instanceMatrix.needsUpdate = true;
  }, [frame]);
  return <instancedMesh ref={ref} args={[undefined, undefined, 240]}>
    <sphereGeometry args={[1, 8, 4]}/><meshStandardMaterial color="#626d46" roughness={.95}/>
  </instancedMesh>;
}
