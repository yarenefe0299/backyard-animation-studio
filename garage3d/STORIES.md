# Make a video from a story folder

The story pipeline turns a structured script into an animated Blender scene, offline narration, outlined captions, sound effects, and a verified H.264/AAC MP4. It runs on GitHub's Ubuntu runners; your iPhone or work Mac only needs a browser.

Start with **hidden-garage** to review the revised story opening: the car drives toward the house, parks, the camera reveals the underground space, and the lift descends. The full script then explains the excavation, supports, hydraulics, drainage, sensors, and matching cover. **hydraulic-basics** is a separate 15-second story using the same pipeline with a laboratory template. It demonstrates that the renderer is not limited to one garage script.

This is an automatic renderer for the declared 3D templates and actions. It does not infer an unfamiliar machine, character, or professional 3D asset from arbitrary prose or a reference image. A new subject that needs new objects requires a modeled asset/template adapter once; subsequent scripts can reuse it. References are saved and hashed for look development and provenance. They are not substituted for modeled scenes or silently turned into AI pictures.

## Render from an iPhone or browser

1. Open the story pull request's **Checks → Review story direction → Details**. Its automatic run produces separate **opening** and **mechanism** videos at draft quality so the hook and close-ups can be reviewed first. The manual Render engineering story form defaults to mechanism review. The workflow renders sharper review images. Repository Actions must be enabled; GitHub can require the owner to approve a first contributor's workflow.
2. After the new workflow is on the default branch, open **Actions → Render engineering story → Run workflow**. Select the branch containing your story, enter `stories/hidden-garage` or another story folder, choose **mechanism**, **opening** or **full**, and choose a quality. The manual button may not appear while the workflow exists only on an unmerged branch. The initial pull-request run does not require merging to review the direction.
3. Wait for the run to finish. **mechanism** selects the first garage `hydraulics` section (seven seconds in this story), or the lab's first `extend` section. **opening** renders the first scripted shot, including narration and captions. **full** renders every shot. Changing narration, camera beats or supported story actions requires editing the folder, not Blender code.
4. Download `engineering-video-…` from the run's **Artifacts**. It contains `story.mp4`, caption files, reports, and available review images. Download `engineering-review-…` for the editable master and diagnostic images. These are ZIP downloads; iPhone Files can extract them. GitHub requires sign-in for artifact downloads.

The mechanism and opening are review deliverables. A green check proves the automated checks passed; it does not approve the visual style or factual content. Review the focused explanation and hook before spending CPU time on the complete episode, and review the complete film before publishing it.

## Add your next story

Create a folder under `stories/`, using `stories/_template/` as a starting point. On GitHub's website, **Add file → Create new file** accepts a full path such as `stories/my-topic/story.json`; copy the template file's contents into it. Repeat for `script.md` and `references/style.md`, and use **Upload files** to add images or a recording. Commit the files to a separate branch. Once the workflow exists on the default branch, select that branch and folder in **Run workflow**. No installation or command line is required on your device.

```text
stories/my-topic/
├── story.json
├── script.md
├── direction.json          # optional authored focal views and camera timing
├── references/
│   ├── style.md
│   └── storyboard.jpg       # optional extra reference
├── narration.m4a           # optional iPhone Voice Memos recording
└── captions.srt            # optional authored timing
```

Every story needs at least one reference file. `references/style.md` can describe palette, materials, framing and visual priorities. The loader inventories everything under `references/` by default; an explicit `references` array can select files instead. All referenced paths must remain inside that story folder. Missing files, unknown settings, unsupported actions, invalid headings and fractional frame timings fail before rendering.

A minimal `story.json`:

```json
{
  "schema_version": 1,
  "id": "my-topic",
  "title": "How a Hydraulic Lift Works",
  "template": "hydraulic_lab",
  "fps": 30,
  "script": "script.md",
  "audio": {"mode": "espeak", "voice": "en-us", "rate": 175}
}
```

Use a lowercase, hyphenated `id`. The `garage` template provides the house, car, driveway, underground chamber and engineering mechanisms. The `hydraulic_lab` template provides a separate close-up mechanism setting. Optional `references` values are relative file paths, for example `"references": ["references/style.md", "references/storyboard.jpg"]`.

Write each narration beat below a structured heading in `script.md`:

```markdown
# How a Hydraulic Lift Works

## S01 | 5.0 | pressure | hydraulics
A pump sends oil through the pressure line into the cylinder.

## S02 | 5.0 | extend | cutaway
The piston moves, extending the rod and lifting the supported load.

## S03 | 5.0 | retract | hydraulics
Oil returns to the reservoir, letting the load settle smoothly.
```

The four heading fields are **shot ID | seconds | action | camera**. Shot IDs must be unique (`S01`, `S02`, …). The narration paragraph is plain text. Duration must cover whole frames at the configured fps; for example, 3.4 seconds is 102 frames at 30 fps. The compiler calculates all start/end frames, total length, caption windows and render chunks. It preserves your declared timing rather than guessing a new story from the reference image.

| Template | Supported actions |
| --- | --- |
| `garage` | `arrive`, `excavate`, `collapse`, `reinforce`, `load`, `hydraulics`, `rain`, `drainage`, `pinch`, `sensors`, `conceal`, `payoff` |
| `hydraulic_lab` | `pressure`, `extend`, `retract` |

