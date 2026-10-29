import {Euler, Matrix4, Quaternion, Vector3} from 'three';
import {smooth} from './motion.ts';
import {episode, paperReleaseFrame} from './story.ts';
import type {Episode} from './story.ts';

export function paperPose(frame: number, release: {position: Vector3; quaternion: Quaternion}, ep: Episode = episode) {
  const t = Math.max(0, (frame - paperReleaseFrame(ep)) / 30);
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
