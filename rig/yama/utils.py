# encoding: utf8

import maya.cmds as mc


def create_hook(node, suffix_name='hook', parent=None):
    if mc.objExists('{}_{}'.format(node.name, suffix_name)):
        suffix_name += '#'
    hook = mc.group(em=True, n='{}_{}'.format(node, suffix_name))
    mmx = mc.createNode('multMatrix', n='mmx_{}_{}'.format(node, suffix_name))
    dmx = mc.createNode('decomposeMatrix', n='dmx_{}_{}'.format(node, suffix_name))
    mc.connectAttr('{}.worldMatrix[0]'.format(node), '{}.matrixIn[1]'.format(mmx), f=True)
    mc.connectAttr('{}.parentInverseMatrix[0]'.format(hook), '{}.matrixIn[2]'.format(mmx), f=True)
    mc.connectAttr('{}.matrixSum'.format(mmx), '{}.inputMatrix'.format(dmx), f=True)
    mc.connectAttr('{}.outputShear'.format(dmx), '{}.shear'.format(hook), f=True)
    mc.connectAttr('{}.outputTranslate'.format(dmx), '{}.translate'.format(hook), f=True)
    mc.connectAttr('{}.outputScale'.format(dmx), '{}.scale'.format(hook), f=True)
    mc.connectAttr('{}.outputRotate'.format(dmx), '{}.rotate'.format(hook), f=True)
    if parent and mc.objExists(parent):
        mc.parent(hook, parent)
    return hook
