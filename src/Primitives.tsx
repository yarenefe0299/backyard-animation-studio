import {useMemo} from 'react';
import type {ThreeElements} from '@react-three/fiber';
import {roundedGeometry} from './rounded-geometry';

type PartProps = {
  size: [number, number, number]; color: string; radius?: number;
  metalness?: number; roughness?: number; glow?: number;
} & Omit<ThreeElements['mesh'], 'args' | 'geometry' | 'material'>;

export const Part = ({size, color, radius = .06, metalness = 0,
  roughness = .65, glow = 0, ...props}: PartProps) => {
  const geometry = useMemo(() => roundedGeometry(size, radius),
    [size[0], size[1], size[2], radius]);
  return <mesh {...props} geometry={geometry} castShadow receiveShadow>
    <meshStandardMaterial color={color} roughness={roughness} metalness={metalness}
      emissive={color} emissiveIntensity={glow}/>
  </mesh>;
};

export const Ball = ({color, ...props}: {color: string} & ThreeElements['mesh']) =>
  <mesh {...props} castShadow receiveShadow><sphereGeometry args={[1, 24, 16]}/>
    <meshStandardMaterial color={color} roughness={.6}/></mesh>;

export const Ring = ({color, radius = .2, ...props}: {color: string; radius?: number} & ThreeElements['mesh']) =>
  <mesh {...props} castShadow><torusGeometry args={[radius, Math.min(.018, radius * .14), 8, 24]}/>
    <meshStandardMaterial color={color} roughness={.35} metalness={.3}/></mesh>;
