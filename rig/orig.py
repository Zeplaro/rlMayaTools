import maya.cmds as mc


def do_orig(objs=None, jnt=False):

    if not objs:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if not objs:
            mc.warning('Please select an object')
            return

    origs = []
    for obj in objs:
        orig = obj+'_orig'
        if jnt:
            mc.select(cl=True)
            orig = mc.joint(n=orig)
        else:
            orig = mc.group(em=True, n=orig)
        origs += [orig]

        if mc.listRelatives(obj, ap=True):
            if jnt:
                mc.parent(orig, mc.listRelatives(obj, ap=True), r=True)
            else:
                mc.parent(orig, mc.listRelatives(obj, ap=True))
                sh = mc.xform(obj, q=True, r=True, sh=True)
                mc.xform(orig, sh=sh, ws=True)
        t = mc.xform(obj, q=True, ws=True, t=True)
        ro = mc.xform(obj, q=True, ws=True, ro=True)
        s = mc.xform(obj, q=True, r=True, s=True)
        if jnt:
            mc.xform(orig, t=t, ro=ro, s=s, ws=True)
            mc.makeIdentity(orig, apply=True, r=True)
        else:
            sh = mc.xform(obj, q=True, r=True, sh=True)
            mc.xform(orig, t=t, ro=ro, s=s, sh=sh, ws=True)

        mc.parent(obj, orig)
    return origs
