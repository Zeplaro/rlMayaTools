import maya.cmds as mc


def do_avLoc():

    sel = mc.ls(sl=True, fl=True)
    vtxs = mc.ls(mc.polyListComponentConversion(sel, tv=True), fl=True)
    if not vtxs:
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
