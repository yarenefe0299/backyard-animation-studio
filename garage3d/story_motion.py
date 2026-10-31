"""Narrative choreography sampled into portable Blender keyframes."""
import math
import bpy
from mathutils import Vector
from geometry import empty, box, cylinder
from mechanism import pose,point_on_polyline


def ease(t):
    t=max(0.,min(1.,t))
    return t*t*t*(t*(t*6-15)+10)


def mix(a,b,t):
    return tuple(x+(y-x)*t for x,y in zip(a,b))


def camera_pose(camera,position,target,scale):
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=scale


def descendants(root):
    return [root,*root.children_recursive]


def parent_world(objects,root):
    bpy.context.view_layer.update()
    for ob in objects:
        matrix=ob.matrix_world.copy()
        ob.parent=root
        ob.matrix_world=matrix


def keyed_visible(objects,visible,frame,cache):
    for ob in objects:
        state=not visible
        if cache.get(ob.name) != state:
            if frame>1:
                ob.keyframe_insert(data_path='hide_render',frame=frame-1)
            ob.hide_render=state
            # Viewport visibility is not keyed: hide_viewport prevents dependency
            # graph updates in some builds. Keep all meshes evaluable for checks.
            ob.hide_viewport=False
            ob.keyframe_insert(data_path='hide_render',frame=frame)
            cache[ob.name]=state


def prepare_groups(env,mech,car,props,mats):
    wallprefix=('Chamber /','Wall /','Masonry /','Left wall /','Rear wall /','Left masonry /','Right return /')
    walls=[o for o in env['cutaway'].objects if o.name.startswith(wallprefix)]
    wallroot=empty('STORY / growing reinforced chamber',(0,0,-3.65))
    parent_world(walls,wallroot)
    rebar=[]
    for x in [-1.68,1.68]:
        for y in [-2.3,-1.15,0,1.15,2.3]:
            rebar.append(cylinder('Reinforcement / vertical steel',(x,y,-3.58),(x,y,-.10),.019,mats['steel']))
    for z in [-3.25,-2.35,-1.45,-.55]:
        for x in [-1.68,1.68]:
            rebar.append(cylinder('Reinforcement / horizontal tie',(x,-2.4,z),(x,2.4,z),.013,mats['steel']))
    liftfamily=set(descendants(mech['lift']))
    carfamily=set(descendants(car)) if car else set()
    moving=set([*mech['mid_stages'],*mech['rods']])
    movingfamily=set(o for root in moving for o in descendants(root))
    mechanism_names=('Anchored cylinder','Base anchor','Fixed pressure','Barrel end','Fixed guide','Wall rail','Oil reservoir','Reservoir ','Hydraulic ','Pump motor','Motor cooling','Pressure gauge','Ivory pressure','Gauge needle','Transparent pressure','Steel return','Threaded barrel','Oil flow','Blue cylinder')
    hardware=[o for o in bpy.context.scene.objects if o.name.startswith(mechanism_names)]
    drainage=[o for o in bpy.context.scene.objects if o.name.startswith(('Sump','Drain grate'))]
    platform=list(liftfamily-carfamily)
    shell=list(env['exterior_only'].objects)+props['road']
    # Diagnostic cutaway reveal: fade only camera-facing banks/road, preserving
    # every original mesh and the same chamber coordinates throughout the film.
    shellmats={}
    processed_data=set()
    for ob in set(shell):
        if ob.type not in ('MESH','CURVE') or ob.data in processed_data:continue
        processed_data.add(ob.data)
        for slot in ob.material_slots:
            original=slot.material
            if not original:continue
            if original.name not in shellmats:
                material=original.copy();material.name=original.name+' / cutaway reveal'
                n=material.node_tree.nodes;links=material.node_tree.links
                output=n.get('Material Output');previous=output.inputs['Surface'].links[0].from_socket
                transparent=n.new('ShaderNodeBsdfTransparent');blend=n.new('ShaderNodeMixShader')
                blend.name='Cutaway reveal';blend.inputs[0].default_value=0
                links.new(previous,blend.inputs[1]);links.new(transparent.outputs[0],blend.inputs[2]);links.new(blend.outputs[0],output.inputs['Surface'])
                shellmats[original.name]=(material,blend.inputs[0])
            slot.material=shellmats[original.name][0]
    # A pale-blue traced discharge is a second fluid path, separate from oil.
    discharge=props['drainage_overlay']
    return {'walls':walls,'wallroot':wallroot,'rebar':rebar,'platform':platform,
            'hardware':hardware+list(movingfamily),'drainage':[o for o in drainage if not o.name.startswith('Sump discharge')],'waterflow':[o for o in discharge if o.type=='CURVE'],'water_tracers':[o for o in discharge if o.type=='MESH'],
            'solid_discharge':[o for o in drainage if o.name.startswith('Sump discharge')],
            'car':list(carfamily),'shell':list(set(shell)),
            'shell_alpha':[v[1] for v in shellmats.values()]}


