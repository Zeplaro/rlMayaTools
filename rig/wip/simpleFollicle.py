import maya.cmds as mc
import rig.selShape as ss

def do_follicle(nb=1,even=False):
    surfaces = mc.ls(sl=1)
    follicleshapes = []
    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0/(nb-1)
        pos = 0.0
    for i in range(nb):
        for surface in surfaces:
            surfaceshape = ss.do_selShape(surface)[0]
            follicleshape = mc.createNode('follicle', n=surface+'_follicleShape')
            follicleshapes.append(follicleshape)
            follicle = mc.listRelatives(follicleshape, p=1)[0]
            follicle = mc.rename(follicle, surface+'_follicle', ignoreShape=1)
            mc.connectAttr(surfaceshape+'.local', follicleshape+'.inputSurface', f=1)
            mc.connectAttr(surfaceshape+'.worldMatrix[0]', follicleshape+'.inputWorldMatrix', f=1)
            mc.connectAttr(follicleshape+'.outRotate', follicle+'.rotate', f=1)
            mc.connectAttr(follicleshape+'.outTranslate', follicle+'.translate', f=1)
            for manip in 'tr':
                for dir in 'xyz':
                    mc.setAttr(follicle+'.'+manip+dir, lock=1)
            if even:
                mc.setAttr(follicleshape+'.parameterU', pos)
                pos += dif
                mc.setAttr(follicleshape+'.parameterV', 0.5)

    return follicleshapes
