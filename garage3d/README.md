# Hidden driveway: Blender style test

This independent Python/Blender pipeline is the first visual review deliverable for **How to Hide a Car Under Your Driveway**. It keeps the existing Remotion flying-armor episode and its workflow intact. It uses modeled geometry, procedural materials, Blender Cycles, and FFmpeg; no paid API, subscription, downloaded asset, or local installation on your phone/Mac is needed for the GitHub workflow.

The deliverable is three portrait preview images and a **four-second, 120-frame, 30 fps animation** of the silver car riding the lift while the camera moves. It is silent. Narration, captions, sound effects, and the 12-scene episode are intentionally behind the visual review gate.

## Render on GitHub from an iPhone or browser

1. Open the pull request for the `garage3d/style-test` branch, then open **Checks → Render garage style test → Details**. A change under `garage3d/` triggers the draft render automatically for the pull request. Repository Actions must be enabled, and GitHub may require the repository owner to approve a first contributor's workflow run.
2. Wait for the run to finish. A green run means the render/encoding checks passed; visual approval is still yours. A failed or timed-out run is not a completed video.
3. Open that run's **Artifacts**. Download `garage-style-video-…-draft` for `style-test.mp4`, and `garage-style-review-…-draft` for the three PNGs, `.blend` master scene, and reports. Artifacts are ZIP downloads; iPhone Files can open them. Sign into GitHub to download them. They expire after 14 days.
4. For another draft run, use **Re-run all jobs** on the run. After this workflow exists on the default branch, open **Actions → Render garage style test → Run workflow**, choose the branch and quality, then run it. GitHub's manual-run button may not appear while the workflow exists only on this unmerged branch. Do not merge solely to obtain that button; the pull-request run provides the initial review.

The workflow installs Blender and FFmpeg on a remote Ubuntu 24.04 runner. It does not invoke the existing Node/Remotion workflow. GitHub Actions availability and usage limits still apply. Final quality can be slow on the runner's CPU; use draft for motion and review for image detail. The job stops after 180 minutes; available images and diagnostics upload even if animation fails, and a completed-video artifact is only uploaded after encoding verifies every frame.

## Outputs and quality settings

| Output | Review purpose |
| --- | --- |
| `exterior.png` | Warm daylight, silver car shape, cream plaster, oak, glass, pavers, driveway framing |
| `cutaway.png` | Persistent scene geometry, layered soil/pebbles, masonry, chamber/lift relationship; S02-inspired comparison |
| `hydraulics.png` | Connected cylinders, rods and platform, translucent blue overlays/flow; S06-inspired comparison |
| `style-test.mp4` | Genuine animated geometry/camera, easing and mechanical alignment |
| `style_test.blend` | Reusable editable 3D master, not a flattened image |
| `scene_report.json` | Build/render diagnostics emitted by the Blender script |
| `video_report.json` | Actual FFprobe dimensions, fps, decoded frame count, codec and color tags |

| Preset | Portrait resolution | Cycles samples | Intended use |
| --- | --- | --- | --- |
| `draft` | 270 × 480 | 16 | Low-cost first render and motion review |
| `review` | 540 × 960 | 64 | Materials, shadows and detail review |
| `final` | 1080 × 1920 | 128 | Full-resolution style-test export after review |

All presets render the same geometry and animation at 30 fps. Resolution/sample reduction controls time without replacing the scene with placeholder assets. This pipeline does not claim that small draft frames prove final production quality.

The renderer detects whether Blender was compiled with Open Image Denoise and enables Cycles denoising only when supported. Some distribution builds, including the local Debian Blender build used during development, omit it. Draft images can show sampling grain at 16 samples; `scene_report.json` records the actual denoising state. Use review quality to inspect materials and shadows, and increase samples for clean final exports if the runner's build lacks denoising.

## Optional command-line use

These commands are for a machine with Blender 4.x, Python 3, and FFmpeg/FFprobe installed. You can use the remote workflow instead.

