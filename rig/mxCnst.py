import maya.cmds as mc


def do_mxCnst(master=None, slave=None):

    target = []
    if not master or not slave:
        target = mc.ls(sl=True, tr=True, fl=True)
        if not target:
            mc.warning('Select two objects')
            return
    else:
        target.append(master)
        target.append(slave)

    mmx = mc.createNode('multMatrix', n='mmx_'+target[0])
    dmx = mc.createNode('decomposeMatrix', n='dmx_'+target[0])
    cmx = mc.createNode('composeMatrix', n='cmx_'+target[0])
    mc.connectAttr(cmx+'.outputMatrix', mmx+'.matrixIn[0]', f=True)
    mc.connectAttr(target[0]+'.worldMatrix[0]', mmx+'.matrixIn[1]', f=True)
    mc.connectAttr(target[1]+'.parentInverseMatrix[0]', mmx+'.matrixIn[2]', f=True)
    mc.connectAttr(mmx+'.matrixSum', dmx+'.inputMatrix', f=True)

    loc1 = mc.spaceLocator(n=target[0]+'_loc')[0]
    ro = mc.xform(target[0], q=True, ws=True, ro=True)
    t = mc.xform(target[0], q=True, ws=True, t=True)
    mc.xform(loc1, ws=True, ro=ro, t=t)
    loc2 = mc.spaceLocator(n=target[1]+'_loc')[0]
    ro = mc.xform(target[1], q=True, ws=True, ro=True)
    t = mc.xform(target[1], q=True, ws=True, t=True)
    mc.xform(loc2, ws=True, ro=ro, t=t)
    mc.parent(loc2, loc1)

    mc.setAttr(cmx+'.inputTranslate', *mc.getAttr(loc2+'.translate')[0])
    mc.setAttr(cmx+'.inputRotate', *mc.getAttr(loc2+'.rotate')[0])
    mc.setAttr(cmx+'.inputScale', *mc.getAttr(loc2+'.scale')[0])
    mc.setAttr(cmx+'.inputShear', *mc.getAttr(loc2+'.shear')[0])

    mc.connectAttr(dmx+'.outputTranslate', target[1]+'.translate', f=True)
    mc.connectAttr(dmx+'.outputRotate', target[1]+'.rotate', f=True)
    mc.connectAttr(dmx+'.outputScale', target[1]+'.scale', f=True)
    mc.connectAttr(dmx+'.outputShear', target[1]+'.shear', f=True)

    mc.delete(loc1, loc2)

    return target
