# backyard-animation-studio

A procedural Remotion + React Three Fiber studio, initially adapted from
[template-three](https://github.com/remotion-dev/template-three). Everything is
developed in Codex Cloud. Video rendering is reserved for GitHub Actions; nothing
needs to be installed on your Mac.

The first deliverable is **BackyardPreview**, a 10-second, 300-frame 3D proof of
concept at **1080 × 1920, 30 fps**. It contains an original inventor in one fixed
backyard, a hand-held armor sketch, a cardboard failure, assembling titanium-gray
and turquoise panels, and a short unstable fictional hover. It uses articulated
joint hierarchies, animated facial expressions, soft shadow filtering, rounded
geometry, animated foliage and laundry, and four moving camera setups. Captions
carry the joke; this proof has no audio track.

## Render from the GitHub website

This new workflow must exist on the repository's default branch (`main`) before
GitHub exposes **Run workflow**. This PR is deliberately left unmerged. After you
review and merge it yourself:

1. Open this repository → **Actions**.
2. Select **Render backyard preview** in the left sidebar.
3. Click **Run workflow**, select `main` (or a later development branch containing
   the workflow), then click the green **Run workflow** button.
4. Open the new run and wait for the `render` job to finish.
5. Under **Artifacts**, confirm `backyard-preview-<run number>` appears. It includes
   `backyard-preview.mp4`, seven PNG review frames, `probe.json`, and dependency
   license notices, retained for **3 days**. Do not download it onto the work Mac.
   Give Codex the run URL and ask it to retrieve and inspect the artifact in Cloud.
   GitHub does not play MP4 files directly from an Actions artifact in its website.

The workflow runs **only** through `workflow_dispatch`. No push, pull-request or
scheduled renders. It uses standard `ubuntu-latest`, two Chromium workers, CPU
SwiftShader, and a hard **15-minute** job timeout. The repository is public, for
which standard hosted runners are free under GitHub's current public-repository
policy. No paid runner, API, subscription, remote media or GPU service is used.
If visibility changes, check GitHub's included minutes before running.

## Cloud development

Use these commands only in Codex Cloud, not on the Mac:

```sh
npm ci --no-audit --no-fund
npm run typecheck
npm test
npm run build
```

`npm run build` bundles JavaScript without rendering video. `npm run
render:preview` is the GitHub runner's MP4 entry point. Keep video and still-frame
rendering on GitHub Actions. `npm run licenses` preserves dependency notices.

## Reusing the studio

`src/story.ts` is the storyboard: ordered semantic shot IDs, durations, captions,
delivery settings and the seven-beat full-episode editorial plan. Composition
duration is calculated automatically from the preview shots. `src/motion.ts`
evaluates character state directly at a frame, independent of playback order.
`src/Inventor.tsx` owns the consistent cast and joint hierarchy;
`src/Backyard.tsx` owns the fixed set; `src/Scene.tsx` owns lighting, camera and
caption composition. Change shot data and implement the corresponding camera and
motion action to make another story. New actions need implementation; this is
not a text-to-video model that invents arbitrary choreography.

The full episode, **How You Built Flying Metal Armor in Your Backyard**, has
seven planned beats: cardboard, heavy metal, assisted joints, fictional miniature
power/cooling, failed hover, stabilization, and final flight. Only the preview is
registered as a composition; there is no full-episode render to trigger yet.
All flight technology is fantasy. There are no engineering dimensions, propulsion
recipes or real human-flight construction instructions.

## Verification and quality limits

See [docs/VERIFICATION.md](docs/VERIFICATION.md) for actual checks and render status.
Bundling and motion tests establish software behavior, not visual polish. The
first GitHub render must still be reviewed for framing, shadow artifacts,
intersections, readable captions, comedic timing and CPU duration. No claim of
high-end animated Shorts quality is made before that inspection.

If software rendering hits the time limit, reduce shadow casters/geometry detail,
share repeated meshes through instancing and bake ambient occlusion into original
vertex colors. Keep 1080 × 1920 and 30 fps for delivery. For greater character
polish, author an original skinned GLB in cloud tooling, improve hand contacts,
add squash/stretch and facial blend shapes, and keep the same set and palette.
Those changes can use free tools and original/CC0 assets; a full Blender/GPU
pipeline has not been demonstrated practical within this runner limit.

## Attribution

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and `licenses/`. Remotion's
runtime license differs from the template's MIT license; its individual-use tier
is free. No commercially restricted media is used. Preserve dependency notices
when distributing source or bundles.
