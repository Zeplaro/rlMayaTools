# Mirror JNT & orient L>R
import maya.cmds as mc


def doMirrorJnt(side='L'):
    sel = mc.ls(sl=1)
    if side=='R':
        side=['R_','L_']
    else:
        side=['L_','R_']

    for each in sel:
        right = each.replace(side[0], side[1], 1)
        mc.duplicate(each, n=right)
        try:
            mc.parent(right, w=1)
        except:
            pass
        mc.setAttr(right + '.translateX', mc.getAttr(right + '.translateX') * -1)
        X = mc.getAttr(right + '.jointOrientX')
        Y = mc.getAttr(right + '.jointOrientY')
        Z = mc.getAttr(right + '.jointOrientZ')
        mc.setAttr(right + '.jointOrientX', X)
        mc.setAttr(right + '.jointOrientY', Y * -1)
        mc.setAttr(right + '.jointOrientZ', Z * -1)
        try:
            if mc.listRelatives(each, ap=1):
                mc.parent(right, mc.listRelatives(each, ap=1)[0].replace(side[0], side[1], 1))
        except:
            pass
