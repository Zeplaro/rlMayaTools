import maya.cmds as mc


def do_selRevert():
    sel = mc.ls(sl=True, fl=True)
    print(sel)
    sel = sel[::-1]
    print(sel)
    mc.select(sel, r=True)
    return sel
