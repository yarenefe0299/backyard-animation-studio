"""Connected telescopic lift and hydraulic power unit. Fictional visualization."""
import bpy
import math
from mathutils.geometry import interpolate_bezier
from geometry import box, cylinder, empty, pipe


def build_mechanism(m):
    lift = empty('LIFT • master carriage')
    box('Reinforced platform deck', (0,0,-.14), (2.90,5.03,.20), m['concrete'], lift, .035)
    for x in [-1.34,1.34]:
        for z in [-.27,-.43]:
            box('Lift I-beam flange', (x,0,z), (.19,4.94,.045), m['black'], lift,.008)
        box('Lift I-beam web', (x,0,-.35), (.045,4.94,.16), m['black'],lift,.005)
    for y in [-2.32,0,2.32]:
        box('Transverse chassis bearer', (0,y,-.28), (2.72,.13,.16),m['black'],lift,.012)
    # Match the stationary driveway's running bond, including cut edge stones.
    for row in range(13):
        y=-3.9+row*.63
        for column in range(12):
            x=-3.50+column*.68+(row%2)*.34
            x0=max(-1.45,x-.33);x1=min(1.45,x+.33)
            y0=max(-2.515,y-.305);y1=min(2.515,y+.305)
            if x1-x0>.035 and y1-y0>.035:
                paving=m.get('pavers',[m['concrete']])
                box('Carriage inset paver',((x0+x1)/2,(y0+y1)/2,-.025),
                    (x1-x0,y1-y0,.055),paving[(row+column)%len(paving)],lift,.008)
    mids=[]
    rods=[]
    for x in [-1.25,1.25]:
        y=.35
        box('Anchored cylinder baseplate', (x,y,-3.60), (.45,.45,.08),m['black'],bevel=.016)
        for dx in [-.15,.15]:
            for dy in [-.15,.15]:
                cylinder('Base anchor nut',(x+dx,y+dy,-3.56),(x+dx,y+dy,-3.52),.025,m['steel'],vertices=6)
        cylinder('Fixed pressure barrel',(x,y,-3.55),(x,y,-2.36),.145,m['blue'])
        for z in [-3.48,-2.42]:
            cylinder('Barrel end collar',(x,y,z-.035),(x,y,z+.035),.17,m['steel'])
        mid = empty('Telescopic first stage', (x,y,0))
        cylinder('Honed first stage sleeve',(0,0,-3.50),(0,0,-2.40),.109,m['steel'],mid)
        cylinder('First stage gland',(0,0,-2.44),(0,0,-2.35),.124,m['black'],mid)
        rod = empty('Telescopic final rod', (x,y,0))
        cylinder('Polished final piston rod',(0,0,-1.42),(0,0,-.22),.073,m['steel'],rod)
        cylinder('Rod attachment boss',(0,0,-.27),(0,0,-.20),.114,m['steel'],rod)
        box('Bolted thrust mounting', (x,y,-.225), (.34,.33,.09),m['black'],lift,.016)
        mids.append(mid)
        rods.append(rod)
    for x in [-1.49,1.49]:
        for y in [-2.27,2.27]:
            box('Fixed guide mast', (x,y,-1.83),(.06,.12,3.5),m['steel'],bevel=.009)
            box('Carriage guide shoe',(x-math.copysign(.02,x),y,-.37),(.14,.24,.21),m['blue'],lift,.025)
            for z in [-3.3,-2.2,-1.1,-.15]:
                box('Wall rail bracket',(x,y,z),(.26,.25,.08),m['black'],bevel=.01)
    box('Oil reservoir rounded tank',(-.75,-2.10,-3.29),(.7,.58,.52),m['blue'],bevel=.065)
    cylinder('Reservoir fill cap',(-.95,-2.10,-3.03),(-.95,-2.10,-2.94),.06,m['brass'])
    box('Hydraulic valve manifold',(-.56,-2.10,-2.96),(.31,.3,.13),m['steel'],bevel=.02)
    cylinder('Pump motor casing',(-.75,-2.10,-2.88),(-.75,-1.73,-2.88),.14,m['black'])
    for y in [-2.05,-1.99,-1.93,-1.87,-1.81]:
        cylinder('Motor cooling rib',(-.75,y-.008,-2.88),(-.75,y+.008,-2.88),.155,m['black'])
    cylinder('Pressure gauge steel rim',(-.52,-2.25,-2.77),(-.52,-2.31,-2.77),.085,m['steel'])
    cylinder('Ivory pressure dial',(-.52,-2.313,-2.77),(-.52,-2.318,-2.77),.071,m['concrete'])
    pipe('Gauge needle',[(-.52,-2.321,-2.77),(-.55,-2.321,-2.73)],.004,m['black'])
    paths=[]
    for x in [-1.25,1.25]:
        points=[(-.40,-2.10,-2.97),(-.14,-2.10,-3.12),(x,-1.85,-3.12),(x,-.1,-3.12),(x,.22,-3.30),(x,.35,-3.30)]
        line=pipe('Transparent pressure line',points,.043,m['ghost'])
        bpy.context.view_layer.update()
        bezier=line.data.splines[0].bezier_points
        samples=[]
        for a,b in zip(bezier, list(bezier)[1:]):
            samples.extend(tuple(p) for p in interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,32)[:-1])
        samples.append(tuple(bezier[-1].co))
        paths.append(samples)
        pipe('Steel return line',[(x,.35,-2.52),(x,.05,-2.52),(x,-.20,-3.34),(x,-1.9,-3.42),(-.8,-2.10,-3.42)],.022,m['steel'])
        for z in [-3.30,-2.52]:
            cylinder('Threaded barrel port',(x,.15,z),(x,.35,z),.05,m['brass'])
        for y in [-1.7,-.85,-.25]:
            box('Hydraulic line saddle',(x,y,-3.16),(.15,.045,.035),m['black'],bevel=.008)
    pulses=[]
    for path in paths:
        for j in range(14):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.026)
            ob=bpy.context.object
            ob.name='Oil flow tracer'
            ob.data.materials.append(m['fluid'])
            pulses.append((ob,path,j/14))
    overlays=[]
    for x in [-1.25,1.25]:
        overlays.append(cylinder('Blue cylinder x-ray envelope',(x,.35,-3.55),(x,.35,-2.32),.178,m['ghost']))
    box('Sump drain surround',(.7,1.8,-3.63),(.7,.5,.035),m['black'],bevel=.04)
    for i in range(11):
        box('Drain grate bar',(.4+i*.06,1.8,-3.60),(.021,.43,.03),m['steel'],bevel=.005)
    pipe('Sump discharge pipe',[(.7,2.05,-3.58),(1.05,2.2,-3.5),(1.1,2.3,-2.5),(1.1,2.4,-.2)],.047,m['concrete'])
    return {'lift':lift,'mid_stages':mids,'rods':rods,'pulses':pulses,'overlays':overlays}


def point_on_polyline(points,t):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
    distance=(t%1)*sum(lengths)
    for a,b,length in zip(points,points[1:],lengths):
        if distance <= length:
            return tuple(x+(y-x)*distance/length for x,y in zip(a,b))
        distance-=length
    return points[-1]


def pose(mechanism,z,frame):
    mechanism['lift'].location.z=z
    travel=z+2.1
    for ob in mechanism['mid_stages']:
        ob.location.z=travel/2
    for ob in mechanism['rods']:
        ob.location.z=z
    for ob,path,offset in mechanism['pulses']:
        ob.location=point_on_polyline(path,offset+(frame-1)/70)
