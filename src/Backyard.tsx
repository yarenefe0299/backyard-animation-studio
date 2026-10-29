import {Ball, Part, Ring} from './Primitives';
import {Terrain, Leaves} from './Terrain';

export const Backyard = ({frame}: {frame: number}) => <group>
  <Terrain/>
  {/* Picket fence, posts, rails and a back gate share one fixed world. */}
  {[-1, 1].map(side => <group key={side}>
    {Array.from({length: 25}, (_, i) => <Part key={i} size={[.32, 1.7 + (i % 3) * .04, .12]}
      position={[side === -1 ? -6 : i * .48 - 5.8, .82, side === -1 ? i * .48 - 5.8 : -5.8]}
      rotation={[0, side === -1 ? Math.PI / 2 : 0, 0]} color={i % 2 ? '#afab97' : '#bcb6a0'} radius={.08}/>)}
  </group>)}
  {[.4, 1.15].map(y => <Part key={y} size={[12, .12, .16]} position={[0, y, -5.65]} color="#918976"/>)}
  {/* Tool shed with roof, door, trim, window, hinges and flower box. */}
  <group position={[-3.4, 0, -3.65]}>
    <Part size={[3.1, 2.6, 2.5]} position={[0, 1.3, 0]} color="#b2aa95" radius={.1}/>
    {[-1, 1].map(s => <Part key={s} size={[1.94, .18, 2.9]} position={[s * .78, 2.88, 0]}
      rotation={[0, 0, -s * .4]} color="#566269"/>)}
    <Part size={[1.05, 2.08, .13]} position={[-.55, 1.08, 1.29]} color="#737c77"/>
    {[-1, 1].map(s => <Part key={s} size={[.1, 2.22, .17]} position={[-.55 + s * .58, 1.1, 1.36]} color="#c9c5b4"/>)}
    <Part size={[1.25, .13, .17]} position={[-.55, 2.15, 1.36]} color="#c9c5b4"/>
    <Ball color="#edc16c" position={[-.22, 1, 1.4]} scale={.07}/>
    <Part size={[.85, .85, .1]} position={[.85, 1.7, 1.3]} color="#425f69"/>
    <Part size={[.67, .67, .11]} position={[.85, 1.7, 1.37]} color="#bde6de"/>
    {[0, 1].map(i => <Part key={i} size={i ? [.78, .06, .08] : [.06, .78, .08]} position={[.85, 1.7, 1.45]} color="#c9c5b4"/>)}
    <Part size={[1, .28, .35]} position={[.85, 1.1, 1.45]} color="#ba7261"/>
    {[-.25, 0, .25].map((x, i) => <Ball key={x} color={['#ffe189', '#ed9a9e', '#f7c25e'][i]}
      position={[.85 + x, 1.35, 1.48]} scale={.15}/>)}
  </group>
  {/* Rounded workbench, pegboard and original inventor's props. */}
  <group position={[-2.15, 0, -.25]}>
    <Part size={[2.1, .18, .95]} position={[0, 1.17, 0]} color="#cd925e"/>
    {[-.85, .85].flatMap(x => [-.33, .33].map(z => <Part key={`${x}${z}`} size={[.13, 1.1, .13]}
      position={[x, .55, z]} color="#687d80"/>))}
    <Part size={[1.9, .9, .1]} position={[0, 1.8, -.4]} color="#b78152"/>
    {Array.from({length: 24}, (_, i) => <Ball key={i} color="#815a42" scale={.022}
      position={[(i % 8) * .22 - .77, 1.58 + Math.floor(i / 8) * .2, -.33]}/>)}
    <Part size={[.5, .07, .15]} position={[.5, 1.34, -.1]} rotation={[0, -.4, 0]} color="#6e858e"/>
    <Part size={[.13, .22, .27]} position={[.3, 1.31, .1]} color="#d56352"/>
    <Part size={[.4, .06, .32]} position={[-.3, 1.3, .1]} color="#f7e4ba"/>
    <Ring position={[-.7, 1.4, -.25]} rotation={[Math.PI / 2, 0, 0]} radius={.13} color="#47bbb9"/>
  </group>
  {/* Tree, planter, stepping stones and motion in foliage. */}
  <group position={[3.65, 0, -3.4]}>
    <Part size={[.45, 2.5, .48]} position={[0, 1.2, 0]} rotation={[0, 0, -.1]} color="#98704e"/>
    <group position={[0, 2, 0]}>
      {[-1, 1].map(side => <Part key={side} size={[.16, 1.1, .16]}
        position={[side * .35, .3, 0]} rotation={[0, 0, -side * .65]} color="#73614c"/>)}
      <Leaves frame={frame}/>
    </group>
  </group>
  <group position={[2.8, 0, -.8]}>
    <Part size={[1.6, .35, .7]} position={[0, .15, 0]} color="#b8775e"/>
    {[-.5, 0, .5].map((x, i) => <group key={x} position={[x, .3, 0]}>
      <Part size={[.04, .65, .04]} position={[0, .3, 0]} color="#487c52"/>
      {Array.from({length: 5}, (_, j) => <Ball key={j} color={i % 2 ? '#ffd17c' : '#e99c9e'}
        scale={[.13, .13, .07]} position={[Math.cos(j * 1.257) * .13, .65 + Math.sin(j * 1.257) * .13, .05]}/>)}
      <Ball color="#926644" scale={.08} position={[0, .65, .13]}/>
    </group>)}
  </group>
  {Array.from({length: 7}, (_, i) => <Part key={i} size={[.7, .07, .47]} color={i % 2 ? '#cfbfa3' : '#e3cfad'}
    radius={.15} position={[-.6 + Math.sin(i) * .13, .01, -4.7 + i * .65]} rotation={[0, i * .13, 0]}/>)}
  {Array.from({length: 22}, (_, i) => <group key={i} position={[Math.sin(i * 13) * 5.3, 0, Math.cos(i * 7) * 4.9]}>
    {[0, 1, 2].map(j => <Part key={j} size={[.035, .15 + j * .025, .045]} radius={.015}
      position={[(j - 1) * .05, .06, 0]} rotation={[0, 0, (j - 1) * .3]} color="#66955d"/>)}
  </group>)}
  {/* A little watering can and a laundry line add recognizable backyard scale. */}
  <group position={[2.3, .25, -1.5]}>
    <Part size={[.4, .45, .35]} color="#e7bb60"/>
    <Part size={[.5, .1, .1]} position={[-.35, .05, 0]} rotation={[0, 0, -.45]} color="#e7bb60"/>
    <Ring position={[.25, .1, 0]} radius={.19} color="#e7bb60"/>
  </group>
  {[1.2, 4.8].map(x => <Part key={x} size={[.08, 2.65, .08]} position={[x, 1.3, -4.65]} color="#82949a"/>)}
  <Part size={[3.6, .025, .025]} position={[3, 2.5, -4.65]} color="#f4e7d1"/>
  {[1.8, 2.8, 3.8].map((x, i) => <Part key={x} size={[.65, .9, .03]} position={[x, 2.02, -4.65]}
    rotation={[Math.sin(frame * .035 + i) * .07, 0, .04]} color={['#f5dcac', '#74bbbd', '#dc978b'][i]}/>)}
</group>;
