"""Measure the saved story master; no rebuilding and no image rendering.

blender -b --python-exit-code 1 --python garage3d/test_story_scene.py -- master.blend
The inspected poses and tolerances are written beside the master as
``scene_checks.json``. Assertions fail the process rather than claiming approval.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import interpolate_bezier


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return tuple((min(p[axis] for p in points), max(p[axis] for p in points)) for axis in range(3))


def family(root):
    return [root, *root.children_recursive]


def geometry(root):
    return [obj for obj in family(root) if obj.type in ('MESH', 'CURVE')]


def at(scene, frame):
    scene.frame_set(int(frame))
    bpy.context.view_layer.update()


def shot_frames(shot):
    first, last = shot['start_frame'], shot['end_frame']
    return sorted({first, (first+last)//2, last})


def frame_at(scene, shot, seconds):
    return min(shot['end_frame'], shot['start_frame']+round(seconds*scene.render.fps))


def reveal_sockets():
    sockets=[]
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        nodes=[node for node in material.node_tree.nodes if node.name.startswith('Cutaway reveal')]
        assert len(nodes) <= 1, 'Shared material was repeatedly wrapped in cutaway shaders: '+material.name
        sockets.extend(node.inputs[0] for node in nodes)
    return sockets


def curve_segments(objects):
    segments=[]
    for obj in objects:
        if obj.type != 'CURVE':
            continue
        for spline in obj.data.splines:
            if spline.type != 'BEZIER':
                continue
            points=list(spline.bezier_points)
            for first,last in zip(points,points[1:]):
                samples=interpolate_bezier(first.co,first.handle_right,last.handle_left,last.co,65)
                world=[obj.matrix_world @ point for point in samples]
                segments.extend(zip(world,world[1:]))
    return segments


def centreline_distance(point, segments):
    result=float('inf')
    for start,end in segments:
        delta=end-start
        fraction=max(0,min(1,(point-start).dot(delta)/delta.length_squared)) if delta.length_squared else 0
        result=min(result,(point-start-delta*fraction).length)
    return result


def fluid_check(scene, frames):
    """Check visible oil and water particles against actual curved pipe geometry."""
    pipes=[obj for obj in scene.objects if obj.name.startswith(
        ('Transparent pressure line','Drainage / transparent discharge','Sump discharge'))]
    segments=curve_segments(pipes)
    tracers=[obj for obj in scene.objects if obj.name.startswith(
        ('Oil flow tracer','Drainage / moving water tracer','Drainage / water flow tracer'))]
    assert segments and tracers, 'Story must retain its modeled hydraulic flow path'
    maximum=0.
    checked=0
    for frame in frames:
        at(scene,frame)
        for tracer in tracers:
            if tracer.hide_render:
                continue
            distance=centreline_distance(tracer.matrix_world.translation,segments)
            maximum=max(maximum,distance)
            assert distance < .004, f'{tracer.name} leaves curved pipe by {distance:.6f}m at frame {frame}'
            checked+=1
    return {'enabled_tracer_samples':checked,'max_centreline_error_m':maximum}


def cover_check(scene, car, frame):
    covers=[obj for obj in scene.objects if obj.name.startswith('Concealing driveway roof /') and obj.type=='EMPTY']
    assert len(covers)==2, 'The driveway cover must be separate from its vehicle carriage'
    car_geometry=geometry(car)
    car_bounds=[bounds(obj) for obj in car_geometry]
    car_xy=[(min(v[a][0] for v in car_bounds),max(v[a][1] for v in car_bounds)) for a in (0,1)]
    car_top=max(v[2][1] for v in car_bounds)
    measured=[]
    for cover in covers:
        pieces=[obj for obj in geometry(cover) if not obj.hide_render]
        if not pieces:
            continue
        part_bounds=[bounds(obj) for obj in pieces]
        roof_xy=[(min(v[a][0] for v in part_bounds),max(v[a][1] for v in part_bounds)) for a in (0,1)]
        overlaps=all(min(car_xy[a][1],roof_xy[a][1])-max(car_xy[a][0],roof_xy[a][0]) > .001 for a in (0,1))
        if overlaps:
            underside=min(v[2][0] for v in part_bounds)
            clearance=underside-car_top
            assert clearance > .008, f'Roof intersects car or aerial at frame {frame}: clearance {clearance:.5f}m'
            measured.append(clearance)
        if abs(abs(cover.location.x)-.725)<.02:
            assert abs(cover.location.z)<.012, 'Closed roof should finish flush with driveway grade'
            assert car_top < -.05, 'Cover must not close until the entire car is below grade'
    return min(measured) if measured else None


def mechanical_checks(scene,frames):
    rods=sorted([obj for obj in scene.objects if obj.name.startswith('Telescopic final rod')],key=lambda obj:obj.location.x)
    sleeves=sorted([obj for obj in scene.objects if obj.name.startswith('Telescopic first stage')],key=lambda obj:obj.location.x)
    barrels=sorted([obj for obj in scene.objects if obj.name.startswith('Fixed pressure barrel')],key=lambda obj:obj.location.x)
    assert len(rods)==len(sleeves)==len(barrels)==2, 'Two connected telescopic cylinders are required'
    beams=[obj for obj in scene.objects if obj.name.startswith('Lift I-beam')]
    fixed=[obj for obj in scene.objects if obj.name.startswith(('Fixed pressure barrel','Barrel end collar'))]
    minimum=float('inf')
    for frame in frames:
        at(scene,frame)
        for rod,sleeve,barrel in zip(rods,sleeves,barrels):
            rod_mesh=next(obj for obj in rod.children if obj.name.startswith('Polished final piston rod'))
            sleeve_mesh=next(obj for obj in sleeve.children if obj.name.startswith('Honed first stage sleeve'))
            for first,last in [(rod_mesh,sleeve_mesh),(sleeve_mesh,barrel)]:
                a,b=bounds(first)[2],bounds(last)[2]
                overlap=min(a[1],b[1])-max(a[0],b[0])
                minimum=min(minimum,overlap)
                assert overlap>-.005, f'Telescopic stages disconnect at frame {frame}'
        # Model-space AABBs are conservative for these axis-aligned beams and
        # vertical cylinders. They catch a barrel entering its deck beam at the
        # fully retracted pose, a defect that hierarchy checks alone would miss.
        for cylinder in fixed:
            cb=bounds(cylinder)
            for beam in beams:
                bb=bounds(beam)
                penetration=[min(cb[a][1],bb[a][1])-max(cb[a][0],bb[a][0]) for a in range(3)]
                assert not all(depth>.001 for depth in penetration), f'Fixed cylinder intersects lift beam at frame {frame}: {cylinder.name}'
    return {'telescopic_min_overlap_m':minimum,'checked_poses':len(frames)}


def construction_guide_check(scene):
    guides=[obj for obj in scene.objects if obj.name.startswith('Excavation / translucent construction edge')]
    assert len(guides)==12, 'Construction guide should trace the actual twelve chamber-box edges'
    degrees={}
    for guide in guides:
        z=[vertex.co.z for vertex in guide.data.vertices]
        for depth in (min(z),max(z)):
            point=guide.matrix_world @ Vector((0,0,depth))
            key=tuple(round(float(v),4) for v in point)
            degrees[key]=degrees.get(key,0)+1
    assert len(degrees)==8 and set(degrees.values())=={3}, 'Blue construction edges must meet at eight shared corners'
    return {'modeled_edges':len(guides),'connected_corners':len(degrees)}


def sensor_checks(scene,shots,lift):
    shot=next((shot for shot in shots if shot['action']=='sensors'),None)
    if not shot:
        return None
    crates=[obj for obj in scene.objects if obj.type=='EMPTY' and obj.get('story_role')=='safety_crate']
    beams=[obj for obj in scene.objects if obj.name.startswith('Safety beam / active')]
    warnings=[obj for obj in scene.objects if obj.name.startswith('Safety indicator / red stop')]
    assert len(crates)==len(beams)==len(warnings)==1, 'The safety demonstration needs a crate, real beam and stop indicator'
    crate_parts=geometry(crates[0]);beam=beams[0];warning=warnings[0]
    blocked=[];heights={}
    for frame in range(shot['start_frame'],shot['end_frame']+1):
        at(scene,frame)
        assert not beam.hide_render, 'Sensor beam must be active during obstruction detection'
        b=bounds(beam);parts=[bounds(obj) for obj in crate_parts]
        c=[(min(v[a][0] for v in parts),max(v[a][1] for v in parts)) for a in range(3)]
        if all(min(b[a][1],c[a][1])-max(b[a][0],c[a][0])>.0001 for a in range(3)):
            blocked.append(frame)
        heights[frame]=lift.matrix_world.translation.z
    assert blocked, 'The modeled crate must actually cross the optical beam'
    first=blocked[0]
    overrun=max(abs(z-heights[first]) for frame,z in heights.items() if frame>=first)
    assert overrun<.003, f'Lift keeps moving after the optical beam is blocked: {overrun:.5f}m'
    at(scene,min(first+3,shot['end_frame']))
    assert not warning.hide_render, 'Stop indicator must respond promptly to the blocked beam'
    return {'first_blocked_frame':first,'movement_after_beam_blocked_m':overrun}


def garage_checks(scene, shots):
    cars=[obj for obj in scene.objects if obj.get('asset_type')=='original_procedural_hatchback']
    assert len(cars)==1, 'One persistent car identity is required'
    car=cars[0]
    lift=car.parent
    assert lift and lift.animation_data, 'Vehicle must ride an animated carriage'
    tires=[obj for obj in family(car) if obj.type=='MESH' and obj.name.startswith('Car tire ')]
    wheels=[obj for obj in family(car) if obj.get('story_role')=='rolling_wheel']
    assert len(tires)==len(wheels)==4, 'Four actual tires and four rolling wheel assemblies are required'
    assert all(tire.parent in wheels for tire in tires), 'Animated wheels must carry the modeled tires'
    assert all(len(wheel.children)>5 for wheel in wheels), 'Wheel pivots must animate real wheel detail'
    all_samples=sorted({frame for shot in shots for frame in shot_frames(shot)})
    minimum_cover_clearance=None
    for frame in all_samples:
        at(scene,frame)
        assert abs(car.matrix_world.translation.z-lift.matrix_world.translation.z)<.005, f'Car/deck hierarchy separated at {frame}'
        shot=next(shot for shot in shots if shot['start_frame']<=frame<=shot['end_frame'])
        if shot['action'] in ('excavate','collapse','reinforce'):
            assert all(obj.hide_render for obj in geometry(car)), f'Build explanation must hide the payoff car at frame {frame}'
        clearance=cover_check(scene,car,frame)
        if clearance is not None:
            minimum_cover_clearance=clearance if minimum_cover_clearance is None else min(clearance,minimum_cover_clearance)
    arrival=next((shot for shot in shots if shot['action']=='arrive'),None)
    drive={}
    if arrival:
        at(scene,arrival['start_frame'])
        start_y=car.location.y
        start_angles=[wheel.rotation_euler.x for wheel in wheels]
        assert abs(start_y+7)<.02, 'Car should begin down the approach, away from the house'
        start_alpha=[socket.default_value for socket in reveal_sockets()]
        assert start_alpha and max(start_alpha)<.005, 'Opening must keep the underground shell opaque before the reveal'
        park_frame=frame_at(scene,arrival,2.8)
        at(scene,park_frame)
        finish_y=car.location.y
        assert abs(finish_y)<.02, 'Car must reach the centre of the driveway before descending'
        for wheel,start_angle in zip(wheels,start_angles):
            travelled=(wheel.rotation_euler.x-start_angle)*wheel['wheel_radius_m']
            assert abs(travelled-(finish_y-start_y))<.025, 'Wheel rotation must agree with driven distance'
        # Measure actual mesh soles against both road and carriage top surfaces.
        road=[obj for obj in scene.objects if obj.name.startswith('Approach / limestone')]
        pavers=[obj for obj in lift.children if obj.name.startswith('Carriage inset paver')]
        assert road and pavers, 'Driving approach and carriage must both have modeled paving'
        road_top=max(bounds(obj)[2][1] for obj in road)
        deck_top=max(bounds(obj)[2][1] for obj in pavers)
        tire_frames=sorted({arrival['start_frame'],park_frame,*range(arrival['start_frame'],park_frame+1,max(1,scene.render.fps//2))})
        worst_contact=0.
        for frame in tire_frames:
            at(scene,frame)
            for tire in tires:
                bb=bounds(tire)
                centre_y=(bb[1][0]+bb[1][1])/2
                expected=deck_top if -2.50 < centre_y < 2.50 else road_top
                # A rotated tire's object AABB encloses empty corner space.
                # Contact must use real tread/sidewall vertices, not its box.
                sole=min((tire.matrix_world @ vertex.co).z for vertex in tire.data.vertices)
                error=abs(sole-expected)
                worst_contact=max(worst_contact,error)
                assert error<.013, f'Tire loses actual road/deck contact at frame {frame}: {error:.5f}m'
        late=frame_at(scene,arrival,min(arrival['duration_s']*.72,arrival['duration_s']-.15))
        at(scene,late)
        assert min(socket.default_value for socket in reveal_sockets())>.99, 'The chamber must be revealed after parking'
        at(scene,arrival['end_frame'])
        assert abs(lift.matrix_world.translation.z+2.1)<.01, 'Arrival payoff must lower the car into the chamber'
        assert max(bounds(obj)[2][1] for obj in geometry(car))<-.05, 'Entire parked car, including aerial, must fit below grade'
        drive={'driven_distance_m':finish_y-start_y,'tire_contact_max_error_m':worst_contact,'park_frame':park_frame}
    return {'pose_samples':len(all_samples),'cover_min_clearance_m':minimum_cover_clearance,
            'arrival':drive,'guide':construction_guide_check(scene),'safety':sensor_checks(scene,shots,lift),**fluid_check(scene,all_samples)}


def lab_checks(scene,shots):
    assert not any(obj.get('asset_type')=='original_procedural_hatchback' for obj in scene.objects), 'Hydraulic lab must not depend on a car scene'
    lifts=[obj for obj in scene.objects if obj.type=='EMPTY' and obj.name.startswith('LIFT')]
    assert len(lifts)==1
    lift=lifts[0]
    ranges=[]
    for shot in shots:
        at(scene,shot['start_frame']);first=lift.matrix_world.translation.z
        at(scene,shot['end_frame']);last=lift.matrix_world.translation.z
        if shot['action']=='extend':
            assert last-first>1.9, 'Lab extension must visibly raise its platform'
        elif shot['action']=='retract':
            assert first-last>1.9, 'Lab retraction must visibly lower its platform'
        ranges.append({'action':shot['action'],'start_z':first,'end_z':last})
    frames=sorted({frame for shot in shots for frame in shot_frames(shot)})
    return {'platform_ranges':ranges,**fluid_check(scene,frames)}


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('master',type=Path)
    options=parser.parse_args(args)
    master=options.master.resolve()
    bpy.ops.wm.open_mainfile(filepath=str(master))
    scene=bpy.context.scene
    template=scene.get('story_template')
    assert template in ('garage','hydraulic_lab'), 'Expected a saved story master with template metadata'
    shots=json.loads(scene['story_shots'])
    assert shots and scene.get('story_scope') in ('opening','full')
    assert scene.frame_start==1 and scene.frame_end==shots[-1]['end_frame']
    assert all(a['end_frame']+1==b['start_frame'] for a,b in zip(shots,shots[1:])), 'Shot frames must cover one continuous timeline'
    camera=scene.camera
    assert camera and camera.animation_data
    for shot in shots:
        at(scene,shot['start_frame']);start=camera.matrix_world.translation.copy()
        at(scene,shot['end_frame']);finish=camera.matrix_world.translation.copy()
        assert (finish-start).length>.025, f'Camera must move within story beat {shot["id"]}'
    frames=sorted({frame for shot in shots for frame in shot_frames(shot)})
    mechanics=mechanical_checks(scene,frames)
    measurements=garage_checks(scene,shots) if template=='garage' else lab_checks(scene,shots)
    measurements['mechanics']=mechanics
    report={'status':'passed','story_id':scene.get('story_id'),'template':template,
            'scope':scene.get('story_scope'),'fps':scene.render.fps,'timeline_frames':scene.frame_end,
            'blender_version':bpy.app.version_string,'measurements':measurements}
    (master.parent/'scene_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('STORY_SCENE_CHECKS_PASS '+json.dumps(report))


if __name__=='__main__':
    main()
