import maya.cmds as mc


def do_orig(jnt=False, objs=None):

    if not objs:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if not objs:
            mc.warning('Please select an object')
            return

    grps = []
    for obj in objs:
        grp = obj+'_orig'
        if mc.objExists(grp):
            mc.warning(grp+' already exits')
            continue
        if jnt:
            mc.select(cl=True)
            grp = mc.joint(n=grp)
        else:
            grp = mc.group(em=True, n=grp)
        grps += [grp]

        if mc.listRelatives(obj, ap=True):
            if jnt:
                mc.parent(grp, mc.listRelatives(obj, ap=True), r=True)
            else:
                mc.parent(grp, mc.listRelatives(obj, ap=True))
                sh = mc.xform(obj, q=True, r=True, sh=True)
                mc.xform(grp, sh=sh, ws=True)
        t = mc.xform(obj, q=True, ws=True, t=True)
        ro = mc.xform(obj, q=True, ws=True, ro=True)
        s = mc.xform(obj, q=True, r=True, s=True)
        if jnt:
            mc.xform(grp, t=t, ro=ro, s=s, ws=True)
            mc.makeIdentity(grp, apply=True, r=1)
        else:
            sh = mc.xform(obj, q=True, r=True, sh=True)
            mc.xform(grp, t=t, ro=ro, s=s, sh=sh, ws=True)

        mc.parent(obj, grp)
    return grps
