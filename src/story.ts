// One set, one cast member; timing is data, motion is evaluated at any frame.
export const preview = {
  id: 'BackyardPreview', fps: 30, width: 1080, height: 1920,
  title: 'How You Built Flying Metal Armor in Your Backyard',
  shots: [
    {id: 'idea', frames: 72, words: ['You', 'built', 'flying', 'armor.']},
    {id: 'collapse', frames: 84, words: ['Cardboard', 'had', 'other', 'plans.']},
    {id: 'upgrade', frames: 66, words: ['Metal.', 'Fictional', 'hover', 'modules.']},
    {id: 'hover', frames: 78, words: ['Gravity', 'requested', 'a', 'refund.']},
  ],
} as const;

// Editorial plan only: deliberately NOT registered as a renderable full episode.
export const episodePlan = [
  {id: 'cardboard', gag: 'The crude sketch is sturdier than the suit.'},
  {id: 'heavy-metal', gag: 'One heroic step. One very unheroic lawn dent.'},
  {id: 'joints', gag: 'Assisted joints turn a shuffle into an accidental dance.'},
  {id: 'power-cooling', gag: 'A fictional pocket sun needs a tiny vacation fan.'},
  {id: 'hover-test', gag: 'Fictional hover modules levitate the inventor into the laundry.'},
  {id: 'stabilization', gag: 'The control system insists on a calming breath.'},
  {id: 'flight', gag: 'Titanium-gray and turquoise armor flies above the same backyard.'},
] as const;

export const totalFrames = preview.shots.reduce((sum, shot) => sum + shot.frames, 0);

export const shotStart = (id: typeof preview.shots[number]['id']) => {
  let start = 0;
  for (const shot of preview.shots) {
    if (shot.id === id) return start;
    start += shot.frames;
  }
  throw new Error(`Unknown action: ${id}`);
};
export const propReleaseFrame = shotStart('collapse') + 20;

export function shotAt(frame: number) {
  let start = 0;
  for (const shot of preview.shots) {
    if (frame < start + shot.frames) return {...shot, start, local: Math.max(0, frame - start)};
    start += shot.frames;
  }
  const shot = preview.shots[preview.shots.length - 1];
  return {...shot, start: totalFrames - shot.frames, local: shot.frames - 1};
}
