import maya.cmds as mc
# todo : don't do anything if attr connected


def do_resetAttr(*objs):

    if not objs:
        objs = mc.ls(sl=True, fl=True)
        if not objs:
            mc.warning('Select a least one object')
            return

    for obj in objs:
        for axe in 'xyz':
            for tr in 'tr':
                if mc.getAttr(obj+'.'+tr+axe, settable=True):
                    mc.setAttr(obj+'.'+tr+axe, 0)
            if mc.getAttr(obj+'.s'+axe, settable=True):
                mc.setAttr(obj+'.s'+axe, 1)
        if mc.getAttr(obj+'.v', settable=True):
            mc.setAttr(obj+'.v', True)

        attrs = mc.listAttr(obj, ud=True, visible=True) or []
        for attr in attrs:
            if not mc.getAttr(obj+'.'+attr, settable=True):
                continue
            dv = mc.addAttr(obj+'.'+attr, q=True, dv=True)
            mc.setAttr(obj+'.'+attr, dv)
    return objs
