"""Independent Blender look-development entry point; never imports Remotion.

blender -b --python garage3d/style_test.py -- --mode all --quality draft
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from materials import library
from environment import build_environment
from car import build_car
from mechanism import build_mechanism, pose

PRESETS = {'draft': (270,480,16), 'review': (540,960,64), 'final': (1080,1920,128)}
FPS = 30
FRAMES = 120


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'output')
    parser.add_argument('--quality', choices=PRESETS, default='draft')
    parser.add_argument('--mode', choices=['all','stills','animation','build'], default='all')
    parser.add_argument('--still', choices=['exterior','cutaway','hydraulics'], help='Render only this still when mode=stills')
    return parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def aim(ob, target):
    ob.rotation_euler = (Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()


def area(name, location, energy, size, color, target):
    data = bpy.data.lights.new(name,'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    ob = bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(ob)
    ob.location = location
    aim(ob,target)
    return ob


def configure_scene(quality):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = PRESETS[quality][2]
    scene.cycles.seed = 17
    # Debian builds can omit OIDN. Never assume the denoiser is compiled in.
    scene.cycles.use_denoising = bool(getattr(bpy.app.build_options, 'openimagedenoise', False))
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 8
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 4
    scene.render.resolution_x,scene.render.resolution_y,_ = PRESETS[quality]
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = .0
    scene.render.use_persistent_data = True
    scene.world.use_nodes = True
    world = scene.world.node_tree.nodes.get('Background')
    world.inputs['Color'].default_value = (.76,.80,.84,1)
    world.inputs['Strength'].default_value = .40
    area('Large warm daylight key',(-3,-4,9),1800,7,(1,.88,.72),(0,0,-.4))
    area('Soft sky window fill',(6,-1,5),1100,6,(.80,.88,1),(0,0,-1))
    area('Chamber soft bounce',(1,-4,-.8),180,4,(1,.91,.78),(0,1,-2.9))
    area('House soft rim',(-3,6,6),1000,5,(1,.93,.83),(0,0,0))
    data=bpy.data.cameras.new('Master vertical camera')
    camera=bpy.data.objects.new('Master vertical camera',data)
    bpy.context.collection.objects.link(camera)
    scene.camera=camera
    data.type='ORTHO'
    data.lens=45
    data.clip_start=.05
    data.clip_end=200
    scene.frame_start=1
    scene.frame_end=FRAMES
    return scene,camera


def smoother(t):
    t=max(0,min(1,t))
    return t*t*t*(t*(t*6-15)+10)


def set_camera(camera, position, target, scale):
    camera.location=position
    aim(camera,target)
    camera.data.ortho_scale=scale


def animate(scene,camera,mechanism,environment):
    environment['exterior_only'].hide_render=True
    environment['exterior_only'].hide_viewport=True
    for frame in range(1,FRAMES+1):
        t=(frame-1)/(FRAMES-1)
        z=-2.1*smoother((t-.08)/.84)
        pose(mechanism,z,frame)
        arc=smoother(t)
        set_camera(camera,(7-.8*arc,-16+.6*arc,5.5-.4*arc),(0,.15,-.70-.25*arc),11.25-.30*arc)
        for ob in [mechanism['lift'],*mechanism['mid_stages'],*mechanism['rods']]:
            ob.keyframe_insert(data_path='location',frame=frame)
        for ob,_,_ in mechanism['pulses']:
            ob.keyframe_insert(data_path='location',frame=frame)
        camera.keyframe_insert(data_path='location',frame=frame)
        camera.keyframe_insert(data_path='rotation_euler',frame=frame)
        camera.data.keyframe_insert(data_path='ortho_scale',frame=frame)
    # Every frame sampled from one smooth analytic trajectory. Linear interpolation
    # avoids Bezier overshoot at the stops and keeps film-time exactly reproducible.
    for data in [o for o in bpy.data.objects]+[camera.data]:
        if data.animation_data and data.animation_data.action:
            for fc in data.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation='LINEAR'
    scene.frame_set(1)


def validate(scene,camera,car,mechanism):
    measurements=[]
    for frame in [1,30,60,90,120]:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        lift=mechanism['lift'].matrix_world.translation.z
        car_z=car.matrix_world.translation.z
        assert abs(car_z-lift)<1e-6, 'Vehicle must stay attached to its deck'
        for rod in mechanism['rods']:
            assert abs(rod.location.z-lift)<1e-6, 'Rod and carriage must remain connected'
        for mid in mechanism['mid_stages']:
            assert abs(mid.location.z-(lift+2.1)/2)<1e-6
        measurements.append({'frame':frame,'deck_z':round(lift,6),'car_root_z':round(car_z,6),'camera':list(camera.location)})
    assert measurements[0]['deck_z']==0
    assert abs(measurements[-1]['deck_z']+2.1)<1e-6
    assert measurements[0]['camera']!=measurements[-1]['camera']
    assert len([o for o in bpy.data.objects if o.type=='MESH'])>300
    scene.frame_set(1)
    return measurements


def still(scene,camera,environment,mechanism,output,shot):
    scene.frame_set(1)
    # Stills change only pose, camera, and the near cutaway shell; all meshes are
    # the same persistent master geometry. Save the animated master before this.
    for ob in [camera,*mechanism['mid_stages'],*mechanism['rods'],mechanism['lift'],*[p[0] for p in mechanism['pulses']]]:
        ob.animation_data_clear()
    camera.data.animation_data_clear()
    exterior=shot=='exterior'
    environment['exterior_only'].hide_render=exterior is False
    if exterior:
        pose(mechanism,0,1)
        set_camera(camera,(7.8,-12,6.8),(0,.9,.7),8.1)
    elif shot=='cutaway':
        pose(mechanism,-.65,45)
        set_camera(camera,(7,-16,5.5),(0,.2,-.70),11.25)
    else:
        pose(mechanism,-.35,65)
        set_camera(camera,(2.5,-8,-.4),(-.2,-.15,-2.1),5.9)
    bpy.context.view_layer.update()
    scene.render.filepath=str(output/(shot+'.png'))
    bpy.ops.render.render(write_still=True)


def main():
    args=arguments()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    scene,camera=configure_scene(args.quality)
    print('Building procedural master environment...', flush=True)
    mats=library()
    environment=build_environment(mats)
    mats.update(environment['materials'])
    print('Building connected hydraulics...', flush=True)
    mechanism=build_mechanism(mats)
    print('Building the silver hatchback...', flush=True)
    car=build_car(mats)
    car.parent=mechanism['lift']
    animate(scene,camera,mechanism,environment)
    samples=validate(scene,camera,car,mechanism)
    manifest=HERE.parent/'hidden_garage_3d_scene_manifest.json'
    report={
        'title':'How to Hide a Car Under Your Driveway — style test',
        'stage':'style review pending; full episode deliberately not implemented',
        'blender_version':bpy.app.version_string,'quality':args.quality,
        'resolution':list(PRESETS[args.quality][:2]),'cycles_samples':scene.cycles.samples,
        'denoising':scene.cycles.use_denoising,'fps':FPS,'frames':FRAMES,'duration_s':4,
        'object_count':len(bpy.data.objects),'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),
        'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'source_notes':'Named .md blueprint absent; repository Script.txt read as available blueprint. Storyboard JPG inspected; source movie not present.',
        'coordinate_system':'meters; Z up; vehicle nose -Y; ground 0; chamber floor -3.65',
        'pose_checks':samples,'completed_this_invocation':[],
    }
    # This file is useful even if an expensive render is interrupted; completion
    # is recorded separately only after Blender returns from each render call.
    def write_report():
        (output/'scene_report.json').write_text(json.dumps(report,indent=2)+'\n')
    write_report()
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'style_test.blend'))
    report['completed_this_invocation'].append('style_test.blend')
    if args.mode in ('stills','all'):
        for shot in ([args.still] if args.still else ['cutaway','hydraulics','exterior']):
            still(scene,camera,environment,mechanism,output,shot)
            report['completed_this_invocation'].append(shot+'.png')
            write_report()
    if args.mode in ('animation','all'):
        # Reload restores all baked animation, even after separate still poses.
        bpy.ops.wm.open_mainfile(filepath=str(output/'style_test.blend'))
        scene=bpy.context.scene
        frames=output/'frames'
        frames.mkdir(exist_ok=True)
        scene.render.filepath=str(frames/'frame_')
        bpy.ops.render.render(animation=True)
        report['completed_this_invocation'].append('120 rendered animation frames')
    write_report()
    print('GARAGE3D_COMPLETE '+json.dumps(report['completed_this_invocation']))


if __name__=='__main__':
    main()
