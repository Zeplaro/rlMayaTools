import maya.cmds as mc


def do_hook():
    if not mc.ls(sl=1, tr=1) == []:
        targets = mc.ls(sl=1, tr=1)
        for target in targets:
            hook = mc.group(em=1, n=target + '_hook')
            mmx = mc.createNode('multMatrix', n='mmx_' + target)
            dmx = mc.createNode('decomposeMatrix', n='dmx_' + target)
            mc.connectAttr(target + '.worldMatrix[0]', mmx + '.matrixIn[1]', f=1)
            mc.connectAttr(hook + '.parentInverseMatrix[0]', mmx + '.matrixIn[2]', f=1)
            mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=1)

            mc.connectAttr(dmx + '.outputShear', hook + '.shear', f=1)
            mc.connectAttr(dmx + '.outputTranslate', hook + '.translate', f=1)
            mc.connectAttr(dmx + '.outputScale', hook + '.scale', f=1)
            mc.connectAttr(dmx + '.outputRotate', hook + '.rotate', f=1)
    else:
        mc.warning('Select at least one object')