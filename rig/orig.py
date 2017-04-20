import maya.cmds as mc
# TODO : add jntOrig in


def do_orig():
    sel = mc.ls(sl=True, typ='transform', fl=True)
    grps = []
    if sel:
        for obj in sel:
            grp = obj+'_orig'
            if mc.objExists(grp):
                mc.warning('Group orig already exits')
            else:
                grp = mc.group(em=True, n=grp)
                grps += [grp]
                if mc.listRelatives(obj, ap=True):
                    mc.parent(grp, mc.listRelatives(obj, ap=True))
                    sh = mc.xform(obj, q=True, r=True, sh=True)
                    mc.xform(grp, sh=sh, ws=True)
                t = mc.xform(obj, q=True, ws=True, t=True)
                ro = mc.xform(obj, q=True, ws=True, ro=True)
                s = mc.xform(obj, q=True, r=True, s=True)
                sh = mc.xform(obj, q=True, r=True, sh=True)
                mc.xform(grp, t=t, ro=ro, s=s, sh=sh, ws=True)
                mc.parent(obj, grp)
        mc.select(sel, r=True)
        return grps
    else:
        mc.warning('Please select an object')
