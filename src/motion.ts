import {episode, featureStart, shotAt} from './story.ts';
import type {Episode, Feature} from './story.ts';
export const clamp = (v: number) => Math.max(0, Math.min(1, v));
export const smooth = (v: number) => {const t = clamp(v); return t * t * (3 - 2 * t);};
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;

export function poseAt(frame: number, ep: Episode = episode) {
  const shot = shotAt(frame, ep), f = shot.local, phase = f / (shot.frames - 1);
  const progress = Object.fromEntries((['cardboard', 'metal', 'joints', 'power', 'cooling', 'hover', 'stabilizers'] as Feature[])
    .map(feature => [feature, feature === 'cardboard' ? 1 : smooth((frame - featureStart(feature, ep) - 8) / 32)])) as Record<Feature, number>;
  const flags = Object.fromEntries(Object.entries(progress).map(([k, v]) => [k, v > 0])) as Record<Feature, boolean>;
  let lift = 0, wobble = 0, stride = 0, strain = 0, pathX = 0, pathZ = 0;
  if (shot.action === 'heavy-step') {
    const effort = smooth((phase - .3) / .2) * (1 - smooth((phase - .8) / .18));
    stride = Math.sin(clamp((phase - .3) / .55) * Math.PI) * .12;
    strain = effort;
  }
  if (shot.action === 'assisted-step') stride = Math.sin(clamp((phase - .25) / .7) * Math.PI * 4) * .13 * progress.joints;
  if (shot.action === 'unstable-hover') {
    const air = Math.sin(clamp((phase - .25) / .68) * Math.PI);
    lift = air * .65;
    wobble = Math.sin(f * .22) * air;
    pathX = wobble * .26;
  }
  if (shot.action === 'balance') {
    lift = smooth((phase - .25) / .35) * .35;
    wobble = Math.sin(f * .22) * (1 - smooth(phase / .55)) * .35;
  }
  if (shot.action === 'flight') {
    const takeoff = smooth(phase / .72);
    lift = .35 + takeoff * 2.65;
    pathX = Math.sin(phase * Math.PI) * .65;
    pathZ = -takeoff * 1.1;
  }
  const heat = shot.action === 'power-up' ? smooth((phase - .28) / .45)
    : shot.action === 'cool-down' ? 1 - smooth((phase - .12) / .4) : 0;
  const blinkPhase = frame % 149;
  const blink = blinkPhase > 139 ? Math.sin(clamp((blinkPhase - 140) / 8) * Math.PI) : 0;
  return {shot, progress, flags, lift, wobble, stride, strain, pathX, pathZ, blink, heat,
    sag: shot.action === 'sketch' ? smooth((phase - .48) / .18) : 1,
    headTilt: Math.sin(frame * .025) * .018 - wobble * .025,
    yaw: -.08 + wobble * .1 + (shot.action === 'power-up' ? Math.sin(phase * Math.PI) * .5 : 0) + (shot.action === 'flight' ? phase * -.22 : 0),
  };
}
