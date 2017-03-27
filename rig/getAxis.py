import maya.cmds as mc
import math


def do_getAxis(obj, os=False, exact=False):
    '''
    Find objects axis direction compared to world or parent axis
    :param str obj: object to query
    :param bool os: False(default) query direction compared to world, True query direction compared to parent
    :return: axis direction in a list [1,1,1]
    '''

    vp=mc.createNode('vectorProduct',n='_vp')
    mc.setAttr(vp+'.operation',3)
    if os:
        mc.connectAttr(obj+'.matrix',vp+'.matrix',f=1)
    else:
        mc.connectAttr(obj+'.worldMatrix',vp+'.matrix',f=1)
    axis=[1,1,1]
    val=[1,0,0]
    xyz='XYZ'
    fullval=[]
    for i in range(3):
        j=0
        for dir in xyz:
            mc.setAttr(vp+'.input1'+dir,val[j])
            j+=1
        for dir in xyz:
            fullval.append(mc.getAttr(vp+'.output'+dir))
        axis[i]=mc.getAttr(vp+'.output'+xyz[i])
        if axis[i]<0:
            axis[i]=-1
        else:
            axis[i]=1
        val=val[-1:]+val[:-1]
    fullval=[fullval[:3]]+[fullval[3:6]]+[fullval[6:]]
    mc.delete(vp)
    if exact:
        return axis,fullval
    else:
        return axis


def getMirrorTable(master,slave):

    M=getAxisDir(master)
    S=getAxisDir(slave)
    mirtable=[1,1,1]
    for i in range(3):
        if not M[i] == S[i]:
            mirtable[i]=-1
    return mirtable

def getAxisDir(obj):
    objdir=do_getAxis(obj, exact=True)[-1]
    face=[]
    for i in range(3):
        val = []
        for j in range(3):
            val.append(objdir[i][j])
        if abs(val[0])>abs(val[1]):
            if abs(val[0])>abs(val[2]):
                if val[0]<0:
                    face.append('-x')
                else:
                    face.append('x')
            else:
                if val[2]<0:
                    face.append('-z')
                else:
                    face.append('z')
        else:
            if abs(val[1])>abs(val[2]):
                if val[1]<0:
                    face.append('-y')
                else:
                    face.append('y')
            else:
                if val[2]<0:
                    face.append('-z')
                else:
                    face.append('z')
    return face

