import maya.cmds as mc


def do_jntOrig():

    jnts = []
    sel = mc.ls(sl=True, typ='transform', fl=True)
    if sel:
        for obj in sel:
            jnt = obj+'_orig'
            if mc.objExists(jnt):
                mc.warning('Group orig already exits')
            else:
                mc.select(cl=True)
                jnt = mc.joint(n=jnt)
                jnts += [jnt]
                if mc.listRelatives(obj, ap=True):
                    mc.parent(jnt, mc.listRelatives(obj, ap=True), r=True)
                t = mc.xform(obj, q=True, ws=True, t=True)
                ro = mc.xform(obj, q=True, ws=True, ro=True)
                s = mc.xform(obj, q=True, r=True, s=True)
                mc.xform(jnt, t=t, ro=ro, s=s, ws=True)
                mc.parent(obj, jnt)
        mc.select(sel, r=True)
        return jnts
    else:
        mc.warning('Please select an object')
