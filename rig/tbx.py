import maya.cmds as mc


def get_skinCluster(obj):

    sknclust = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')
    return sknclust[0] if sknclust else None


def get_shape(obj):

    shapes = mc.listRelatives(obj, s=True, pa=1, ni=True) or []
    return shapes


def get_mirrorTable (left, right, miraxis='x'):
    """
    Return a mirror table between two object on chosen axis
    :param str left: object to compare to slave
    :param str right: object to compare to master
    :param str miraxis: 'x'(default) chosen world axis on wich mirror is wanted
    :return: list: return a mirror table list, e.g.:[-1, 1, 1]
    """
    leftOrient = get_axisOrientation(left)
    rightOrient = get_axisOrientation(right)
    mirtable = [1, 1, 1]
    for i in range(3):
        if leftOrient[i][-1] == rightOrient[i][-1]:
            if not leftOrient[i][0] == rightOrient[i][0]:
                mirtable[i] = -1
            if leftOrient[i][-1] == miraxis:
                mirtable[i] *= -1
        else:
            mirtable[i] = 0
    return mirtable


def get_axisOrientation(obj, os=False):
    """
    Return a list of axis direction compared to world or parent
    :param str obj: object on wich to check the axis
    :param bool os: False if compared to the world, True if compared to the parent
    :return: list: return an axis direction list compared to world,
                    first index giving the x axis direction and so on e.g.:[y, -z, -x],
                    for a object matching world axis it will return : [x, y, z]
    """
    if not os:
        mx = mc.getAttr('{}.worldMatrix'.format(obj))
    else:
        mx = mc.getAttr('{}.matrix'.format(obj))
    mxRot = mx[:3], mx[4:7], mx[8:11]

    axisDir = [0, 0, 0]
    for axis in range(3):
        vals = mxRot[0][axis], mxRot[1][axis], mxRot[2][axis]  # Gathering values for each axis
        index = vals.index(max(vals, key=abs))  # Getting the index of the highest absolute value in vals
        if index == 0:
            axisDir[axis] = 'x'
        elif index == 1:
            axisDir[axis] = 'y'
        else:
            axisDir[axis] = 'z'
        if vals[index] < 0:
            axisDir[axis] = '-{}'.format(axisDir[axis])
    return axisDir
