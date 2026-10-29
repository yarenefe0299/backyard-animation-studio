# Verification record

## Reference-style revision (not yet rendered)

The scene has been rebuilt around the user's three supplied reference screenshots.
See REFERENCE_STYLE.md and assets/MAKEHUMAN.md for art direction and asset provenance.

Verified in Codex Cloud:

- TypeScript checking and production Remotion bundling pass.
- Nine tests cover storyboard timing, finite frame poses, hover bounds, render-order
  determinism, outward thin-panel normals, valid skin topology/weights, deformed
  sole grounding, hand-to-paper release and continuous cardboard descent.
- The 13,380-vertex CC0 human is bundled locally; no external media request is
  required by the renderer.
- Dependency/asset license collection completes.

No revised MP4 or revised output frame has been rendered or inspected. Rendering
is reserved for GitHub Actions. This revision's visual appearance and runtime on
that runner remain unverified. Tests validate rig behavior and geometry properties;
they do not certify the requested animation quality.

The connector has no workflow-dispatch operation, and the cloud CLI's attempt to
read the workflow API returned Forbidden. Start a new manual run on the review
branch using the GitHub website; no Mac installation or download is necessary.

## Earlier preview evidence (superseded visual design)

[Run 40879220130](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/40879220130)
rendered and encoded all 300 frames in about 150 seconds on a standard Ubuntu CPU
runner. The later ffprobe step failed because ffprobe was absent. The MP4 was
uploaded and retrieved in Codex Cloud. It passed encoding assertions.

[Run 40880391908](https://github.com/yarenefe0299/backyard-animation-studio/actions/runs/40880391908)
succeeded, including encoding verification, frame extraction and artifact upload
after explicit FFmpeg installation. Seven extracted frames (30, 100, 150, 180,
210, 262 and 290) were inspected. H.264, 1080 × 1920, 30 fps, 300 frames and exactly
10 seconds were confirmed. The complete MP4 was not watched in real time.

The user rejected that design's quality. It showed pinched armor surfaces,
primitive character anatomy, an oversized head, a flat environment treatment and
abrupt prop transitions. Those old render results do not validate the new design.

## New-render acceptance checklist

- Frame 30: natural-proportioned human, backyard continuity and soil cutaway.
- Frames 100/150: cardboard and drawing fall from plausible release positions.
- Frames 180/210: smooth titanium panels, visible skin/workwear, correct joint contact.
- Frames 262/290: fictional hover, body balance, clean boot contact and landing.
- Whole clip: stable eyes and facial skin, no exposed garment gaps, no clipping,
  readable one-word captions, appropriate timing and smooth camera movement.
- Record runner duration. The 15-minute limit is a ceiling, not a benchmark for
  the revised geometry, reflections and higher-resolution shadows.

Keep the seven-beat full episode unregistered until this preview is accepted.
