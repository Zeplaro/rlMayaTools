import maya.cmds as mc
import selShape as ss


def do_follicle(nb=1, param='U', objs=None):

    if not objs:
        objs = mc.ls(sl=True, fl=True)
    if not objs:
        mc.warning('Select a nurbs surface')
        return
    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0/(nb-1)
        pos = 0.0
    follicleshapes = []
    for i in range(nb):
        for surface in objs:
            surfaceshape = ss.do_selShape([surface])[0]
            if not mc.nodeType(surfaceshape) == 'nurbsSurface':
                continue
            follicleshape = mc.createNode('follicle', n=surface+'_follicleShape#')
            follicleshapes.append(follicleshape)
            follicle = mc.listRelatives(follicleshape, p=True)[0]
            follicle = mc.rename(follicle, surface+'_follicle', ignoreShape=True)
            mc.connectAttr(surfaceshape+'.local', follicleshape+'.inputSurface', f=True)
            mc.connectAttr(surfaceshape+'.worldMatrix[0]', follicleshape+'.inputWorldMatrix', f=True)
            mc.connectAttr(follicleshape+'.outRotate', follicle+'.rotate', f=True)
            mc.connectAttr(follicleshape+'.outTranslate', follicle+'.translate', f=True)
            for manip in 'tr':
                for axis in 'xyz':
                    mc.setAttr(follicle+'.'+manip+axis, lock=True)
            if not param == 'U':
                param = ['V', 'U']
            else:
                param = ['U', 'V']
            mc.setAttr(follicleshape+'.parameter'+param[0], pos)
            pos += dif
            mc.setAttr(follicleshape+'.parameter'+param[1], 0.5)

    return follicleshapes
