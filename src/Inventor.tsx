import {useLayoutEffect, useMemo} from 'react';
import {createPortal} from '@react-three/fiber';
import {Matrix4, Quaternion, Vector3} from 'three';
import {Ball, Part, Ring} from './Primitives';
import {createHumanRig} from './human-rig';
import {poseAt} from './motion';
import {cardboardPose, paperPose} from './prop-motion';
import data from './assets/inventor.json';
import {propReleaseFrame, shotStart} from './story';

const metal = '#82939c', edge = '#34434e', turquoise = '#3aa9ae';
function Plate({size, color = metal}: {size: [number, number, number]; color?: string}) {
  return <group>
    <Part size={size} color={color} radius={.025} metalness={.18} roughness={.6}/>
    <Part size={[size[0] * .58, .012, .006]} radius={.002}
      position={[0, size[1] * .31, size[2] / 2 + .003]} color={edge}/>
    {[-1, 1].map(s => <Ball key={s} color={edge} scale={.009}
      position={[s * size[0] * .34, -size[1] * .32, size[2] / 2 + .006]}/>)}
  </group>;
}
function Sketch() {
  return <group>
    <Part size={[.3, .38, .006]} radius={.001} color="#dfd3b7"/>
    <Ring radius={.03} color="#53636b" position={[0, .105, .006]} scale={.6}/>
    <Part size={[.065, .105, .002]} radius={.001} color="#53636b" position={[0, .015, .007]}/>
    {[-1, 1].map(s => <group key={s}>
      <Part size={[.006, .08, .002]} radius={.001} color="#53636b" position={[s * .05, .01, .008]} rotation={[0, 0, s * .3]}/>
      <Part size={[.006, .075, .002]} radius={.001} color="#53636b" position={[s * .024, -.075, .008]}/>
    </group>)}
  </group>;
}

