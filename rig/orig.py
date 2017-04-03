import maya.cmds as mc


def do_orig():
    sel = mc.ls(sl=1, typ='transform')
    grps = []
    if sel:
        for obj in sel:
            grp = obj+'_orig'
            if mc.objExists(grp):
                mc.warning('Group orig already exits')
            else:
                grp = mc.group(em=1, n=grp)
                grps += [grp]
                if mc.listRelatives(obj, ap=1):
                    mc.parent(grp, mc.listRelatives(obj, ap=1))
                    sh = mc.xform(obj, q=1, r=1, sh=1)
                    mc.xform(grp, sh=sh, ws=1)
                t = mc.xform(obj, q=1, ws=1, t=1)
                ro = mc.xform(obj, q=1, ws=1, ro=1)
                s = mc.xform(obj, q=1, r=1, s=1)
                sh = mc.xform(obj, q=1, r=1, sh=1)
                mc.xform(grp, t=t, ro=ro, s=s, sh=sh, ws=1)
                mc.parent(obj, grp)
        mc.select(sel, r=1)
        return grps
    else:
        mc.warning('Please select an object')
