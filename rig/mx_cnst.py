import maya.cmds as mc


def mx_cnst(master=None, slave=None):

    target = []
    if not master or not slave:
        target = mc.ls(sl=True, tr=True, fl=True)
        if not target:
            mc.warning('Select two objects')
            return
    else:
        target.append(master)
        target.append(slave)

    mmx = mc.createNode('multMatrix', n='mmx_{}'.format(target[0]))
    dmx = mc.createNode('decomposeMatrix', n='dmx_{}'.format(target[0]))
    cmx = mc.createNode('composeMatrix', n='cmx_{}'.format(target[0]))
    mc.connectAttr('{}.outputMatrix'.format(cmx), '{}.matrixIn[0]'.format(mmx), f=True)
    mc.connectAttr('{}.worldMatrix[0]'.format(target[0]), '{}.matrixIn[1]'.format(mmx), f=True)
    mc.connectAttr('{}.parentInverseMatrix[0]'.format(target[1]), '{}.matrixIn[2]'.format(mmx), f=True)
    mc.connectAttr('{}.matrixSum'.format(mmx), '{}.inputMatrix'.format(dmx), f=True)

    loc1 = mc.spaceLocator(n='{}_loc'.format(target[0]))[0]
    ro = mc.xform(target[0], q=True, ws=True, ro=True)
    t = mc.xform(target[0], q=True, ws=True, t=True)
    mc.xform(loc1, ws=True, ro=ro, t=t)
    loc2 = mc.spaceLocator(n='{}_loc'.format(target[1]))[0]
    ro = mc.xform(target[1], q=True, ws=True, ro=True)
    t = mc.xform(target[1], q=True, ws=True, t=True)
    mc.xform(loc2, ws=True, ro=ro, t=t)
    mc.parent(loc2, loc1)

    mc.setAttr('{}.inputTranslate'.format(cmx), *mc.getAttr('{}.translate'.format(loc2))[0])
    mc.setAttr('{}.inputRotate'.format(cmx), *mc.getAttr('{}.rotate'.format(loc2))[0])
    mc.setAttr('{}.inputScale'.format(cmx), *mc.getAttr('{}.scale'.format(loc2))[0])
    mc.setAttr('{}.inputShear'.format(cmx), *mc.getAttr('{}.shear'.format(loc2))[0])

    mc.connectAttr('{}.outputTranslate'.format(dmx), '{}.translate'.format(target[1]), f=True)
    mc.connectAttr('{}.outputRotate'.format(dmx), '{}.rotate'.format(target[1]), f=True)
    mc.connectAttr('{}.outputScale'.format(dmx), '{}.scale'.format(target[1]), f=True)
    mc.connectAttr('{}.outputShear'.format(dmx), '{}.shear'.format(target[1]), f=True)

    mc.delete(loc1, loc2)

    return target
