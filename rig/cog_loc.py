import maya.cmds as mc


def do_avLoc():

    sel = mc.ls(sl=True, fl=True)
    if not sel:
        return
    bb = mc.exactWorldBoundingBox(sel)

    avPos = [(bb[0]+bb[3])/2, (bb[1]+bb[4])/2, (bb[2]+bb[5])/2]
    loc = mc.spaceLocator(n='avLoc#')
    mc.xform(loc, ws=True, t=avPos)
    mc.select(sel, r=True)
    return loc
