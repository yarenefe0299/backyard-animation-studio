import {Ball, Part, Ring} from './Primitives';
import {poseAt} from './motion';

const skin = '#cd926e', dark = '#374d58', teal = '#46bfc1', metal = '#9caeb5';
export const Inventor = ({frame}: {frame: number}) => {
  const p = poseAt(frame);
  const plateColor = p.metal ? metal : '#c3965f';
  const plateMaterial = {metalness: p.metal ? .48 : 0, roughness: p.metal ? .36 : .9};
  return <group position={[.3 + p.wobble * .15, p.lift, .65]} rotation={[0, -.12, p.lean]}>
    {/* Hip, shoulders, elbows, knees: all parts stay parented to their joint. */}
    <Part size={[.72, .38, .48]} position={[0, 1.05, 0]} color={dark}/>
    {[-1, 1].map(side => <group key={side} position={[side * .24, 1, 0]} rotation={[p.knee, 0, side * .04]}>
      <Part size={[.31, .54, .34]} position={[0, -.25, 0]} color={dark}/>
      <Part size={[.36, .43, .18]} position={[side * p.panelSpread * .2, -.23, .2]} color={plateColor} {...plateMaterial}/>
      <group position={[0, -.5, 0]} rotation={[-p.knee * 1.8, 0, 0]}>
        <Ball color={p.metal ? teal : dark} scale={.17}/>
        <Part size={[.3, .39, .34]} position={[0, -.22, 0]} color={dark}/>
        <Part size={[.35, .34, .18]} position={[0, -.23, .19]} color={plateColor} {...plateMaterial}/>
        <Part size={[.4, .24, .65]} position={[0, -.42, .12]} color={p.metal ? metal : '#625c50'} {...plateMaterial}/>
        {p.metal && <>
          <Part size={[.31, .045, .45]} position={[0, -.54, .11]} color={teal} glow={.8}/>
          <mesh position={[0, -.65, .13]} scale={[.2 * p.hover, .18 + p.hover * .45, .2 * p.hover]}>
            <coneGeometry args={[1, 1, 20]}/><meshBasicMaterial color="#a7ffff" transparent opacity={p.hover * .55}/>
          </mesh>
        </>}
      </group>
    </group>)}
    <group position={[0, 1.38, 0]}>
      <Part size={[.85, .8, .49]} color="#d8a45e" radius={.14}/>
      <Part size={[.9, .16, .54]} position={[0, -.32, 0]} color={dark}/>
      {/* The cardboard bib physically drops and lands; the metal plates close in. */}
      {(p.metal || p.fail < .95) && <group position={[0, p.metal ? 0 : -p.fail * .45, .31 + p.panelSpread]}
        rotation={[p.metal ? 0 : p.fail * .9, 0, p.metal ? 0 : p.fail * .25]}>
        <Part size={[.91, .67, .18]} color={plateColor} {...plateMaterial} radius={p.metal ? .12 : .025}/>
        <Part size={[.16, .62, .025]} position={[0, 0, .11]} color={p.metal ? teal : '#e9d0a2'} glow={p.metal ? .25 : 0}/>
        {p.metal && [-1, 1].map(s => <Part key={s} size={[.2, .08, .035]} position={[s * .24, .17, .12]}
          rotation={[0, 0, s * .15]} color={teal} glow={.3}/>)}
        {!p.metal && <Part size={[.83, .12, .025]} color="#e9d0a2" position={[0, .02, .12]}/>}
      </group>}
      {[-1, 1].map(side => <group key={side} position={[side * .55, .19, 0]} rotation={[.08, 0, side * -p.arm]}>
        <Ball color={dark} scale={.21}/>
        <Part size={[.4, .29, .5]} position={[side * (.03 + p.panelSpread * .4), .06, 0]} color={plateColor} {...plateMaterial}/>
        <Part size={[.24, .42, .28]} position={[0, -.26, 0]} color={dark}/>
        <group position={[0, -.45, 0]} rotation={[-.35 - (p.metal ? p.hover * .35 : .2), 0, 0]}>
          <Ball color={p.metal ? teal : dark} scale={.14}/>
          <Part size={[.29, .36, .31]} position={[0, -.19, 0]} color={plateColor} {...plateMaterial}/>
          <Ball color={skin} scale={[.14, .18, .13]} position={[0, -.43, 0]}/>
          {side === -1 && !p.metal && p.fail < .05 && <group position={[0, -.43, .2]} rotation={[-.2, 0, -.18]}>
            <Part size={[.56, .68, .015]} color="#fff0cc"/>
            {/* Crude original armor doodle: no outside image or font. */}
            <Ring radius={.07} color="#638d96" position={[0, .19, .018]}/>
            <Part size={[.18, .22, .012]} color="#638d96" position={[0, -.01, .022]} radius={.01}/>
            {[-1, 1].map(s => <group key={s}>
              <Part size={[.025, .17, .015]} color="#638d96" position={[s * .13, -.02, .025]} rotation={[0, 0, s * .5]}/>
              <Part size={[.025, .16, .015]} color="#638d96" position={[s * .06, -.19, .025]} rotation={[0, 0, s * .2]}/>
            </group>)}
          </group>}
        </group>
      </group>)}
      <group position={[0, .68, 0]} rotation={[0, 0, p.headTilt]}>
        <Part size={[.26, .3, .27]} position={[0, -.2, 0]} color={skin}/>
        <Ball color={skin} scale={[.43, .48, .38]} position={[0, .14, 0]}/>
        {[-1, 1].map(s => <Ball key={s} color={skin} scale={[.1, .15, .1]} position={[s * .43, .12, 0]}/>)}
        <Ball color="#77513e" scale={[.43, .19, .35]} position={[0, .5, -.05]}/>
        {[-.22, -.05, .12].map((x, i) => <Ball key={x} color="#77513e" scale={[.17, .2 + i * .025, .17]}
          position={[x, .57 + i * .025, -.04]} rotation={[0, 0, -.4]}/>)}
        <Ball color="#dca27c" scale={[.12, .14, .15]} position={[0, .08, .36]}/>
        {[-1, 1].map(s => <group key={s} position={[s * .19, .22, .335]}>
          <Ball color="#fffae9" scale={[.13, p.blink ? .015 : .145, .055]}/>
          <Ball color="#344852" scale={[.055, p.blink ? .008 : .073, .025]} position={[-s * .012, 0, .05]}/>
          <Ball color="#ffffff" scale={.018} position={[-.018, .03, .073]}/>
          <Part size={[.2, .035, .05]} color="#77513e" position={[0, p.surprise ? .2 : .15, 0]}
            rotation={[0, 0, s * (p.surprise ? -.24 : .12)]}/>
          <Ring radius={.14} color={teal} position={[0, .42, -.08]} rotation={[.45, 0, 0]}/>
        </group>)}
        <Part size={[.13, p.surprise ? .14 : .045, .03]} color="#794d40" position={[0, -.12, .34]} radius={.018}/>
      </group>
    </group>
    {p.metal && <group position={[0, 1.47, -.37]}>
      <Part size={[.66, .65, .27]} color={dark}/>
      {[-1, 1].map(s => <Part key={s} size={[.18, .48, .3]} color={teal} position={[s * .22, 0, -.08]} metalness={.4}/>)}
      {[0, 1, 2].map(i => <Part key={i} size={[.2, .035, .05]} color={metal} position={[0, i * .1 - .1, -.16]}/>)}
    </group>}
  </group>;
};

export const FallenCardboard = ({frame}: {frame: number}) => {
  const p = poseAt(frame);
  if (p.fail < .05) return null;
  return <group>
    {[-1, 1].map((s, i) => <Part key={s} size={[.8, .045, .6]} color="#c3965f" radius={.02}
      position={[.3 + s * p.fail * .8, p.debrisY, .9 + p.fail * (i ? .7 : .3)]}
      rotation={[0, p.fail * s * .7, (1 - p.fail) * s * .8]}/>)}
    <Part size={[.53, .02, .65]} color="#fff0cc" radius={.01}
      position={[-.6, Math.max(.045, .8 - p.fail * 1.2), 1.5]} rotation={[0, -.5, 0]}/>
  </group>;
};
