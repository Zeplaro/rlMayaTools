import maya.cmds as mc


def do_avLoc():

    vtxs = [x for x in mc.ls(sl=True, fl=True) if '.vtx' in x] or []
    posx = []
    posy = []
    posz = []
    for vtx in vtxs:
        posx.append(mc.xform(vtx, q=1, ws=1, t=1)[0])
        posy.append(mc.xform(vtx, q=1, ws=1, t=1)[1])
        posz.append(mc.xform(vtx, q=1, ws=1, t=1)[2])
    av = [(min(posx)+max(posx))/2, (min(posy)+max(posy))/2, (min(posz)+max(posz))/2]
    loc = mc.spaceLocator(n='avLoc_#')
    mc.xform(loc, ws=1, t=av)
    return loc
