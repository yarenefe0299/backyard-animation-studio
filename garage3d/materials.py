"""Shared procedural materials. No external textures or asset downloads."""
import bpy


def surface(name, color, roughness=.5, metallic=0, noise=0, scale=45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    if noise:
        tex = n.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = scale
        tex.inputs['Detail'].default_value = 3
        ramp = n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .18
        ramp.color_ramp.elements[0].color = (*(c*.78 for c in color), 1)
        ramp.color_ramp.elements[1].position = .82
        ramp.color_ramp.elements[1].color = (*(min(1, c*1.12) for c in color), 1)
        m.node_tree.links.new(tex.outputs['Fac'], ramp.inputs[0])
        m.node_tree.links.new(ramp.outputs[0], p.inputs['Base Color'])
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .22
        bump.inputs['Distance'].default_value = noise
        m.node_tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs[0], p.inputs['Normal'])
    return m


def library():
    mats = {
        'silver': surface('Satin silver automotive clearcoat', (.52,.57,.60), .24, .8, .0004, 210),
        'steel': surface('Brushed stainless steel', (.38,.43,.46), .29, .86, .0008, 160),
        'black': surface('Graphite powder coat', (.037,.045,.048), .43, .4, .0006),
        'rubber': surface('Carbon rubber', (.018,.022,.025), .78, 0, .002, 100),
        'concrete': surface('Warm mineral concrete', (.43,.43,.39), .85, 0, .018, 36),
        'glass': surface('Smoked blue automotive glass', (.065,.12,.15), .12, .32),
        'blue': surface('Hydraulic enamel blue', (.035,.19,.34), .32, .5),
        'brass': surface('Machined brass fittings', (.47,.30,.105), .27, .75),
    }
    mats['silver'].node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value = .42
    p = mats['glass'].node_tree.nodes.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value = .22
    p.inputs['IOR'].default_value = 1.46
    ghost = surface('Blue transparent diagnostic jacket', (.08,.44,.8), .17, .05)
    n = ghost.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Transmission Weight'].default_value = .35
    transparent = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .22
    ghost.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
    ghost.node_tree.links.new(p.outputs[0], mix.inputs[2])
    ghost.node_tree.links.new(mix.outputs[0], n.get('Material Output').inputs['Surface'])
    mats['ghost'] = ghost
    fluid = surface('Blue oil diagnostic tracer', (.03,.43,.8), .2, .12)
    p = fluid.node_tree.nodes.get('Principled BSDF')
    p.inputs['Emission Color'].default_value = (.01,.18,.45,1)
    p.inputs['Emission Strength'].default_value = .45
    mats['fluid'] = fluid
    return mats
