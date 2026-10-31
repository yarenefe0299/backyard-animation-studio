#!/usr/bin/env python3
"""One story-folder interface for planning, offline audio and verified assembly."""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
PRESETS={'draft':(270,480,16),'review':(540,960,64),'final':(1080,1920,128)}


def story_path(value):
    path=Path(value).resolve()
    if not path.is_relative_to((REPO/'stories').resolve()):
        raise ValueError('Story folders must be inside this repository\'s stories/ directory')
    return path


def effective_story(directory,scope):
    from story import load_story
    story=load_story(story_path(directory))
    story['source_duration_s']=story['duration_s']
    story['scope']=scope
    if scope=='opening':
        story['shots']=story['shots'][:1]
        story['frames']=story['shots'][0]['end_frame']
        story['duration_s']=story['frames']/story['fps']
    return story


def make_plan(directory,output,quality='draft',scope='opening'):
    story=effective_story(directory,scope)
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    size=10 if quality=='final' else (90 if quality=='draft' and story['frames']>=600 else 30)
    count=math.ceil(story['frames']/size)
    if count>256:raise ValueError('Story exceeds the 256-chunk workflow limit; split it into episodes')
    matrix={'include':[{'id':f'{i:03d}','from':i*size+1,'to':min(story['frames'],(i+1)*size)} for i in range(count)]}
    renderer_digest=hashlib.sha256()
    for path in sorted(HERE.glob('*.py')):
        if not path.name.startswith('test_'):
            renderer_digest.update(path.name.encode());renderer_digest.update(path.read_bytes())
    plan={**story,'renderer_sha256':renderer_digest.hexdigest(),'quality':quality,'resolution':list(PRESETS[quality][:2]),'cycles_samples':PRESETS[quality][2],
          'matrix':matrix,'story_folder':Path(story['root']).relative_to(REPO).as_posix(),
          'denoising':'Intel Open Image Denoise 2.3.3 CPU, color-only sRGB; raw inputs preserved',
          'status':'planned; no renders or encoded video claimed'}
    previous=output/'plan.json'
    if previous.exists() and any((output/'frames').glob('frame_*.png')):
        old=json.loads(previous.read_text())
        if any(old.get(k)!=plan.get(k) for k in ('source_sha256','renderer_sha256','quality','scope')):
            raise ValueError('Existing frames belong to a different plan. Choose a fresh output directory.')
    previous.write_text(json.dumps(plan,indent=2)+'\n')
    return plan


def prepare(directory,output,quality,scope):
    from audio import prepare_audio
    plan=make_plan(directory,output,quality,scope)
    return prepare_audio(plan,story_path(directory),output)


