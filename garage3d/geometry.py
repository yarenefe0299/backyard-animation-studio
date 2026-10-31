"""Blender modeling helpers; dimensions are meters, Z is vertical."""
import bpy
from mathutils import Vector


def empty(name, loc=(0,0,0), parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    ob.parent = parent
    return ob


def finish(ob, name, mat, parent=None, bevel=0, smooth=False):
    ob.name = name
    if mat:
        ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    if bevel:
        mod = ob.modifiers.new('Machined edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod = ob.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
        mod.keep_sharp = True
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = True
    return ob


def box(name, loc, dims, mat, parent=None, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(ob, name, mat, parent, bevel)


def cylinder(name, a, b, radius, mat, parent=None, vertices=48):
    a,b = Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    ob = bpy.context.object
    ob.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    return finish(ob, name, mat, parent, min(radius*.12,.008), True)


def pipe(name, points, radius, mat, parent=None):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 16
    c.bevel_depth = radius
    c.bevel_resolution = 4
    spline = c.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for bp,co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new(name,c)
    bpy.context.collection.objects.link(ob)
    c.materials.append(mat)
    ob.parent = parent
    return ob
