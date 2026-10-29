import {useLayoutEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {PCFSoftShadowMap, ACESFilmicToneMapping, Vector3, PMREMGenerator} from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
import {Backyard} from './Backyard';
import {Inventor} from './Inventor';
import {mix, poseAt, smooth} from './motion';

// Procedural studio reflections: no HDRI download, consistent on every worker.
function StudioReflections() {
  const {gl, scene} = useThree();
  useLayoutEffect(() => {
    const generator = new PMREMGenerator(gl);
    const room = new RoomEnvironment();
    const map = generator.fromScene(room, .04);
    scene.environment = map.texture;
    scene.environmentIntensity = .32;
    return () => {scene.environment = null; map.dispose(); room.dispose(); generator.dispose();};
  }, [gl, scene]);
  return null;
}

function Camera({frame}: {frame: number}) {
  const {camera} = useThree();
  const {shot, lift} = poseAt(frame);
  const t = smooth(shot.local / (shot.frames - 1));
  useLayoutEffect(() => {
    if (shot.id === 'idea') {
      camera.position.set(mix(6.2, 4.6, t), mix(5.2, 4.0, t), mix(14.5, 12, t));
      camera.lookAt(new Vector3(-.15, 1.0, -.6));
    } else if (shot.id === 'collapse') {
      // Close enough to read hands, eyes and the cardboard separation.
      camera.position.set(mix(1.8, 1.15, t), mix(2.4, 2.05, t), mix(5.4, 5.7, t));
      camera.lookAt(new Vector3(.2, mix(1.65, 1.45, t), .7));
    } else if (shot.id === 'upgrade') {
      camera.position.set(mix(-1.8, -1.2, t), 2.35, mix(5.6, 5.35, t));
      camera.lookAt(new Vector3(.3, 1.6, .65));
    } else {
      camera.position.set(mix(2.25, 2.7, t), 1.95 + lift * .2, mix(7.7, 8.2, t));
      camera.lookAt(new Vector3(.3, 1.45 + lift * .4, .65));
    }
    camera.updateMatrixWorld();
  }, [camera, shot.id, t, lift]);
  return null;
}

export const BackyardFilm = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const {shot, hover} = poseAt(frame);
  const index = Math.min(shot.words.length - 1, Math.floor(shot.local / shot.frames * shot.words.length));
  const word = shot.words[index];
  const phase = (shot.local / shot.frames * shot.words.length) % 1;
  const captionScale = .94 + smooth(phase / .22) * .06;
  return <AbsoluteFill style={{background: '#a5c8d9'}}>
    <ThreeCanvas width={width} height={height} shadows={{type: PCFSoftShadowMap}}
      camera={{fov: 38, near: .1, far: 120}}
      gl={{antialias: true, alpha: false, toneMapping: ACESFilmicToneMapping, toneMappingExposure: 1}}>
      <color attach="background" args={['#a5c8d9']}/>
      <fog attach="fog" args={['#a5c8d9', 20, 65]}/>
      <StudioReflections/>
      <Camera frame={frame}/>
      <hemisphereLight args={['#d4e9f3', '#727a5d', .85]}/>
      <directionalLight position={[-4, 8, 5]} intensity={2.7} color="#ffe4c3" castShadow
        shadow-mapSize={[2048, 2048]} shadow-bias={-.00015} shadow-normalBias={.018}
        shadow-camera-left={-7} shadow-camera-right={7} shadow-camera-top={7}
        shadow-camera-bottom={-7} shadow-camera-near={.5} shadow-camera-far={25}
        shadow-radius={4}/>
      <directionalLight position={[4, 4, -3]} intensity={1.25} color="#b4e8fa"/>
      <directionalLight position={[1, 3, 8]} intensity={.4} color="#e0eaf0"/>
      <Backyard frame={frame}/>
      <Inventor frame={frame}/>
      {hover > 0 && <pointLight position={[.3, .3, .65]} intensity={hover * 1.1} color="#65fafa" distance={2}/>}
    </ThreeCanvas>
    <AbsoluteFill style={{pointerEvents: 'none',
      background: 'radial-gradient(ellipse at 50% 43%, transparent 40%, rgba(15,29,40,.17) 100%)'}}/>
    <AbsoluteFill style={{pointerEvents: 'none', fontFamily: 'Arial, sans-serif', color: 'white'}}>
      <div style={{position: 'absolute', top: '62%', width: '100%', textAlign: 'center',
        fontWeight: 900, fontSize: 76, lineHeight: 1, letterSpacing: -1.5,
        WebkitTextStroke: '7px #10171c', paintOrder: 'stroke fill',
        textShadow: '0 5px 8px #10171c99', transform: `scale(${captionScale})`}}>{word}</div>
      <div style={{position: 'absolute', bottom: 145, width: '100%', textAlign: 'center',
        fontSize: 18, letterSpacing: 2, opacity: .85, textShadow: '0 2px 5px #152832'}}>FICTIONAL TECHNOLOGY</div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
