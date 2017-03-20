import maya.cmds as mc


def do_selRevert():
    sel=mc.ls(sl=1)
    print sel
    sel=sel[::-1]
    print sel
    mc.select(sel,r=1)