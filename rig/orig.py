import maya.cmds as mc


def orig(objs=None, jnt=False):

    if not objs:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if not objs:
            mc.warning('Please select an object')
            return

    origs = []
    for obj in objs:
        orig_grp = '{}_orig'.format(obj)
        if jnt:
            mc.select(cl=True)
            orig_grp = mc.joint(n=orig_grp)
        else:
            orig_grp = mc.group(em=True, n=orig_grp)
        origs += [orig_grp]

        if mc.listRelatives(obj, ap=True):
            if jnt:
                mc.parent(orig_grp, mc.listRelatives(obj, ap=True), r=True)
            else:
                mc.parent(orig_grp, mc.listRelatives(obj, ap=True))
                sh = mc.xform(obj, q=True, r=True, sh=True)
                mc.xform(orig_grp, sh=sh, ws=True)
        t = mc.xform(obj, q=True, ws=True, t=True)
        ro = mc.xform(obj, q=True, ws=True, ro=True)
        s = mc.xform(obj, q=True, r=True, s=True)
        if jnt:
            mc.xform(orig_grp, t=t, ro=ro, s=s, ws=True)
            mc.makeIdentity(orig_grp, apply=True, r=True)
        else:
            sh = mc.xform(obj, q=True, r=True, sh=True)
            mc.xform(orig_grp, t=t, ro=ro, s=s, sh=sh, ws=True)

        mc.parent(obj, orig_grp)
    return origs
