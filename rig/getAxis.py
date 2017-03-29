import maya.cmds as mc
import math


def do_getAxis(obj, os=False, exact=False):
    """
    Find objects axis direction compared to world or parent axis
    :param str obj: object to query
    :param bool os: False(default) query direction compared to world, True query direction compared to parent
    :param bool exact: True return exact direction value for each axis
    :return: axis direction in a list, e.g.:[1, 1, 1]
    """

    vp = mc.createNode('vectorProduct', n='_vp')
    mc.setAttr(vp+'.operation', 3)
    if os:
        mc.connectAttr(obj+'.matrix', vp+'.matrix', f=1)
    else:
        mc.connectAttr(obj+'.worldMatrix', vp+'.matrix', f=1)
    axis = [1, 1, 1]
    val = [1, 0, 0]
    xyz = 'XYZ'
    fullval = []
    for i in range(3):
        j = 0
        for dir in 'XYZ':
            mc.setAttr(vp+'.input1'+dir, val[j])
            j += 1
        for dir in 'XYZ':
            fullval.append(mc.getAttr(vp+'.output'+dir))
        axis[i] = mc.getAttr(vp+'.output'+xyz[i])
        if axis[i] < 0:
            axis[i] = -1
        else:
            axis[i] = 1
        val = val[-1:]+val[:-1]
    fullval = [fullval[:3]]+[fullval[3:6]]+[fullval[6:]]
    mc.delete(vp)
    if exact:
        return axis, fullval
    else:
        return axis


def getMirrorTable (master, slave, miraxis='x'):
    """
    Return a mirror table between two object on chosen axis
    :param str master: object to compare to slave
    :param str slave: object to compare to master
    :param str miraxis: 'x'(default) chosen world axis on wich mirror is wanted
    :return: list: return a mirror table list, e.g.:[-1, 1, 1]
    """

    m = getAxisDir(master)
    s = getAxisDir(slave)
    mirtable = [1, 1, 1]
    for i in range(3):
        if m[i][-1] == s[i][-1]:
            if not m[i][0] == s[i][0]:
                mirtable[i] = -1
            if m[i][-1] == miraxis:
                mirtable[i] *= -1
        else:
            mirtable[i] = 0
    return mirtable


def getAxisDir (obj):
    """
    Return a list of axis direction compared to world
    :param str obj: object on wich to check the axis
    :return: list: return an axis direction list compared to world,
                    first index giving the x axis direction and so on e.g.:[y, -z, -x],
                    for a object matching world axis it will return : [x, y, z]
    """

    objdir = do_getAxis(obj, exact=True)[-1]
    dir = []
    for i in range(3):
        val = []
        for j in range(3):
            val.append(objdir[i][j])
        if abs(val[0]) > abs(val[1]):
            if abs(val[0]) > abs(val[2]):
                if val[0] < 0:
                    dir.append('-x')
                else:
                    dir.append('x')
            else:
                if val[2] < 0:
                    dir.append('-z')
                else:
                    dir.append('z')
        else:
            if abs(val[1]) > abs(val[2]):
                if val[1] < 0:
                    dir.append('-y')
                else:
                    dir.append('y')
            else:
                if val[2] < 0:
                    dir.append('-z')
                else:
                    dir.append('z')
    return dir