def pose_garage(shot,t,seconds,state):
    camera,mech,car,p,g=state['camera'],state['mechanism'],state['car'],state['props'],state['groups']
    a=shot['action'];u=ease(t);local=seconds-shot['start'];z=0.;car_y=0.;reveal=1.;cover=0.;water=.02
    visible={'walls':True,'hardware':True,'platform':True,'car':True,'drainage':a in {'arrive','drainage','pinch','sensors','conceal','payoff'},
             'guide':False,'clods':False,'excavation_fill':False,'crate_parts':False,
             'solid_discharge':a in {'arrive','drainage','pinch','sensors','conceal','payoff'},'sensors':False,'beam':False,'warning':False,'rain':False,'water':False,'rebar':False,'waterflow':False,'water_tracers':False,'drainage_parts':a in {'arrive','drainage','pinch','sensors','conceal','payoff'},'drainage_fill':a=='drainage'}
    wall_scale=1.
    if a=='arrive':
        local=t*7.0  # Normalize the choreography to this shot's declared length.
        travel=ease(local/2.8);car_y=-7*(1-travel)
        reveal=ease((local-3.35)/.95)
        z=-2.1*ease((local-4.25)/1.7)
        cover=ease((local-6.05)/.8)
        c=ease(local/3.4)
        exterior=(mix((9,-18,7),(8,-14,6),c),mix((0,-3,.8),(0,0,.7),c),13.8-4.3*c)
        camera_pose(camera,mix(exterior[0],(7,-16,5.5),reveal),mix(exterior[1],(0,.15,-.7),reveal),exterior[2]+(11.25-exterior[2])*reveal)
    else:
        presets={'exterior':((7.4,-13,6),(0,.25,.7),8.8),
                 'cutaway':((7,-16,5.5),(0,.15,-.7),11.25),
                 'hydraulics':((2.8,-8,.0),(-.1,-.1,-1.8),6.5),
                 'drainage':((-.6,-5,-2.8),(.8,1.9,-3.25),2.0),
                 'sensor':((4.2,-7,3.0),(.4,-1.8,.0),5.9)}
        pos,target,scale=presets.get(shot['camera'],presets['cutaway'])
        camera_pose(camera,mix(pos,(pos[0]-.25,pos[1]+.15,pos[2]-.08),u),target,scale-.15*u)
        if a=='excavate':
            visible.update(walls=False,hardware=False,platform=False,car=False,drainage=False,guide=True,excavation_fill=t<.97)
            for i,ob in enumerate(p['excavation_fill']):
                amount=ease((t-i*.12)/.55);ob.scale.z=max(.001,1-amount);ob.location.z=-2*amount
        elif a=='collapse':
            visible.update(walls=False,hardware=False,platform=False,car=False,drainage=False,clods=True,guide=True,warning=False)
        elif a=='reinforce':
            visible.update(hardware=False,platform=False,car=False,drainage=False,rebar=t<.65,guide=True)
            wall_scale=max(.001,ease((t-.18)/.7))
        elif a=='load':
            visible.update(hardware=False,drainage=False,guide=True)
        elif a=='hydraulics':
            z=-2.1*(1-ease((t-.2)/.75));visible['drainage']=False
        elif a=='rain':
            z=-2.1;water=.03+1.55*u;visible.update(rain=True,water=True)
        elif a=='drainage':
            # Empty the basin in the first half, then hold the clear close-up
            # while the narration explains the pump and closing check valve.
            z=-2.1;water=1.58*(1-ease(t/.50))+.025
            # Isolate the drainage diagnostic in the persistent chamber: nearby
            # hydraulic guides otherwise conceal the small pump and valve.
            visible.update(water=True,waterflow=True,water_tracers=.12 <= t < .90,solid_discharge=False,hardware=False)
        elif a in ('pinch','sensors'):
            stop=.24 if a=='sensors' else .58
            z=-.40+.27*ease(min(t/stop,1))
            visible.update(crate_parts=True,sensors=a=='sensors',beam=a=='sensors',warning=a=='sensors' and t>=stop)
        elif a=='conceal':
            z=-2.1*ease(t/.6);cover=ease((t-.62)/.32);reveal=1-ease((t-.70)/.29)
        elif a=='payoff':
            # One complete return-and-hide cycle, with the cover retracted before
            # the roof reaches grade; it closes only after the car is below it.
            if t<.18:cover=1-ease(t/.18);z=-2.1
            elif t<.50:z=-2.1*(1-ease((t-.18)/.32))
            elif t<.83:z=-2.1*ease((t-.5)/.33)
            else:z=-2.1;cover=ease((t-.83)/.17)
    pose(mech,z,round(seconds*state['fps'])+1)
    car.location=(0,car_y,0);car.rotation_euler.z=math.pi
    for pivot in p['wheel_pivots']:
        pivot.rotation_euler.x=(car_y+7)/.351
    # Move leaves beneath the surrounding driveway, then raise them flush only
    # after closing. This cover is separate from the vehicle-carrying platform.
    for sign,key in [(-1,'cover_left'),(1,'cover_right')]:
        p[key].location.x=sign*(3.20-(3.20-.725)*cover)
        p[key].location.z=-.13+.13*ease((cover-.8)/.2)
    p['water'].scale.z=water
    p['check_valve'].rotation_euler.x=math.radians(70)*ease(t/.15)*(1-ease((t-.90)/.10)) if a=='drainage' else 0
    p['crate'].location.x=1.90-.6*ease(t/.6)
    for i,ob in enumerate(p['clods']):
        ob.location.z=-.20-3.65*ease((t-(i%6)*.05)/.55)
        ob.rotation_euler=(u*(i%3+1),u*3,u*2)
    for ob in p['rain']:
        ob.location.z=5.8-((seconds*5+ob['phase']*5.8)%5.8)
    for ob,path,offset in p['drain_pulses']:
        ob.location=point_on_polyline(path,offset+seconds*.8)
    g['wallroot'].scale.z=wall_scale
    for alpha in g['shell_alpha']:
        alpha.default_value=reveal
    visible['cover_parts']=a in ('arrive','conceal','payoff')
    return visible


