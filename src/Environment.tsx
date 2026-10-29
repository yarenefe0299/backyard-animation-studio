import {useLayoutEffect, useMemo, useRef} from 'react';
import {DataTexture, DoubleSide, InstancedMesh, Object3D, Quaternion, RGBAFormat,
  RepeatWrapping, Shape, SRGBColorSpace, Vector3} from 'three';
import {Ball, Part} from './Primitives';

const rand = (n: number) => {const v = Math.sin(n * 127.1) * 43758.5453; return v - Math.floor(v);};
function surface(kind: 'wood' | 'roof' | 'bark') {
  const size = 128, data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const grain = .8 + rand(x * 19 + y * 31) * .2;
    const stripe = Math.sin(x * .65 + Math.sin(y * .035) * 2) * .06;
    const seam = kind === 'roof' && (y % 21 < 2 || (x + Math.floor(y / 21) % 2 * 16) % 32 < 1) ? .65 : 1;
    const base = kind === 'wood' ? [144, 127, 103] : kind === 'bark' ? [102, 86, 65] : [72, 80, 83];
    for (let c = 0; c < 3; c++) data[(y * size + x) * 4 + c] = base[c] * (grain + stripe) * seam;
    data[(y * size + x) * 4 + 3] = 255;
  }
  const map = new DataTexture(data, size, size, RGBAFormat);
  map.colorSpace = SRGBColorSpace; map.wrapS = map.wrapT = RepeatWrapping;
  map.needsUpdate = true;
  return map;
}
function Box({size, color, position, rotation}: {size: [number, number, number]; color: string;
  position?: [number, number, number]; rotation?: [number, number, number]}) {
  return <mesh position={position} rotation={rotation} castShadow receiveShadow><boxGeometry args={size}/>
    <meshStandardMaterial color={color} roughness={.9}/></mesh>;
}

export function Shed() {
  const maps = useMemo(() => ({wood: surface('wood'), roof: surface('roof')}), []);
  const gable = useMemo(() => new Shape().moveTo(-1.55, 0).lineTo(0, .66).lineTo(1.55, 0).closePath(), []);
  useLayoutEffect(() => () => Object.values(maps).forEach(m => m.dispose()), [maps]);
  return <group position={[-3.4, 0, -3.65]}>
    <Box size={[3.3, .12, 2.7]} position={[0, 0, 0]} color="#9b9b8f"/>
    <mesh position={[0, 1.24, 0]} castShadow receiveShadow><boxGeometry args={[3.1, 2.4, 2.5]}/>
      <meshStandardMaterial map={maps.wood} bumpMap={maps.wood} bumpScale={.014} roughness={.95}/></mesh>
    <mesh position={[0, 2.44, -1.25]} castShadow><extrudeGeometry args={[gable, {depth: 2.5, bevelEnabled: false}]}/>
      <meshStandardMaterial map={maps.wood} roughness={.95}/></mesh>
    {[-1, 1].map(s => <mesh key={s} position={[s * .87, 2.787, 0]} rotation={[0, 0, -s * Math.atan2(.66, 1.55)]} castShadow receiveShadow>
      <boxGeometry args={[1.9, .105, 2.95]}/><meshStandardMaterial map={maps.roof} bumpMap={maps.roof} bumpScale={.01} roughness={.95}/>
    </mesh>)}
    <Box size={[.1, .08, 3.02]} position={[0, 3.17, 0]} color="#485053"/>
    {[-1, 1].map(s => <Box key={s} size={[.09, 2.48, .1]} position={[s * 1.53, 1.24, 1.28]} color="#b7b2a4"/>)}
    {Array.from({length: 18}, (_, i) => <Box key={i} size={[.012, 2.36, .012]} position={[-1.47 + i * .173, 1.24, 1.258]} color="#817664"/>)}
    <Box size={[1.14, 2.14, .09]} position={[-.58, 1.11, 1.29]} color="#c5c1b4"/>
    <Box size={[.98, 2.0, .07]} position={[-.58, 1.08, 1.36]} color="#737b73"/>
    {[-.33, 0, .33].map(x => <Box key={x} size={[.012, 1.96, .015]} position={[-.58 + x, 1.08, 1.405]} color="#5d665e"/>)}
    <Box size={[.84, .075, .035]} position={[-.58, .35, 1.42]} color="#9d9e8b"/>
    <Box size={[.84, .075, .035]} position={[-.58, 1.8, 1.42]} color="#9d9e8b"/>
    <Ball color="#353f42" scale={.028} position={[-.22, 1.05, 1.44]}/>
    <Box size={[.87, .92, .07]} position={[.8, 1.68, 1.29]} color="#c5c1b4"/>
    <Box size={[.72, .77, .06]} position={[.8, 1.68, 1.34]} color="#69828c"/>
    <Box size={[.04, .78, .06]} position={[.8, 1.68, 1.38]} color="#c5c1b4"/>
    <Box size={[.74, .04, .06]} position={[.8, 1.68, 1.38]} color="#c5c1b4"/>
    <Box size={[.96, .07, .21]} position={[.8, 1.22, 1.38]} color="#bcb9ab"/>
    <Part size={[.86, .22, .3]} position={[.8, 1.08, 1.43]} color="#8b6b54" radius={.008}/>
    {[-.26, 0, .26].map((x, i) => <group key={x} position={[.8 + x, 1.24, 1.43]}>
      <Part size={[.025, .2, .025]} position={[0, .09, 0]} color="#606a49" radius={.005}/>
      <Ball color={i % 2 ? '#c4aa72' : '#b78276'} scale={[.06, .04, .06]} position={[0, .21, 0]}/>
    </group>)}
  </group>;
}

