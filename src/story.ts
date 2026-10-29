export type Feature = 'cardboard' | 'metal' | 'joints' | 'power' | 'cooling' | 'hover' | 'stabilizers';
export type Action = 'sketch' | 'heavy-step' | 'assisted-step' | 'power-up' | 'cool-down' | 'unstable-hover' | 'balance' | 'flight';
export type CameraShot = 'wide' | 'medium' | 'detail' | 'orbit' | 'low' | 'flight';
export type StoryStep = {
  id: string; frames: number; add: readonly Feature[]; action: Action; camera: CameraShot;
  title: string; result: string; narration: string;
};
export type Episode = {
  id: string; compositionId: string; title: string; fps: number; width: number; height: number;
  shots: readonly StoryStep[];
};

// Each step ADDS to the same suit. It never replaces the accumulated state.
export const episode: Episode = {
  id: 'flying-armor', compositionId: 'FlyingArmorEpisode',
  title: 'How You Built Flying Metal Armor in Your Backyard',
  fps: 30, width: 1080, height: 1920,
  shots: [
    {id: 'cardboard', frames: 180, add: ['cardboard'], action: 'sketch', camera: 'wide',
      title: 'CARDBOARD', result: 'A shape to build on.',
      narration: 'Start with cardboard armor and a sketch. It folds before you do. Keep the foundation.'},
    {id: 'metal', frames: 180, add: ['metal'], action: 'heavy-step', camera: 'medium',
      title: '+ METAL PLATES', result: 'More protection. Much more weight.',
      narration: 'Add metal plates over the cardboard for protection. Now it is strong. Your knees disagree.'},
    {id: 'joints', frames: 180, add: ['joints'], action: 'assisted-step', camera: 'detail',
      title: '+ ASSISTED JOINTS', result: 'Movement returns. You supply the effort.',
      narration: 'Keep the plates. Add assisted joints. You can move again, but now you are the battery.'},
    {id: 'power', frames: 180, add: ['power'], action: 'power-up', camera: 'orbit',
      title: '+ FICTIONAL POWER', result: 'Powered joints. Too much heat.',
      narration: 'Add a fictional power cell to drive the joints. Now the suit runs. And you are roasting.'},
    {id: 'cooling', frames: 180, add: ['cooling'], action: 'cool-down', camera: 'detail',
      title: '+ COOLING PACK', result: 'Cool again. Still stuck on the ground.',
      narration: 'Add cooling fins and a fan. The heat drops. You can breathe again. But you still cannot fly.'},
    {id: 'hover-test', frames: 180, add: ['hover'], action: 'unstable-hover', camera: 'low',
      title: '+ FICTIONAL HOVER MODULES', result: 'Lift arrives before balance.',
      narration: 'Add imaginary hover modules to the powered boots. You float. Then wobble. The garden files a complaint.'},
    {id: 'stabilization', frames: 180, add: ['stabilizers'], action: 'balance', camera: 'medium',
      title: '+ STABILIZATION + CONTROL', result: 'Lift becomes a steady hover.',
      narration: 'Keep the lift. Add stabilization and control pods. The wobble settles. Gravity requests a meeting.'},
    {id: 'flight', frames: 180, add: [], action: 'flight', camera: 'flight',
      title: 'EVERY UPGRADE, WORKING TOGETHER', result: 'Controlled fictional flight.',
      narration: 'With every upgrade working together, rise above your backyard. Titanium gray, turquoise, and absolutely no warranty.'},
  ],
};
export const episodes: readonly Episode[] = [episode];
export const totalFrames = (ep: Episode = episode) => ep.shots.reduce((sum, shot) => sum + shot.frames, 0);
export function episodeById(id: string) {
  const ep = episodes.find(e => e.id === id);
  if (!ep) throw new Error(`Unknown episode: ${id}`);
  return ep;
}
export function shotStart(id: string, ep: Episode = episode) {
  let start = 0;
  for (const shot of ep.shots) {if (shot.id === id) return start; start += shot.frames;}
  throw new Error(`Unknown shot: ${id}`);
}
export const paperReleaseFrame = (ep: Episode = episode) => Math.floor(ep.shots[0].frames * 2 / 3);
export function shotAt(frame: number, ep: Episode = episode) {
  const safeFrame = Math.max(0, Math.min(totalFrames(ep) - 1, frame));
  let start = 0;
  for (let index = 0; index < ep.shots.length; index++) {
    const shot = ep.shots[index];
    if (safeFrame < start + shot.frames) return {...shot, index, start, local: safeFrame - start};
    start += shot.frames;
  }
  throw new Error('Episode has no shots');
}
export function featureStart(feature: Feature, ep: Episode = episode) {
  let start = 0;
  for (const shot of ep.shots) {
    if (shot.add.includes(feature)) return start;
    start += shot.frames;
  }
  return Infinity;
}
export function captionAt(frame: number, ep: Episode = episode) {
  const shot = shotAt(frame, ep);
  const words = shot.narration.split(/\s+/);
  const phase = shot.local / shot.frames * words.length;
  return {word: words[Math.min(words.length - 1, Math.floor(phase))], phase: phase % 1};
}
export function validateEpisode(ep: Episode) {
  if (ep.fps !== 30 || ep.width !== 1080 || ep.height !== 1920) throw new Error('Delivery must be 1080×1920 at 30 fps');
  if (!ep.shots.length || ep.shots[0].add[0] !== 'cardboard') throw new Error('Start with the cardboard foundation');
  const seen = new Set<Feature>();
  const ids = new Set<string>();
  for (const shot of ep.shots) {
    if (ids.has(shot.id) || !Number.isInteger(shot.frames) || shot.frames < 1 || !shot.narration.trim()) throw new Error('Invalid shot data');
    ids.add(shot.id);
    for (const feature of shot.add) {
      if (seen.has(feature)) throw new Error(`Feature added twice: ${feature}`);
      seen.add(feature);
    }
    if (seen.has('joints') && !seen.has('metal')) throw new Error('Assisted joints need the metal frame');
    if (seen.has('power') && !seen.has('joints')) throw new Error('Power drives the assisted joints');
    if (seen.has('cooling') && !seen.has('power')) throw new Error('Cooling resolves the power heat');
    if (seen.has('hover') && !(seen.has('power') && seen.has('cooling'))) throw new Error('Hover requires fictional power and cooling');
    if (seen.has('stabilizers') && !seen.has('hover')) throw new Error('Stabilize the existing lift');
    if (shot.action === 'flight' && !seen.has('stabilizers')) throw new Error('Controlled flight requires stabilization');
  }
  return ep;
}
