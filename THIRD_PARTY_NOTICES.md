# Third-party attribution and licenses

## Initial framework

Based on [remotion-dev/template-three](https://github.com/remotion-dev/template-three),
reviewed at commit `fb33b614d8442a1d75a79b8355a35b31772ca4af`.
The registration entry point is copied; TypeScript settings, package structure,
Composition registration, ThreeCanvas integration and CLI configuration are adapted.
The phone/tablet demo, videos and models are deliberately omitted.
Copyright (c) 2021 Jonny Burger. The complete MIT notice is retained in
`licenses/template-three-MIT.txt`.

## Design research

[DvaitAI-tech/anim-studio](https://github.com/DvaitAI-tech/anim-studio): reviewed
README.md, scene.schema.md and _test_shot.json on 2026-10-29. Its named cast,
one-set storyboard, semantic actions and explicit shot durations informed this
project's independent TypeScript implementation. No anim-studio code, assets,
voices, Blender pipeline or external animation clips are included.

## Runtime dependencies

Three.js and React Three Fiber use MIT licensing; React is MIT. Remotion runtime
packages use the Remotion License, distinct from the template's MIT license.
The installed Remotion license permits free video creation by individuals,
nonprofits, and for-profit organizations with up to three employees, including
commercial video creation. Larger for-profit organizations need a company license.
This project selects the user's individual, free use case; it does not purchase a
license or call a hosted service. See the preserved full text for exact terms.

`npm run licenses` copies installed LICENSE/NOTICE/COPYING files, a package license
inventory and these notices into `out/licenses`. The workflow uploads those files
alongside the preview. Do not discard notices when redistributing source or
dependency bundles. The lockfile pins all dependency versions.

The reference-style revision uses MakeHuman's CC0 hm08 human base mesh, male
morph, skeleton and skin weights, compiled into src/assets/inventor.json. Full
provenance, source commit, copyright notices and reproduction details are in
assets/MAKEHUMAN.md; the complete CC0 text is in licenses/MakeHuman-CC0.txt. No
MakeHuman application code is imported. Workwear colors, armor, motion, captions,
backyard geometry and procedural terrain/sky textures are independently authored.
No creator footage, superhero models, third-party audio, fonts or synthetic voices
are bundled.
System Arial/sans-serif is used for captions. The preview has no audio track.
