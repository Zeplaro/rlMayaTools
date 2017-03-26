import maya.cmds as mc


def do_getAxis(obj,space='ws'):
    '''
    Find objects axis direction compared to world or parent axis
    :param str obj: object to query
    :param str space: 'ws'(default) query direction compared to world, 'os' query direction compared to parent
    :return: axis direction in a list [1,1,1]
    '''

    vp=mc.createNode('vectorProduct',n='_vp')
    mc.setAttr(vp+'.operation',3)
    if space=='os':
        mc.connectAttr(obj+'.matrix',vp+'.matrix',f=1)
    else:
        mc.connectAttr(obj+'.worldMatrix',vp+'.matrix',f=1)
    axis=[1,1,1]
    val=[1,0,0]
    xyz='XYZ'
    for i in range(3):
        j=0
        for dir in 'XYZ':
            mc.setAttr(vp+'.input1'+dir,val[j])
            j+=1
        axis[i]=mc.getAttr(vp+'.output'+xyz[i])
        if axis[i]<0:
            axis[i]=-1
        else:
            axis[i]=1
        val=val[-1:]+val[:-1]
    mc.delete(vp)
    return axis