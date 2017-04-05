import maya.cmds as mc
from marsTools.mirror_table import getMirrorValues


def mirror(shape, slaveshape, table, miraxis='x', ws=False):
    """
    :param str shape: shape to copy from
    :param str slaveshape: slave shape modified
    :param list table: mirror table
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    """
    # defining index of axis to mirror on chosen axis
    if miraxis == 'z':
        mirindex = 2
    elif miraxis == 'y':
        mirindex = 1
    else:
        mirindex = 0

    cvs = mc.getAttr(shape+'.cp', s=1)
    for cv in range(cvs):
        cp = '.cp['+str(cv)+']'
        if ws:  # mirror on world space
            pos = mc.xform(shape+cp, q=1, ws=1, t=1)
            pos[mirindex] *= -1  # mirroring on chosen axis
            mc.xform(slaveshape+cp, ws=1, t=pos)

        else:  # mirror on object space
            pos = mc.xform(shape+cp, q=1, os=1, t=1)
            for k in range(3):
                pos[k] = pos[k] * table[k]
            mc.xform(slaveshape+cp, os=1, t=pos)


def do_shapeMirror(miraxis='x', ws=False, copy=False):
    """
    Mirror objects shape on defined axis in world or object space
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    :param bool copy: True perform a simple copy of the shape without any mirroring
    """

    ctrls = mc.ls(sl=1)

    if not copy:
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

            # getting ctrls axis in case of object space
            table = getMirrorValues(master, slave)

            # Checking if the selection is valid
            if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
                master = mc.listRelatives(master, c=1, s=1, pa=1, type='nurbsCurve') or []
                slave = mc.listRelatives(slave, c=1, s=1, pa=1, type='nurbsCurve') or []
            elif mc.objectType(ctrl, isType='nurbsCurve'):
                master = [master]
                slave = [slave]
            else:
                continue

            # checking nbr of shapes in master and slave
            while len(master) > len(slave):
                master.pop(-1)

            i = 0
            for shape in master:
                mirror(shape, slave[i], table, miraxis, ws)
                i += 1
    else:
        masters = [item for item in mc.listRelatives(ctrls[0], s=True, fullPath=True, type='nurbsCurve') or []]
        slaves = [item for item in mc.listRelatives(ctrls[1:], s=True, fullPath=True, type='nurbsCurve') or []]
        # checking nbr of shapes in master and slave
        while len(masters) > len(slaves):
            masters.pop(-1)
        i = 0
        for master in masters:
            mirror(master, slaves[i], [1, 1, 1])
            i += 1

    mc.select(ctrls, r=1)
    print('__DONE__')
