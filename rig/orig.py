import maya.cmds as mc


def do_orig():
    sel=mc.ls(sl=1,typ='transform')
    if sel:
        for obj in sel:
            grp=obj+'_orig'
            if mc.objExists(grp):
                mc.warning('Group orig already exits')
            else:
                grp=mc.group(em=1,n=grp)
                mc.xform(grp,t=mc.xform(obj,q=1,ws=1,t=1),ro=mc.xform(obj,q=1,ws=1,ro=1),s=mc.xform(obj,q=1,ws=1,s=1),ws=1)
                if mc.listRelatives(obj,ap=1):
                    mc.parent(grp,mc.listRelatives(obj,ap=1))
                    mc.parent(obj,grp)
                else:
                    mc.parent(obj,grp)
        mc.select(sel,r=1)
    else:
        mc.warning('Please select an object')