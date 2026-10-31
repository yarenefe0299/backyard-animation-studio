"""Build a persistent narrated story master; bake all motion before rendering."""
import argparse
import json
from pathlib import Path
import sys

import bpy
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from pipeline import PRESETS,SCOPES,make_plan
from style_test import configure_scene
from materials import library
from environment import build_environment
from mechanism import build_mechanism
from car import build_car
from geometry import cylinder
from story_assets import augment_garage
from story_motion import bake


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--story',type=Path,default=HERE.parent/'stories/hidden-garage')
    p.add_argument('--output',type=Path,default=HERE/'output/story')
    p.add_argument('--quality',choices=PRESETS,default='draft')
    p.add_argument('--scope',choices=SCOPES,default='opening')
    p.add_argument('--mode',choices=['build','stills','animation','all'],default='all')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output=args.output.resolve();plan=make_plan(args.story,output,args.quality,args.scope)
    scene,camera=configure_scene(args.quality)
    scene.cycles.transparent_max_bounces=32
    scene.render.resolution_x,scene.render.resolution_y,scene.cycles.samples=PRESETS[args.quality]
    mats=library();mats['silver'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.38,.43,.47,1)
    if plan['template']=='garage':
        print('Building persistent garage and arrival set...',flush=True)
        env=build_environment(mats);mats.update(env['materials'])
        mech=build_mechanism(mats);car=build_car(mats);car.parent=mech['lift']
        props=augment_garage(env,mech,car,mats)
        print('Baking narrative cameras, rolling wheels and story mechanisms...',flush=True)
        result=bake(plan,args.scope,scene,camera,mech,env,car,props,mats)
    else:
        print('Building independent hydraulic lab story...',flush=True)
        cylinder('Laboratory / beveled display plinth',(0,0,-3.92),(0,0,-3.65),3.7,mats['concrete'],vertices=96)
        mech=build_mechanism(mats)
        result=bake(plan,args.scope,scene,camera,mech)
    report={'status':'built; render completion recorded separately','story_id':plan['id'],'source_sha256':plan['source_sha256'],
            'scope':args.scope,'template':plan['template'],'blender_version':bpy.app.version_string,
            'frames':result['frames'],'fps':plan['fps'],'resolution':list(PRESETS[args.quality][:2]),
            'cycles_samples':scene.cycles.samples,'native_denoising':scene.cycles.use_denoising,
            'object_count':len(scene.objects),'completed':[]}
    def save_report():(output/'render_report.json').write_text(json.dumps(report,indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'master.blend'));report['completed'].append('master.blend');save_report()
    if args.mode in ['stills','all']:
        if plan['template']=='garage' and args.scope=='opening':times=[min(25,result['frames']),min(70,result['frames']),result['frames']]
        elif args.scope=='mechanism' and result['shots'][0].get('direction'):
            shot=result['shots'][0]
            choices=[beat for beat in shot['direction'] if beat['view'] in {'pump','cylinder','lift'}]
            times=[min(result['frames'],1+round((beat['at']+beat['move']+.3)*plan['fps'])) for beat in choices[:3]]
        elif plan['template']=='garage':
            # Review distinct visual requirements, rather than three adjacent
            # construction beats that omit the installed mechanism entirely.
            choices=[('arrive',.40),('reinforce',.90),('hydraulics',.50)]
            times=[]
            for action,fraction in choices:
                shot=next((s for s in result['shots'] if s['action']==action),result['shots'][len(times)%len(result['shots'])])
                times.append(shot['start_frame']+round((shot['frames']-1)*fraction))
        else:times=[s['start_frame']+(s['frames']-1)//2 for s in result['shots'][:3]]
        while len(times)<3:times.append(result['frames'])
        report['preview_frames']=times
        for i,frame in enumerate(times):
            scene.frame_set(frame);scene.render.filepath=str(output/f'preview_{i+1:02d}.png')
            bpy.ops.render.render(write_still=True);report['completed'].append(f'preview_{i+1:02d}.png');save_report()
    if args.mode in ['animation','all']:
        (output/'frames').mkdir(exist_ok=True)
        scene.render.filepath=str(output/'frames/frame_');scene.frame_set(1)
        bpy.ops.render.render(animation=True)
        report['completed'].append(f'{result["frames"]} rendered animation frames');save_report()
    print('STORY_RENDER_COMPLETE '+json.dumps(report['completed']),flush=True)


if __name__=='__main__':main()