export const Inventor = ({frame}: {frame: number}) => {
  const p = poseAt(frame);
  const rig = useMemo(createHumanRig, []);
  // Calculate the precise hand transform at release, independently of render
  // order. The falling drawing starts where the hand really was.
  const release = useMemo(() => {
    rig.setFrame(propReleaseFrame);
    const actor = new Matrix4().makeRotationY(-.08).setPosition(.3, -.05, .65);
    const local = new Matrix4().makeTranslation(0, -.075, .05);
    const m = actor.multiply(rig.bones['wrist.R'].matrixWorld).multiply(local);
    const position = new Vector3(), quaternion = new Quaternion(), scale = new Vector3();
    m.decompose(position, quaternion, scale);
    return {position, quaternion};
  }, [rig]);
  useLayoutEffect(() => {rig.setFrame(frame);}, [rig, frame]);
  useLayoutEffect(() => () => rig.dispose(), [rig]);
  const spread = (1 - p.assemble) * .9;
  const paperHeld = frame < propReleaseFrame;
  return <>
    <group position={[.3, -.05 + p.lift, .65]} rotation={[0, -.08, 0]}>
      <primitive object={rig.mesh}/>
      {data.eyes.map((eye, i) => {
        const head = data.bones.find(b => b.name === 'head')!;
        return createPortal(<group key={`eye-${i}`} position={[eye[0] - head.head[0], eye[1] - head.head[1], eye[2] - head.head[2]]}>
          <Ball color="#d9d6c9" scale={.031}/>
          <Ball color="#687970" position={[0, 0, .029]} scale={[.012, .012, .004]}/>
          <Ball color="#1c2426" position={[0, 0, .033]} scale={[.005, .007, .002]}/>
          <Ball color="#e9f0ed" position={[-.003, .004, .035]} scale={.002}/>
        </group>, rig.bones.head);
      })}
      {!p.metal && paperHeld && createPortal(<group position={[0, -.075, .05]}><Sketch/></group>, rig.bones['wrist.R'])}
      {p.metal && <>
        {createPortal(<group>
          {[-1, 1].map(s => <group key={s} position={[s * .128, .015, .3 + spread]} rotation={[0, -s * .1, 0]}>
            <Plate size={[.24, .34, .07]}/>
            <Part size={[.02, .18, .008]} color={turquoise} radius={.003} position={[s * -.07, .015, .04]}/>
          </group>)}
          {[0, 1, 2].map(i => <group key={i} position={[0, -.23 - i * .085, .27]}><Plate size={[.34 - i * .015, .075, .045]}/></group>)}
          <Part size={[.31, .05, .06]} position={[0, .23, .25]} color={edge} radius={.01}/>
          <Part size={[.32, .4, .16]} position={[0, .015, -.15 - spread * .3]} color={edge} radius={.025}/>
          {[-1, 1].map(s => <Part key={s} size={[.065, .27, .05]} color={turquoise}
            position={[s * .1, .015, -.25]} radius={.01}/>)}
        </group>, rig.bones.spine01)}
        {(['L', 'R'] as const).map((suffix, i) => {
          const s = i === 0 ? 1 : -1;
          return <group key={suffix}>
            {createPortal(<group position={[s * (.02 + spread * .3), -.045, .03]}><Plate size={[.27, .16, .28]}/></group>, rig.bones[`upperarm01.${suffix}`])}
            {createPortal(<group position={[s * .035, -.13, .135]} rotation={[0, 0, -s * .4]}>
              <Plate size={[.15, .27, .075]}/>
              <Part size={[.018, .15, .01]} position={[s * .045, .01, .043]} radius={.003} color={turquoise}/>
              <Part size={[.022, .23, .022]} position={[s * .08, -.01, -.08]} radius={.008} color="#9eacb3" metalness={.3}/>
            </group>, rig.bones[`lowerarm01.${suffix}`])}
            {createPortal(<group position={[s * .025, -.29, .15 + spread * .2]}><Plate size={[.23, .4, .065]}/></group>, rig.bones[`upperleg01.${suffix}`])}
            {createPortal(<group position={[s * .025, -.3, .125]}>
              <Plate size={[.18, .38, .065]}/>
              <Part size={[.018, .23, .008]} position={[s * .05, 0, .04]} color={turquoise} radius={.003}/>
            </group>, rig.bones[`lowerleg01.${suffix}`])}
            {createPortal(<group position={[0, -.035, .115]}>
              <Part size={[.2, .14, .4]} color={metal} radius={.03} metalness={.18} roughness={.6}/>
              <Part size={[.2, .025, .4]} position={[0, -.065, 0]} radius={.008} color={edge}/>
              <Part size={[.14, .012, .26]} position={[0, -.083, 0]} color={turquoise} radius={.003} glow={.3}/>
              {p.hover > .01 && <mesh position={[0, -.16, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <ringGeometry args={[.06, .12 + p.hover * .05, 32]}/><meshBasicMaterial color="#85e1dd" transparent opacity={p.hover * .4} side={2}/>
              </mesh>}
            </group>, rig.bones[`foot.${suffix}`])}
          </group>;
        })}
      </>}
    </group>
    {!paperHeld && <FallingSketch frame={frame} release={release}/>}
    {!p.metal && <Cardboard frame={frame}/>}
    {p.metal && <Cardboard frame={shotStart('upgrade') - 1}/>}
  </>;
};

function FallingSketch({frame, release}: {frame: number; release: {position: Vector3; quaternion: Quaternion}}) {
  const pose = paperPose(frame, release);
  return <group position={pose.position} quaternion={pose.quaternion}><Sketch/></group>;
}

function Cardboard({frame}: {frame: number}) {
  const pose = cardboardPose(frame);
  return <group position={pose.position} rotation={pose.rotation}>
    <Part size={[.61, .58, .025]} color="#aa8864" radius={.002}/>
    <Part size={[.095, .56, .005]} color="#c7b18b" position={[0, 0, .016]} radius={.001}/>
    <Part size={[.6, .065, .005]} color="#c7b18b" position={[0, .025, .017]} radius={.001}/>
    {Array.from({length: 11}, (_, i) => <Part key={i} size={[.005, .55, .001]} color="#9f7e5a"
      radius={.0004} position={[(i - 5) * .052, 0, .013]}/>)}
  </group>;
}


