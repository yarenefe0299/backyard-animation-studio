"""Blender camera rigs focused on real parts in the persistent master scene."""
import bpy
from mathutils import Vector
from direction import VIEWS, DETAIL_VIEWS, beat_at


def _centre(objects):
    points=[ob.matrix_world@Vector(corner) for ob in objects for corner in ob.bound_box]
    return Vector(tuple((min(v[a] for v in points)+max(v[a] for v in points))/2 for a in range(3)))


def build_anchors(mechanism, car, props):
    bpy.context.view_layer.update()
    objects=bpy.context.scene.objects
    def named(*prefixes):return [ob for ob in objects if ob.type in ('MESH','CURVE') and ob.name.startswith(prefixes)]
    anchors={
        'driveway':Vector((0,-.2,.35)), 'chamber':Vector((0,.1,-1.15)),
        'excavation':Vector((0,.1,-1.65)), 'soil':Vector((1.42,.35,-1.55)),
        'wall':Vector((-.35,2.22,-1.75)), 'load':Vector((0,-.1,-.65)),
        'pump':_centre(named('Oil reservoir rounded','Pump motor casing','Hydraulic valve manifold')),
        'line':Vector((-.65,-1.0,-3.12)), 'lift':Vector((0,.1,-.8)),
        'rim':Vector((0,-1.0,-.08)), 'flood':Vector((0,.3,-2.45)),
    }
    if car:
        anchors['sump']=_centre(named('Drainage pump / sealed blue','Drainage pump / cast volute','Drainage pump / stainless motor cap'))
        body=next(ob for ob in objects if ob.get('story_role')=='check_valve_housing')
        anchors['valve']=body.matrix_world.translation.copy()
        lenses=sorted(named('Photoelectric sensor / optical lens'),key=lambda ob:ob.location.x)
        anchors['sensor']=_centre(lenses[:1]);anchors['beam']=Vector((0,-1.82,.25))
    return anchors


def _focus(view,state):
    key=VIEWS[view][0];mech=state['mechanism']
    if key=='car':
        car=state['car']
        return Vector((car.location.x,car.location.y,mech['lift'].location.z+.65))
    if key=='cylinder':
        rod=mech['rods'][0]
        return Vector((rod.location.x,.35,(-3.55+rod.location.z-.22)/2))
    if key=='pinch':
        return state['props']['crate'].location+Vector((0,0,.18))
    return state['anchors'][key].copy()


def _rig(view,scale,state):
    target=_focus(view,state)
    # Keep a telescopic cylinder and its moving tip in frame as it extends.
    if view=='cylinder':
        height=state['mechanism']['rods'][0].location.z-.22+3.55
        scale=max(scale,height*1.35)
    if view in DETAIL_VIEWS:target.z-=scale*.06
    offset=Vector(VIEWS[view][1])
    return target+offset,target,scale


def direct(shot,seconds,state):
    from story_motion import camera_pose,ease,mix
    local=seconds-shot['start']
    beat,previous,travel,push=beat_at(shot['direction'],local,shot['duration_s'])
    scale=beat['scale']+(beat['end_scale']-beat['scale'])*ease(push)
    position,target,scale=_rig(beat['view'],scale,state)
    if travel<1:
        old_position,old_target,old_scale=_rig(previous['view'],previous['end_scale'],state)
        amount=ease(travel)
        position=Vector(mix(old_position,position,amount));target=Vector(mix(old_target,target,amount));scale=old_scale+(scale-old_scale)*amount
    camera_pose(state['camera'],position,target,scale)
    fill=state['props'].get('drainage_fill',[None])[0] if state.get('props') else None
    if fill and beat['view'] in DETAIL_VIEWS:
        toward=(position-target).normalized()
        fill.location=target+toward*(scale*.8)+Vector((0,0,scale*.25))
        fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler()
        fill.data.energy=12*scale*scale;fill.data.size=max(.35,scale*.65)
    return beat['view']
