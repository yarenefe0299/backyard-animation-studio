import {Euler, Matrix4, Quaternion, Vector3} from 'three';
import {clamp, mix, smooth} from './motion.ts';
import {propReleaseFrame} from './story.ts';

export function cardboardPose(frame: number) {
  const t = Math.max(0, (frame - propReleaseFrame) / 30);
  const progress = smooth(t / .72);
  const angle = mix(0, -Math.PI / 2, progress);
  const rotation: [number, number, number] = [angle, -.08, progress * .15];
  const m = new Matrix4().makeRotationFromEuler(new Euler(...rotation)).elements;
  const contactHeight = -.04 + .305 * Math.abs(m[1]) + .29 * Math.abs(m[5]) + .0125 * Math.abs(m[9]);
  return {
    position: [.3, Math.max(contactHeight, 2.03 - 3.8 * t * t), .98 + clamp(t / .8) * .16] as [number, number, number],
    rotation,
  };
}

export function paperPose(frame: number, release: {position: Vector3; quaternion: Quaternion}) {
  const t = Math.max(0, (frame - propReleaseFrame) / 30);
  const progress = smooth(t / .72);
  const target = new Quaternion().setFromEuler(new Euler(-Math.PI / 2, 0, .2));
  const quaternion = release.quaternion.clone().slerp(target, progress);
  const m = new Matrix4().makeRotationFromQuaternion(quaternion).elements;
  const contactHeight = -.041 + .15 * Math.abs(m[1]) + .19 * Math.abs(m[5]) + .003 * Math.abs(m[9]);
  return {
    position: [release.position.x + Math.min(t, .8) * .15,
      Math.max(contactHeight, release.position.y - 3.8 * t * t),
      release.position.z + Math.min(t, .8) * .18] as [number, number, number],
    quaternion,
  };
}
