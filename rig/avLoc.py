import maya.cmds as mc
import getShape as gs
# todo : cv compatible


def get_component(obj):
    
    comps = mc.ls(mc.polyListComponentConversion(obj, tv=True), fl=True) or []
    if not mc.nodeType(gs.do_getShape(obj)) == 'nurbsCurve':
        complen = mc.getAttr(obj+'.cp', s=1)
        print(complen)
        if complen:
            for j in range(complen):
                comps.append(obj+'.cp['+str(j)+']')
    [comps.append(x) for x in [obj] if '.cv' in x]
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
    for vtx in vtxs:
        pos.append(mc.xform(vtx, q=True, ws=True, t=True))

    posx = []
    posy = []
    posz = []
    for each in pos:
        posx.append(each[0])
        posy.append(each[1])
        posz.append(each[2])
    av = [(min(posx)+max(posx))/2, (min(posy)+max(posy))/2, (min(posz)+max(posz))/2]
    loc = mc.spaceLocator(n='avLoc#')
    mc.xform(loc, ws=True, t=av)
    mc.select(sel, r=True)
    return loc
