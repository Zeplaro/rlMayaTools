#Mirror JNT & orient L>R
import maya.cmds as mc

def doMirrorjnt():
    sel=mc.ls(sl=1)

    for each in sel:
        right=each.replace('L_','R_',1)
        mc.duplicate(each,n=right)
        mc.parent(right,w=1)
        mc.setAttr(right+'.translateX',mc.getAttr(right+'.translateX')*-1)
        X=mc.getAttr(right+'.jointOrientX')
        Y=mc.getAttr(right+'.jointOrientY')
        Z=mc.getAttr(right+'.jointOrientZ')
        mc.setAttr(right+'.jointOrientX',X)
        mc.setAttr(right+'.jointOrientY',Y*-1)
        mc.setAttr(right+'.jointOrientZ',Z*-1)

        if mc.listRelatives(each,ap=1):
            mc.parent(right,mc.listRelatives(each,ap=1)[0].replace('L_','R_',1))
