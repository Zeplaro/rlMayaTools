# Mirror Facial shapes_orig and Guides L->R
import maya.cmds as mc
import mayaRigTools_sk.sandBox.laro.shapeMirror as sm

"""
import mayaRigTools_sk.sandBox.laro.facial_mirror as fm
reload(fm)
fm.do_facial_mirror()
"""


def do_facial_mirror():
    # switch L and R to mirror R->L
    sides = ['L_', 'R_']

    sel = mc.ls(sl=True)
    # Getting list of origs to mirror, in 'facialDrivers' group
    origs = mc.listRelatives('facialDrivers', ad=True, type='transform')[::-1]
    origs = [orig for orig in origs if orig.startswith(sides[0]) and '_orig' in orig and 'TRASH' not in orig]
    missing = []
    for orig in origs:
        # _orig mirror
        origAlt = orig.replace(sides[0], sides[1], 1)
        if not mc.objExists(origAlt):
            missing.append(origAlt)
            print(origAlt+' missing')
            continue

        origloc = mc.spaceLocator(n=orig + '_loc#')[0]
        mc.parent(origloc, orig, r=True)
        origgrp = mc.group(em=True, n=orig + '_grp#')
        mc.parent(origloc, origgrp)
        mc.setAttr(origgrp + '.scaleX', -1)
        p = mc.listRelatives(origAlt, ap=True, type='transform')[0]
        mc.parent(origloc, p)
        for axe in 'xyz':
            mc.setAttr(origloc + '.s' + axe, 1)
        mc.parent(origAlt, origloc)
        for axe in 'xyz':
            for attr in 'tr':
                mc.setAttr(origAlt + '.' + attr + axe, 0)
        mc.parent(origAlt, p)

        # eye_corner rotation exception
        if orig == 'L_eyeCorner_in_ctrl_orig' or orig == 'L_eyeCorner_out_ctrl_orig':
            mc.rotate(0, 0, 180, origAlt, r=True, os=True)
        mc.delete(origloc, origgrp)

        # Scale mirror
        if cmp(mc.getAttr(orig + '.sz'), 0) != cmp(mc.getAttr(origAlt + '.sz'), 0):
            for axe in 'xy':
                mc.setAttr(origAlt + '.s' + axe, mc.getAttr(orig + '.s' + axe))
            mc.setAttr(origAlt + '.sz', mc.getAttr(orig + '.sz') * -1)
        else:
            for axe in 'xyz':
                mc.setAttr(origAlt + '.s' + axe, mc.getAttr(orig + '.s' + axe))

    # Mirror ctrl shapes
    ctrls = mc.listRelatives('facialDrivers', ad=True, type='transform')[::-1]
    ctrls = [ctrl for ctrl in ctrls if ctrl.startswith(sides[0]) and '_ctrl' in ctrl and 'TRASH' not in ctrl and '_orig' not in ctrl]
    mc.select(ctrls)
    sm.do_shapeMirror()

    # Guides mirror
    guides = [sides[0] + 'teeth_dn_jnt_GUIDE', sides[0] + 'teeth_up_jnt_GUIDE']
    for guide in guides:
        guideAlt = guide.replace(sides[0], sides[1], 1)
        for axe in 'xyz':
            for attr in 'tr':
                mc.setAttr(guideAlt + '.' + attr + axe, mc.getAttr(guide + '.' + attr + axe))
        mc.setAttr(guideAlt + '.tx', mc.getAttr(guide + '.tx') * -1)
    mc.select(sel, r=True)
