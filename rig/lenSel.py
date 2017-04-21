import maya.cmds as mc


def do_lenSel ():

    sel = mc.ls(sl=True, fl=True)
    size = len(sel)
    print(size)
    mc.warning(size)
    return size
