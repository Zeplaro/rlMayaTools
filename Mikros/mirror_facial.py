import maya.cmds as mc
import mayaRigTools_sk.sandBox.viba.shapes.mirror_shape as ms


def do_facial_mirror():
    # switch L and R to mirror R->L
    sides = ['L_', 'R_']

    sel = mc.ls(sl=1)
    # Getting list of origs to mirror, in 'facialDrivers' group
    origs = mc.listRelatives('facialDrivers', ad=1)
    origs = origs[::-1]
    origs = [l for l in origs if
             l.find(sides[0]) != -1 and l.find('_orig') != -1 and l.find('TRASH') == -1 and l.find('Shape') == -1]

    for orig in origs:
        # _orig mirror
        mc.spaceLocator(n=orig + '_loc')
        mc.parent(orig + '_loc', orig, r=1)
        mc.group(em=1, n=orig + '_grp')
        mc.parent(orig + '_loc', orig + '_grp')
        mc.setAttr(orig + '_grp.scaleX', -1)
        p = mc.listRelatives(orig.replace(sides[0], sides[1], 1), ap=1)
        mc.parent(orig + '_loc', p)
        for axe in 'xyz':
            mc.setAttr(orig + '_loc.s' + axe, 1)
        mc.parent(orig.replace(sides[0], sides[1], 1), orig + '_loc')
        for axe in 'xyz':
            for attr in 'tr':
                mc.setAttr(orig.replace(sides[0], sides[1], 1) + '.' + attr + axe, 0)
        mc.parent(orig.replace(sides[0], sides[1], 1), p)

        # eye_corner rotation exception
        if orig == 'L_eyeCorner_in_ctrl_orig' or orig == 'L_eyeCorner_out_ctrl_orig':
            mc.rotate(0, 0, 180, orig.replace(sides[0], sides[1], 1), r=1, os=1)
        mc.delete(orig + '_loc', orig + '_grp')

        # Scale mirror
        if (mc.getAttr(orig + '.sz') < 0 or mc.getAttr(orig.replace(sides[0], sides[1], 1) + '.sz') < 0) and (
                    mc.getAttr(orig + '.sz') != mc.getAttr(orig.replace(sides[0], sides[1], 1) + '.sz')):
            for axe in 'xy':
                mc.setAttr(orig.replace(sides[0], sides[1], 1) + '.s' + axe, mc.getAttr(orig + '.s' + axe))
            mc.setAttr(orig.replace(sides[0], sides[1], 1) + '.sz', mc.getAttr(orig + '.sz') * -1)
        else:
            for axe in 'xyz':
                mc.setAttr(orig.replace(sides[0],sides[1],1)+'.s'+axe,mc.getAttr(orig+'.s'+axe))

    # Mirror ctrl shapes
    ctrls = mc.listRelatives('facialDrivers', ad=1)
    ctrls = ctrls[::-1]
    ctrls = [l for l in ctrls if l.find(sides[0]) != -1 and l.find('_ctrl') != -1 and l.find('TRASH') == -1 and l.find(
        'Shape') == -1 and l.find('_orig') == -1]
    mc.select(ctrls)
    ms.do_mirror()

    # Guides mirror
    guides = [sides[0] + 'teeth_dn_jnt_GUIDE', sides[0] + 'teeth_up_jnt_GUIDE']
    for guide in guides:
        for axe in 'xyz':
            for attr in 'tr':
                mc.setAttr(guide.replace(sides[0], sides[1], 1) + '.' + attr + axe,
                           mc.getAttr(guide + '.' + attr + axe))
        mc.setAttr(guide.replace(sides[0], sides[1], 1) + '.tx', mc.getAttr(guide + '.tx') * -1)
    mc.select(sel, r=1)
    
do_facial_mirror()
