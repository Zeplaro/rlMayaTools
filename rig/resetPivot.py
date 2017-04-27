import maya.cmds as mc


def do_resetPivot(objs=None):

    if not objs:
        objs = mc.ls(sl=True, fl=True)

    for obj in objs:
        pivot = mc.group(em=True, w=True, n=obj+'Pivot#')
        mc.delete(mc.parentConstraint(obj, pivot, mo=False))
        dad = mc.listRelatives(obj, ap=True, f=True)
        mc.parent(obj, pivot)
        mc.makeIdentity(a=True, r=False, s=False, t=True)
        if dad:
            mc.parent(obj, dad)
        else:
            mc.parent(obj, w=True)
        mc.delete(pivot)

    return objs