export function Tree({frame, position, scale = 1}: {frame: number; position: [number, number, number]; scale?: number}) {
  const branchRef = useRef<InstancedMesh>(null), leafRef = useRef<InstancedMesh>(null);
  const bark = useMemo(() => surface('bark'), []);
  const spec = useMemo(() => {
    const branches: {a: Vector3; b: Vector3; radius: number}[] = [{a: new Vector3(0, 0, 0), b: new Vector3(.08, 2.4, 0), radius: .14}];
    const tips: Vector3[] = [];
    for (let i = 0; i < 5; i++) {
      const angle = i * 2.4;
      const a = new Vector3(.04, 1.45 + i * .13, 0);
      const b = new Vector3(Math.cos(angle) * .78, 2.5 + rand(i + 1) * .6, Math.sin(angle) * .7);
      branches.push({a, b, radius: .055});
      for (let j = 0; j < 5; j++) {
        const theta = angle + (j - 2) * .5;
        const end = b.clone().add(new Vector3(Math.cos(theta) * .65, .3 + rand(i * 9 + j) * .4, Math.sin(theta) * .6));
        branches.push({a: b, b: end, radius: .02}); tips.push(end);
      }
    }
    const leaf = new Shape().moveTo(0, -.065).quadraticCurveTo(.04, -.025, 0, .065).quadraticCurveTo(-.04, -.025, 0, -.065).closePath();
    return {branches, tips, leaf};
  }, []);
  useLayoutEffect(() => () => bark.dispose(), [bark]);
  useLayoutEffect(() => {
    const m = new Object3D(), up = new Vector3(0, 1, 0);
    spec.branches.forEach((b, i) => {
      const delta = b.b.clone().sub(b.a);
      m.position.copy(b.a).add(b.b).multiplyScalar(.5);
      m.quaternion.copy(new Quaternion().setFromUnitVectors(up, delta.clone().normalize()));
      m.scale.set(b.radius, delta.length(), b.radius); m.updateMatrix(); branchRef.current?.setMatrixAt(i, m.matrix);
    });
    if (branchRef.current) branchRef.current.instanceMatrix.needsUpdate = true;
  }, [spec]);
  useLayoutEffect(() => {
    const m = new Object3D();
    for (let i = 0; i < 1600; i++) {
      const tip = spec.tips[i % spec.tips.length], angle = i * 2.4;
      const radius = Math.sqrt(rand(i + 8)) * .36;
      m.position.copy(tip).add(new Vector3(Math.cos(angle) * radius, (rand(i + 17) - .5) * .55, Math.sin(angle) * radius));
      m.rotation.set(rand(i + 2) * 3.14, angle + Math.sin(frame * .025 + i) * .025, rand(i + 5) * 3.14);
      const s = .7 + rand(i + 4) * .65; m.scale.set(s, s, s); m.updateMatrix(); leafRef.current?.setMatrixAt(i, m.matrix);
    }
    if (leafRef.current) leafRef.current.instanceMatrix.needsUpdate = true;
  }, [spec, frame]);
  return <group position={position} scale={scale}>
    <instancedMesh ref={branchRef} args={[undefined, undefined, spec.branches.length]} castShadow receiveShadow>
      <cylinderGeometry args={[.65, 1, 1, 8]}/><meshStandardMaterial map={bark} roughness={1}/>
    </instancedMesh>
    <instancedMesh ref={leafRef} args={[undefined, undefined, 1600]} castShadow={scale === 1}>
      <shapeGeometry args={[spec.leaf, 3]}/><meshStandardMaterial color="#6c7750" roughness={1} side={DoubleSide}/>
    </instancedMesh>
  </group>;
}

export function Neighborhood({frame}: {frame: number}) {
  const gable = useMemo(() => new Shape().moveTo(-3, 0).lineTo(0, 1.1).lineTo(3, 0).closePath(), []);
  return <group>
    {[-1, 1].map(s => <group key={s}>
      <Tree frame={frame} position={[s * 8.5, -.05, -11]} scale={1.4}/>
      <group position={[s * 6, 0, -16]}>
        <Box size={[6, 3.7, 4.5]} position={[0, 1.8, 0]} color={s === 1 ? '#b7afa1' : '#a8a795'}/>
        <mesh position={[0, 3.65, -2.25]} castShadow><extrudeGeometry args={[gable, {depth: 4.5, bevelEnabled: false}]}/>
          <meshStandardMaterial color={s === 1 ? '#b7afa1' : '#a8a795'} roughness={1}/></mesh>
        {[-1, 1].map(side => <Box key={side} size={[3.5, .16, 5]} position={[side * 1.5, 4.285, 0]} rotation={[0, 0, -side * Math.atan2(1.1, 3)]} color="#646c6a"/>)}
        <Box size={[.12, .08, 5.04]} position={[0, 4.9, 0]} color="#646c6a"/>
        {[-1.7, 0, 1.7].map(x => <Box key={x} size={[.8, 1.05, .06]} position={[x, 2.3, 2.28]} color="#536e7d"/>)}
      </group>
    </group>)}
    {[-20, 18].map(x => <mesh key={x} position={[x, -.7, -40]} scale={[22, 3.5, 14]} receiveShadow>
      <sphereGeometry args={[1, 20, 12]}/><meshStandardMaterial color="#77846c" roughness={1}/>
    </mesh>)}
  </group>;
}
