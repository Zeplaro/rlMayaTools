import maya.cmds as mc


def get_skinCluster(obj):

    sknclust = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')
    return sknclust[0] if sknclust else None


def get_shape(obj):

    shapes = mc.listRelatives(obj, s=True, pa=1, ni=True) or []
    return shapes


def get_mirrorTable (master, slave, miraxis='x'):
    """
    Return a mirror table between two object on chosen axis
    :param str master: object to compare to slave
    :param str slave: object to compare to master
    :param str miraxis: 'x'(default) chosen world axis on wich mirror is wanted
    :return: list: return a mirror table list, e.g.:[-1, 1, 1]
    """

    m = get_axisDir(master)
    s = get_axisDir(slave)
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


def get_axis(obj, os=False, exact=False):
    """
    Find objects axis direction compared to world or parent axis
    :param str obj: object to query
    :param bool os: False(default) query direction compared to world, True query direction compared to parent
    :param bool exact: True return exact direction value for each axis
    :return: axis direction in a list, e.g.:[1, 1, 1]
    """

    vp = mc.createNode('vectorProduct', n='_vp')
    mc.setAttr('{}.operation'.format(vp), 3)
    if os:
        mc.connectAttr('{}.matrix'.format(obj), '{}.matrix'.format(vp), f=True)
    else:
        mc.connectAttr('{}.worldMatrix'.format(obj), '{}.matrix'.format(vp), f=True)
    axis = [1, 1, 1]
    val = [1, 0, 0]
    xyz = 'XYZ'
    fullval = []
    for i in range(3):
        j = 0
        for axe in 'XYZ':
            mc.setAttr('{}.input1{}'.format(vp, axe), val[j])
            j += 1
        for axe in 'XYZ':
            fullval.append(mc.getAttr('{}.output{}'.format(vp, axe)))
        axis[i] = mc.getAttr('{}.output{}'.format(vp, xyz[i]))
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


def get_axisDir(obj):
    """
    Return a list of axis direction compared to world
    :param str obj: object on wich to check the axis
    :return: list: return an axis direction list compared to world,
                    first index giving the x axis direction and so on e.g.:[y, -z, -x],
                    for a object matching world axis it will return : [x, y, z]
    """

    objdir = get_axis(obj, exact=True)[-1]
    axe = []
    for i in range(3):
        val = []
        for j in range(3):
            val.append(objdir[i][j])
        if abs(val[0]) > abs(val[1]):
            if abs(val[0]) > abs(val[2]):
                if val[0] < 0:
                    axe.append('-x')
                else:
                    axe.append('x')
            else:
                if val[2] < 0:
                    axe.append('-z')
                else:
                    axe.append('z')
        else:
            if abs(val[1]) > abs(val[2]):
                if val[1] < 0:
                    axe.append('-y')
                else:
                    axe.append('y')
            else:
                if val[2] < 0:
                    axe.append('-z')
                else:
                    axe.append('z')
    return axe
