import maya.cmds as mc


def do_getAxis(obj):
    vp=mc.createNode('vectorProduct',n='_vp')
    mc.setAttr(vp+'.operation',3)
    mc.connectAttr(obj+'.worldMatrix',vp+'.matrix',f=1)
    mc.setAttr(vp+'.input1X',1)
    mc.setAttr(vp+'.input1Y',0)
    mc.setAttr(vp+'.input1Z',0)
    x=mc.getAttr(vp+'.outputX')
    if x<0:
        x=-1
    else:
        x=1
    print(x)
    mc.setAttr(vp+'.input1X',0)
    mc.setAttr(vp+'.input1Y',1)
    mc.setAttr(vp+'.input1Z',0)
    y=mc.getAttr(vp+'.outputY')
    if y<0:
        y=-1
    else:
        y=1
    print(y)
    mc.setAttr(vp+'.input1X',0)
    mc.setAttr(vp+'.input1Y',0)
    mc.setAttr(vp+'.input1Z',1)
    z=mc.getAttr(vp+'.outputZ')
    if z<0:
        z=-1
    else:
        z=1
    print(z)
    axis=[x,y,z]
    mc.delete(vp)
    return axis