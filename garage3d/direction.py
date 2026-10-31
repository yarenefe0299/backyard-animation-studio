"""Portable, frame-checked camera beats supplied by a story folder.

A beat names a modeled focal subject. It holds that subject until the next beat;
``move`` is the time spent travelling into the new view (zero means a cut).
"""
import math


# focus, camera offset from focus, vertical field of view in metres, caption y.
# Positions are resolved against the persistent scene by shot_director.py.
VIEWS = {
    'approach': ('car', (6.5,-12,6), 7.8, 1510),
    'driveway': ('driveway', (7,-12,7), 7.2, 1510),
    'chamber': ('chamber', (6,-13,6), 8.5, 580),
    'excavation': ('excavation', (5,-11,5), 6.8, 580),
    'soil': ('soil', (5,-9,2.8), 3.8, 1540),
    'wall': ('wall', (4,-10,2.8), 4.7, 1530),
    'load': ('load', (4,-10,2.7), 5.8, 1510),
    'pump': ('pump', (1.2,-5,1.1), 1.55, 1640),
    'line': ('line', (.4,-4,2.0), 2.65, 1640),
    'cylinder': ('cylinder', (2.3,-6,1.3), 2.8, 1640),
    'lift': ('lift', (5,-12,4.8), 7.8, 570),
    'rim': ('rim', (5,-8,4.3), 5.7, 1490),
    'flood': ('flood', (5,-10,2.8), 6.0, 580),
    'sump': ('sump', (-1.2,-6,.8), 1.7, 1640),
    'valve': ('valve', (.25,-4,.15), .68, 1660),
    'pinch': ('pinch', (3,-5,2.6), 2.8, 1530),
    'sensor': ('sensor', (4,-3,1.3), .95, 1560),
    'beam': ('beam', (4,-8,3.3), 5.4, 1530),
    'seam': ('rim', (4,-6,5), 3.5, 550),
}
LAB_VIEWS = frozenset({'pump','line','cylinder','lift'})
DETAIL_VIEWS = frozenset({'pump','line','cylinder','sump','valve'})


def _number(value, label, minimum, maximum):
    if type(value) not in (int,float) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f'{label} must be a finite number from {minimum} to {maximum}')
    return float(value)


def validate_direction(document, shots, template, fps):
    if not isinstance(document,dict) or set(document) != {'schema_version','shots'} or type(document['schema_version']) is not int or document['schema_version'] != 1:
        raise ValueError('direction.json needs schema_version=1 and a shots object')
    mapping=document['shots']
    if not isinstance(mapping,dict):raise ValueError('Direction shots must be an object keyed by script shot ID')
    by_id={shot['id']:shot for shot in shots}
    if set(mapping)-set(by_id):raise ValueError('Direction references an unknown script shot ID')
    result={}
    for shot_id,beats in mapping.items():
        shot=by_id[shot_id]
        if not isinstance(beats,list) or not beats:raise ValueError(f'{shot_id}: direction needs at least one beat')
        normalized=[]
        for index,beat in enumerate(beats):
            if not isinstance(beat,dict) or set(beat)-{'at','view','move','scale','end_scale'} or not {'at','view'} <= set(beat):
                raise ValueError(f'{shot_id}: each camera beat needs at/view and only optional move/scale/end_scale')
            at=_number(beat['at'],f'{shot_id} at',0,shot['duration_s'])
            move=_number(beat.get('move',0),f'{shot_id} move',0,shot['duration_s'])
            for value in (at,move):
                if abs(value*fps-round(value*fps))>1e-6:raise ValueError(f'{shot_id}: camera timing must cover whole frames')
            if at >= shot['duration_s'] or at+move >= shot['duration_s']:
                raise ValueError(f'{shot_id}: camera beat/arrival must be before the shot ends')
            if (index==0 and (at!=0 or move!=0)) or (index>0 and at <= normalized[-1]['at']):
                raise ValueError(f'{shot_id}: beats must start at zero with a cut and increase strictly')
            view=beat['view']
            if not isinstance(view,str) or view not in VIEWS or (template=='hydraulic_lab' and view not in LAB_VIEWS):
                raise ValueError(f'{shot_id}: unsupported focal view {view!r} for {template}')
            scale=_number(beat.get('scale',VIEWS[view][2]),f'{shot_id} scale',.35,30)
            end_scale=_number(beat.get('end_scale',scale),f'{shot_id} end_scale',.35,30)
            normalized.append({'at':at,'view':view,'move':move,'scale':scale,'end_scale':end_scale})
        for first,second in zip(normalized,normalized[1:]):
            if first['at']+first['move']>second['at']:raise ValueError(f'{shot_id}: camera travel overlaps the next beat')
        result[shot_id]=normalized
    return result


def beat_at(beats, seconds, duration):
    """Return current/previous beat, travel amount and post-arrival push amount."""
    index=max(i for i,beat in enumerate(beats) if beat['at']<=max(0,seconds)+1e-7)
    beat=beats[index];previous=beats[max(0,index-1)]
    travel=min(1,max(0,(seconds-beat['at'])/beat['move'])) if beat['move'] else 1.
    end=beats[index+1]['at'] if index+1<len(beats) else duration
    start=beat['at']+beat['move']
    push=min(1,max(0,(seconds-start)/max(1e-9,end-start)))
    return beat,previous,travel,push


def caption_y(shot, seconds):
    beats=shot.get('direction')
    if not beats:return 650 if shot.get('camera') in {'hydraulics','cutaway'} else 1500
    beat,_,_,_=beat_at(beats,max(0,seconds-shot['start']),shot['duration_s'])
    return VIEWS[beat['view']][3]
