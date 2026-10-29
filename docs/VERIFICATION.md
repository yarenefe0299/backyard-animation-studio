# Verification record

## Full episode revision

The user approved the overall visual direction of the reference-style proof and
requested a full causal story, a grounded background, calmer facial treatment,
and better environment construction. The full timeline is now 48 seconds, 1440
frames at 1080 × 1920 / 30 FPS, with eight cumulative six-second beats.

Completed in Codex Cloud:

- TypeScript checking and production Remotion bundling.
- Thirteen tests: full timeline, cumulative features, heat/cooling and stability,
  dependency validation, render-order determinism, thin-panel normals, human
  topology/weights, deformed sole grounding, hand-to-forehead reach, corrected
  finger colors, paper release, chunk coverage and encoding validation.
- Full render plan generated: eight contiguous render jobs, 16 review frames,
  exact 48-second transcript and encoding expectations.
- Workflow YAML parsed and manual-only/Ubuntu/job-timeout constraints checked.
- License collector includes the template, MakeHuman CC0 and original asset notices.

**Not verified yet:** a render of the new full episode, its output frames, facial
appearance, environment finish, heat/cooling storytelling, final concatenation
in GitHub Actions, or per-segment CPU duration. No full MP4 or new still frame
has been rendered in Cloud. All rendering remains on GitHub Actions.

The connector has no dispatch operation and the cloud CLI previously returned
Forbidden for workflow API access. The full run must be triggered through the
GitHub website on `codex/full-episode`, before or after owner review/merge.

## Latest reference-style proof (prior revision)

[Run 40890084240](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/40890084240)
completed successfully. Its logs show rendering from 17:18:56 to encoding
completion at 17:28:03 Istanbul time (UTC+3): about 548 seconds for 300 frames. The user supplied
screenshots and identified the floating terrain boundary, bulging/staring eyes,
weak progression, swollen roof/boards, oversized foliage and poorly formed props.

These findings led to continuous terrain and surrounding houses, a sky material
excluded from fog (the old sky sphere was fogged to a flat color), rebuilt gables
and roof planes, physically uniform bevel radii, smaller instanced leaves and
connected branches, anchored props, reduced eye globes, calmer facial bones,
corrected finger skin colors, and the full problem→fix→new-problem story.

The previous timing makes a single 48-second job impractical within 15 minutes.
The new design partitions the full global timeline into <=7-second render chunks,
then verifies and joins them. Every job still has a 15-minute timeout. A failed
chunk blocks assembly; a successful build alone does not establish render success.

## Full-output review

Inspect both planned frames for every beat, then watch the complete joined clip:

- Landscape continues past the yard with no visible floating platform edge.
- Shed roof boards meet the ridge/gable, trees have connected branches and small
  foliage, and bench, planter, watering can and laundry have visible support.
- Eyes sit naturally in the face, lids do not deform brows, fingers are skin-toned.
- The power beat visibly causes heat; the cooling beat visibly relieves it.
- Cardboard, metal, joints, power and cooling remain when later modules arrive.
- Hover is absent until the hover beat, wobbles before stabilization, and becomes
  steady before the final flight above the same backyard.
- Frame transitions at every render-chunk boundary match the continuous timeline.
- MP4 is H.264/yuv420p, 1080 × 1920, 30 FPS, 1440 frames and 48 seconds.

## Earlier historical evidence

Run 40879220130 rendered the original toy-style proof but failed at missing
ffprobe. Run 40880391908 passed after explicit FFmpeg installation. Seven frames
from that earlier design were inspected. The user rejected its art direction;
those outputs do not validate this full-episode revision.
