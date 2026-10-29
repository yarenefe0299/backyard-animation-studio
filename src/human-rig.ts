import {Bone, BufferGeometry, Float32BufferAttribute, MeshStandardMaterial,
  Quaternion, Skeleton, SkinnedMesh, Uint16BufferAttribute, Vector3} from 'three';
import data from './assets/inventor.json' with {type: 'json'};
import {poseAt, smooth} from './motion.ts';

export function createHumanRig() {
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
    const p = poseAt(frame);
    mesh.position.set(0, 0, 0);
    for (const [name, bone] of Object.entries(bones)) {
      bone.position.copy(rest[name]); bone.quaternion.copy(identity);
    }
    const sway = Math.sin(frame * .055) * .012;
    for (const [suffix, side] of [['L', 1], ['R', -1]] as const) {
      // Convert the source A-pose into a relaxed standing pose, then perform
      // anticipation, recoil and balance corrections through the actual skin rig.
      bones[`upperarm01.${suffix}`].rotation.z = side * (-.65 + p.hover * .38 + p.fail * (p.metal ? 0 : .12));
      bones[`upperarm01.${suffix}`].rotation.x = sway * side;
      bones[`lowerarm01.${suffix}`].rotation.x = suffix === 'R' && !p.metal ? -.8 + p.fail * .55 : -.16 - p.hover * .2;
      bones[`upperleg01.${suffix}`].rotation.x = -p.hover * .13 + p.wobble * side * .035;
      bones[`lowerleg01.${suffix}`].rotation.x = p.hover * .3;
      bones[`foot.${suffix}`].rotation.x = -p.hover * .12;
      for (let finger = 2; finger <= 5; finger++) for (let joint = 1; joint <= 3; joint++) {
        bones[`finger${finger}-${joint}.${suffix}`].rotation.x = suffix === 'R' && !p.metal && p.fail < .03 ? -.18 : -.035;
      }
      if (p.blink) {
        bones[`oculi01.${suffix}`].position.y -= .018;
        bones[`oculi02.${suffix}`].rotation.z = -side * .12;
      }
    }
    bones.spine01.rotation.z = -p.wobble * .045;
    bones.spine02.rotation.x = Math.sin(frame * .06) * .005 + (!p.metal ? p.fail * .025 : 0);
    bones.head.rotation.y = Math.sin(frame * .027) * .055;
    bones.head.rotation.z = p.headTilt * .25;
    bones.jaw.rotation.x = p.surprise ? .055 : 0;
    // A small anticipation crouch at ignition, evaluated directly from the shot.
    const crouch = p.shot.id === 'hover' ? Math.sin(smooth(p.shot.local / 12) * Math.PI) * .07 : 0;
    bones['upperleg01.L'].rotation.x -= crouch;
    bones['upperleg01.R'].rotation.x -= crouch;
    bones['lowerleg01.L'].rotation.x += crouch * 2;
    bones['lowerleg01.R'].rotation.x += crouch * 2;
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
