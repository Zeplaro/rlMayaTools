import maya.cmds as mc

def do_mxCnst():
    target = mc.ls(sl=1, tr=1)
    if len(target) == 2:
        mmx = mc.createNode('multMatrix', n='mmx_' + target[0])
        dmx = mc.createNode('decomposeMatrix', n='dmx_' + target[0])
        cmx = mc.createNode('composeMatrix', n='cmx_' + target[0])
        mc.connectAttr(cmx + '.outputMatrix', mmx + '.matrixIn[0]', f=1)
        mc.connectAttr(target[0] + '.worldMatrix[0]', mmx + '.matrixIn[1]', f=1)
        mc.connectAttr(target[1] + '.parentInverseMatrix[0]', mmx + '.matrixIn[2]', f=1)
        mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=1)

        loc1 = mc.spaceLocator(n=target[0] + '_loc')[0]
        mc.xform(loc1, ws=1, ro=mc.xform(target[0], q=1, ws=1, ro=1), t=mc.xform(target[0], q=1, ws=1, t=1))
        loc2 = mc.spaceLocator(n=target[1] + '_loc')[0]
        mc.xform(loc2, ws=1, ro=mc.xform(target[1], q=1, ws=1, ro=1), t=mc.xform(target[1], q=1, ws=1, t=1))
        mc.parent(loc2, loc1)

        mc.connectAttr(loc2 + '.translate', cmx + '.inputTranslate', f=1)
        mc.connectAttr(loc2 + '.rotate', cmx + '.inputRotate', f=1)
        mc.connectAttr(loc2 + '.scale', cmx + '.inputScale', f=1)
        mc.connectAttr(loc2 + '.shear', cmx + '.inputShear', f=1)

        mc.disconnectAttr(loc2 + '.translate', cmx + '.inputTranslate')
        mc.disconnectAttr(loc2 + '.rotate', cmx + '.inputRotate')
        mc.disconnectAttr(loc2 + '.scale', cmx + '.inputScale')
        mc.disconnectAttr(loc2 + '.shear', cmx + '.inputShear')

        mc.connectAttr(dmx + '.outputShear', target[1] + '.shear', f=1)
        mc.connectAttr(dmx + '.outputTranslate', target[1] + '.translate', f=1)
        mc.connectAttr(dmx + '.outputScale', target[1] + '.scale', f=1)
        mc.connectAttr(dmx + '.outputRotate', target[1] + '.rotate', f=1)

        mc.delete(loc1, loc2)

    else:
        mc.warning('Wrong number of objects selected')
