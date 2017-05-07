import maya.cmds as mc
import getShape as gs

# todo : UI



def roll(size=1):

    rollgrp = mc.group(em=1, w=1, n='customroll_grp#')

    path = mc.circle(nr=[0, 1, 0], r=1, n='path', ch=0)[0]

    rollparent = mc.group(em=1, p=rollgrp, n='rollparent')
    mc.setAttr(rollparent+'.ry', lock=1, keyable=0, channelBox=0)

    rollctrl = mc.circle(nr=[0, 1, 0], r=1, n='roll_ctrl', ch=0)[0]
    mc.setAttr(rollctrl+'.rotateOrder', 2)
    mc.setAttr(rollctrl+'.ry', lock=1, keyable=0, channelBox=0)
    for dir in 'xyz':
        mc.setAttr(rollctrl+'.t'+dir, lock=1, keyable=0, channelBox=0)
        mc.setAttr(rollctrl+'.s'+dir, lock=1, keyable=0, channelBox=0)
    for i in range(8):
        if i % 2 == 0:
            mc.move(0, 1, 0, rollctrl+'.cv['+str(i)+']', r=1, os=1, wd=1)
        else:
            mc.move(0, 1.5, 0, rollctrl+'.cv['+str(i)+']', r=1, os=1, wd=1)

    mc.parent(path, rollctrl, rollgrp)

    pivotpos = mc.group(em=1, p=rollgrp, n='pivotpos')
    mc.setAttr(pivotpos+'.displayRotatePivot', 1)

    pivotguide = mc.group(em=1, p=rollctrl, n='pivotguide')
    mc.move(0, size*2, 0, pivotguide, r=1, os=1, wd=1)
    mc.setAttr(pivotguide+'.displayScalePivot', 1)

    pivotguideflat = mc.group(em=1, p=rollgrp, n='pivotguideflat')
    mc.setAttr(pivotguide+'.displayScalePivot', 1)
    mc.pointConstraint(pivotguide, pivotguideflat, mo=0, sk='y')

    nearpoc = mc.createNode('nearestPointOnCurve', n='nearpoc#')
    pathshape = gs.do_getShape(path)[0]

    mc.connectAttr(pathshape+'.local', nearpoc+'.inputCurve')
    mc.connectAttr(pivotguideflat+'.translate', nearpoc+'.inPosition')
    mc.connectAttr(nearpoc+'.position', pivotpos+'.translate')
    mc.connectAttr(pivotpos+'.translate', rollparent+'.rotatePivot')
    mc.connectAttr(rollctrl+'.rotate', rollparent+'.rotate')
    return
