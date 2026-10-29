"""Build a dressed, skinned inventor from CC0 MakeHuman data; no application code.
Usage: python scripts/compile-human.py SOURCE_DIRECTORY
Inputs: base.obj, male.target, default.mhskel, default_weights.mhw.
Source URLs, commit and asset licenses: assets/MAKEHUMAN.md.
This runs in Codex Cloud; the compiled JSON is committed, not fetched at render.
"""
import collections
import json
import math
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
vertices, faces, groups = [], [], collections.defaultdict(set)
group = ''
for line in (source / 'base.obj').read_text().splitlines():
    fields = line.split()
    if not fields:
        continue
    if fields[0] == 'v':
        vertices.append(list(map(float, fields[1:4])))
    elif fields[0] == 'g':
        group = fields[1]
    elif fields[0] == 'f':
        ids = [int(v.split('/')[0]) - 1 for v in fields[1:]]
        groups[group].update(ids)
        if group == 'body':
            for j in range(1, len(ids) - 1):
                faces.append([ids[0], ids[j], ids[j + 1]])
for line in (source / 'male.target').read_text().splitlines():
    fields = line.split()
    if fields and not fields[0].startswith('#'):
        i = int(fields[0])
        vertices[i] = [v + float(delta) for v, delta in zip(vertices[i], fields[1:])]

# One deterministic, metric-sized actor. No helper cages or anatomical accessories.
used = sorted({i for face in faces for i in face})
remap = {old: new for new, old in enumerate(used)}
floor = min(vertices[i][1] for i in used)
scale = .16

def point(v):
    return [round(v[0] * scale, 6), round((v[1] - floor) * scale, 6), round(v[2] * scale, 6)]

rig = json.loads((source / 'default.mhskel').read_text())
weights = json.loads((source / 'default_weights.mhw').read_text())['weights']

def joint(name):
    indices = rig['joints'][name]
    return point([sum(vertices[i][a] for i in indices) / len(indices) for a in range(3)])

bones = [{'name': name, 'parent': b['parent'], 'head': joint(b['head']), 'tail': joint(b['tail'])}
         for name, b in rig['bones'].items()]
bone_ids = {b['name']: i for i, b in enumerate(bones)}
per_vertex = collections.defaultdict(list)
for name, pairs in weights.items():
    for i, w in pairs:
        if i in remap and w > 0:
            per_vertex[i].append((bone_ids[name], w))

skin_indices, skin_weights = [], []
for i in used:
    pairs = sorted(per_vertex[i], key=lambda pair: pair[1], reverse=True)[:4]
    if not pairs:
        pairs = [(bone_ids['root'], 1)]
    total = sum(w for _, w in pairs)
    pairs += [(0, 0)] * (4 - len(pairs))
    skin_indices.extend(b for b, _ in pairs)
    skin_weights.extend(round(w / total, 7) for _, w in pairs)

# Original workwear, shaved hair, subtle lip/brow tones. Colors stored in linear
# space because Three's vertex colors are linear, avoiding a washed-out result.
def linear(hexcolor):
    rgb = [int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]

positions, colors, regions = [], [], []
for i in used:
    x, y, z = vertices[i]
    ax = abs(x)
    c, region = '#c09276', 'skin'
    hand_weight = sum(w for bone, w in per_vertex[i] if bones[bone]['name'].startswith(('wrist.', 'finger', 'metacarpal')))
    if hand_weight > .15:
        c, region = '#c09276', 'skin'
    elif y < -7.1:
        c, region = '#333c42', 'boots'
    elif y < 1.8:
        c, region = '#3c4b57', 'trousers'
    elif y < 6.35 and (ax < 1.85 or (y > 3.9 and ax < 3.7)):
        c, region = '#607784', 'shirt'
    elif y > 8.65 or (y > 7.95 and z < .2):
        c = '#352d29'
    elif 8.4 < y < 8.53 and .12 < ax < .56 and z > 1.1:
        c = '#574037'
    elif 7.67 < y < 7.83 and ax < .28 and z > 1.25:
        c = '#95665b'
    # Small deterministic cloth variation, no random flicker or texture fetches.
    shade = 1 + .025 * math.sin(x * 23 + y * 13) * math.sin(z * 31)
    positions.extend(point(vertices[i]))
    colors.extend(round(v * shade, 5) for v in linear(c))
    regions.append(region)

out = {
    'source': 'MakeHuman hm08 + caucasian-male-young, CC0; see assets/MAKEHUMAN.md',
    'position': positions,
    'index': [remap[i] for face in faces for i in face],
    'color': colors,
    'skinIndex': skin_indices,
    'skinWeight': skin_weights,
    'bones': bones,
    'eyes': [joint('eye.L____head'), joint('eye.R____head')],
}
dest = pathlib.Path('src/assets/inventor.json')
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, separators=(',', ':')) + '\n')
print(f'{len(used)} vertices, {len(faces)} triangles, {len(bones)} bones; {dest.stat().st_size:,} bytes')
print('eye centers:', out['eyes'])
print('body extent:', [max(positions[a::3]) - min(positions[a::3]) for a in range(3)])
