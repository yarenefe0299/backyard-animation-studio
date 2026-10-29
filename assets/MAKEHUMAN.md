# Human mesh provenance and reproduction

The inventor's anatomy, topology and skin weights derive from CC0 graphical data
bundled by [MakeHuman Community](https://github.com/makehumancommunity/makehuman),
commit `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`.

MakeHuman's [license section C](https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.md#c-the-license-for-the-bundled-assets)
explicitly releases the base mesh, targets, poses and graphical assets under CC0.
The complete CC0 text is retained in `licenses/MakeHuman-CC0.txt`. Original asset
notices identify Data Collection AB, Joel Palmius and Jonas Hauquier (2020);
the morph also credits Manuel Bastioni (2014).

Only graphical data is reused. No MakeHuman application, AGPL program logic,
Blender pipeline, proprietary model, reference video or creator branding is bundled.
The conversion script, workwear colors, action evaluation, armor and episode are
independent project code.

## Inputs

All paths below are relative to that pinned MakeHuman repository commit:

| Upstream path | Local compiler input | SHA-256 |
| --- | --- | --- |
| makehuman/data/3dobjs/base.obj | base.obj | 8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c |
| makehuman/data/targets/macrodetails/caucasian-male-young.target | male.target | 9fc09223ef1150868f859d617350461ec92ed5f9b08ca0c7df900ae02c0b14de |
| makehuman/data/rigs/default.mhskel | default.mhskel | 99f179bce0aa850b45d4191a1d0d234c5851f881c057439470ded3bddf729a24 |
| makehuman/data/rigs/default_weights.mhw | default_weights.mhw | 0f3641d651ae3d00ad6b4ccee43142edb109d3bd909d27d9e4139ef1beed8625 |

Download these inputs **in Codex Cloud only**, retaining the pinned commit in
raw.githubusercontent.com URLs. Then, from the studio repository:

```sh
python scripts/compile-human.py /workspace/work/makehuman
npm run typecheck
npm test
npm run build
```

The compiler applies the male target, removes helper cages, triangulates the
body, normalizes the four strongest skin weights, dresses the character with
original workwear/scalp vertex colors and records joint positions. Its output,
`src/assets/inventor.json`, has 13,380 vertices, 26,756 triangles and 163 bones.
It is committed, so GitHub rendering needs no upstream asset download, Python
package, MakeHuman installation or Blender installation.

The original files need not be committed again; the pinned URLs, notices and
conversion script describe exactly how to reproduce the derived CC0 asset.
