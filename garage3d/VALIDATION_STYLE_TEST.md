# Style-test validation

Visual approval is pending. These checks establish functioning geometry, animation and rendering; they do not approve a match to the reference. The 12-scene episode is intentionally outside this deliverable.

## Executed locally

- Blender **4.3.2** rendered all three corrected review views at **540 × 960**, **64 Cycles samples**: `exterior.png`, `cutaway.png`, and `hydraulics.png`. The generated report records all three as completed. All three images were inspected.
- This Debian Blender build omits Open Image Denoise. The images therefore contain sampling grain. The renderer reads Cycles' actual `with_openimagedenoise` capability and enables denoising on builds that support it.
- `test_scene.py` passed on the saved master across **120 evaluated poses**: four tire contacts against modeled pavers, overlap of both telescopic stages, continuous descent, actual camera travel, and the entire car below grade at the end. The largest sampled oil-tracer centerline error was **0.506 mm**, inside the 4 mm test threshold.
- Start, midpoint and end poses were also rendered and inspected at 270 × 480 to check the visible descent and camera framing.
- A second complete local animation render from the validated saved master finished all **120 frames** at 270 × 480. Encoding and FFprobe verification also passed: H.264/yuv420p, 30 fps, four seconds, 120 decoded frames, Rec.709.
- All **six encoder tests** passed, including a real H.264 encode and FFprobe round trip, missing/stale sequence rejection, inconsistent-size rejection, and removal of stale success outputs on failure.
- Python syntax compilation and workflow YAML structure checks passed. The diff adds only `garage3d/` and the separate garage workflow; the flying-armor source and workflow are unchanged.

## Animation and remote run

The complete remote workflow [run 41149365464](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41149365464) **passed** on source commit `17333e6cccf7029ef4b6d20353cd2dfde930359d`, using **Blender 4.0.2** on Ubuntu. Installation, six encoder tests, three still renders, saved-master integration, the complete animation render, encoding verification, and both artifact uploads succeeded.

The downloaded artifact reports were inspected, and the downloaded MP4 was independently checked with FFprobe. Its decoded beginning, midpoint and final frames were inspected for the expected car descent and camera framing.

| Verified output | Actual result |
| --- | --- |
| Three review stills | 540 × 960, 64 Cycles samples, all three completed |
| Animation source | 120 genuinely rendered frames, 270 × 480, 16 samples |
| MP4 | H.264, yuv420p, 30 fps, 4.000000 seconds, 120 decoded frames |
| Color metadata | Rec.709 matrix, primaries and transfer; limited TV range |
| Denoising on remote runner | Unavailable; sampling grain remains |

Download [review images and master](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41149365464/artifacts/13023145813) and [verified video](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41149365464/artifacts/13022982145). These artifacts expire on November 14, 2026; rerun the workflow to regenerate them.

A documentation-only follow-up records these results without repeating the expensive render. The workflow run above identifies the exact validated source revision.

Final-quality 1080 × 1920 output is configurable but has not been rendered. Narration, captions, sound effects and the 51-second episode remain behind the user's visual review gate.
