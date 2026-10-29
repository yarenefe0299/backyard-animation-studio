import {probeVideo, verifyVideo} from './video.ts';
const frames = Number(process.argv[3]);
if (!Number.isInteger(frames) || frames < 1) throw new Error('Expected frame count required');
verifyVideo(await probeVideo(process.argv[2]), {width: 1080, height: 1920, fps: 30, frames});
console.log(`Verified chunk: ${frames} frames, 1080×1920, 30 fps.`);
