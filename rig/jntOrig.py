import maya.cmds as mc


def do_jntOrig():
    jnts = []
    sel = mc.ls(sl=1, typ='transform')
    if sel:
        for obj in sel:
            jnt = obj+'_orig'
            if mc.objExists(jnt):
                mc.warning('Group orig already exits')
            else:
                mc.select(cl=1)
                jnt = mc.joint(n=jnt)
                jnts += [jnt]
                if mc.listRelatives(obj, ap=1):
                    mc.parent(jnt, mc.listRelatives(obj, ap=1), r=1)
                t = mc.xform(obj, q=1, ws=1, t=1)
                ro = mc.xform(obj, q=1, ws=1, ro=1)
                s = mc.xform(obj, q=1, r=1, s=1)
                mc.xform(jnt, t=t, ro=ro, s=s, ws=1)
                mc.parent(obj, jnt)
        mc.select(sel, r=1)
        return jnts
    else:
        mc.warning('Please select an object')
