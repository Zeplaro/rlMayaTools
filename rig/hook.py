import maya.cmds as mc


def do_hook(objs=None):
    hooks = []
    if objs:
        if isinstance(objs, str) or isinstance(objs, unicode):  # if a string is given converts it in a list
            objs = [objs]
    else:
        objs = mc.ls(sl=True, tr=True, fl=True)
    if objs:
        for obj in objs:
            if not mc.objExists(obj):
                continue
            hook = mc.group(em=1, n=obj + '_hook')
            hooks += [hook]
            mmx = mc.createNode('multMatrix', n='mmx_' + obj)
            dmx = mc.createNode('decomposeMatrix', n='dmx_' + obj)
            mc.connectAttr(obj + '.worldMatrix[0]', mmx + '.matrixIn[1]', f=True)
            mc.connectAttr(hook + '.parentInverseMatrix[0]', mmx + '.matrixIn[2]', f=True)
            mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=True)

            mc.connectAttr(dmx + '.outputShear', hook + '.shear', f=True)
            mc.connectAttr(dmx + '.outputTranslate', hook + '.translate', f=True)
            mc.connectAttr(dmx + '.outputScale', hook + '.scale', f=True)
            mc.connectAttr(dmx + '.outputRotate', hook + '.rotate', f=True)
        return hooks
    else:
        mc.warning('Select at least one object')
