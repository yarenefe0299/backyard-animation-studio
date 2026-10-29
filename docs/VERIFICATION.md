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

### First GitHub render: 2026-10-29

Run 40879220130 rendered and encoded all 300 frames in about 150 seconds on a
standard Ubuntu 26 CPU runner. The MP4 was uploaded despite the job failure.
The post-render step failed with exit 127: `ffprobe: command not found`.
The follow-up workflow explicitly installs FFmpeg (which includes ffprobe), pins
the standard Ubuntu 24.04 image and updates actions to Node 24 releases.
The revised workflow has not yet run on GitHub.

The existing artifact was retrieved into Codex Cloud. Its actual MP4 passed the
same verification assertions: H.264, 1080 × 1920, 30 fps, 300 frames, 10.000 seconds.
Six extracted frames (30, 100, 150, 180, 210, 262) were visually inspected together.
They show the same inventor/backyard, cardboard detaching and lying on the lawn,
metal panel assembly and raised boots during hover. Captions are present.
The entire MP4 has not been watched in real time. Surface pinching on several
rounded armor pieces and abrupt paper/cardboard contact transitions need further
art direction; the requested high-end Shorts polish has not been achieved.

### Original pre-render status (historical)

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
