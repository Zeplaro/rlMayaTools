import maya.cmds as mc
from tbx import get_shape
from tbx import get_mirrorTable


def mirror(mastershape, slaveshape, table, miraxis='x', ws=False):
    """
    :param str mastershape: shape to copy from
    :param str slaveshape: slave shape modified
    :param list table: mirror table
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    """

    nb_of_cv = mc.getAttr('{}.spans'.format(mastershape)) + mc.getAttr('{}.degree'.format(mastershape))
    if ws:  # mirror on world space
        pos = [mc.xform('{}.cv[{}]'.format(mastershape, cv_index), q=True, ws=True, t=True) for cv_index in range(nb_of_cv)]
        if not miraxis:  # if World space copy:
            pass
        elif miraxis == 'z':
            pos = [(x, y, -z) for x, y, z in pos]
        elif miraxis == 'y':
            pos = [(x, -y, z) for x, y, z in pos]
        else:
            pos = [(-x, y, z) for x, y, z in pos]
        for cv_index in range(nb_of_cv):
            mc.xform('{}.cv[{}]'.format(slaveshape, cv_index), ws=True, t=pos[cv_index])

    else:  # mirror on object space
        pos = [mc.xform('{}.cv[{}]'.format(mastershape, cv_index), q=True, os=True, t=True) for cv_index in range(nb_of_cv)]
        for cv_index in range(nb_of_cv):
            cv_pos = pos[cv_index]
            for i in range(3):
                cv_pos[i] *= table[i]
            mc.xform('{}.cv[{}]'.format(slaveshape, cv_index), os=True, t=cv_pos)


def do_shapeMirror(miraxis='x', ws=False, copy=False, solo=False):
    """
    Mirror curves on defined axis in world or object space
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    :param bool copy: True, performs a simple copy of the shape without any mirroring
    :param bool solo: True, performs a miror of each shape to itself
    """

    ctrls = [x for x in mc.ls(sl=True, fl=True)
             if mc.nodeType(x) == 'nurbsCurve' or mc.nodeType(x) == 'transform' or mc.nodeType(x) == 'joint']
    if not ctrls:
        mc.warning('No curve selected')
        return

    mc.undoInfo(openChunk=True)
    if solo:

        if miraxis == 'z':
            table = [1, 1, -1]
        elif miraxis == 'y':
            table = [1, -1, 1]
        else:
            table = [-1, 1, 1]

        for each in ctrls:
            if mc.nodeType(each) == 'nurbsCurve':
                mirror(each, each, table, miraxis, ws)
            for shape in get_shape(each):
                if not mc.nodeType(shape) == 'nurbsCurve':
                    continue
                mirror(shape, shape, table, miraxis, ws)

    elif copy:
        master = ctrls[0]
        slaves = ctrls[1:]
        for slave in slaves:
            if mc.nodeType(master) == 'nurbsCurve':  # if shapes are selected
                mastershape = [master]
                slaveshape = slaves
            else:  # if transforms are selected
                mastershape = get_shape(master)
                slaveshape = get_shape(slave)
            while len(slaveshape) < len(mastershape):
                mastershape.pop(-1)
            for i in range(len(mastershape)):
                if not mc.nodeType(slaveshape[i]) == 'nurbsCurve':
                    continue
                mirror(mastershape[i], slaveshape[i], table=[1, 1, 1], miraxis=None, ws=ws)

    else:
        for ctrl in ctrls:
            # checking for namespaces
            nspace = ctrl.split(':')
            name = nspace[-1]
            if len(nspace) > 1:
                nspace.pop(-1)
                nspace = ':'.join(nspace)
                nspace += ':'
            else:
                nspace = ''

            # checking for side mark
            if name.startswith('L_'):
                master = ctrl
                slave = nspace+name.replace('L_', 'R_', 1)
            elif name.startswith('R_'):
                master = ctrl
                slave = nspace+name.replace('R_', 'L_', 1)
            else:
                continue
            if not mc.objExists(slave):
                continue

            # getting ctrls axis for object space
            table = get_mirrorTable(master, slave, miraxis=miraxis)

            # Checking if the selection is valid
            if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
                master = get_shape(master)
                slave = get_shape(slave)
            elif mc.objectType(ctrl, isType='nurbsCurve'):
                master = [master]
                slave = [slave]
            else:
                continue

            # checking nbr of shapes in master and slave
            while len(master) > len(slave):
                master.pop(-1)

            i = 0
            if not master or not slave:
                continue
            for shape in master:
                mirror(shape, slave[i], table, miraxis, ws)
                i += 1
            print('{} mirrored'.format(ctrl))

    mc.select(ctrls, r=True)
    mc.undoInfo(closeChunk=True)
