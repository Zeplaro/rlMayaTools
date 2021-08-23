import maya.cmds as mc
import maya.mel as mel
from functools import wraps


def get_skinCluster(obj):

    sknclust = mel.eval('findRelatedSkinCluster '+obj)
    return sknclust if sknclust else None


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


def matrix_sum_bis(*matrices):
    mx_sum = matrices[0]
    for mx in matrices[1:]:
        mx_temp = mx_sum[:]
        index = 0
        for i in range(0, 13, 4):
            for j in range(4):
                mx_temp[index] = mx_sum[i] * mx[j] + mx_sum[i+1] * mx[j+4] + mx_sum[i+2] * mx[j+8] + mx_sum[i+3] * mx[j+12]
                index += 1
        mx_sum = mx_temp[:]
    return mx_sum


def matrix_sum(*matrices):
    matrices = [matrix_list2row(mx) for mx in matrices]
    mx_sum = matrices[0]
    for mx in matrices[1:]:
        mx_temp = mx_sum[:]
        for i in range(4):
            for j in range(4):
                mx_temp[i][j] = []
                for k in range(4):
                    mx_temp[i][j] += mx_sum[i][j] * mx[j]
    return mx_sum


def matrix_list2row(matrix, size=4):
    row_matrix = []
    start = 0
    for row in range(size):
        row_matrix.append(matrix[start:start+size])
        start += 4
    return row_matrix


def keepsel(func):
    """
    Decorator that keeps maya current selection after running a function that might change the current selection.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sel = mc.ls(sl=True, fl=True)
        result = func(*args, **kwargs)
        mc.select(sel)
        return result
    return wrapper


def mayaundo(func):
    """
    Decorator that allows the function to be undone as single undo chunk.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print("Exception raised from : {}".format(func.__name__))
            raise e
        finally:
            mc.undoInfo(closeChunk=True)
        return result
    return wrapper
