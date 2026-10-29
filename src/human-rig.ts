import {Bone, BufferGeometry, Float32BufferAttribute, MeshStandardMaterial,
  Quaternion, Skeleton, SkinnedMesh, Uint16BufferAttribute, Vector3} from 'three';
import data from './assets/inventor.json' with {type: 'json'};
import {poseAt} from './motion.ts';
import {episode, paperReleaseFrame} from './story.ts';
import type {Episode} from './story.ts';

export function createHumanRig(ep: Episode = episode) {
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new Float32BufferAttribute(data.position, 3));
  geometry.setAttribute('color', new Float32BufferAttribute(data.color, 3));
  geometry.setAttribute('skinIndex', new Uint16BufferAttribute(data.skinIndex, 4));
  geometry.setAttribute('skinWeight', new Float32BufferAttribute(data.skinWeight, 4));
  geometry.setIndex(data.index);
  geometry.computeVertexNormals();
  const material = new MeshStandardMaterial({color: '#ffffff', vertexColors: true, roughness: .8});
  const mesh = new SkinnedMesh(geometry, material);
  mesh.castShadow = mesh.receiveShadow = true;
  mesh.frustumCulled = false;
  const bones: Record<string, Bone> = {};
  for (const def of data.bones) {bones[def.name] = new Bone(); bones[def.name].name = def.name;}
  for (const def of data.bones) {
    const bone = bones[def.name];
    const parentDef = data.bones.find(d => d.name === def.parent);
    bone.position.fromArray(def.head);
    if (parentDef) {
      bone.position.sub(new Vector3().fromArray(parentDef.head));
      bones[parentDef.name].add(bone);
    } else mesh.add(bone);
  }
  mesh.updateMatrixWorld(true);
  const skeleton = new Skeleton(data.bones.map(b => bones[b.name]));
  mesh.bind(skeleton);
  const rest = Object.fromEntries(Object.entries(bones).map(([key, bone]) => [key, bone.position.clone()]));
  const soleIndices = data.position.flatMap((v, i) => i % 3 === 1 && v < .08 ? [(i - 1) / 3] : []);
  const v = new Vector3();
  const identity = new Quaternion();

  function setFrame(frame: number) {
    const p = poseAt(frame, ep);
    mesh.position.set(0, 0, 0);
    for (const [name, bone] of Object.entries(bones)) {
      bone.position.copy(rest[name]); bone.quaternion.copy(identity);
    }
    const sway = Math.sin(frame * .055) * .008;
    for (const [suffix, side] of [['L', 1], ['R', -1]] as const) {
      bones[`upperarm01.${suffix}`].rotation.z = side * (-.65 + Math.min(1, p.lift) * .22 + p.strain * .07) + p.wobble * .12;
      bones[`upperarm01.${suffix}`].rotation.x = sway * side - p.stride * side * .3;
      bones[`lowerarm01.${suffix}`].rotation.x = suffix === 'R' && frame < paperReleaseFrame(ep) ? -.8 : -.18 - Math.min(p.lift, .6) * .15;
      bones[`upperleg01.${suffix}`].rotation.x = p.stride * side - Math.min(p.lift, .6) * .12;
      bones[`lowerleg01.${suffix}`].rotation.x = Math.max(0, -p.stride * side) * 1.6 + Math.min(p.lift, .6) * .28;
      bones[`foot.${suffix}`].rotation.x = -Math.min(p.lift, .6) * .1;
      for (let finger = 2; finger <= 5; finger++) for (let joint = 1; joint <= 3; joint++) {
        bones[`finger${finger}-${joint}.${suffix}`].rotation.x = suffix === 'R' && frame < paperReleaseFrame(ep) ? -.12 : -.025;
      }
      // Facial skin stays at its neutral bind pose. Eyelids are rendered in the
      // eye socket; moving the facial bones had distorted the brows and cheeks.
    }
    bones.spine01.rotation.z = -p.wobble * .09;
    bones.spine02.rotation.x = Math.sin(frame * (.06 + p.heat * .06)) * (.003 + p.heat * .004) + p.strain * .04 + p.heat * .025;
    bones.head.rotation.y = Math.sin(frame * .02) * .025;
    bones.head.rotation.z = p.headTilt;
    bones.jaw.rotation.x = p.strain * .004;
    if (p.heat > .01) {
      mesh.updateMatrixWorld(true);
      const target = bones['wrist.L'].getWorldPosition(new Vector3());
      const raised = mesh.localToWorld(new Vector3(.22, 2.54, .29));
      target.lerp(raised, Math.min(1, p.heat * 1.5));
      for (let iteration = 0; iteration < 6; iteration++) {
        for (const name of ['lowerarm01.L', 'upperarm01.L']) {
          const bone = bones[name];
          mesh.updateMatrixWorld(true);
          const origin = bone.getWorldPosition(new Vector3());
          const current = bones['wrist.L'].getWorldPosition(new Vector3()).sub(origin).normalize();
          const desired = target.clone().sub(origin).normalize();
          const delta = new Quaternion().setFromUnitVectors(current, desired);
          const angle = identity.angleTo(delta);
          if (angle > .35) delta.copy(identity.clone().slerp(delta, .35 / angle));
          const world = bone.getWorldQuaternion(new Quaternion()).premultiply(delta);
          const parent = bone.parent!.getWorldQuaternion(new Quaternion()).invert();
          bone.quaternion.copy(parent.multiply(world));
        }
      }
    }
    mesh.updateMatrixWorld(true);
    // Ground the actual deformed soles, rather than guessing a root height.
    let lowest = Infinity;
    for (const i of soleIndices) {
      v.fromBufferAttribute(geometry.attributes.position, i);
      mesh.applyBoneTransform(i, v);
      lowest = Math.min(lowest, v.y);
    }
    mesh.position.y = -lowest;
    mesh.updateMatrixWorld(true);
    skeleton.update();
  }
  return {mesh, bones, setFrame, dispose() {geometry.dispose(); material.dispose(); skeleton.dispose();}};
}
