# Story-pipeline validation

Visual approval remains pending. A completed draft render is not reference-quality sign-off or a completed 1080 × 1920 export.

## Previous narrative renders (earlier direction)

[GitHub Actions run 41189095379](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41189095379) succeeded at source commit `749688c0e2bc8268f7a3d33546662aac1417ae58`: prepare, all 17 frame chunks, and assembly passed. Its [completed video artifact](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41189095379/artifacts/13039991069) contains the film, captions, review images and reports. The [review artifact](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41189095379/artifacts/13038755443) also contains the editable master. Download these before their 14 November 2026 expiration.

The actual remote encoder/FFprobe report, retrieved from the successful assembly job logs, records:

| Property | Verified result |
| --- | --- |
| Story | `hidden-garage`, full scope, 12 shots |
| Frames and timing | 1,530 decoded frames; 51.000000 seconds; 30 fps |
| Picture | 270 × 480; H.264; yuv420p; Rec.709 limited range |
| Sound | AAC-LC; 48 kHz mono; 51.000000 seconds |
| Captions | Burned bold outlined ASS; separate SRT |
| Filtering | Intel Open Image Denoise applied before captions |
| MP4 SHA-256 | `c53931fbfeaac1ca8ebde331e0f3f2eaea01a0376cb71524ae6504bfc61624cd` |

This establishes an actual complete remote MP4. The final artifact ZIP could not be materialized through the available connector download path in the development workspace, so it has not been manually watched end to end here. Representative frames rendered locally from the same scene were inspected. GitHub artifact downloads remain available to a signed-in repository user.

## Previous framing checkpoint

Source `76f8e5da55cb0cbf67752dc302e392404652649d` improves the drainage close-up: it isolates the pump and valve in the same chamber, adds a soft inspection fill, and lets water recede before the explanation finishes. Full-garage review stills now select the exterior, reinforced chamber and hydraulics. The historical README's workflow instructions were corrected.

The revised full master built locally with 2,133 objects and passed all 36 sampled poses, including pump/valve screen placement above the lower captions and the water-recession check. Open/closed-valve frames were rendered, denoised and inspected; a captioned drainage frame was also inspected for obstruction.

[Run 41215412467](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41215412467) passed its remote prepare job, including unit checks, narration/captions/sound preparation, master build, saved-scene checks and all three sharper still renders. The [current review artifact](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41215412467/artifacts/13047699938) is complete and contains the revised editable master and preview images. That run subsequently completed all 17 chunks and verified its 51-second MP4. Its [video artifact](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/41215412467/artifacts/13049462629) has MP4 SHA-256 `9990c82b8bedc79deb7f7e0c3e0b33daedba00a2912763de2d9af58641dc8c94`. It remains an earlier direction draft; it does not contain the new part-focused edit described below.

## Earlier pipeline checks

- 46 unit tests passed across story-folder validation, offline audio, real OIDN filtering, encoder failure handling, and actual captioned H.264/AAC assembly. Blender integration scripts run inside Blender separately from these tests.
- The garage script compiles to 12 beats, 51 seconds, 1,530 frames and 144 words. The opening includes approach, parking, underground reveal, descent and cover closure.
- Local Blender 4.3.2 and remote Blender 4.0.2 built the full persistent scene. The remote master contains 2,132 objects. Full-story geometry checks sampled 36 shot poses and the complete sensor interruption.
- Measured seven-metre driving and matching wheel rotation; tyre contact error below 2.5 mm; selected closed-cover guide clearance 155 mm; telescopic-stage overlap 70 mm; hydraulic tracer centre-line error below 0.52 mm. These are the tested relationships, not a general collision or real-world engineering certification.
- Movement after the safety beam was blocked was 0.179 mm. The drainage check requires a modeled pump and valve, correct pipe alignment, a flap that opens with flow and closes afterwards, and hardware that remains absent before installation.
- Native iPhone Voice Memos AAC/M4A conversion was tested. Offline narration/soundtrack preparation completed at exactly 51 seconds, 48 kHz mono, with 48 phrase captions. The default voice is a synthetic draft voice; uploaded recordings and authored SRT timing are supported.
- The independent `hydraulic-basics` story completed the one-command local pipeline: 450 rendered frames, 15 seconds, 270 × 480, 30 fps, verified H.264/AAC, denoising and burned captions. Its MP4 SHA-256 is `e33a8d3cb14501d689fef50bb2b3c79b36fd66959549139f31fcb9df0f7f64ad`. This verifies a second modeled template, not arbitrary prose-to-3D generation.
- Arrival, parking, descent, closed-cover and hydraulic poses were rendered and inspected. A chronological nine-shot review additionally covered excavation, collapse, reinforcement, load, rain, pinch point, sensors, concealment and payoff. No severe disconnected geometry or black shell was found. Detail views crop portions of the car; draft denoising visibly smooths fine detail.
- Intel Open Image Denoise 2.3.3 CPU was downloaded from its official release, SHA-256 checked, and applied to actual Blender stills. Raw frames are preserved. Color-only filtering has no albedo/normal guidance or temporal history.
- Existing flying-armor source, assets and workflow remain unchanged.

The `review` and `final` presets are configured. No complete 1080 × 1920 narrative film has been rendered. Review style, motion, caption timing and narration before publishing or requesting a final export. The original four-second comparison is documented separately in [VALIDATION_STYLE_TEST.md](VALIDATION_STYLE_TEST.md); usage is in [STORIES.md](STORIES.md).

## Part-focused editorial revision

The latest user feedback accepts the models and requests a stronger hook, meaningful zooms and clearer part demonstrations. [DIRECTION.md](DIRECTION.md) records primary-source research, its limits, the revised edit, and the reusable direction-file format. The new script keeps 12 sections and 51 seconds; `direction.json` authors 26 focal views within them. The six-second opening tracks the arriving car and reveals its descent earlier. The seven-second hydraulic section moves from pump to oil line to telescopic cylinder, then shows the car rising. Valve and sensor explanations have their own close-ups.

All 53 local unit tests passed. The new direction loader checks timing, unknown subjects/shot IDs, overlapping travel, confined file paths and source hashes. Tests cover camera beats, caption changes at cuts and correct extraction of a later section from a full recording/SRT. Both review workflow files passed actionlint 1.7.7. The original scene-modeling files remain unchanged.

A new full Blender master was built, with the camera pass revised on that persistent geometry. Representative frames were rendered and inspected. Subsequent lighting and cutaway isolation remove the power lead from the valve view and preserve metal/enamel contrast. Captions reserve space below small parts. The revised saved master passed all 36 sampled poses and the complete sensor-stop check. Focal parts occupy 61.4% (pump assembly), 47.8% (moving rod), 66.6% (valve housing) and 11.2% (sensor lens, within its larger assembly) of frame height in the measured close-ups. Checks require the parts to be rendered and uncropped, with foreground occluders hidden. These checks are not visual approval. New review-video results are recorded after their actual renders finish; a saved master is not presented as a finished film.

Pull-request reviews now produce **opening** and **mechanism** videos separately through a reusable workflow, with scope-specific artifact names and concurrency groups. The revised complete 51-second film and final 1080 × 1920 film have not been rendered. Review these short direction tests before spending time on the complete timeline.
