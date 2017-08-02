import maya.cmds as mc
from marsTools.mirror_table import getMirrorValues

'''
import mayaRigTools_sk.sandBox.laro.shapeMirror as sm
reload(sm)
sm.do_shapeMirror()
'''


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

    cvs = mc.getAttr(shape+'.cp', size=True)
    for cv in range(cvs):
        cp = '.cp['+str(cv)+']'
        if ws:  # mirror on world space
            pos = mc.xform(shape+cp, q=True, ws=True, t=True)
            pos[mirindex] *= -1  # mirroring on chosen axis
            mc.xform(slaveshape+cp, ws=True, t=pos)

        else:  # mirror on object space
            pos = mc.xform(shape+cp, q=True, os=True, t=True)
            for k in range(3):
                pos[k] = pos[k] * table[k]
            mc.xform(slaveshape+cp, os=True, t=pos)


def do_shapeMirror(miraxis='x', ws=False, copy=False):
    """
    Mirror objects shape on defined axis in world or object space
    :param str miraxis: world axis on wich you want to mirror 'x'(default), 'y', 'z'
    :param bool ws: False(default) mirror on object space, True mirror on world space
    :param bool copy: True perform a simple copy of the shape without any mirroring
    """

    ctrls = mc.ls(sl=True, fl=True)

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
                master = mc.listRelatives(master, c=True, s=True, pa=True, type='nurbsCurve') or []
                slave = mc.listRelatives(slave, c=True, s=True, pa=True, type='nurbsCurve') or []
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
        master = ctrls[0]
        slaves = ctrls[1:]
        for slave in slaves:
            if mc.nodeType(master) == 'nurbsCurve':  # if shapes are selected
                mastershape = [master]
                slaveshape = slaves
                while len(slaveshape) > len(mastershape):
                    mastershape.append(mastershape[0])
            else:  # if transforms are selected
                mastershape = mc.listRelatives(master, c=True, s=True, pa=True, type='nurbsCurve') or []
                slaveshape = mc.listRelatives(slave, c=True, s=True, pa=True, type='nurbsCurve') or []
                while len(slaveshape) > len(mastershape):
                    slaveshape.pop(-1)
                while len(slaveshape) < len(mastershape):
                    mastershape.pop(-1)
            for i in range(len(mastershape)):
                mirror(mastershape[i], slaveshape[i], [1, 1, 1])

    mc.select(ctrls, r=True)
    print('__DONE__')
