import {useLayoutEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {PCFSoftShadowMap, ACESFilmicToneMapping, Vector3, PMREMGenerator} from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {Backyard} from './Backyard';
import {Inventor} from './Inventor';
import {mix, poseAt, smooth} from './motion';
import {captionAt, episodeById} from './story';
import type {Episode} from './story';

function StudioReflections() {
  const {gl, scene} = useThree();
  useLayoutEffect(() => {
    const generator = new PMREMGenerator(gl), room = new RoomEnvironment();
    const map = generator.fromScene(room, .04);
    scene.environment = map.texture; scene.environmentIntensity = .24;
    return () => {scene.environment = null; map.dispose(); room.dispose(); generator.dispose();};
  }, [gl, scene]);
  return null;
}
function Camera({frame, episode}: {frame: number; episode: Episode}) {
  const {camera} = useThree();
  const p = poseAt(frame, episode), t = smooth(p.shot.local / (p.shot.frames - 1));
  useLayoutEffect(() => {
    switch (p.shot.camera) {
      case 'wide':
        camera.position.set(mix(6.2, 3.5, t), mix(4, 2.9, t), mix(13, 9, t));
        camera.lookAt(new Vector3(-.15, 1.25, -.3)); break;
      case 'medium':
        camera.position.set(mix(2.2, 1.4, t), 2.35, mix(7.1, 6.6, t));
        camera.lookAt(new Vector3(.3 + p.pathX, 1.5 + p.lift * .3, .65)); break;
      case 'detail':
        camera.position.set(mix(-1.8, -.9, t), 2.45, mix(5.8, 5.6, t));
        camera.lookAt(new Vector3(.3, p.heat > .1 ? 1.95 : 1.65, .65)); break;
      case 'orbit':
        camera.position.set(mix(2.8, -.8, t), 2.65, mix(6.5, 4.9, t));
        camera.lookAt(new Vector3(.2, mix(1.65, 2.05, t), .65)); break;
      case 'low':
        camera.position.set(mix(2.3, 3, t), 1.9 + p.lift * .2, 8);
        camera.lookAt(new Vector3(.3 + p.pathX, 1.45 + p.lift * .4, .65)); break;
      case 'flight':
        camera.position.set(mix(4.4, 6.2, t), mix(4.4, 6.5, t), mix(11.5, 13, t));
        camera.lookAt(new Vector3(.3 + p.pathX * .4, 1.65 + p.lift * .33, .1)); break;
    }
    camera.updateMatrixWorld();
  }, [camera, p.shot.camera, t, p.heat, p.lift, p.pathX]);
  return null;
}
export const BackyardFilm = ({episodeId}: {episodeId: string}) => {
  const episode = episodeById(episodeId);
  const frame = useCurrentFrame(), {width, height} = useVideoConfig();
  const p = poseAt(frame, episode), caption = captionAt(frame, episode);
  const captionScale = .96 + smooth(caption.phase / .22) * .04;
  return <AbsoluteFill style={{background: '#adb9bd'}}>
    <ThreeCanvas width={width} height={height} shadows={{type: PCFSoftShadowMap}}
      camera={{fov: 38, near: .1, far: 160}}
      gl={{antialias: true, alpha: false, toneMapping: ACESFilmicToneMapping, toneMappingExposure: 1}}>
      <color attach="background" args={['#adb9bd']}/><fog attach="fog" args={['#adb9bd', 24, 80]}/>
      <StudioReflections/><Camera frame={frame} episode={episode}/>
      <hemisphereLight args={['#d4e9f3', '#727a5d', .85]}/>
      <directionalLight position={[-4, 8, 5]} intensity={2.7} color="#ffe4c3" castShadow
        shadow-mapSize={[2048, 2048]} shadow-bias={-.00015} shadow-normalBias={.018}
        shadow-camera-left={-8} shadow-camera-right={8} shadow-camera-top={8}
        shadow-camera-bottom={-8} shadow-camera-near={.5} shadow-camera-far={30} shadow-radius={4}/>
      <directionalLight position={[4, 4, -3]} intensity={1.25} color="#b4e8fa"/>
      <directionalLight position={[1, 3, 8]} intensity={.4} color="#e0eaf0"/>
      <Backyard frame={frame}/><Inventor frame={frame} episode={episode}/>
      {p.lift > 0 && <pointLight position={[.3 + p.pathX, p.lift + .05, .65 + p.pathZ]} intensity={.6} color="#65dddd" distance={2}/>}
    </ThreeCanvas>
    <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(ellipse at 50% 43%, transparent 45%, rgba(15,29,40,.12) 100%)'}}/>
    <AbsoluteFill style={{pointerEvents: 'none', fontFamily: 'Arial, sans-serif', color: 'white'}}>
      <div style={{position: 'absolute', top: 110, left: 62, right: 62,
        textShadow: '0 2px 5px #152832', WebkitTextStroke: '1px #24333a', paintOrder: 'stroke fill'}}>
        <div style={{fontSize: 24, fontWeight: 800, letterSpacing: 1.5}}>{p.shot.title}</div>
        <div style={{fontSize: 29, fontWeight: 700, marginTop: 10, opacity: smooth((p.shot.local / p.shot.frames - .48) / .1)}}>{p.shot.result}</div>
      </div>
      <div style={{position: 'absolute', top: '64%', width: '100%', textAlign: 'center',
        fontWeight: 900, fontSize: 76, lineHeight: 1, letterSpacing: -1.5,
        WebkitTextStroke: '7px #10171c', paintOrder: 'stroke fill', textShadow: '0 5px 8px #10171c99',
        transform: `scale(${captionScale})`}}>{caption.word}</div>
      <div style={{position: 'absolute', bottom: 145, width: '100%', textAlign: 'center',
        fontSize: 18, letterSpacing: 2, opacity: .85, textShadow: '0 2px 5px #152832'}}>FICTIONAL TECHNOLOGY</div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
