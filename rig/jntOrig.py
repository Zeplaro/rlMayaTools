import maya.cmds as mc


def do_jntOrig():
    sel=mc.ls(sl=1,typ='transform')
    if sel:
        for obj in sel:
            jnt=obj+'_orig'
            if mc.objExists(jnt):
                mc.warning('Group orig already exits')
            else:
                jnt=mc.joint(n=jnt)
                mc.parent(jnt,w=1)
                mc.xform(jnt,t=mc.xform(obj,q=1,ws=1,t=1),ro=mc.xform(obj,q=1,ws=1,ro=1),s=mc.xform(obj,q=1,ws=1,s=1),ws=1)
                if mc.listRelatives(obj,ap=1):
                    mc.parent(jnt,mc.listRelatives(obj,ap=1))
                    mc.parent(obj,jnt)
                else:
                    mc.parent(obj,jnt)
        mc.select(sel,r=1)
    else:
        mc.warning('Please select an object')