Camera names are `arrival`, `exterior`, `cutaway`, `hydraulics`, `drainage`, and `sensor`. Choose a camera that shows the cause of the action clearly. For precise cuts, subject tracking and mechanism close-ups, add `"direction": "direction.json"` to `story.json` and follow [DIRECTION.md](DIRECTION.md). A beat names a modeled subject such as `pump`, `cylinder`, `valve` or `sensor`, plus its timing and framing. The action controls modeled movement; narration alone does not invent an additional mechanism or physical event.

## Narration, captions and sound

`audio.mode: "espeak"` uses the free offline eSpeak NG voice. This makes a complete draft without an API key or subscription. It is a synthetic preview voice; it is not a cloned creator voice or a promise of studio narration. The renderer measures and fits each spoken segment to the shot timing.

For a polished recorded voice, export a recording from iPhone Voice Memos, upload its M4A file, and select it. WAV, MP3, AAC, FLAC and OGG are also accepted; the runner converts them automatically:

```json
"audio": {
  "mode": "file",
  "file": "narration.m4a",
  "captions_file": "captions.srt"
}
```

The recording and optional SRT belong inside the story folder. Author them against the full-story timings; mechanism scope extracts the matching interval automatically. Without an authored SRT, captions group the script into short phrases and estimate timing within the measured speech windows; this is not phoneme-level or word-for-word alignment. Captions use bold white type with a black outline. Directed views place them in each view's safe zone and split cues at camera-beat boundaries. Fallback cameras retain their earlier placement. Procedural mechanical, water, rain and warning effects are mixed automatically. `audio.mode: "none"` intentionally omits narration.

## Rendering and review

The workflow builds one persistent master per run, checks the saved scene, prepares audio and captions, and distributes its exact frame ranges to render workers. Each worker checks that its own PNG sequence is complete. Assembly rejects missing, extra or inconsistent frames before encoding, then checks the actual MP4. A failed or timed-out render does not produce a completed-video artifact.

For a full garage story, the three sharper review stills select the arrival exterior, installed underground walls, and operating hydraulics when those actions are present. The contact sheet samples the complete chronological story. Inspect the drainage and safety close-ups there and in the moving video as well.

| Quality | Animation resolution | Intended use |
| --- | --- | --- |
| `draft` | 270 × 480 | Story structure, timing, movement and audio review |
| `review` | 540 × 960 | Material detail, framing and polish review |
| `final` | 1080 × 1920 | Full-resolution export after review |

The render preset also controls sampling. Review stills use review quality, or final when final is selected, while animation uses your selected quality. The new pipeline additionally runs pinned Intel Open Image Denoise 2.3.3 on the CPU, even when Blender lacks its native denoiser. Raw PNGs remain separate from cleaned frames; captions are composited after denoising. This color-only sRGB pass reduces grain but has no normal/albedo guidance or temporal history, so inspect fine detail and motion for smoothing or flicker. The reports record actual settings and completed outputs; choosing a final preset does not establish that a final render has completed.

Rendering uses at most four concurrent chunk workers, with a 180-minute timeout per Blender job. Full-resolution work can take much longer than a draft. Frame-chunk artifacts expire after one day; completed video and review artifacts expire after 14 days. Download the final artifacts to keep them. GitHub's usage and concurrency limits still apply even though the pipeline has no paid API or subscription dependency.

The supplied board guides the warm, softly lit material palette and persistent engineering cutaways. The story grammar is an establishing action, an early reveal, then visible problem/solution beats and close-ups of the mechanism. Professional short-form 3D production combines modeling, animation, editing and look development; the reusable template is what makes repeated rendering automatic. See the [Zack D Films 3D animator brief](https://zackdfilms.recruitee.com/o/3d-generalist) and [an animator's account of producing these films](https://supersets.chrisreillyportfolio.com/zackdfilms.php) for primary-source context. This project uses original narration and assets rather than copying their films or voices.

## Optional developer commands

These commands are for a cloud workspace or other machine that already has Blender, FFmpeg/FFprobe, eSpeak NG and DejaVu fonts. Browser users can use the workflow above.

```bash
python3 garage3d/pipeline.py plan \
  --story stories/hidden-garage --output garage3d/output/story \
  --quality draft --scope opening

blender -b -t 2 --python-exit-code 1 --python garage3d/render_story.py -- \
  --story stories/hidden-garage --output garage3d/output/story \
  --quality draft --scope opening --mode build

blender -b -t 2 --python-exit-code 1 --python garage3d/test_story_scene.py -- \
  garage3d/output/story/master.blend

python3 garage3d/pipeline.py audio \
  --story stories/hidden-garage --output garage3d/output/story \
  --quality draft --scope opening

# Render the master directly, then assemble all completed frames.
mkdir -p garage3d/output/story/frames
blender -b garage3d/output/story/master.blend -t 2 \
  -o "$PWD/garage3d/output/story/frames/frame_" -F PNG -a
python3 garage3d/pipeline.py assemble --output garage3d/output/story
```

Use `--scope full` consistently in planning, building and audio preparation for the whole script. The workflow does this automatically. To add new modeled subjects or animation behaviors, extend a template adapter and validate it with representative stills and motion before reusing it across new story folders.

The denoiser is downloaded from the [official Intel OIDN 2.3.3 release](https://github.com/RenderKit/oidn/releases/tag/v2.3.3), verified against a pinned SHA-256, and runs entirely on the runner. Images are not sent to a service. The release is Apache-2.0 with its bundled dependency notices.
