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
                if mc.getAttr('{}.{}{}'.format(obj, tr, axe), settable=True):
                    mc.setAttr('{}.{}{}'.format(obj, tr, axe), 0)
            if mc.getAttr('{}.s{}'.format(obj, axe), settable=True):
                mc.setAttr('{}.s{}'.format(obj, axe), 1)
        if mc.getAttr('{}.v'.format(obj), settable=True):
            mc.setAttr('{}.v'.format(obj), True)

        attrs = mc.listAttr(obj, ud=True, visible=True) or []
        for attr in attrs:
            if not mc.getAttr('{}.'.format(obj, attr), settable=True):
                continue
            dv = mc.addAttr('{].{]'.format(obj, attr), q=True, dv=True)
            mc.setAttr('{}.'.format(obj, attr), dv)
    return objs
