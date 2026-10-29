import {shotAt} from './story.ts';

export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const smooth = (v: number) => {const t = clamp(v); return t * t * (3 - 2 * t);};
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

export function poseAt(frame: number) {
  const shot = shotAt(frame);
  const f = shot.local;
  const fail = shot.id === 'collapse' ? smooth((f - 18) / 36) : shot.id === 'idea' ? 0 : 1;
  const metal = shot.id === 'upgrade' || shot.id === 'hover';
  const assemble = shot.id === 'upgrade' ? smooth((f - 5) / 32) : 1;
  const hover = shot.id === 'hover' ? Math.sin(clamp((f - 10) / 60) * Math.PI) : 0;
  const wobble = shot.id === 'hover' ? Math.sin(f * .23) * hover : 0;
  return {
    shot, fail, metal, assemble, hover, wobble,
    lift: hover * .85,
    lean: metal ? wobble * .15 : -fail * .16,
    knee: metal ? .12 + hover * .3 : .07 + fail * .26,
    arm: metal ? -.12 - hover * .65 : -.2 - fail * .65,
    blink: frame % 113 >= 105 && frame % 113 <= 109,
    headTilt: metal ? wobble * -.2 : Math.sin(frame * .035) * .08 + fail * .2,
    panelSpread: metal ? (1 - assemble) * 2.4 : 0,
    // Ballistic cardboard debris: ground contact is clamped, never passes below grass.
    debrisY: Math.max(.07, 1.35 - 2.3 * fail * fail),
    surprise: shot.id === 'collapse' && f > 16 || hover > .25,
  };
}
