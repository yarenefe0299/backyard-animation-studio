"""Reusable modeled story props for the hidden-garage scene.

All meshes use the same metre/Z-up coordinate system as the master. Visibility is
controlled by the caller: Blender's empty-object visibility does not hide children,
so flat ``*_parts`` groups are returned alongside movable assembly roots.
"""
import math
import random

import bpy
from mathutils import Vector
from mathutils.geometry import interpolate_bezier

from geometry import box, cylinder, empty, pipe
from materials import surface


def _put(obj, collection=None, role=None):
    if collection:
        for previous in list(obj.users_collection):
            previous.objects.unlink(obj)
        collection.objects.link(obj)
    if role:
        obj['story_role'] = role
    return obj


def _sphere(name, position, size, material, collection=None, role=None, subdivisions=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    obj.data.materials.append(material)
    for face in obj.data.polygons:
        face.use_smooth = True
    return _put(obj, collection, role)


def _children(root):
    return [root, *root.children_recursive]


def _hide(objects):
    for obj in objects:
        obj.hide_render = True
        obj.hide_viewport = True


def _wheel_pivots(car):
    """Make tires, treads, spokes and rotors roll about their actual hub centres.

    The body builder stores several wheel meshes at object origin with absolute
    local vertices; grouping by object.location would incorrectly select the front
    left wheel for those meshes. Use each modeled bound-box centre instead.
    """
    bpy.context.view_layer.update()
    centres = [Vector((x, y, .351)) for x, y in
               [(-.819, -1.28), (.819, -1.28), (-.819, 1.26), (.819, 1.26)]]
    pivots = [empty('Car rolling wheel pivot %d' % i, tuple(co), car)
              for i, co in enumerate(centres)]
    for pivot in pivots:
        pivot['wheel_radius_m'] = .351
        pivot['story_role'] = 'rolling_wheel'
    bpy.context.view_layer.update()
    rotating = ('Car tire ', 'Car alloy barrel ', 'Car ventilated brake rotor ',
                'Car brake drilling', 'Car forged alloy spoke', 'Car hub cap ',
                'Car wheel lug', 'Car directional tread')
    inverse = car.matrix_world.inverted()
    for obj in list(car.children):
        if not obj.name.startswith(rotating):
            continue
        centre = sum((inverse @ obj.matrix_world @ Vector(v) for v in obj.bound_box), Vector()) / 8
        number = min(range(4), key=lambda i: (centre - centres[i]).length_squared)
        world = obj.matrix_world.copy()
        obj.parent = pivots[number]
        obj.matrix_world = world
    bpy.context.view_layer.update()
    for pivot in pivots:
        if len(pivot.children) < 70:
            raise RuntimeError('Incomplete modeled wheel grouping: ' + pivot.name)
    return pivots


def add_paving_rim(environment,materials):
    """Narrow stationary coping leaves an intentional 10–15 mm deck joint."""
    paving=materials.get('pavers',[materials['concrete']])
    result=[]
    for sign in (-1,1):
        result.append(_put(box('Drive / precision opening trim',(sign*1.49,0,-.06),(.06,5.06,.12),paving[2%len(paving)],bevel=.006),environment['ground'],'paving_rim'))
        result.append(_put(box('Drive / precision opening trim',(0,sign*2.565,-.06),(2.92,.07,.12),paving[2%len(paving)],bevel=.006),environment['ground'],'paving_rim'))
    for x in [-1.49,1.49]:
        for y in [-2.565,2.565]:
            result.append(_put(box('Drive / precision trim corner',(x,y,-.06),(.06,.07,.12),paving[2%len(paving)],bevel=.006),environment['ground'],'paving_rim'))
    return result


def _road(environment, materials):
    add_paving_rim(environment,materials)
    col = environment['exterior_only']
    paving = materials.get('pavers', [materials['concrete']])
    lawn = surface('Approach lawn / olive blades', (.19, .30, .085), .95, noise=.006, scale=18)
    earth = materials.get('soil', [materials['concrete']])[0]
    objects = []
    def add(ob):
        objects.append(_put(ob, col, 'approach_road'))
        return ob
    add(box('Approach / uncut ground apron', (0,-3,-.22), (40,50,.10), lawn, bevel=.03))
    add(box('Approach / continuous mineral bed', (0, -7.67, -.16), (3.55, 7.25, .22), materials['concrete'], bevel=.025))
    add(box('Approach / earth under paving', (0, -7.67, -.36), (5.55, 7.25, .24), earth, bevel=.035))
    # Keep the same stagger and stone dimensions as the stationary driveway.
    for row in range(-11, 0):
        y = -3.9 + row * .63
        for k in range(12):
            x = -3.50 + k * .68 + (row % 2) * .34
            lo, hi = max(-1.72, x-.33), min(1.72, x+.33)
            if hi-lo > .035:
                add(box('Approach / limestone running-bond sett', ((lo+hi)/2, y, -.06),
                        (hi-lo, .61, .12), paving[(row+k) % len(paving)], bevel=.012))
    for sign in (-1, 1):
        add(box('Approach / lawn shoulder', (sign*2.19, -7.67, -.065), (.88, 7.25, .17), lawn, bevel=.055))
        for i in range(12):
            add(box('Approach / cut limestone curb', (sign*1.79, -11.0+(i+.5)*.59, .015),
                    (.11, .57, .12), paving[i % len(paving)], bevel=.018))
    # A shared crossed-leaf mesh makes the shoulder dimensional without hundreds
    # of expensive unique mesh datablocks or billboard texture assets.
    mesh = bpy.data.meshes.new('Approach / modeled grass blade cluster')
    mesh.from_pydata([(-.013,0,0),(.013,0,0),(.002,0,.075),
                     (0,-.013,0),(0,.013,0),(0,.003,.065)], [], [(0,1,2),(3,4,5)])
    mesh.materials.append(lawn)
    rng = random.Random(8702)
    for i in range(145):
        ob = bpy.data.objects.new('Approach / grass cluster', mesh)
        col.objects.link(ob)
        ob.location = (rng.choice((-1,1))*rng.uniform(1.87,2.55), rng.uniform(-11.2,-4.15), .02)
        ob.rotation_euler.z = rng.random()*math.tau
        ob.scale *= rng.uniform(.5,1.25)
        ob['story_role'] = 'approach_road'
        objects.append(ob)
    return objects


def _cover(materials):
    paving = materials.get('pavers', [materials['concrete']])
    result = []
    for sign in (-1, 1):
        centre = sign*.725
        root = empty('Concealing driveway roof / '+('left' if sign < 0 else 'right'), (centre,0,0))
        root['closed_x'] = centre
        root['open_x'] = sign*3.20
        root['slide_z'] = -.13
        root['story_role'] = 'concealing_roof'
        box('Roof / reinforced sliding pan', (0,0,-.15), (1.45,5.03,.24), materials['concrete'], root, .025)
        for x in (-.70,.70):
            box('Roof / steel edge bearer', (x,0,-.205), (.045,4.99,.07), materials['steel'], root, .008)
        for y in (-2.47,2.47):
            box('Roof / steel end bearer', (0,y,-.205), (1.43,.045,.07), materials['steel'], root, .008)
        world_lo, world_hi = ((-1.45,0) if sign < 0 else (0,1.45))
        for row in range(13):
            y = -3.9 + row*.63
            ya, yb = max(-2.515,y-.305), min(2.515,y+.305)
            if yb-ya <= .035:
                continue
            for k in range(12):
                x = -3.50+k*.68+(row%2)*.34
                xa, xb = max(world_lo,x-.33), min(world_hi,x+.33)
                if xb-xa > .035:
                    box('Roof / precisely matching paving', ((xa+xb)/2-centre,(ya+yb)/2,-.025),
                        (xb-xa,yb-ya,.055), paving[(row+k)%len(paving)], root, .008)
        for y in (-2.39,2.39):
            cylinder('Roof / guide roller axle', (-.61,y,-.24),(.61,y,-.24),.025,materials['steel'],root)
        for obj in _children(root):
            obj['story_role'] = 'concealing_roof'
        _hide(_children(root))
        result.append(root)
    return result


def _crate(materials):
    oak = materials.get('oak') or surface('Crate / pale pine', (.48,.29,.13), .6, noise=.002, scale=12)
    root = empty('Safety demonstration / wooden crate', (1.24,-1.82,.003))
    for axis in (0,1):
        for sign in (-1,1):
            for row in range(4):
                loc = [0,0,.075+row*.13]
                loc[axis] = sign*.275
                dims = [.56,.045,.115]
                if axis == 0:
                    dims = [.045,.56,.115]
                box('Crate / individual pine side slat', loc, dims, oak, root, .009)
    for x in (-.24,.24):
        for y in (-.24,.24):
            box('Crate / corner post', (x,y,.275), (.065,.065,.55),oak,root,.012)
            for z in (.10,.43):
                cylinder('Crate / flush nail head', (x,y-.034,z),(x,y-.038,z),.009,materials['steel'],root,16)
    for i in range(5):
        box('Crate / floor board',(-.22+i*.11,0,.035),(.105,.50,.055),oak,root,.008)
    # Slotted handle plates reinforce the readable silhouette at sensor scale.
    for sign in (-1,1):
        box('Crate / handle recess',(0,sign*.301,.43),(.21,.012,.040),materials['black'],root,.018)
    for obj in _children(root):
        obj['story_role'] = 'safety_crate'
    _hide(_children(root))
    return root


def _safety(materials):
    amber = surface('Safety beam / soft amber',(.65,.27,.025),.25)
    p = amber.node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value = (1,.30,.025,1)
    p.inputs['Emission Strength'].default_value = .9
    red = surface('Safety stop / ruby indicator',(.5,.018,.012),.22)
    p = red.node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value = (.8,.015,.008,1)
    p.inputs['Emission Strength'].default_value = .7
    parts=[]
    for sign in (-1,1):
        parts.append(box('Photoelectric sensor / mounting foot',(sign*1.68,-1.82,.035),(.24,.23,.07),materials['steel'],bevel=.018))
        parts.append(box('Photoelectric sensor / upright bracket',(sign*1.60,-1.82,.19),(.055,.18,.32),materials['steel'],bevel=.012))
        parts.append(box('Photoelectric sensor / sealed housing',(sign*1.51,-1.82,.34),(.15,.17,.17),materials['black'],bevel=.035))
        parts.append(cylinder('Photoelectric sensor / optical lens',(sign*1.46,-1.82,.34),(sign*1.43,-1.82,.34),.045,materials['glass']))
        for dx in (-.065,.065):
            parts.append(cylinder('Photoelectric sensor / mounting bolt',(sign*1.68+dx,-1.82,.073),(sign*1.68+dx,-1.82,.086),.013,materials['steel'],vertices=6))
    beam = cylinder('Safety beam / active light path',(-1.43,-1.82,.34),(1.43,-1.82,.34),.009,amber)
    parts.append(cylinder('Safety indicator / brushed collar',(1.68,-1.82,.40),(1.68,-1.82,.45),.057,materials['steel']))
    warning = _sphere('Safety indicator / red stop lens',(1.68,-1.82,.48),(.055,.055,.053),red)
    for obj in [*parts,beam,warning]:
        obj['story_role']='sensor_system'
    _hide([*parts,beam,warning])
    return parts,beam,warning


def _construction(materials):
    guide=[]
    corners=[(x,y,z) for z in (-3.60,-.08) for y in (-2.53,2.53) for x in (-1.47,1.47)]
    for a,b in [(0,1),(1,3),(3,2),(2,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,6),(3,7)]:
        guide.append(cylinder('Excavation / translucent construction edge',corners[a],corners[b],.017,materials['ghost']))
    rng=random.Random(6732)
    soils=materials.get('soil',[materials['concrete']])
    clods=[]
    for i in range(24):
        loc=(rng.uniform(1.44,1.65),rng.uniform(-2.25,2.25),rng.uniform(-2.8,-.25))
        size=(rng.uniform(.06,.15),rng.uniform(.06,.16),rng.uniform(.06,.18))
        ob=_sphere('Soil failure / modeled earth clod',loc,size,soils[i%len(soils)],role='soil_clod',subdivisions=2)
        ob.rotation_euler=(rng.random()*3,rng.random()*3,rng.random()*3)
        ob['rest_location']=list(loc)
        ob['phase']=rng.random()
        clods.append(ob)
    fill=[]
    for index,(top,bottom) in enumerate([(-.18,-.38),(-.38,-1.25),(-1.25,-2.4),(-2.4,-3.58)]):
        vertices=[(-1.47,-2.53,bottom),(1.47,-2.53,bottom),(1.47,2.53,bottom),(-1.47,2.53,bottom),
                  (-1.47,-2.53,top),(1.47,-2.53,top),(1.47,2.53,top),(-1.47,2.53,top)]
        mesh=bpy.data.meshes.new('Excavation / retained soil layer')
        mesh.from_pydata(vertices,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        mesh.materials.append(soils[index%len(soils)])
        ob=bpy.data.objects.new('Excavation / removable earth layer %d'%index,mesh)
        bpy.context.collection.objects.link(ob)
        mod=ob.modifiers.new('Earth section edge softness','BEVEL');mod.width=.018;mod.segments=2
        ob['story_role']='excavation_fill'
        fill.append(ob)
    _hide([*guide,*clods,*fill])
    return guide,clods,fill


def _weather(materials):
    water=surface('Rainwater / translucent pale blue',(.14,.37,.50),.18)
    nodes=water.node_tree.nodes
    p=nodes.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value=.70
    p.inputs['IOR'].default_value=1.333
    n=nodes.new('ShaderNodeTexNoise');n.name='Water surface ripple';n.inputs['Scale'].default_value=13
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.012
    water.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height'])
    water.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
    volume=box('Rainwater / accumulating chamber volume',(0,0,-3.60),(3.10,5.10,1),water,bevel=.012)
    # The object's local origin is the basin floor, so scale.z is water depth in m.
    for vert in volume.data.vertices:
        vert.co.z+=.5
    volume.scale.z=.08
    volume['basin_floor_z']=-3.60
    volume['story_role']='rainwater'
    rain=[]
    rng=random.Random(427)
    template=_sphere('Rain / master modeled droplet',(0,0,2),(.013,.013,.11),water,subdivisions=1)
    template.data.name='Rain / shared droplet mesh'
    for i in range(72):
        ob=template if i==0 else bpy.data.objects.new('Rain / falling droplet',template.data)
        if i:
            bpy.context.collection.objects.link(ob)
            ob.scale=template.scale
        ob.location=(rng.uniform(-2.7,2.7),rng.uniform(-3.3,3.3),rng.uniform(.1,6))
        ob['phase']=rng.random()
        ob['story_role']='rainfall'
        rain.append(ob)
    _hide([volume,*rain])
    return volume,rain


def _drainage(materials):
    source=next((obj for obj in bpy.context.scene.objects
                 if obj.type=='CURVE' and obj.name.startswith('Sump discharge pipe')),None)
    if source is None:
        raise RuntimeError('The drainage diagnostic requires the modeled sump discharge pipe')
    # Copy the actual route and control handles, including the constrained riser.
    # A second independently authored point list can drift inside walls or deck.
    curve=source.data.copy();curve.name='Drainage / actual discharge route copy'
    curve.materials.clear();curve.materials.append(materials['ghost']);curve.bevel_depth=.058
    line=bpy.data.objects.new('Drainage / transparent discharge diagnostic',curve)
    bpy.context.collection.objects.link(line);line.matrix_world=source.matrix_world.copy()
    bpy.context.view_layer.update()
    bezier=line.data.splines[0].bezier_points
    path=[]
    for a,b in zip(bezier,list(bezier)[1:]):
        path.extend(tuple(v) for v in interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,32)[:-1])
    path.append(tuple(bezier[-1].co))
    tracers=[]
    for i in range(16):
        obj=_sphere('Drainage / moving water tracer',path[0],(.026,.026,.026),materials['fluid'],role='drainage_tracer',subdivisions=1)
        tracers.append((obj,path,i/16))
    objects=[line,*[v[0] for v in tracers]]
    _hide(objects)
    return objects,tracers


def _annulus(name, location, outer, inner, thickness, material, parent=None):
    """A genuinely open, machined flange; the fluid bore stays unobstructed."""
    steps=48
    vertices=[]
    for radius,z in [(outer,-thickness/2),(inner,-thickness/2),
                     (outer,thickness/2),(inner,thickness/2)]:
        vertices.extend((radius*math.cos(i*math.tau/steps),radius*math.sin(i*math.tau/steps),z) for i in range(steps))
    faces=[]
    for i in range(steps):
        j=(i+1)%steps
        faces.extend([(i,steps+i,steps+j,j),(2*steps+i,2*steps+j,3*steps+j,3*steps+i),
                      (i,j,2*steps+j,2*steps+i),(steps+i,3*steps+i,3*steps+j,steps+j)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.materials.append(material)
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    obj.location=location;obj.parent=parent
    bevel=obj.modifiers.new('Turned flange edge radius','BEVEL');bevel.width=.003;bevel.segments=3
    obj.modifiers.new('Machined face normals','WEIGHTED_NORMAL')
    return obj


def _discharge_axis(height):
    """Locate the valve on the actual pipe spline rather than an approximate box."""
    line=next((obj for obj in bpy.context.scene.objects if obj.name.startswith('Drainage / transparent discharge diagnostic')),None)
    if line:
        bpy.context.view_layer.update()
        points=list(line.data.splines[0].bezier_points)
        samples=[]
        for first,last in zip(points,points[1:]):
            samples.extend(line.matrix_world @ value for value in interpolate_bezier(first.co,first.handle_right,last.handle_left,last.co,129))
        for first,last in zip(samples,samples[1:]):
            if first.z <= height <= last.z and last.z-first.z > 1e-8:
                amount=(height-first.z)/(last.z-first.z)
                return first+(last-first)*amount,(last-first).normalized()
    return Vector((1.1,2.285,height)),Vector((0,.05,1)).normalized()


def _sump_hardware(materials):
    """Submersible pump, strainer, power cord and an operating swing check valve.

    The valve sits below the lowered carriage envelope. Its flap rotates around
    its own hinge; +X rotation opens it in the upward discharge-flow direction.
    """
    steel,blue,black=materials['steel'],materials['blue'],materials['black']
    pump=empty('Drainage pump / complete submersible assembly',(.7,1.8,-3.60))
    for i in range(3):
        angle=i*math.tau/3
        foot=box('Drainage pump / rubber isolation foot',(.155*math.cos(angle),.155*math.sin(angle),.022),
                 (.09,.075,.044),materials['rubber'],pump,.012)
        foot.rotation_euler.z=angle
    _annulus('Drainage pump / intake base ring',(0,0,.053),.181,.12,.026,steel,pump)
    for i in range(16):
        angle=i*math.tau/16;x=.162*math.cos(angle);y=.162*math.sin(angle)
        cylinder('Drainage pump / open strainer bar',(x,y,.062),(x,y,.15),.007,steel,pump,16)
    cylinder('Drainage pump / cast volute housing',(0,0,.135),(0,0,.19),.177,blue,pump)
    cylinder('Drainage pump / sealed blue motor housing',(0,0,.18),(0,0,.37),.143,blue,pump)
    for z in (.20,.34):
        _annulus('Drainage pump / motor body seal',(0,0,z),.147,.135,.012,black,pump)
    cylinder('Drainage pump / stainless motor cap',(0,0,.365),(0,0,.403),.15,steel,pump)
    cap=_sphere('Drainage pump / domed cap',(0,0,.395),(.145,.145,.036),steel)
    cap.parent=pump
    for i in range(4):
        angle=math.pi/4+i*math.pi/2;x=.112*math.cos(angle);y=.112*math.sin(angle)
        cylinder('Drainage pump / cap fastener',(x,y,.408),(x,y,.425),.011,steel,pump,6)
    pipe('Drainage pump / lifting handle',[(-.075,0,.413),(-.075,0,.49),(.075,0,.49),(.075,0,.413)],.014,steel,pump)
    # This elbow meets the existing diagnostic discharge point exactly.
    pipe('Drainage pump / connected outlet elbow',[(0,.14,.13),(0,.22,.08),(0,.25,.02)],.045,steel,pump)
    cylinder('Drainage pump / threaded outlet collar',(0,.13,.13),(0,.19,.13),.060,materials['brass'],pump)
    pipe('Drainage pump / sealed power lead',[(.04,.04,.43),(.14,.16,.49),(.36,.47,.49),(.70,.78,.76)],.010,black,pump)
    box('Drainage pump / wall electrical junction',(.70,.80,.76),(.13,.07,.16),black,pump,.018)
    for x in (.66,.74):
        for z in (.71,.81):
            cylinder('Drainage pump / junction cover screw',(x,.766,z),(x,.759,z),.005,steel,pump,12)
    box('Drainage pump / tethered level switch',(.215,.02,.18),(.08,.14,.065),black,pump,.025)
    pipe('Drainage pump / float switch lead',[(.11,.03,.38),(.24,.02,.31),(.215,.02,.20)],.006,black,pump)
    for obj in _children(pump):obj['story_role']='sump_pump_part'
    pump['story_role']='sump_pump'
    pump['floor_z']=-3.60

    centre,direction=_discharge_axis(-3.18)
    body=empty('Drainage check valve / aligned housing',tuple(centre))
    body.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    cylinder('Drainage check valve / transparent inspection body',(0,0,-.145),(0,0,.145),.097,materials['ghost'],body)
    for z in (-.165,.165):
        _annulus('Drainage check valve / open stainless flange',(0,0,z),.119,.053,.026,steel,body)
        _annulus('Drainage check valve / dark flange gasket',(0,0,z*.89),.103,.052,.014,black,body)
    for i in range(6):
        angle=math.pi/6+i*math.tau/6;x=.102*math.cos(angle);y=.102*math.sin(angle)
        cylinder('Drainage check valve / housing tie bolt',(x,y,-.19),(x,y,.19),.006,steel,body,16)
        for z in (-.187,.187):
            cylinder('Drainage check valve / hexagonal flange nut',(x,y,z-.009),(x,y,z+.009),.012,steel,body,6)
    _annulus('Drainage check valve / machined valve seat',(0,0,-.008),.079,.059,.013,materials['brass'],body)
    flap=empty('Drainage check valve / hinged nonreturn flap',(0,-.064,0),body)
    disc=cylinder('Drainage check valve / swing disc',(0,.064,-.005),(0,.064,.005),.064,materials['brass'],flap)
    cylinder('Drainage check valve / horizontal hinge pin',(-.081,-.064,0),(.081,-.064,0),.010,steel,body)
    for x in (-.074,.074):
        box('Drainage check valve / hinge support',(x,-.064,-.015),(.024,.026,.056),steel,body,.007)
    for obj in _children(body):obj['story_role']='check_valve_part'
    body['story_role']='check_valve_housing'
    flap['story_role']='check_valve_flap'
    flap['open_angle_rad']=math.radians(70)
    disc['story_role']='check_valve_disc'
    parts=_children(pump)+_children(body)
    _hide(parts)
    return parts,flap,_children(body)


def augment_garage(environment, mechanism, car, materials):
    """Build all story props once and return animation-friendly assemblies.

    ``cover_left/right.location.x``: closed ±.725, parked open ±3.2.
    Covers slide at root z=-.13 under neighbouring pavers, then rise flush.
    ``water.scale.z``: depth in metres above basin floor z=-3.60.
    ``wheel_pivots.rotation_euler.x``: rolling angle, wheel radius .351m.
    Root assemblies are accompanied by flat descendant lists for visibility keys.
    """
    road=_road(environment,materials)
    covers=_cover(materials)
    crate=_crate(materials)
    sensors,beam,warning=_safety(materials)
    guide,clods,fill=_construction(materials)
    water,rain=_weather(materials)
    wheels=_wheel_pivots(car)
    drainage,drain_pulses=_drainage(materials)
    drainage_parts,check_valve,check_valve_parts=_sump_hardware(materials)
    return {
        'cover_left':covers[0],'cover_right':covers[1],
        'cover_parts':_children(covers[0])+_children(covers[1]),
        'crate':crate,'crate_parts':_children(crate),
        'water':water,'rain':rain,'clods':clods,'guide':guide,
        'excavation_fill':fill,
        'sensors':sensors,'beam':beam,'warning':warning,
        'road':road,'wheel_pivots':wheels,
        'drainage_overlay':drainage,'drain_pulses':drain_pulses,
        'drainage_parts':drainage_parts,'check_valve':check_valve,'check_valve_parts':check_valve_parts,
    }
