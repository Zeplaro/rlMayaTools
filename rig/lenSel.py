import maya.cmds as mc


def do_lenSel ():
    sel = mc.ls(sl=1)
    size = len(sel)
    if size > 1 or size == 0:
        print(size)
        mc.warning(size)
    else:
        size = len(mc.listRelatives(sel[0], c=1))
        print(size)
        mc.warning(size)
    return size