def assemble(output,denoise=True):
    from encode import inspect_sequence
    output=Path(output).resolve()
    plan=json.loads((output/'plan.json').read_text())
    frames,fps=plan['frames'],plan['fps']
    target=output/'story.mp4';report_path=output/'video_report.json';temporary=output/'.story.encoding.mp4'
    target.unlink(missing_ok=True);report_path.unlink(missing_ok=True)
    width,height=inspect_sequence(output/'frames',frames)
    if [width,height]!=plan['resolution']:raise ValueError('Rendered resolution does not match the plan')
    if not (output/'soundtrack.wav').is_file() or not (output/'captions.ass').is_file():
        raise ValueError('Prepare the story audio and captions before assembly')
    source='frames'
    denoise_report=None
    if denoise:
        from denoise import install_oidn,denoise_frames
        executable=install_oidn()
        denoise_report=denoise_frames(output/'frames',output/'denoised',executable)
        inspect_sequence(output/'denoised',frames);source='denoised'
        (output/'denoise_report.json').write_text(json.dumps(denoise_report,indent=2)+'\n')
    try:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-threads','2',
            '-framerate',str(fps),'-start_number','1','-i',f'{source}/frame_%04d.png',
            '-i','soundtrack.wav','-map','0:v:0','-map','1:a:0','-frames:v',str(frames),
            '-vf','ass=captions.ass,scale=out_color_matrix=bt709:out_range=tv',
            '-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p',
            '-x264-params','colorprim=bt709:transfer=bt709:colormatrix=bt709',
            '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv',
            '-c:a','aac','-b:a','160k','-ar','48000','-t',str(frames/fps),'-movflags','+faststart',temporary.name],cwd=output,check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(temporary)],text=True))
        video=next(s for s in info['streams'] if s['codec_type']=='video')
        audio=next(s for s in info['streams'] if s['codec_type']=='audio')
        expected={'codec_name':'h264','pix_fmt':'yuv420p','width':width,'height':height,'nb_read_frames':str(frames),
                  'color_space':'bt709','color_primaries':'bt709','color_transfer':'bt709','color_range':'tv'}
        for k,v in expected.items():
            if video.get(k)!=v:raise ValueError(f'Encoded {k}: {video.get(k)!r}, expected {v!r}')
        if Fraction(video['r_frame_rate'])!=fps or abs(float(video['duration'])-frames/fps)>1/fps:
            raise ValueError('Encoded video timing differs from planned story')
        if audio['codec_name']!='aac' or audio['sample_rate']!='48000' or abs(float(audio['duration'])-frames/fps)>.08:
            raise ValueError('Encoded audio does not cover the story correctly')
        temporary.replace(target)
        report={'status':'encoded_and_verified','story_id':plan['id'],'scope':plan['scope'],
                'source_sha256':plan['source_sha256'],'renderer_sha256':plan.get('renderer_sha256'),'video':'story.mp4','frames':frames,'fps':fps,'duration_seconds':frames/fps,
                'video_stream':video,'audio_stream':audio,'captions':'burned bold outlined ASS; SRT also exported',
                'denoising':bool(denoise_report),'visual_approval':'pending user review',
                'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        report_path.write_text(json.dumps(report,indent=2)+'\n')
        # A small chronological contact sheet is a review artifact, never input to
        # the video. It is decoded from the finished MP4 after verification.
        indexes=sorted(set([0,frames//2,frames-1]+[(s['start_frame']+s['end_frame'])//2-1 for s in plan['shots']]))
        expression='+'.join(f'eq(n\\,{n})' for n in indexes)
        rows=math.ceil(len(indexes)/3)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-i',str(target),
                        '-vf',f'select={expression},scale=180:320,tile=3x{rows}','-frames:v','1','-threads','1',str(output/'contact-sheet.png')],check=True)
        return report
    finally:temporary.unlink(missing_ok=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ['plan','audio','run']:
        p=commands.add_parser(name);p.add_argument('--story',type=Path,default=REPO/'stories/hidden-garage')
        p.add_argument('--output',type=Path,default=HERE/'output/story');p.add_argument('--quality',choices=PRESETS,default='draft')
        p.add_argument('--scope',choices=['opening','full'],default='opening')
        if name=='plan':p.add_argument('--github-output',type=Path)
    p=commands.add_parser('assemble');p.add_argument('--output',type=Path,default=HERE/'output/story');p.add_argument('--no-denoise',action='store_true')
    args=parser.parse_args()
    if args.command=='plan':
        result=make_plan(args.story,args.output,args.quality,args.scope)
        if args.github_output:
            with args.github_output.open('a') as f:f.write('matrix='+json.dumps(result['matrix'],separators=(',',':'))+'\n')
        print(json.dumps({k:result[k] for k in ['id','frames','fps','duration_s','resolution','matrix']},indent=2))
    elif args.command=='audio':print(json.dumps(prepare(args.story,args.output,args.quality,args.scope),indent=2))
    elif args.command=='assemble':print(json.dumps(assemble(args.output,not args.no_denoise),indent=2))
    else:
        make_plan(args.story,args.output,args.quality,args.scope)
        prepare(args.story,args.output,args.quality,args.scope)
        subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python',str(HERE/'render_story.py'),'--',
                        '--story',str(args.story),'--output',str(args.output),'--quality',args.quality,'--scope',args.scope,'--mode','all'],check=True)
        print(json.dumps(assemble(args.output),indent=2))


if __name__=='__main__':main()
