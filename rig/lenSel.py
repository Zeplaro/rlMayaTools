import maya.cmds as mc


def doLenSel ():
    sel = mc.ls(sl=1, typ='transform')
    size = len(sel)
    if size > 1 or size == 0:
        print size
        mc.warning(size)
    else:
        size = len(mc.listRelatives(sel[0], c=1, typ='transform'))
        print size
        mc.warning(size)