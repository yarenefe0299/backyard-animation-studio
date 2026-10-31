# Story-pipeline validation

Visual review remains pending; no claim of final reference-quality sign-off is made.

## Current implementation

- Story-folder compiler: hidden-garage has 12 beats, 51.0 seconds, 1,530 frames and 144 words. A separate hydraulic-basics story has 450 frames/15 seconds.
- 44 tests passed across folder validation, offline audio, real OIDN filtering, encoder failure handling, and actual captioned H.264/AAC assembly.
- Blender 4.3.2 built the seven-second arrival master and the full 51-second master. Scene checks passed on both: seven metres of driving, matching wheel rotation, tyre contact within 2.5 mm, cover clearance of 155 mm, connected telescopic stages and oil tracers within 0.52 mm of pipe centre lines.
- Full-story checks sampled 36 shot poses and the complete sensor interruption: movement after beam blocking was 0.179 mm.
- Full offline narration/soundtrack preparation completed at exactly 51 seconds, 48 kHz mono, with 48 phrase captions. The default voice is explicitly a synthetic draft voice; user-recorded WAV/SRT inputs are supported.
- Revised arrival, parking, descent and closed-cover poses were rendered and inspected; an opaque ground apron now preserves the intended underground reveal.
- Intel Open Image Denoise 2.3.3 CPU was downloaded from its official release, SHA-256 checked, and tested on actual Blender stills. Raw frames are preserved. Color-only filtering can smooth detail and has no temporal history.

The new complete narrative MP4 and remote workflow results will be recorded after the render finishes. Planned frame counts and a saved master alone are not presented as a completed film. The 1080 × 1920 preset is configured but has not been rendered.

The earlier four-second comparison is documented separately in [VALIDATION_STYLE_TEST.md](VALIDATION_STYLE_TEST.md).
