import {useLayoutEffect, useMemo} from 'react';
import {DoubleSide, PlaneGeometry} from 'three';
import {Ball, Part} from './Primitives';

export function GardenBed() {
  return <group position={[2.8, -.04, -.8]}>
    {[-1, 1].map(s => <Part key={s} size={[1.65, .25, .045]} position={[0, .125, s * .37]} color="#89745e" radius={.004}/>)}
    {[-1, 1].map(s => <Part key={s} size={[.045, .25, .75]} position={[s * .82, .125, 0]} color="#89745e" radius={.004}/>)}
    <Part size={[1.56, .2, .66]} position={[0, .1, 0]} color="#584b37" radius={.003}/>
    {[-.5, 0, .5].map((x, i) => <group key={x} position={[x, .2, 0]}>
      <mesh position={[0, .25, 0]} castShadow><cylinderGeometry args={[.009, .013, .5, 8]}/><meshStandardMaterial color="#5a704c" roughness={1}/></mesh>
      {[-1, 1].map(s => <mesh key={s} position={[s * .055, .17 + i * .025, 0]} rotation={[.25, 0, s * -.55]} scale={[.075, .025, .025]}>
        <sphereGeometry args={[1, 10, 6]}/><meshStandardMaterial color="#687a4e" roughness={1}/>
      </mesh>)}
      <group position={[0, .5, .015]} rotation={[-.15, i * .15, 0]}>
        {Array.from({length: 7}, (_, j) => <mesh key={j} position={[Math.cos(j * Math.PI * 2 / 7) * .055, Math.sin(j * Math.PI * 2 / 7) * .055, 0]}
          rotation={[0, 0, j * Math.PI * 2 / 7]} scale={[.05, .022, .009]} castShadow>
          <sphereGeometry args={[1, 10, 6]}/><meshStandardMaterial color={i % 2 ? '#c6b07a' : '#b98376'} roughness={.9}/>
        </mesh>)}
        <Ball color="#7d6842" scale={[.025, .025, .016]} position={[0, 0, .016]}/>
      </group>
    </group>)}
  </group>;
}
export function WateringCan() {
  return <group position={[2.3, .13, -1.5]}>
    <mesh castShadow><cylinderGeometry args={[.16, .18, .34, 24]}/><meshStandardMaterial color="#99936f" roughness={.7} metalness={.2}/></mesh>
    <mesh position={[-.27, .07, 0]} rotation={[0, 0, 1.05]} castShadow>
      <cylinderGeometry args={[.025, .045, .38, 12]}/><meshStandardMaterial color="#99936f" roughness={.7} metalness={.2}/>
    </mesh>
    <mesh position={[-.43, .165, 0]} rotation={[0, 0, 1.05]} castShadow>
      <cylinderGeometry args={[.06, .025, .04, 16]}/><meshStandardMaterial color="#8c927f" roughness={.65}/>
    </mesh>
    <mesh position={[.22, .02, 0]} castShadow><torusGeometry args={[.145, .017, 8, 24]}/>
      <meshStandardMaterial color="#99936f" roughness={.7} metalness={.2}/></mesh>
  </group>;
}
function Cloth({frame, offset, color}: {frame: number; offset: number; color: string}) {
  const geometry = useMemo(() => new PlaneGeometry(.6, .82, 8, 8), []);
  useLayoutEffect(() => {
    const positions = geometry.attributes.position;
    for (let i = 0; i < positions.count; i++) {
      const free = (.41 - positions.getY(i)) / .82;
      positions.setZ(i, Math.sin(frame * .035 + positions.getX(i) * 5 + offset) * .055 * free);
    }
    positions.needsUpdate = true; geometry.computeVertexNormals();
  }, [geometry, frame, offset]);
  useLayoutEffect(() => () => geometry.dispose(), [geometry]);
  return <mesh geometry={geometry} receiveShadow><meshStandardMaterial color={color} side={DoubleSide} roughness={1}/></mesh>;
}
export function Laundry({frame}: {frame: number}) {
  return <group>
    {[1.2, 4.8].map(x => <Part key={x} size={[.055, 2.6, .055]} position={[x, 1.25, -4.65]} color="#7c8588" radius={.004}/>)}
    <Part size={[3.6, .012, .012]} position={[3, 2.5, -4.65]} color="#bdb9a7" radius={.002}/>
    {[1.8, 2.8, 3.8].map((x, i) => <group key={x} position={[x, 2.08, -4.65]}>
      <Cloth frame={frame} offset={i} color={['#b9b19b', '#7b9799', '#a68c80'][i]}/>
      {[-1, 1].map(s => <Part key={s} size={[.02, .07, .025]} position={[s * .22, .4, .005]} color="#8f7962" radius={.002}/>)}
    </group>)}
  </group>;
}
