import maya.cmds as mc


def get_skinCluster(obj):

    sknclust = mc.ls(mc.listHistory(obj, ac=True, pdo=True), type='skinCluster')
    return sknclust[0] if sknclust else None


def get_shape(obj):

    shapes = mc.listRelatives(obj, s=True, pa=1, ni=True) or []
    return shapes


def get_mirror_table (left, right, miraxis='x'):
    """
    Return a mirror table between two object on chosen axis
    :param str left: object to compare to slave
    :param str right: object to compare to master
    :param str miraxis: 'x'(default) chosen world axis on wich mirror is wanted
    :return: list: return a mirror table list, e.g.:[-1, 1, 1]
    """
    left_orient = get_axis_orientation(left)
    right_orient = get_axis_orientation(right)
    mirtable = [1, 1, 1]
    for i in range(3):
        if left_orient[i][-1] == right_orient[i][-1]:
            if not left_orient[i][0] == right_orient[i][0]:
                mirtable[i] = -1
            if left_orient[i][-1] == miraxis:
                mirtable[i] *= -1
        else:
            mirtable[i] = 0
    return mirtable


def get_axis_orientation(obj):
    """
    Return a list of axis direction compared to the world
    :param str obj: object on wich to check the axis
    :return: list: return an axis direction list compared to world,
                    first index giving the x axis direction and so on e.g.:[y, -z, -x],
                    for a object matching world axis it will return : [x, y, z]
    """
    mx = mc.getAttr('{}.worldMatrix'.format(obj))
    mx_rot = mx[:3], mx[4:7], mx[8:11]

    axis_dir = [0, 0, 0]
    for axis in range(3):
        vals = mx_rot[0][axis], mx_rot[1][axis], mx_rot[2][axis]  # Gathering values for each axis
        index = vals.index(max(vals, key=abs))  # Getting the index of the highest absolute value in vals
        if index == 0:
            axis_dir[axis] = 'x'
        elif index == 1:
            axis_dir[axis] = 'y'
        else:
            axis_dir[axis] = 'z'
        if vals[index] < 0:
            axis_dir[axis] = '-{}'.format(axis_dir[axis])
    return axis_dir