```bash
# From the repository root: build and render all three stills plus animation.
blender --background --threads 2 --python-exit-code 1 \
  --python garage3d/style_test.py -- \
  --output garage3d/output --quality draft --mode all

# Encode only a complete frame sequence, and verify the resulting file.
python3 garage3d/encode.py --output garage3d/output

# Stills-only look development, without spending time on animation.
blender --background --threads 2 --python-exit-code 1 \
  --python garage3d/style_test.py -- \
  --output garage3d/output --quality review --mode stills

# Render one comparison view while adjusting materials or framing.
blender --background --threads 2 --python-exit-code 1 \
  --python garage3d/style_test.py -- \
  --output garage3d/output/review --quality review --mode stills --still hydraulics

# Inspect evaluated geometry in the saved master without rendering again.
blender --background --python-exit-code 1 \
  --python garage3d/test_scene.py -- garage3d/output/style_test.blend

# Meaningful encoder tests, including a real H.264 round trip when installed.
python3 -m unittest discover -s garage3d -p 'test_encode.py' -v
```

`--mode build` saves the scene without rendering. `--mode animation` renders the animation sequence. `--mode stills` renders the three review images; add `--still exterior`, `--still cutaway`, or `--still hydraulics` to select one view. Use separate output folders for different qualities; the encoder rejects missing, extra, or inconsistently sized frames. The encoder uses H.264 `yuv420p`, Rec.709 tags, a fast-start MP4, and no artificial repetition of stills to fill missing animation. FFmpeg errors and verification failures propagate as workflow failures.

`test_scene.py` opens the actual saved `.blend` file and evaluates all 120 animation poses. It measures tire contact against the modeled platform pavers, checks overlap between both telescopic stages and their barrels, verifies a steady descent and moving camera, and checks that the car fits below grade at the end. It also measures animated oil tracer positions against the real curved pressure-pipe centerlines at five poses across the shot. The workflow runs this integration check after rendering the stills and before spending time on the animation.

## Reference and visual review gate

The source files inspected for this work are `reference_12_part_storyboard.jpg`, `hidden_garage_3d_scene_manifest.json`, and `Script.txt`. The requested filename `hidden_garage_production_blueprint.md` is absent from the repository version used for this branch; `Script.txt` contains the detailed production blueprint and shot directions. The actual reference movie named in the manifest is not available here, so camera timing and moving-image fidelity cannot be compared directly with that movie.

The provided storyboard establishes warm cream/oak/gray/earth colors, softly lit beveled geometry, pale blue mechanical explanations, visible soil and masonry, and stable three-quarter cutaways. The preview applies that visual grammar to an original car/lift setting. The S02/S06 labels above describe comparison views for the style test, not completed episode shots.

Before approving the 51-second episode, inspect the three images at full size and play the MP4. Check car identity and modeled surfaces, bevels/joints/material grain, soft contact shadows, glass and metal reflections, warm reference palette, portrait framing, visible soil layers/masonry, connected rods/cylinders, stable car contact on the platform, smooth easing/camera motion, and blue fluid remaining inside the pipes. Record specific corrections if the style differs. A passing script or green workflow is not visual sign-off.

Only after explicit visual review should production expand to the manifest's 12 scenes, conversational original narration, bold outlined timed captions, sound effects, and 1080 × 1920 final assembly. This is a fictional engineering visualization; the modeled mechanism is for animation and is not a construction design.

## Source layout

- `style_test.py` builds the master, configures views and keyframes, renders PNG frames and saves the `.blend` scene.
- `materials.py` supplies shared procedural concrete, metal, glass, rubber, and overlay materials; the environment adds architectural and soil finishes.
- `geometry.py` supplies reusable modeled-edge, mesh and curve construction helpers.
- `car.py` models the reusable silver hatchback.
- `environment.py` models the house, driveway, soil and retaining masonry.
- `mechanism.py` builds the connected carriage, telescopic hydraulics, reservoir, pipes and animated oil tracers.
- `encode.py` checks the sequence, invokes FFmpeg, then verifies the real MP4 with FFprobe.
- `test_scene.py` inspects measured geometry and evaluated animation in the saved Blender master.
- `test_encode.py` checks sequence rejection and the video encode/inspect path.
- `../.github/workflows/render-garage-style-test.yml` installs tools and performs the remote render/upload.

Generated renders and `.blend` files belong in ignored output directories or Actions artifacts, not in the source history. See [VALIDATION.md](VALIDATION.md) and the pull request's validation notes for what was actually executed; this README specifies how to run the pipeline and does not assert that any render has already completed.
