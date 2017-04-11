import maya.cmds as mc
import selShape as ss
import hook as hk


def roll():
    rollgrp = mc.group(em=1, w=1, n='customroll_grp')
    path = mc.circle(nr=[0, 1, 0], n='path')[0]
    mc.delete(path, ch=1)
    pivotpos = mc.group(em=1, p=rollgrp, n='pivotpos')
    mc.setAttr(pivotpos+'.displayRotatePivot', 1)

    rollctrl = mc.circle(nr=[0, 1, 0], n='roll_ctrl')[0]
    mc.delete(rollctrl, ch=1)
    for i in range(8):
        if i % 2 == 0:
            mc.move(0, 1, 0, rollctrl+'.cv['+str(i)+']', r=1, os=1, wd=1)
        else:
            mc.move(0, 1.5, 0, rollctrl+'.cv['+str(i)+']', r=1, os=1, wd=1)
    rollctrlhook = hk.do_hook(rollctrl)[0]
    mc.parent(path, rollctrlhook, rollctrl, rollgrp)

    pivotguide = mc.group(em=1, p=rollctrlhook, n='pivotguide')
    mc.move(0, 2, 0, pivotguide, r=1, os=1, wd=1)
    mc.setAttr(pivotguide+'.displayScalePivot', 1)

    nearpoc = mc.createNode('nearestPointOnCurve', n='nearpoc#')
    pathshape = ss.do_selShape(path)[0]

    mc.connectAttr(pathshape+'.local', nearpoc+'.inputCurve')
    dmx = mc.createNode('decomposeMatrix', n='dmx_roll#')
    mc.connectAttr(pivotguide+'.worldMatrix[0]', dmx+'.inputMatrix')
    mc.connectAttr(dmx+'.outputTranslate', nearpoc+'.inPosition')
    mc.connectAttr(nearpoc+'.position', pivotpos+'.translate')
    return
