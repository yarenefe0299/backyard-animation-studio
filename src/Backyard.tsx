import {Ball, Part, Ring} from './Primitives';
import {GardenBed, WateringCan, Laundry} from './Props';
import {Terrain} from './Terrain';
import {Shed, Tree, Neighborhood} from './Environment';

export const Backyard = ({frame}: {frame: number}) => <group>
  <Terrain/>
  {/* Picket fence, posts, rails and a back gate share one fixed world. */}
  {[-1, 1].map(side => <group key={side}>
    {Array.from({length: 25}, (_, i) => <Part key={i} size={[.32, 1.7 + (i % 3) * .04, .12]}
      position={[side === -1 ? -6 : i * .48 - 5.8, .82, side === -1 ? i * .48 - 5.8 : -5.8]}
      rotation={[0, side === -1 ? Math.PI / 2 : 0, 0]} color={i % 2 ? '#afab97' : '#bcb6a0'} radius={.08}/>)}
  </group>)}
  {[.4, 1.15].map(y => <Part key={y} size={[12, .12, .16]} position={[0, y, -5.65]} color="#918976"/>)}
  {[.4, 1.15].map(y => <Part key={`side-${y}`} size={[.16, .12, 12]} position={[-5.85, y, 0]} color="#918976" radius={.008}/>)}
  {[-5.8, -2.9, 0, 2.9, 5.8].map(x => <Part key={`post-${x}`} size={[.13, 1.9, .13]} position={[x, .9, -5.8]} color="#9a927f" radius={.008}/>)}
  <Shed/>
  <Neighborhood frame={frame}/>
  {/* Rounded workbench, pegboard and original inventor's props. */}
  <group position={[-2.15, 0, -.25]}>
    <Part size={[2.1, .18, .95]} position={[0, 1.17, 0]} color="#a58b6d"/>
    {[-.85, .85].flatMap(x => [-.33, .33].map(z => <Part key={`${x}${z}`} size={[.13, 1.18, .13]}
      position={[x, .55, z]} color="#687d80"/>))}
    <Part size={[1.9, .9, .1]} position={[0, 1.8, -.4]} color="#958066"/>
    {Array.from({length: 24}, (_, i) => <Ball key={i} color="#815a42" scale={.022}
      position={[(i % 8) * .22 - .77, 1.58 + Math.floor(i / 8) * .2, -.33]}/>)}
    <Part size={[.5, .07, .15]} position={[.5, 1.34, -.1]} rotation={[0, -.4, 0]} color="#6e858e"/>
    <Part size={[.13, .22, .27]} position={[.3, 1.31, .1]} color="#9e6857"/>
    <Part size={[.4, .06, .32]} position={[-.3, 1.3, .1]} color="#f7e4ba"/>
    <Ring position={[-.7, 1.4, -.25]} rotation={[Math.PI / 2, 0, 0]} radius={.13} color="#47bbb9"/>
  </group>
  {/* Tree, planter, stepping stones and motion in foliage. */}
  <Tree frame={frame} position={[3.65, -.05, -3.4]}/>
  <GardenBed/>
  {Array.from({length: 7}, (_, i) => <Part key={i} size={[.7, .07, .47]} color={i % 2 ? '#cfbfa3' : '#e3cfad'}
    radius={.15} position={[-.6 + Math.sin(i) * .13, -.005, -4.7 + i * .65]} rotation={[0, i * .13, 0]}/>)}
  {Array.from({length: 22}, (_, i) => <group key={i} position={[Math.sin(i * 13) * 5.3, 0, Math.cos(i * 7) * 4.9]}>
    {[0, 1, 2].map(j => <Part key={j} size={[.035, .15 + j * .025, .045]} radius={.015}
      position={[(j - 1) * .05, .03, 0]} rotation={[0, 0, (j - 1) * .3]} color="#66955d"/>)}
  </group>)}
  <WateringCan/>
  <Laundry frame={frame}/>
</group>;