def bake(story,scope,scene,camera,mech,env=None,car=None,props=None,mats=None):
    shots=story['shots'][:1] if scope=='opening' else story['shots']
    frames=shots[-1]['end_frame'];scene.frame_start=1;scene.frame_end=frames;scene.render.fps=story['fps']
    scene['story_id']=story['id'];scene['story_template']=story['template'];scene['story_source_sha256']=story['source_sha256'];scene['story_scope']=scope
    scene['story_shots']=__import__('json').dumps(shots)
    cache={}
    if car:
        env['exterior_only'].hide_render=False;env['exterior_only'].hide_viewport=False
        g=prepare_groups(env,mech,car,props,mats)
        state={'camera':camera,'mechanism':mech,'car':car,'props':props,'groups':g,'fps':story['fps']}
    else:g={}
    for shot in shots:
        scene.timeline_markers.new(shot['id']+' / '+shot['action'],frame=shot['start_frame'])
        for frame in range(shot['start_frame'],shot['end_frame']+1):
            t=(frame-shot['start_frame'])/max(1,shot['frames']-1);seconds=(frame-1)/story['fps']
            if car:
                vis=pose_garage(shot,t,seconds,state)
                keyed_visible(g['shell'],g['shell_alpha'][0].default_value < .999,frame,cache)
                for key,visible in vis.items():
                    objects=g.get(key,props.get(key,[]))
                    if not isinstance(objects,list):objects=[objects]
                    keyed_visible(objects,visible,frame,cache)
                animated=[mech['lift'],*mech['mid_stages'],*mech['rods'],car,
                          *props['wheel_pivots'],props['cover_left'],props['cover_right'],
                          props['water'],props['crate'],props['check_valve'],g['wallroot']]
                if vis['clods']:animated+=props['clods']
                if vis['rain']:animated+=props['rain']
                if vis['excavation_fill']:animated+=props['excavation_fill']
                if vis['water_tracers']:animated+=g['water_tracers']
                for alpha in g['shell_alpha']:alpha.keyframe_insert(data_path='default_value',frame=frame)
            else:
                a=shot['action'];z=-2.1
                if a=='extend':z=-2.1+2.1*ease(t)
                elif a=='retract':z=-2.1*ease(t)
                pose(mech,z,frame)
                wide=shot['camera'] in {'cutaway','arrival','exterior'}
                position=(6.8,-11,2.4) if wide else (3.1,-8,-.2)
                target=(-.1,-.4,-1.7) if wide else (-.1,-.4,-2.2)
                camera_pose(camera,mix(position,(position[0]-.35,position[1]+.15,position[2]),ease(t)),target,8.6 if wide else 5.9)
                animated=[mech['lift'],*mech['mid_stages'],*mech['rods']]
            for ob in animated:
                for path in ('location','rotation_euler','scale'):ob.keyframe_insert(data_path=path,frame=frame)
            for ob,_,_ in mech['pulses']:ob.keyframe_insert(data_path='location',frame=frame)
            camera.keyframe_insert(data_path='location',frame=frame);camera.keyframe_insert(data_path='rotation_euler',frame=frame);camera.data.keyframe_insert(data_path='ortho_scale',frame=frame)
        # Camera shots cut cleanly on their first frame, then ease internally.
    for ob in [*scene.objects,camera.data]:
        if ob.animation_data and ob.animation_data.action:
            for curve in ob.animation_data.action.fcurves:
                for key in curve.keyframe_points:key.interpolation='CONSTANT' if curve.data_path=='hide_render' else 'LINEAR'
    # No interpolation through a shot cut: insert a duplicate of its old camera
    # pose at the previous frame (already baked) and use constant boundary keys.
    scene.frame_set(1);bpy.context.view_layer.update()
    return {'frames':frames,'shots':shots,'groups':g}
