import {useLayoutEffect, useMemo} from 'react';
import {createPortal} from '@react-three/fiber';
import {Matrix4, Quaternion, Vector3} from 'three';
import {Ball, Part, Ring} from './Primitives';
import {createHumanRig} from './human-rig';
import {poseAt} from './motion';
import {paperPose} from './prop-motion';
import {paperReleaseFrame} from './story';
import type {Episode} from './story';
import data from './assets/inventor.json';

const metal = '#82939c', edge = '#34434e', turquoise = '#3aa9ae';
function Plate({size, color = metal}: {size: [number, number, number]; color?: string}) {
  return <group>
    <Part size={size} color={color} radius={.015} metalness={.18} roughness={.6}/>
    <Part size={[size[0] * .58, .012, .006]} radius={.002}
      position={[0, size[1] * .31, size[2] / 2 + .003]} color={edge}/>
    {[-1, 1].map(s => <Ball key={s} color={edge} scale={.007}
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
function CoolingFan({frame}: {frame: number}) {
  return <group>
    <Part size={[.19, .22, .08]} color={edge} radius={.015}/>
    <Ring radius={.07} color="#a6b3b7" position={[0, 0, .048]} scale={.9}/>
    <group position={[0, 0, .05]} rotation={[0, 0, frame * -.38]}>
      {[0, 1, 2, 3].map(i => <Part key={i} size={[.023, .06, .007]} radius={.007}
        position={[Math.sin(i * Math.PI / 2) * .03, Math.cos(i * Math.PI / 2) * .03, 0]}
        rotation={[0, 0, -i * Math.PI / 2]} color="#94b0ba"/>)}
    </group>
    {[0, 1, 2].map(i => <Part key={i} size={[.2, .015, .1]} position={[0, -.14 - i * .035, -.015]} color={metal} radius={.003}/>)}
  </group>;
}

export const Inventor = ({frame, episode}: {frame: number; episode: Episode}) => {
  const p = poseAt(frame, episode);
  const rig = useMemo(() => createHumanRig(episode), [episode]);
  const release = useMemo(() => {
    rig.setFrame(paperReleaseFrame(episode));
    const actor = new Matrix4().makeRotationY(-.08).setPosition(.3, -.05, .65);
    const m = actor.multiply(rig.bones['wrist.R'].matrixWorld).multiply(new Matrix4().makeTranslation(0, -.075, .05));
    const position = new Vector3(), quaternion = new Quaternion(), scale = new Vector3();
    m.decompose(position, quaternion, scale);
    return {position, quaternion};
  }, [rig, episode]);
  useLayoutEffect(() => {rig.setFrame(frame);}, [rig, frame]);
  useLayoutEffect(() => () => rig.dispose(), [rig]);
  const metalSpread = (1 - p.progress.metal) * .75;
  const jointSpread = (1 - p.progress.joints) * .3;
  const paperHeld = frame < paperReleaseFrame(episode);
  const energy = p.heat > .4 ? '#ce7149' : turquoise;
  return <>
    <group position={[.3 + p.pathX, -.05 + p.lift, .65 + p.pathZ]} rotation={[0, p.yaw, 0]}>
      <primitive object={rig.mesh}/>
      {data.eyes.map((eye, i) => {
        const head = data.bones.find(b => b.name === 'head')!;
        return createPortal(<group key={`eye-${i}`} position={[eye[0] - head.head[0], eye[1] - head.head[1], eye[2] - head.head[2] - .006]}>
          <mesh scale={[.027, .022, .025]}><sphereGeometry args={[1, 20, 12]}/><meshStandardMaterial color="#c9c5b9" roughness={.75}/></mesh>
          <Ball color="#68776b" position={[0, 0, .024]} scale={[.0135, .013, .003]}/>
          <Ball color="#1c2426" position={[0, 0, .027]} scale={[.006, .007, .002]}/>
          <Ball color="#dce5e4" position={[-.003, .004, .029]} scale={.0015}/>
          <mesh position={[0, .022 * (1 - p.blink), .015]} scale={[.03, .005 + p.blink * .023, .018]}>
            <sphereGeometry args={[1, 20, 12]}/><meshStandardMaterial color="#c09276" roughness={.8}/>
          </mesh>
        </group>, rig.bones.head);
      })}
      {p.heat > .08 && createPortal(<group>
        {[0, 1, 2].map(i => {
          const fall = (frame * .025 + i / 3) % 1;
          return <mesh key={i} position={[(i % 2 ? -1 : 1) * .13, .06 - fall * .16, .14]} scale={[.007, .012, .005]}>
            <sphereGeometry args={[1, 10, 8]}/><meshStandardMaterial color="#8bbfc4" transparent opacity={p.heat * (1 - fall)} roughness={.25}/>
          </mesh>;
        })}
      </group>, rig.bones.head)}
      {paperHeld && createPortal(<group position={[0, -.075, .05]}><Sketch/></group>, rig.bones['wrist.R'])}
      {createPortal(<group>
        {/* Cardboard stays underneath every subsequent upgrade. Only its loose
            lower flap bends in the first gag; the foundation is never discarded. */}
        <group position={[0, -.02, .295]}>
          <Part size={[.62, .44, .024]} color="#a78a65" radius={.003}/>
          <Part size={[.09, .43, .005]} color="#c5b28d" position={[0, 0, .016]} radius={.001}/>
          <group position={[0, -.22, 0]} rotation={[-p.sag * .55 * (1 - p.progress.metal), 0, 0]}>
            <Part size={[.6, .14, .024]} position={[0, -.07, 0]} color="#a78a65" radius={.003}/>
          </group>
        </group>
        {p.flags.metal && <>
          {[-1, 1].map(s => <group key={s} position={[s * .128, .015, .335 + metalSpread]} rotation={[0, -s * .1, 0]}>
            <Plate size={[.24, .34, .065]}/>
            <Part size={[.02, .18, .008]} color={p.flags.power ? energy : '#5b6e76'} radius={.003} position={[s * -.07, .015, .039]} glow={p.flags.power ? .08 : 0}/>
          </group>)}
          {[0, 1, 2].map(i => <group key={i} position={[0, -.23 - i * .085, .31]}><Plate size={[.34 - i * .015, .075, .04]}/></group>)}
          <Part size={[.31, .05, .055]} position={[0, .23, .27]} color={edge} radius={.008}/>
        </>}
        {p.flags.power && <group position={[-.31 - (1 - p.progress.power) * .5, -.02, .12]}>
          <Part size={[.17, .32, .15]} color={edge} radius={.015}/>
          {[0, 1, 2].map(i => <Part key={i} size={[.095, .055, .02]} position={[0, .085 - i * .08, .085]} color={energy} glow={.12} radius={.006}/>)}
        </group>}
        {p.flags.cooling && <group position={[.31 + (1 - p.progress.cooling) * .5, -.015, .16]}><CoolingFan frame={frame}/></group>}
        {p.flags.stabilizers && <>
          <Part size={[.13, .085, .035]} color={turquoise} position={[0, .23, .31]} radius={.009} glow={.1}/>
          {[-1, 1].map(s => <group key={s} position={[s * .38, .2, -.015]} rotation={[0, 0, s * (1 - p.progress.stabilizers) * .5]}>
            <Part size={[.18, .075, .24]} color={metal} radius={.012}/>
            <Part size={[.035, .03, .16]} color={turquoise} position={[s * .06, .05, 0]} radius={.005}/>
          </group>)}
        </>}
      </group>, rig.bones.spine01)}
      {(['L', 'R'] as const).map((suffix, i) => {
        const s = i === 0 ? 1 : -1;
        return <group key={suffix}>
          {createPortal(<group position={[s * .02, -.045, .03]}>
            <Part size={[.25, .14, .23]} color="#a78a65" radius={.004}/>
            {p.flags.metal && <group position={[s * metalSpread * .2, .015, .025]}><Plate size={[.28, .16, .25]}/></group>}
          </group>, rig.bones[`upperarm01.${suffix}`])}
          {p.flags.metal && createPortal(<group position={[s * .035, -.13, .135]} rotation={[0, 0, -s * .4]}>
            <Plate size={[.15, .27, .065]}/>
            {p.flags.joints && <group position={[s * (.085 + jointSpread), .02, -.05]}>
              <Part size={[.025, .25, .025]} radius={.006} color="#aab5ba" metalness={.35}/>
              <Part size={[.05, .09, .05]} position={[0, -.07, 0]} radius={.006} color={edge}/>
              <Ring radius={.032} color={turquoise} position={[0, .13, .025]} scale={.65}/>
            </group>}
          </group>, rig.bones[`lowerarm01.${suffix}`])}
          {p.flags.metal && createPortal(<group position={[s * .025, -.29, .15]}><Plate size={[.23, .4, .06]}/></group>, rig.bones[`upperleg01.${suffix}`])}
          {p.flags.metal && createPortal(<group position={[s * .025, -.3, .125]}>
            <Plate size={[.18, .38, .06]}/>
            {p.flags.joints && <Part size={[.035, .33, .035]} position={[s * (.11 + jointSpread), .07, -.07]} color="#91a7b0" radius={.006}/>}
          </group>, rig.bones[`lowerleg01.${suffix}`])}
          {p.flags.metal && createPortal(<group position={[0, -.035, .115]}>
            <Part size={[.2, .14, .4]} color={metal} radius={.018} metalness={.18} roughness={.6}/>
            <Part size={[.2, .025, .4]} position={[0, -.065, 0]} radius={.004} color={edge}/>
            {p.flags.hover && <group position={[0, -.083 - (1 - p.progress.hover) * .15, 0]}>
              <Part size={[.18, .035, .34]} color={edge} radius={.006}/>
              <Part size={[.14, .012, .26]} position={[0, -.02, 0]} color={turquoise} radius={.003} glow={.25}/>
              {p.lift > .03 && <mesh position={[0, -.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <ringGeometry args={[.06, .14, 24]}/><meshBasicMaterial color="#85e1dd" transparent opacity={.3} side={2}/>
              </mesh>}
            </group>}
          </group>, rig.bones[`foot.${suffix}`])}
        </group>;
      })}
    </group>
    {!paperHeld && <FallingSketch frame={frame} episode={episode} release={release}/>}
  </>;
};
function FallingSketch({frame, episode, release}: {frame: number; episode: Episode; release: {position: Vector3; quaternion: Quaternion}}) {
  const pose = paperPose(frame, release, episode);
  return <group position={pose.position} quaternion={pose.quaternion}><Sketch/></group>;
}
