"""Persistent warm architectural set and selectively removable cutaway shell.

All dimensions are metres; Z is up. No external textures or asset downloads.
"""
import math
import random
import bpy
from mathutils import Vector


def _material(name, color, roughness=.5, metallic=0, noise=0, scale=8, stretch=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    if noise:
        t = n.new('ShaderNodeTexNoise')
        t.inputs['Scale'].default_value = scale
        t.inputs['Detail'].default_value = 3
        tex = n.new('ShaderNodeTexCoord')
        if stretch:
            mapping = n.new('ShaderNodeVectorMath')
            mapping.operation = 'MULTIPLY'
            mapping.inputs[1].default_value = stretch
            m.node_tree.links.new(tex.outputs['Generated'], mapping.inputs[0])
            m.node_tree.links.new(mapping.outputs[0], t.inputs['Vector'])
        else:
            m.node_tree.links.new(tex.outputs['Object'], t.inputs['Vector'])
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .15
        ramp.color_ramp.elements[0].color = (*(v*.72 for v in color), 1)
        ramp.color_ramp.elements[1].position = .85
        ramp.color_ramp.elements[1].color = (*(min(1,v*1.15) for v in color), 1)
        m.node_tree.links.new(t.outputs['Fac'], ramp.inputs[0])
        m.node_tree.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = noise
        bump.inputs['Distance'].default_value = .025 if name != 'Oak / long grain' else .006
        m.node_tree.links.new(t.outputs['Fac'], bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


def _collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def _move(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def _box(name, center, size, mat, collection, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new('Rounded real edges', 'BEVEL')
        b.width = bevel
        b.segments = 3
        b.affect = 'EDGES'
        o.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return _move(o, collection)


def _sphere(name, loc, scale, mat, col, subdivisions=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    if mat: o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return _move(o,col)


def _beam(name, a, b, radius, mat, col):
    d=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=d.length, location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object
    o.name=name
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    be=o.modifiers.new('End bevel','BEVEL');be.width=.012;be.segments=3
    return _move(o,col)


def _soil_piece(name, bounds, ztop, zbottom, mat, col, rng):
    """Subtly irregular layer perimeter, rather than a stack of uniform boxes."""
    x0,x1,y0,y1=bounds
    perimeter=[]
    steps=12
    for edge in range(4):
        for j in range(steps):
            t=j/steps
            if edge==0: x,y=x0+(x1-x0)*t,y0
            elif edge==1:x,y=x1,y0+(y1-y0)*t
            elif edge==2:x,y=x1-(x1-x0)*t,y1
            else:x,y=x0,y1-(y1-y0)*t
            perimeter.append((x,y))
    verts=[(x,y,zbottom+rng.uniform(-.025,.025)) for x,y in perimeter]
    verts += [(x,y,ztop+rng.uniform(-.025,.025)) for x,y in perimeter]
    nn=len(perimeter)
    faces=[tuple(reversed(range(nn))),tuple(range(nn,2*nn))]
    faces += [(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj)
    b=obj.modifiers.new('Soil edge softness','BEVEL');b.width=.018;b.segments=2
    return obj


def build_environment(materials=None):
    """Return named collections. Hide exterior_only for the explanatory cutaway.

    The same pavers, house and remaining masonry stay in every view. The removable
    shell contains only the two camera-facing soil banks and retaining walls.
    """
    materials = materials or {}
    rng=random.Random(7731)
    architecture=_collection('ENV / cream house and oak details')
    ground=_collection('ENV / driveway and landscape')
    cutaway=_collection('ENV / soil strata and exposed masonry')
    exterior=_collection('ENV / removable front and right shell')
    concrete=materials.get('concrete') or _material('Poured concrete / fine aggregate',(.48,.46,.415),.79,noise=.25,scale=28)
    mortar=_material('Lime mortar',(.44,.43,.395),.9,noise=.17,scale=24)
    blocks=[_material('Masonry / warm gray %02d'%i,(.43+i*.018,.425+i*.018,.39+i*.017),.84,noise=.19,scale=34) for i in range(5)]
    plaster=_material('Warm lime plaster',(.79,.725,.60),.83,noise=.16,scale=21)
    oak=_material('Oak / long grain',(.48,.275,.113),.46,noise=.2,scale=6,stretch=(1,45,10))
    darkoak=_material('Oak end-grain',(.28,.145,.065),.65,noise=.22,scale=7,stretch=(3,28,8))
    roof=_material('Roof / matte charcoal ceramic',(.17,.19,.18),.65,noise=.15,scale=23)
    steel=materials.get('steel') or _material('Architectural brushed zinc',(.28,.31,.31),.31,.75)
    glass=materials.get('glass') or _material('House window glass',(.32,.47,.47),.12,.1)
    gp=glass.node_tree.nodes.get('Principled BSDF')
    gp.inputs['Transmission Weight'].default_value=.55
    gp.inputs['IOR'].default_value=1.45
    black=_material('Rubber gasket and gaps',(.028,.033,.031),.75)
    lawn=_material('Lawn / soft olive',(.21,.31,.095),.95,noise=.32,scale=14)
    leaves=[_material('Foliage %d'%i,(.14+i*.018,.235+i*.018,.085+i*.012),.86,noise=.15,scale=12) for i in range(4)]
    soils=[_material('Soil / '+n,c,.98,noise=.45,scale=s) for n,c,s in [('organic topsoil',(.17,.108,.058),23),('ochre sandy loam',(.32,.205,.112),15),('clay and silt',(.26,.145,.075),20),('deep compact subsoil',(.34,.245,.16),18)]]
    stone_mats=[_material('Embedded aggregate %d'%i,c,.92,noise=.25,scale=17) for i,c in enumerate([(.51,.46,.35),(.35,.32,.27),(.66,.59,.45)])]
    pavers=[_material('Driveway limestone %d'%i,(.50+i*.014,.485+i*.013,.43+i*.012),.8,noise=.25,scale=40) for i in range(5)]
    # Earth banks make a real cavity. Facing banks are removed only in cutaway views.
    banks=[((-4.5,-1.9,-4,5),cutaway,'Left bank'),((-1.9,4.5,2.98,5),cutaway,'Rear bank'),((1.9,4.5,-4,1.2),exterior,'Right bank'),((1.9,4.5,1.2,2.98),cutaway,'Right soil return'),((-1.9,1.9,-4,-2.98),exterior,'Front bank')]
    levels=[-.18,-.35,-1.25,-2.45,-4.05]
    for bounds,col,label in banks:
        for i in range(4):
            _soil_piece(label+' / '+str(i),bounds,levels[i],levels[i+1],soils[i],col,rng)
    # A persistent basal earth slice sits directly below the raft and remains
    # visible when the two camera-facing shell walls are removed. Its front cut
    # plane aligns with the foundation, keeping the soil inside a portrait crop.
    for i,(top,bottom) in enumerate([(-4.025,-4.34),(-4.34,-4.85)]):
        _soil_piece('Basal earth / visible stratum '+str(i),(-1.94,4.5,-2.99,3.0),top,bottom,soils[1+i],cutaway,rng)
        _soil_piece('Basal earth / left bank '+str(i),(-4.5,-1.94,-4,5),top,bottom,soils[1+i],cutaway,rng)
    for i in range(92):
        x=rng.uniform(-1.88,4.43);z=rng.uniform(-4.78,-4.09)
        r=rng.uniform(.022,.07)
        o=_sphere('Basal earth / cross-section pebble',(x,-3.005,z),(r,r*.3,r*.57),rng.choice(stone_mats),cutaway)
        o.rotation_euler[1]=rng.uniform(-.8,.8)
    # The right return exposes horizontal strata at its forward cut face.
    for i in range(95):
        x=rng.uniform(1.96,4.44);z=rng.uniform(-3.97,-.15)
        r=rng.uniform(.023,.08)
        o=_sphere('Right return / embedded pebble',(x,1.19,z),(r,r*.32,r*.64),rng.choice(stone_mats),cutaway)
        o.rotation_euler[1]=rng.uniform(-1,1)
    # Pale pebbles embedded in the exposed cut plane and inner soil walls.
    for i in range(105):
        x=rng.uniform(-4.45,-1.96);z=rng.uniform(-3.96,-.12)
        r=rng.uniform(.025,.10)
        o=_sphere('Cut soil / embedded stone', (x,-4.015,z),(r,r*.38,r*.62),rng.choice(stone_mats),cutaway)
        o.rotation_euler=(rng.random(),rng.random(),rng.random()*6)
    for i in range(80):
        y=rng.uniform(-3.9,4.7);z=rng.uniform(-3.9,-.15);r=rng.uniform(.03,.085)
        _sphere('Soil cavity / aggregate',(-1.885,y,z),(r*.3,r,r*.7),rng.choice(stone_mats),cutaway)
    # Chamber slab and separate footing reveal mass and believable wall joints.
    slab=_box('Chamber / raft foundation',(0,0,-3.83),(3.82,5.97,.36),concrete,cutaway,.065)
    _box('Chamber / screed floor',(0,0,-3.637),(3.52,5.67,.065),concrete,cutaway,.018)
    _box('Left wall / footing',(-1.70,0,-3.56),(.48,5.95,.20),concrete,cutaway,.025)
    _box('Rear wall / footing',(0,2.76,-3.56),(3.82,.5,.20),concrete,cutaway,.025)
    # Individual staggered concrete masonry units and recessed mortar joints.
    def wall_x(x,col,ymin=-2.84,ymax=2.84):
        mid=(ymin+ymax)/2
        _box('Wall / mortar backing',(x,mid,-1.85),(.24,ymax-ymin,3.5),mortar,col,.015)
        for row in range(9):
            z=-3.42+row*.385
            for k in range(9):
                y=-2.84+k*.70+(row%2)*.35
                lo=max(ymin,y);hi=min(ymax,y+.68)
                if hi-lo>.08:_box('Masonry / stretcher',(x+.012,(lo+hi)/2,z),(.27,hi-lo,.365),rng.choice(blocks),col,.014)
        _box('Wall / concrete coping',(x,mid,-.035),(.39,ymax-ymin+.08,.16),concrete,col,.022)
    def wall_y(y,col):
        _box('Wall / mortar backing',(0,y,-1.85),(3.52,.24,3.5),mortar,col,.015)
        for row in range(9):
            z=-3.42+row*.385
            for k in range(6):
                x=-1.76+k*.70+(row%2)*.35
                lo=max(-1.76,x);hi=min(1.76,x+.68)
                if hi-lo>.08:_box('Masonry / stretcher',((lo+hi)/2,y-.012,z),(hi-lo,.27,.365),rng.choice(blocks),col,.014)
        _box('Wall / concrete coping',(0,y,-.035),(3.73,.39,.16),concrete,col,.022)
    wall_x(-1.70,cutaway);wall_y(2.76,cutaway)
    _box('Left masonry / finished cut end',(-1.70,-2.855,-1.85),(.30,.065,3.5),concrete,cutaway,.008)
    wall_x(1.70,exterior,ymax=1.2);wall_y(-2.76,exterior)
    wall_x(1.70,cutaway,ymin=1.2)
    _box('Right return / finished cut end',(1.70,1.19,-1.85),(.30,.065,3.5),concrete,cutaway,.008)
    # A continuous bedding ring supports every sett; boundary stones are cut to
    # the rectangular opening instead of leaving arbitrary grid-sized holes.
    for loc,size in [((-2.52,.1,-.105),(2.02,8.2,.13)),((2.52,.1,-.105),(2.02,8.2,.13)),((0,-3.35,-.105),(3.04,1.5,.13)),((0,3.40,-.105),(3.04,1.6,.13))]:
        _box('Drive / concrete bedding ring',loc,size,concrete,ground,.018)
    for row in range(13):
        y=-3.9+row*.63
        for k in range(12):
            x=-3.50+k*.68+(row%2)*.34
            x0=max(-3.52,x-.33);x1=min(3.52,x+.33)
            y0=y-.305;y1=y+.305
            if x1-x0<.04:continue
            pieces=[]
            if x1<=-1.52 or x0>=1.52 or y1<=-2.60 or y0>=2.60:
                pieces=[(x0,x1,y0,y1)]
            else:
                if x0 < -1.52:pieces.append((x0,-1.53,y0,y1))
                if x1 > 1.52:pieces.append((1.53,x1,y0,y1))
                mx0=max(x0,-1.52);mx1=min(x1,1.52)
                if y0 < -2.60:pieces.append((mx0,mx1,y0,-2.61))
                if y1 > 2.60:pieces.append((mx0,mx1,2.61,y1))
            for xa,xb,ya,yb in pieces:
                if xb-xa>.035 and yb-ya>.035:
                    _box('Drive / limestone sett',((xa+xb)/2,(ya+yb)/2,-.06),(xb-xa,yb-ya,.12),rng.choice(pavers),ground,.012)
    for x in (-3.95,3.95):
        _box('Garden / turf bed',(x,.3,-.06),(.95,8.6,.18),lawn,ground,.09)
        # Varied low blades break the lawn silhouette without a particle dependency.
        verts=[];faces=[]
        for i in range(550):
            xx=x+rng.uniform(-.44,.44);yy=rng.uniform(-3.9,4.45);zz=.025
            h=rng.uniform(.035,.095);w=.012
            a=len(verts);verts.extend([(xx-w,yy,zz),(xx+w,yy,zz),(xx+rng.uniform(-.025,.025),yy+.015,zz+h)]);faces.append((a,a+1,a+2))
        me=bpy.data.meshes.new('Individual grass blades');me.from_pydata(verts,[],faces);me.materials.append(lawn)
        ob=bpy.data.objects.new('Garden / fine grass',me);ground.objects.link(ob)
        _box('Garden / curb',(x+(.54 if x<0 else -.54),.2,-.015),(.12,8.6,.18),concrete,ground,.035)
    # Warm architectural backdrop with a true recessed window opening assembled from piers.
    # Window opening x=-.7..1.9 z=.9..2.7; facade front y=4.2.
    _box('House / left plaster pier',(-2.60,4.48,1.8),(3.8,.56,3.6),plaster,architecture,.055)
    _box('House / right plaster pier',(3.20,4.48,1.8),(2.6,.56,3.6),plaster,architecture,.055)
    _box('House / window apron',(.60,4.48,.44),(2.6,.56,.88),plaster,architecture,.035)
    _box('House / window lintel',(.60,4.48,3.17),(2.6,.56,.86),plaster,architecture,.035)
    _box('House / stone plinth',(0,4.14,.15),(9.0,.22,.30),concrete,architecture,.03)
    for x in (-.75,1.95):_box('Window / oak jamb',(x,4.105,1.8),(.15,.20,1.98),oak,architecture,.018)
    for z in (.83,2.77):_box('Window / oak head and sill',(.6,4.105,z),(2.84,.24,.14),oak,architecture,.02)
    _box('Window / deep oak sill',(.6,3.99,.83),(2.98,.46,.12),oak,architecture,.024)
    _box('Window / black gasket',(.6,4.19,1.8),(2.62,.05,1.82),black,architecture,.01)
    _box('Window / glazing',(.6,4.14,1.8),(2.56,.035,1.77),glass,architecture,.01)
    _box('Window / central oak mullion',(.6,4.085,1.8),(.075,.12,1.8),oak,architecture,.014)
    _box('Window / horizontal oak rail',(.6,4.08,1.97),(2.61,.12,.065),oak,architecture,.012)
    # A quiet interior is visible behind the glazing, rather than a flat picture.
    _box('Window / interior shadow',(.6,4.46,1.8),(2.6,.04,1.8),darkoak,architecture,0)
    for x in (-.40,.0,1.25,1.65):
        _box('Window / linen curtain fold',(x,4.23,1.83),(.16,.09,1.65),plaster,architecture,.055)
    # Oak front door with separate boards, inset glass and round metal handle.
    _box('Door / recessed surround',(-2.68,4.12,1.20),(1.20,.15,2.4),darkoak,architecture,.025)
    for i in range(7):
        _box('Door / vertical oak board',(-3.18+i*.164,4.01,1.20),(.157,.10,2.30),oak,architecture,.012)
    _box('Door / inset upper pane',(-2.69,3.944,1.73),(.68,.026,.70),glass,architecture,.025)
    _beam('Door / handle',(-2.29,3.84,1.02),(-2.29,3.84,1.27),.022,steel,architecture)
    _box('Door / threshold',(-2.68,3.87,.035),(1.35,.58,.10),concrete,architecture,.025)
    # Shallow pitched roof and a modeled gutter line complete the upper edge.
    for side in (-1,1):
        o=_box('House / roof plane',(side*2.33,4.55,3.80),(4.82,1.48,.12),roof,architecture,.03)
        o.rotation_euler[1]=side*math.radians(9)
    _box('House / oak eave',(0,3.91,3.56),(9.45,.22,.18),oak,architecture,.025)
    _beam('House / front rain gutter',(-4.62,3.77,3.58),(4.62,3.77,3.58),.065,steel,architecture)
    _beam('House / downpipe',(4.32,3.78,3.56),(4.32,3.78,.13),.05,steel,architecture)
    # Small exterior sconce and its fixture.
    _box('House / sconce mount',(-1.82,4.04,2.20),(.18,.10,.31),steel,architecture,.025)
    _box('House / opal sconce',(-1.82,3.96,2.20),(.11,.10,.22),plaster,architecture,.025)
    # Two organically branched garden shrubs provide a soft silhouette at the edges.
    for tx,ty in [(-4.02,3.45),(4.0,4.3)]:
        _beam('Garden / trunk',(tx,ty,0),(tx+.06,ty,1.55),.065,darkoak,ground)
        for j in range(8):
            a=j*2.399;rad=rng.uniform(.18,.50)
            end=(tx+math.cos(a)*rad,ty+math.sin(a)*rad,1.2+rng.random()*.7)
            _beam('Garden / branch',(tx,ty,.70),end,.025,darkoak,ground)
            _sphere('Garden / leaf crown',end,(.42,.35,.42),rng.choice(leaves),ground,3)
    return {'architecture':architecture,'ground':ground,'cutaway':cutaway,
            'exterior_only':exterior,'floor':slab,
            'materials':{'concrete':concrete,'oak':oak,'plaster':plaster,'soil':soils,'pavers':pavers}}
