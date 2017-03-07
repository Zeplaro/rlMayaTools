# Mirror JNT & orient L>R
import maya.cmds as mc

def doMirror(side='L'):
    sel = mc.ls(sl=1)
    if side=='R':
        side=['R_','L_']
    else:
        side=['L_','R_']

    for each in sel:
        alt = each.replace(side[0], side[1], 1)
        mc.duplicate(each, n=alt)
        mc.parent(alt, w=1)
        mc.setAttr(alt + '.translateX', mc.getAttr(alt + '.translateX') * -1)
        X = mc.getAttr(alt + '.jointOrientX')
        Y = mc.getAttr(alt + '.jointOrientY')
        Z = mc.getAttr(alt + '.jointOrientZ')
        mc.setAttr(alt + '.jointOrientX', X)
        mc.setAttr(alt + '.jointOrientY', Y * -1)
        mc.setAttr(alt + '.jointOrientZ', Z * -1)

        if mc.listRelatives(each, ap=1):
            mc.parent(alt, mc.listRelatives(each, ap=1)[0].replace(side[0], side[1], 1))