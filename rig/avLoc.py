import maya.cmds as mc
import utils as ut


def get_component(obj):
    
    comps = mc.ls(mc.polyListComponentConversion(obj, tv=True), fl=True) or []

    [comps.append(x) for x in [obj] if '.cv' in x]

    if mc.nodeType(ut.getShape(obj)) == 'nurbsCurve' and '.cv' not in obj:
        complen = mc.getAttr(obj+'.cp', s=1)
        print(complen)
        if complen:
            for j in range(complen):
                comps.append(obj+'.cp['+str(j)+']')

    return comps


def do_avLoc():

    sel = mc.ls(sl=True, fl=True) or []
    comps = []
    for i in sel:
        comps.extend(get_component(i))

    if not comps:
        mc.warning('Select components or meshes and try again')
        return

    pos = []
    for comp in comps:
        pos.append(mc.xform(comp, q=True, ws=True, t=True))

    posx = []
    posy = []
    posz = []
    for x, y, z in pos:
        posx.append(x)
        posy.append(y)
        posz.append(z)
    av = [(min(posx)+max(posx))/2, (min(posy)+max(posy))/2, (min(posz)+max(posz))/2]
    loc = mc.spaceLocator(n='avLoc#')
    mc.xform(loc, ws=True, t=av)
    mc.select(sel, r=True)
    return loc
