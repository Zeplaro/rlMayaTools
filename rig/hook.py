import maya.cmds as mc


def do_hook(objs=None):
    hooks = []
    if objs:
        if isinstance(objs, str) or isinstance(objs, unicode):  # if a string is given converts it in a list
            objs = [objs]
    else:
        objs = mc.ls(sl=1, tr=1)
    if objs:
        for obj in objs:
            if not mc.objExists(obj):
                continue
            hook = mc.group(em=1, n=obj + '_hook')
            hooks += [hook]
            mmx = mc.createNode('multMatrix', n='mmx_' + obj)
            dmx = mc.createNode('decomposeMatrix', n='dmx_' + obj)
            mc.connectAttr(obj + '.worldMatrix[0]', mmx + '.matrixIn[1]', f=1)
            mc.connectAttr(hook + '.parentInverseMatrix[0]', mmx + '.matrixIn[2]', f=1)
            mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=1)

            mc.connectAttr(dmx + '.outputShear', hook + '.shear', f=1)
            mc.connectAttr(dmx + '.outputTranslate', hook + '.translate', f=1)
            mc.connectAttr(dmx + '.outputScale', hook + '.scale', f=1)
            mc.connectAttr(dmx + '.outputRotate', hook + '.rotate', f=1)
        return hooks
    else:
        mc.warning('Select at least one object')
