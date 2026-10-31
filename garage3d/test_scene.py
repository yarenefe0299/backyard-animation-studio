"""Inspect the saved Blender master, without rendering or rebuilding it.

blender -b --python-exit-code 1 --python garage3d/test_scene.py -- garage3d/output/style_test.blend
Checks measured geometry and evaluated motion rather than only script constants.
"""
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.geometry import interpolate_bezier


def z_bounds(obj):
    return min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box), max((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)


def overlaps(a, b, tolerance=.01):
    return min(a[1], b[1])-max(a[0], b[0]) >= -tolerance


def nearest_segment_distance(point, segments):
    best=float('inf')
    for a,b in segments:
        delta=b-a
        t=max(0,min(1,(point-a).dot(delta)/delta.length_squared)) if delta.length_squared else 0
        best=min(best,(point-a-delta*t).length)
    return best


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    path=Path(args[0]) if args else Path(__file__).resolve().parent/'output/style_test.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    scene=bpy.context.scene
    assert scene.render.fps==30 and scene.frame_start==1 and scene.frame_end==120
    assert scene.camera and scene.camera.animation_data
    cars=[o for o in scene.objects if o.get('asset_type')=='original_procedural_hatchback']
    assert len(cars)==1, 'The scene must preserve one reusable car assembly'
    car=cars[0]
    lift=car.parent
    assert lift and lift.animation_data, 'Car must ride an animated carriage'
    tires=[o for o in car.children if o.name.startswith('Car tire ') and o.type=='MESH']
    assert len(tires)==4, 'Four modeled tires required'
    pavers=[o for o in lift.children if o.name.startswith('Carriage inset paver')]
    assert pavers
    rods=[o for o in scene.objects if o.name.startswith('Telescopic final rod')]
    sleeves=[o for o in scene.objects if o.name.startswith('Telescopic first stage')]
    barrels=[o for o in scene.objects if o.name.startswith('Fixed pressure barrel')]
    assert len(rods)==len(sleeves)==len(barrels)==2
    pulses=[o for o in scene.objects if o.name.startswith('Oil flow tracer')]
    pipes=[o for o in scene.objects if o.name.startswith('Transparent pressure line')]
    assert pulses and len(pipes)==2
    segments=[]
    for pipe in pipes:
        points=pipe.data.splines[0].bezier_points
        for a,b in zip(points, list(points)[1:]):
            samples=interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,129)
            samples=[pipe.matrix_world @ v for v in samples]
            segments.extend(zip(samples,samples[1:]))
    camera_start=None
    deck_heights=[]
    car_offsets=[]
    max_pipe_error=0
    for frame in range(1,121):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        z=lift.matrix_world.translation.z
        deck_heights.append(z)
        car_offsets.append(car.matrix_world.translation.z-z)
        # All four tire soles remain on the real paver mesh, not merely on an
        # asserted parent coordinate; the modeled tread allowance is 1 cm.
        deck_top=max(z_bounds(o)[1] for o in pavers)
        for tire in tires:
            assert abs(z_bounds(tire)[0]-deck_top)<.01, f'Tire/deck separation at frame {frame}'
        for rod,sleeve,barrel in zip(sorted(rods,key=lambda o:o.location.x),sorted(sleeves,key=lambda o:o.location.x),sorted(barrels,key=lambda o:o.location.x)):
            rod_mesh=next(o for o in rod.children if o.name.startswith('Polished final piston rod'))
            sleeve_mesh=next(o for o in sleeve.children if o.name.startswith('Honed first stage sleeve'))
            assert overlaps(z_bounds(rod_mesh),z_bounds(sleeve_mesh)), f'Disconnected rod at {frame}'
            assert overlaps(z_bounds(sleeve_mesh),z_bounds(barrel)), f'Disconnected cylinder at {frame}'
        if frame in (1,30,60,90,120):
            for pulse in pulses:
                error=nearest_segment_distance(pulse.matrix_world.translation,segments)
                max_pipe_error=max(error,max_pipe_error)
                assert error<.004, f'Oil tracer leaves pressure pipe centerline: {error:.5f}m frame {frame}'
        if frame==1:
            camera_start=scene.camera.matrix_world.translation.copy()
    assert max(abs(v) for v in car_offsets)<1e-5, 'Car must retain contact through its full motion'
    assert abs(deck_heights[0])<1e-5 and deck_heights[-1]<-2, 'Lift must move the car below grade'
    assert max(abs(a-b) for a,b in zip(deck_heights,deck_heights[1:]))<.06, 'Motion must avoid discontinuous jumps'
    assert all(b<=a+1e-6 for a,b in zip(deck_heights,deck_heights[1:])), 'Lowering must be mechanically steady'
    assert (scene.camera.matrix_world.translation-camera_start).length>.25, 'Camera must actually move'
    assert max(z_bounds(o)[1] for o in car.children if o.type=='MESH')<0, 'Car must fit entirely beneath grade at the end'
    print(f'GARAGE_SCENE_CHECKS_PASS: 120 evaluated poses, tire contact, stage overlap, camera motion; max oil centerline error {max_pipe_error:.6f} m')


if __name__=='__main__':
    main()
