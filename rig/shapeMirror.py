import maya.cmds as mc
import rig.getAxis as ga
import rig.selShape as ss


def mirror(master, slave, table, ws=False, miraxis='x'):
    # defining index of axis to mirror on chosen axis
    if miraxis == 'z':
        mirindex = 2
    elif miraxis == 'y':
        mirindex = 1
    else:
        mirindex = 0

    # checking nbr of shapes in master and slave
    while len(master) > len(slave):
        master.pop(-1)
    i = 0
    for shape in master:
        cvs = mc.getAttr(shape + '.cp', s=1)
        for cv in range(cvs):
            cp = '.cp[' + str(cv) + ']'
            if ws:  # mirror on world space
                pos = mc.xform(shape + cp, q=1, ws=1, t=1)
                pos[mirindex] *= -1  # mirroring on chosen axis
                mc.xform(slave[i] + cp, ws=1, t=pos)

            else:  # mirror on object space
                pos = mc.xform(shape + cp, q=1, os=1, t=1)
                for k in range(3):
                    pos[k] = pos[k] * table[k]
                mc.xform(slave[i] + cp, os=1, t=pos)
        i += 1


def do_shapeMirror(miraxis='x', ws=False, copy=False):
    """"
    Mirror objects shape on defined axis in world or object space
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    :param bool copy: True perform a simple copy of the shape without any mirroring
    """
    # ToDo: copy shape

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

            # getting ctrls axis for object space
            table = ga.getMirrorTable(master, slave, miraxis=miraxis)

            # Checking if the selection is valid
            if mc.objectType(ctrl, isType='transform') or mc.objectType(ctrl, isType='joint'):
                master = mc.listRelatives(master, c=1, s=1, pa=1, type='nurbsCurve') or []
                slave = mc.listRelatives(slave, c=1, s=1, pa=1, type='nurbsCurve') or []
            elif mc.objectType(ctrl, isType='nurbsCurve'):
                master = [master]
                slave = [slave]
            else:
                continue

            mirror(master, slave, table, ws, miraxis)
    else:
        master = [ctrls[0]]
        master = ss.do_selShape(q=1, objs=master)
        slaves = ss.do_selShape(q=1,objs=ctrls[1:])
        for slave in slaves:
            mirror(master, [slave], [1, 1, 1])

    mc.select(ctrls, r=1)
    print('__DONE__')
