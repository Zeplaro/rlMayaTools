#Creates orig group for each selected objects
import maya.cmds as mc
def doOrig ():
    sel=mc.ls(sl=1)
    if sel:
        for each in sel:
            if mc.objExists(each+'_orig'):
                mc.warning('Group orig already exits')
            else:
                mc.group(em=1,n=each+'_orig')
                mc.xform(each+'_orig',t=mc.xform(each,q=1,ws=1,t=1),ro=mc.xform(each,q=1,ws=1,ro=1),ws=1)
                if mc.listRelatives(each,ap=1):
                    mc.parent(each+'_orig',mc.listRelatives(each,ap=1))
                    mc.parent(each,each+'_orig')
                else:
                    mc.parent(each,each+'_orig')
    else:
        mc.warning('Please select an object')
