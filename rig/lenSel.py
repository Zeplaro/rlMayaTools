import maya.cmds as mc


def do_lenSel ():

    size = len(mc.ls(sl=True, fl=True))
    print(size)
    mc.warning(size)
    return size
