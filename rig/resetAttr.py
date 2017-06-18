import maya.cmds as mc


def do_resetAttr(objs=None):

    if not objs:
        objs = mc.ls(sl=True, fl=True)

    for obj in objs:
        for axe in 'xyz':
            for tr in 'tr':
                mc.setAttr(obj+'.'+tr+axe, 0)
            mc.setAttr(obj+'.s'+axe, 1)
        mc.setAttr(obj+'.v', True)

        attrs = mc.listAttr(obj, ud=True) or []
        for attr in attrs:
            dv = mc.addAttr(obj+'.'+attr, q=True, dv=True)
            mc.setAttr(obj+'.'+attr, dv)
