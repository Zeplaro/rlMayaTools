import maya.cmds as mc


def do_hook(*objs):

    if not objs:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if not objs:
            mc.warning('Select at least one object')
            return
    hooks = []
    for obj in objs:
        hook = mc.group(em=True, n=obj + '_hook')
        mmx = mc.createNode('multMatrix', n='mmx_' + obj)
        dmx = mc.createNode('decomposeMatrix', n='dmx_' + obj)
        mc.connectAttr(obj + '.worldMatrix[0]', mmx + '.matrixIn[1]', f=True)
        mc.connectAttr(hook + '.parentInverseMatrix[0]', mmx + '.matrixIn[2]', f=True)
        mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix', f=True)
        mc.connectAttr(dmx + '.outputShear', hook + '.shear', f=True)
        mc.connectAttr(dmx + '.outputTranslate', hook + '.translate', f=True)
        mc.connectAttr(dmx + '.outputScale', hook + '.scale', f=True)
        mc.connectAttr(dmx + '.outputRotate', hook + '.rotate', f=True)
        hooks.append(hook)
    return hooks
