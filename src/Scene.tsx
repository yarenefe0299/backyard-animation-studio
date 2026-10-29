import {useLayoutEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {PCFSoftShadowMap, ACESFilmicToneMapping, Vector3} from 'three';
import {Backyard} from './Backyard';
import {FallenCardboard, Inventor} from './Inventor';
import {Ball} from './Primitives';
import {mix, poseAt, smooth} from './motion';

function Camera({frame}: {frame: number}) {
  const {camera} = useThree();
  const {shot, lift} = poseAt(frame);
  const t = smooth(shot.local / (shot.frames - 1));
  useLayoutEffect(() => {
    if (shot.id === 'idea') {
      camera.position.set(mix(7.2, 5.7, t), mix(5.3, 4.3, t), mix(15, 12.5, t));
      camera.lookAt(new Vector3(-.3, 1.1, -.4));
    } else if (shot.id === 'collapse') {
      camera.position.set(mix(3.4, 2.5, t), mix(2.8, 2.4, t), mix(8, 7.6, t));
      camera.lookAt(new Vector3(.2, 1.35, .65));
    } else if (shot.id === 'upgrade') {
      camera.position.set(mix(-3.2, -2.3, t), 2.6, mix(7.8, 7.4, t));
      camera.lookAt(new Vector3(.25, 1.5, .65));
    } else {
      camera.position.set(mix(2.9, 4.2, t), 2.9 + lift * .2, mix(9, 10, t));
      camera.lookAt(new Vector3(.3, 1.55 + lift * .3, .65));
    }
    camera.updateMatrixWorld();
  }, [camera, shot.id, t, lift]);
  return null;
}

export const BackyardFilm = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const {shot, hover} = poseAt(frame);
  return <AbsoluteFill style={{background: '#bee4e6'}}>
    <ThreeCanvas width={width} height={height} shadows={{type: PCFSoftShadowMap}}
      camera={{fov: 39, near: .1, far: 100}}
      gl={{antialias: true, alpha: false, toneMapping: ACESFilmicToneMapping, toneMappingExposure: 1.15}}>
      <color attach="background" args={['#bee4e6']}/>
      <fog attach="fog" args={['#bee4e6', 24, 60]}/>
      <Camera frame={frame}/>
      <hemisphereLight args={['#e6f8ff', '#8d966b', 2]}/>
      <ambientLight intensity={.3}/>
      <directionalLight position={[-5, 9, 6]} intensity={3.2} color="#fff0d2" castShadow
        shadow-mapSize={[1024, 1024]} shadow-bias={-.0004} shadow-normalBias={.03}
        shadow-camera-left={-9} shadow-camera-right={9} shadow-camera-top={9}
        shadow-camera-bottom={-9} shadow-camera-near={.5} shadow-camera-far={30}
        shadow-radius={4}/>
      <directionalLight position={[5, 5, -4]} intensity={1.5} color="#a9e7ef"/>
      <Backyard frame={frame}/>
      <Inventor frame={frame}/>
      <FallenCardboard frame={frame}/>
      {hover > 0 && <pointLight position={[.3, .3, .65]} intensity={hover * 2} color="#65fafa" distance={3}/>}
      {/* Clouds are geometry; their slow drift is deterministic too. */}
      {[-1, 1].map(s => <group key={s} position={[s * 6 + Math.sin(frame * .003) * .25, 7, -11]}>
        {[-1, 0, 1].map(i => <Ball key={i} color="#edf4e9" position={[i * .75, i === 0 ? .2 : 0, 0]}
          scale={[1.1, .45, .5]}/>)}
      </group>)}
    </ThreeCanvas>
    <AbsoluteFill style={{padding: '108px 70px 145px', justifyContent: 'space-between',
      pointerEvents: 'none', fontFamily: 'Arial, sans-serif', color: '#263e48'}}>
      <div>
        <div style={{fontSize: 24, letterSpacing: 5, fontWeight: 800}}>BACKYARD / LAB NOTES</div>
        <div style={{fontSize: 58, lineHeight: 1.05, fontWeight: 900, marginTop: 20}}>A VERY SMALL<br/>FLIGHT PLAN.</div>
        <div style={{marginTop: 22, fontSize: 24, fontWeight: 700}}>{shot.tag}</div>
      </div>
      <div>
        <div style={{background: '#fff7e9ed', padding: '26px 32px', borderRadius: 24,
          fontWeight: 800, fontSize: 40, lineHeight: 1.15, boxShadow: '0 6px 0 #577d7925'}}>{shot.caption}</div>
        <div style={{fontSize: 21, letterSpacing: 1.5, marginTop: 22, textAlign: 'center'}}>FICTIONAL TECHNOLOGY • PLEASE DO NOT TRY TO FLY</div>
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
