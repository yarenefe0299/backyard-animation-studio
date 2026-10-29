# Preview verification

## Codex Cloud checks

- Dependencies installed in cloud; exact versions recorded in package-lock.json.
- TypeScript compilation passed.
- Four motion/storyboard assertions passed when executed directly: contiguous
  ten-second sequence, finite poses/grounded debris, collapse/assembly/hover,
  deterministic out-of-order evaluation.
- Remotion's production bundler completed successfully. This is a JavaScript
  bundle, not an MP4 or a visual inspection.

## Rendering status

No video or still frames have been rendered in Codex Cloud, respecting the
GitHub-Actions-only rendering requirement. The initial default branch contains
only a README, so the new manual workflow must first be reviewed and merged by
the owner before GitHub makes workflow_dispatch available. The implementation
PR is left unmerged. No MP4, output-frame inspection, runner benchmark or visual
quality acceptance can be claimed yet.

The workflow will verify H.264, 1080 × 1920, 30 fps, 300 frames and 10 seconds with
ffprobe, then extract frames 30, 100, 150, 180, 210, 262 and 290 for human review.
It preserves the MP4, frames, probe output and dependency notices for three days.

## First-render review checklist

- Frame 30: establishing shot includes inventor, shed, bench, tree and fence.
- Frames 100/150: cardboard visibly separates, descends and stays on the lawn;
  drawing moves from the hand to the ground without distracting discontinuities.
- Frames 180/210: metal panels assemble and remain attached to moving joints.
- Frames 262/290: boots lift, body wobbles, face reacts, feet return to the lawn.
- Watch the entire MP4: camera cuts, expression changes, readable captions,
  consistent identity/set, no clipped bodies or accidental superhero resemblance.
- Record job duration. A 15-minute timeout is an imposed ceiling, not a measured
  guarantee. CPU rendering quality/performance remains unverified.

The prototype uses procedural rounded solids, filtered shadow maps and metallic
materials. It is not ray-traced studio animation. Future improvements should
prioritize sculpted anatomy, original rigged mesh, hand/prop contact continuity,
ambient occlusion, animation arcs and original sound design before extending the
full episode. No paid service is necessary for these improvements.
