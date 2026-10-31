"""Original, modeled compact hatchback. Metres; +Z up; nose faces -Y.

No external meshes or image textures. ``build_car(materials=None)`` returns a
single root; animate that root to carry every mechanical and trim component.
"""
import math
import bpy
from mathutils import Vector


def _material(name, color, metallic=0.0, roughness=0.4, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Transmission Weight'].default_value = transmission
    if metallic > 0.5:
        p.inputs['Coat Weight'].default_value = 0.30
        p.inputs['Coat Roughness'].default_value = 0.18
    return m


def _mesh(name, vertices, faces, mat, root, bevel=0):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root
    obj.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    if bevel:
        mod = obj.modifiers.new('Manufactured edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    return obj


def _box(name, pos, scale, mat, root, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.parent = root
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Soft formed edges', 'BEVEL')
        b.width = bevel
        b.segments = 4
    o.modifiers.new('Weighted face normals', 'WEIGHTED_NORMAL')
    return o


def _curve(name, points, radius, mat, root, cyclic=False):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 16
    c.bevel_depth = radius
    c.bevel_resolution = 3
    s = c.splines.new('BEZIER')
    s.bezier_points.add(len(points) - 1)
    for b, p in zip(s.bezier_points, points):
        b.co = p
        b.handle_left_type = b.handle_right_type = 'VECTOR'
    s.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    o.parent = root
    c.materials.append(mat)
    return o


def _cylinder(name, pos, radius, depth, mat, root, axis='X', vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=pos)
    o = bpy.context.object
    o.name = name
    if axis == 'X':
        o.rotation_euler[1] = math.pi / 2
    elif axis == 'Y':
        o.rotation_euler[0] = math.pi / 2
    o.parent = root
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    b = o.modifiers.new('Machined rim edge', 'BEVEL')
    b.width = 0.005
    b.segments = 3
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return o


def _catmull(p0, p1, p2, p3, t):
    return tuple(0.5 * ((2*b) + (-a+c)*t + (2*a-5*b+4*c-d)*t*t + (-a+3*b-3*c+d)*t*t*t)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def _loft(name, sections, cross, mat, root):
    """Smooth closed body from transverse design sections, without a stock cube."""
    rings = []
    for i in range(len(sections)-1):
        for j in range(5):
            rings.append(_catmull(sections[max(i-1, 0)], sections[i], sections[i+1],
                                  sections[min(i+2, len(sections)-1)], j/5))
    rings.append(sections[-1])
    profile = []
    for i in range(len(cross)):
        for j in range(3):
            profile.append(_catmull(cross[(i-1) % len(cross)], cross[i],
                                    cross[(i+1) % len(cross)], cross[(i+2) % len(cross)], j/3))
    verts = [(x*w, y, low+z*(high-low)) for y, w, low, high in rings for x, z in profile]
    n = len(profile)
    faces = [(i*n+j, i*n+(j+1) % n, (i+1)*n+(j+1) % n, (i+1)*n+j)
             for i in range(len(rings)-1) for j in range(n)]
    faces += [tuple(reversed(range(n))), tuple((len(rings)-1)*n+j for j in range(n))]
    return _mesh(name, verts, faces, mat, root)


def _glass_panel(name, corners, mat, black, root):
    # Rounded, laminated glazing with shallow compound curvature.
    corners = list(map(Vector, corners))
    centre = sum(corners, Vector())/4
    normal = (corners[1]-corners[0]).cross(corners[3]-corners[0]).normalized()
    if normal.dot(Vector((centre.x, centre.y, centre.z-.8))) < 0:
        normal = -normal
    perimeter = []
    for i, corner in enumerate(corners):
        start = corner + .065*(corners[(i-1)%4]-corner)
        end = corner + .065*(corners[(i+1)%4]-corner)
        for step in range(7):
            t = step/6
            perimeter.append((1-t)**2*start + 2*t*(1-t)*corner + t*t*end)
    n = len(perimeter)
    vertices = list(perimeter)
    vertices += [centre+.5*(p-centre)+.013*normal for p in perimeter]
    vertices.append(centre+.018*normal)
    faces = [(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    faces += [(n+i,n+(i+1)%n,2*n) for i in range(n)]
    o = _mesh(name, vertices, faces, mat, root)
    solid = o.modifiers.new('Laminated glass thickness', 'SOLIDIFY')
    solid.thickness = 0.006
    _curve(name+' rubber seal', perimeter, 0.010, black, root, True)
    return o


def _wheel(x, y, mats, root, number):
    silver, rubber, steel, black = (mats[k] for k in ('silver', 'rubber', 'steel', 'black'))
    sign = 1 if x > 0 else -1
    z = 0.351
    # Shaped tire: rounded shoulders, recessed bead and bulging sidewall.
    profile = [(-.117,.250),(-.124,.292),(-.112,.320),(-.082,.343),
               (-.052,.351),(.052,.351),(.082,.343),(.112,.320),(.124,.292),(.117,.250)]
    n = 80
    verts = [(x+ax, y+r*math.cos(a*2*math.pi/n), z+r*math.sin(a*2*math.pi/n))
             for ax,r in profile for a in range(n)]
    faces = [(i*n+j, i*n+(j+1)%n, ((i+1)%len(profile))*n+(j+1)%n,
              ((i+1)%len(profile))*n+j) for i in range(len(profile)) for j in range(n)]
    _mesh('Car tire %d'%number, verts, faces, rubber, root)
    outside = x+sign*.119
    _cylinder('Car alloy barrel %d'%number, (x,y,z), .253,.190,steel,root)
    _cylinder('Car ventilated brake rotor %d'%number,(outside-sign*.040,y,z),.205,.012,steel,root)
    for row, rad in enumerate((.166,.185)):
        for hole in range(14):
            a = hole*2*math.pi/14+row*.14
            _cylinder('Car brake drilling', (outside-sign*.032,y+rad*math.cos(a),z+rad*math.sin(a)),
                      .008,.001,black,root,vertices=12)
    _box('Car brake caliper', (outside-sign*.026,y+.16,z+.01),(.035,.075,.19),black,root,.012)
    # Tapered spokes with actual open space between them.
    for k in range(10):
        a = 2*math.pi*k/10
        pts = []
        for ax in (-.012,.012):
            for r, angle in ((.065,a-.20),(.235,a-.063),(.235,a+.063),(.065,a+.20)):
                pts.append((outside+ax,y+r*math.cos(angle),z+r*math.sin(angle)))
        _mesh('Car forged alloy spoke',pts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),
              (2,6,7,3),(3,7,4,0)],silver,root,.006)
    _cylinder('Car hub cap %d'%number,(outside+sign*.014,y,z),.066,.025,silver,root)
    for k in range(5):
        a = k*2*math.pi/5
        _cylinder('Car wheel lug', (outside+sign*.030,y+.044*math.cos(a),z+.044*math.sin(a)),
                  .008,.009,steel,root,vertices=6)
    # Two molded rim beads and fine tread cuts are real geometry.
    for rad in (.252,.295):
        pts = [(outside+sign*.004,y+rad*math.cos(a*2*math.pi/64),z+rad*math.sin(a*2*math.pi/64)) for a in range(64)]
        _curve('Car tire sidewall molding',pts,.0025,rubber,root,True)
    for k in range(48):
        a = k*2*math.pi/48
        pts = [(x+ax,y+.3515*math.cos(a+offset),z+.3515*math.sin(a+offset))
               for ax,offset in ((-.070,-.025),(0,0),(.070,-.025))]
        _curve('Car directional tread',pts,.003,black,root)


def build_car(materials=None):
    """Return parent root at origin. Ground contact is z=0; full length 4.17 m.

    Optional shared keys: silver, glass, rubber, steel, black. All other trim
    materials are made here. No operators depend on a user selection.
    """
    materials = materials or {}
    mats = dict(materials)
    defaults = {
        'silver': ((.53,.57,.60),.78,.25,0),
        'glass': ((.095,.16,.19),.12,.12,.26),
        'rubber': ((.024,.028,.030),0,.76,0),
        'steel': ((.32,.37,.40),.86,.24,0),
        'black': ((.012,.016,.019),.1,.38,0),
    }
    for key, vals in defaults.items():
        if key not in mats:
            mats[key] = _material('Car '+key,*vals)
    silver, glass, rubber, steel, black = (mats[k] for k in defaults)
    lamp = _material('Car headlamp optical glass',(.78,.88,.92),.28,.12)
    headlens = _material('Car smoked optical headlamp',(.18,.23,.27),.35,.16)
    red = _material('Car ruby tail light lens',(.37,.015,.009),.18,.19)
    fabric = _material('Car charcoal upholstery',(.045,.053,.055),0,.86)
    root = bpy.data.objects.new('Silver hatchback | complete assembly',None)
    bpy.context.collection.objects.link(root)
    root['asset_type'] = 'original_procedural_hatchback'
    root['forward_axis'] = '-Y'
    root['ground_z'] = 0.0
    profile = [(-.74,0),(-.98,.15),(-1,.52),(-.96,.90),(-.82,1),
               (0,1.025),(.82,1),(.96,.90),(1,.52),(.98,.15),(.74,0),(0,0)]
    sections = [(-2.07,.76,.43,.82),(-1.99,.84,.40,.88),(-1.70,.88,.38,.91),
                (-1.12,.90,.38,.96),(-.65,.90,.37,.98),(.45,.90,.37,.99),
                (1.25,.89,.39,.99),(1.76,.86,.42,.95),(2.00,.77,.45,.90),(2.08,.63,.49,.80)]
    hull = _loft('Car sculpted monocoque with wheel arches',sections,profile,silver,root)
    # Apply physically open arches to the continuous body; the silhouette has real voids.
    bpy.context.view_layer.objects.active = hull
    for wheel_y in (-1.28,1.26):
        bpy.ops.mesh.primitive_cylinder_add(vertices=80,radius=.396,depth=2.5,
                                           location=(0,wheel_y,.351),rotation=(0,math.pi/2,0))
        cutter = bpy.context.object
        mod = hull.modifiers.new('Open wheel arch','BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter
        bpy.context.view_layer.objects.active = hull
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    edge = hull.modifiers.new('Rolled fender lips','BEVEL')
    edge.width = .012
    edge.segments = 3
    edge.limit_method = 'ANGLE'
    hull.modifiers.new('Panel normals','WEIGHTED_NORMAL')
    # Cabin is glazed between modeled pillars, not an opaque block under painted windows.
    roof = _loft('Car rounded roof panel',[(-.54,.53,1.375,1.42),(-.42,.66,1.406,1.47),(-.10,.70,1.43,1.505),
                (.55,.70,1.43,1.515),(1.02,.64,1.39,1.47),(1.20,.44,1.32,1.37)],
                [(-1,0),(-.99,.5),(-.87,.85),(0,1),(.87,.85),(.99,.5),(1,0),(0,0)],silver,root)
    _glass_panel('Car curved front windscreen',[(-.804,-1.03,.987),(.804,-1.03,.987),
                 (.651,-.466,1.424),(-.651,-.466,1.424)],glass,black,root)
    _glass_panel('Car rear hatch glazing',[(.769,1.73,1.00),(-.769,1.73,1.00),
                 (-.609,1.071,1.399),(.609,1.071,1.399)],glass,black,root)
    for side in (-1,1):
        sx = lambda x: side*x
        _glass_panel('Car front side window',[(sx(.841),-.93,1.003),(sx(.85),-.015,1.02),
                     (sx(.708),-.015,1.429),(sx(.680),-.429,1.424)],glass,black,root)
        _glass_panel('Car rear side window',[(sx(.85),.063,1.02),(sx(.822),1.43,1.011),
                     (sx(.662),1.021,1.406),(sx(.712),.063,1.434)],glass,black,root)
        for points in [
            [(sx(.824),-1.04,.96),(sx(.785),-.91,1.10),(sx(.657),-.46,1.45)],
            [(sx(.85),.018,1.0),(sx(.72),.018,1.45)],
            [(sx(.84),1.50,.98),(sx(.72),1.27,1.21),(sx(.63),1.05,1.44)]]:
            _curve('Car formed cabin pillar',points,.033,silver,root)
        _curve('Car bright beltline trim',[(sx(.832),-1.04,.98),(sx(.87),-.3,1.005),
                  (sx(.862),.6,1.01),(sx(.80),1.66,.98)],.009,steel,root)
        _curve('Car lower sill',[(sx(.87),-.85,.405),(sx(.90),0,.391),(sx(.87),.86,.41)],.042,silver,root)
        # Fine recessed panel joints and inset door pulls.
        _curve('Car front door shut line',[(sx(.891),-.87,.91),(sx(.909),-.79,.74),
                 (sx(.904),-.74,.48),(sx(.9),-.05,.46),(sx(.914),.015,.73),(sx(.88),.015,.98)],.0035,black,root)
        _curve('Car rear door shut line',[(sx(.88),.055,.98),(sx(.918),.06,.73),
                 (sx(.905),.13,.46),(sx(.905),.72,.47),(sx(.916),.85,.76),(sx(.867),1.40,.97)],.0035,black,root)
        for door_y in (-.19,.82):
            _box('Car inset handle shadow',(sx(.909),door_y,.895),(.015,.18,.041),black,root,.012)
            _box('Car satin door pull',(sx(.926),door_y-.01,.900),(.024,.145,.023),silver,root,.010)
        _curve('Car mirror stalk',[(sx(.82),-.88,1.04),(sx(.97),-.85,1.065)],.023,black,root)
        _box('Car aerodynamic mirror',(sx(1.005),-.86,1.08),(.19,.23,.115),silver,root,.05)
        _box('Car mirror glass',(sx(1.005),-.741,1.085),(.13,.007,.068),glass,root,.023)
    # Hood character lines, split bumper, grille slats and optical lamp internals.
    for side in (-1,1):
        _curve('Car hood pressed crease',[(side*.49,-1.87,.872),(side*.52,-1.48,.937),
                 (side*.58,-1.06,.986)],.004,silver,root)
        _box('Car swept headlamp',(side*.57,-2.082,.757),(.32,.045,.105),headlens,root,.040)
        for optic_x in (.51,.63):
            _cylinder('Car projector headlamp',(side*optic_x,-2.109,.752),.023,.008,lamp,root,axis='Y',vertices=32)
        _curve('Car LED running light',[(side*.71,-2.109,.766),(side*.57,-2.109,.790),
                 (side*.43,-2.109,.790)],.005,lamp,root)
        _box('Car tail lamp',(side*.65,1.991,.835),(.30,.065,.117),red,root,.033)
        _curve('Car tail lamp optic',[(side*.77,2.024,.85),(side*.63,2.034,.85),(side*.53,2.024,.85)],.008,red,root)
    _box('Car lower grille recess',(0,-2.111,.577),(1.13,.032,.145),black,root,.040)
    for i in range(4):
        _box('Car grille horizontal slat',(0,-2.133,.527+i*.028),(1.015,.012,.009),steel,root,.003)
    _box('Car front plate plinth',(0,-2.118,.68),(.41,.024,.095),black,root,.014)
    _box('Car unbranded front registration',(0,-2.137,.686),(.34,.007,.066),lamp,root,.006)
    _box('Car rear bumper valance',(0,2.039,.558),(1.26,.038,.116),black,root,.033)
    _box('Car rear number plate',(0,2.087,.775),(.34,.012,.078),lamp,root,.008)
    _curve('Car rear hatch seam',[(-.76,1.88,.94),(-.75,1.99,.70),(0,2.065,.675),
                 (.75,1.99,.70),(.76,1.88,.94)],.004,black,root)
    _curve('Car windshield wiper',[(-.55,-.978,1.028),(-.10,-.978,1.045),(.25,-.978,1.025)],.008,black,root)
    # Visible interior: dashboard, two seats, headrests, wheel and rear bench.
    _box('Car dashboard',(0,-.84,.974),(1.46,.30,.105),black,root,.055)
    for seat_x in (-.40,.40):
        _box('Car front seat cushion',(seat_x,-.14,.65),(.53,.58,.13),fabric,root,.065)
        seat = _box('Car front seat back',(seat_x,.10,.91),(.51,.135,.56),fabric,root,.065)
        seat.rotation_euler[0] = -.12
        _box('Car seat headrest',(seat_x,.15,1.21),(.29,.115,.17),fabric,root,.045)
    _box('Car rear bench',(0,.95,.77),(1.36,.39,.30),fabric,root,.09)
    _curve('Car steering wheel',[(-.40+.15*math.cos(t*2*math.pi/40),-.69,
                 1.02+.15*math.sin(t*2*math.pi/40)) for t in range(40)],.017,black,root,True)
    _box('Car steering hub',(-.40,-.69,1.02),(.10,.045,.08),black,root,.025)
    _curve('Car roof aerial',[(0,1.00,1.48),(0,1.14,1.67)],.009,black,root)
    _box('Car sealed undertray',(0,0,.401),(1.41,2.73,.075),black,root,.045)
    for axle_y in (-1.28,1.26):
        _cylinder('Car axle and hub carrier',(0,axle_y,.351),.043,1.68,steel,root)
        for side in (-1,1):
            _curve('Car suspension lower arm',[(side*.35,axle_y-.16,.40),
                     (side*.79,axle_y,.34),(side*.35,axle_y+.16,.40)],.023,black,root)
    for number,(x,y) in enumerate(((-.819,-1.28),(.819,-1.28),(-.819,1.26),(.819,1.26))):
        _wheel(x,y,mats,root,number)
    root['component_count'] = len(root.children)
    return root
