# Mirror Facial shapes_orig and Guides L->R
import maya.cmds as mc
import mayaRigTools_sk.sandBox.laro.shapeMirror as sm


def do_facial_mirror():
    # switch L and R to mirror R->L
    sides = ['L_', 'R_']

    sel = mc.ls(sl=1)
    # Getting list of origs to mirror, in 'facialDrivers' group
    origs = mc.listRelatives('facialDrivers', ad=1, type='transform')
    origs = origs[::-1]
    origs = [l for l in origs if
             l.find(sides[0]) != -1 and l.find('_orig') != -1 and l.find('TRASH') == -1 and l.find('Shape') == -1]
    missing = []
    for orig in origs:
        # _orig mirror
        origAlt = orig.replace(sides[0], sides[1], 1)
        if mc.objExists(origAlt):
            origloc = mc.spaceLocator(n=orig + '_loc#')[0]
            mc.parent(origloc, orig, r=1)
            origgrp = mc.group(em=1, n=orig + '_grp#')
            mc.parent(origloc, origgrp)
            mc.setAttr(origgrp + '.scaleX', -1)
            p = mc.listRelatives(origAlt, ap=1, type='transform')
            if mc.objExists(p[0]):
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
                    mc.rotate(0, 0, 180, origAlt, r=1, os=1)
            mc.delete(origloc, origgrp)

            # Scale mirror
            if (mc.getAttr(orig + '.sz') < 0 or mc.getAttr(origAlt + '.sz') < 0) and (
                        mc.getAttr(orig + '.sz') != mc.getAttr(origAlt + '.sz')):
                for axe in 'xy':
                    mc.setAttr(origAlt + '.s' + axe, mc.getAttr(orig + '.s' + axe))
                mc.setAttr(origAlt + '.sz', mc.getAttr(orig + '.sz') * -1)
            else:
                for axe in 'xyz':
                    mc.setAttr(origAlt + '.s' + axe, mc.getAttr(orig + '.s' + axe))
        else:
            missing.append(origAlt)
    if missing:
        print(str(missing) + ' are missing in the scene, check if Left and Right names match')

    # Mirror ctrl shapes
    ctrls = mc.listRelatives('facialDrivers', ad=1, type='transform')
    ctrls = ctrls[::-1]
    ctrls = [l for l in ctrls if l.find(sides[0]) != -1 and l.find('_ctrl') != -1 and l.find('TRASH') == -1 and l.find(
        'Shape') == -1 and l.find('_orig') == -1]
    mc.select(ctrls)
    sm.do_shapeMirror()

    # Guides mirror
    guides = [sides[0] + 'teeth_dn_jnt_GUIDE', sides[0] + 'teeth_up_jnt_GUIDE']
    for guide in guides:
        guideAlt = guide.replace(sides[0], sides[1], 1)
        for axe in 'xyz':
            for attr in 'tr':
                mc.setAttr(guideAlt + '.' + attr + axe,
                           mc.getAttr(guide + '.' + attr + axe))
        mc.setAttr(guideAlt + '.tx', mc.getAttr(guide + '.tx') * -1)
    mc.select(sel, r=1)
