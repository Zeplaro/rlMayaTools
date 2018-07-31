import maya.cmds as mc


def len_sel():
    size = len(mc.ls(sl=True, fl=True))
    print(size)
    mc.warning(size)
    return size
