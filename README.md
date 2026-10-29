# backyard-animation-studio

A reusable Remotion + React Three Fiber storytelling studio. Development happens
in Codex Cloud. Full videos render in GitHub Actions on standard free Ubuntu
runners. Nothing needs installing or downloading on the work Mac.

The registered composition is now **FlyingArmorEpisode**: a complete **48-second**,
**1440-frame**, **1080 × 1920**, **30 FPS** episode titled **How You Built Flying Metal
Armor in Your Backyard**. There is no new ten-second demo composition.

## A problem, a fix, and the next problem

Every upgrade stays on the same character in the same backyard:

1. Cardboard provides the shape, but folds.
2. Metal reinforces the cardboard, but makes the suit heavy.
3. Assisted joints restore movement, but need sustained power.
4. A fictional power cell drives the joints, but overheats the suit. The inventor
   raises a hand to his forehead, sweats and visibly struggles.
5. A cooling pack and spinning fan relieve the heat, but he remains grounded.
6. Imaginary hover modules provide lift, but cause unstable wobble.
7. Stabilizers and control pods settle the hover.
8. All accumulated upgrades work together for controlled flight above the yard.

The episode is caption-driven, with short outlined word captions, concise
addition/result annotations, and an included SRT story transcript. It currently
has **no spoken narration or audio track**. Propulsion, power cells and control
technology are fictional; no real human-flight construction instructions are given.

## Render the full video on GitHub

To test the pending full-episode PR before merging:

1. Open this repository → **Actions** → the existing render workflow. On `main`
   its old display name may still be **Render backyard preview**; the workflow
   filename remains `render-preview.yml` for compatibility.
2. Click **Run workflow** and select **codex/full-episode** from the branch dropdown.
3. Choose `flying-armor` if the episode input appears, then click **Run workflow**.
4. Wait for `plan`, all eight `render` jobs, and `assemble` to finish.
5. The final artifact is **full-backyard-episode-<run number>**, retained for
   **3 days**. It contains `flying-armor.mp4`, 16 PNG review frames, `story.srt`,
   `manifest.json`, `probe.json` and dependency/asset license notices.
6. Share its run/artifact URL with Codex to retrieve and inspect it in Cloud.
   GitHub does not play MP4 files directly from Actions artifacts. Do not download
   artifacts onto the work Mac if that is prohibited by workplace policy.

After owner review and merge, select `main`; its workflow display name becomes
**Render full backyard episode**. Start a **new run** for new code. Re-running an
older run uses that run's original commit. No automatic merging occurs.

## Why several render jobs?

The previous detailed ten-second proof took about nine minutes on a CPU runner.
A longer single-job render would exceed the required 15-minute ceiling. The new
workflow renders contiguous global-frame ranges in separate standard
`ubuntu-24.04` jobs, then joins the H.264 segments without re-encoding. The first
full episode has eight six-second segments. The planner splits longer shots into
segments of at most seven seconds.

Every job has `timeout-minutes: 15`. Dispatch is manual only: no push, PR or
schedule triggers. Intermediate segments expire after one day; the full output
after three days. The repository is public and uses standard hosted runners,
which are free under GitHub's public-repository policy. There are no paid APIs,
premium media tools, larger runners or GPU services. If visibility changes,
check the account's included Actions allowance before running.

The final assembly verifies codec, dimensions, frame rate, pixel format, frame
count and duration, and extracts two review frames for each story beat. A missing
or failed segment prevents publication of a falsely complete episode.

## Development and reuse

In Codex Cloud, run:

```sh
npm ci --no-audit --no-fund
npm run typecheck
npm test
npm run build
npm run plan:episode
```

These commands validate, test, bundle and plan; they do not render video. Video
rendering and assembly belong in GitHub Actions.

`src/story.ts` contains the episode registry, timed narration/captions, upgrade
additions, action selection and camera selection. The composition duration,
render matrix, transcript and review-frame plan are derived automatically.
To make another episode using this action library, add an `Episode` entry to
`episodes` and add its ID to the manual workflow's episode choices. New physical
features/actions require corresponding scene code; this is not a text-to-video
model that invents arbitrary choreography.

`src/motion.ts` evaluates cumulative capabilities, heat, mobility, wobble and
flight at any global frame. `src/human-rig.ts` skins the detailed CC0 actor and
calculates ground contact and the heat reaction. `src/Inventor.tsx` owns the suit,
eye treatment, sweat and bone-attached upgrades. `src/Backyard.tsx`,
`src/Environment.tsx`, `src/Props.tsx` and `src/Terrain.tsx` own the consistent set.
The continuous landscape, neighboring houses, shaped gables, textured roof boards,
branching trees, smaller leaves and anchored props replace the isolated platform.

## Evidence and remaining review

TypeScript checking, 13 tests, production bundling and full-episode planning pass
in Cloud. These checks cover cumulative upgrades, heat/cooling, pose determinism,
skin weights, grounded soles, hand reach, finger colors, prop release, chunk
coverage and encoding validation. **The new full episode has not yet rendered.**
Its background, facial appearance, visual storytelling, joined video and runner
performance require the first full GitHub run and output inspection.
See [docs/VERIFICATION.md](docs/VERIFICATION.md) and [docs/STORY.md](docs/STORY.md).

## Attribution

The initial project uses [remotion-dev/template-three](https://github.com/remotion-dev/template-three)
with its MIT notice preserved. The human mesh, male target, skeleton and skin
weights derive from MakeHuman's CC0 assets; see [assets/MAKEHUMAN.md](assets/MAKEHUMAN.md).
No MakeHuman application or Blender pipeline is installed or bundled. Workwear,
armor, scene choreography and set construction are independently authored.
Remotion runtime uses its own free-individual-use license, distinct from the
template's MIT license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and
`licenses/`. `npm run licenses` preserves installed notices in the final artifact.
