import maya.cmds as mc


def do_selShape():
    sel=mc.ls(sl=1)
    mc.select(cl=1)
    for obj in sel:
        child=mc.listRelatives(obj,c=1,typ='shape')
        mc.select(child,add=1)