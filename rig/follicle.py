import maya.cmds as mc
import tbx


def do_follicle(nb=1, param='U', surface=None):

    if not surface:
        surface = mc.ls(sl=True, fl=True)
    if not surface:
        mc.warning('Select a nurbs surface')
        return
    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0/(nb-1)
        pos = 0.0
    if not param == 'U':
        paramlist = ['V', 'U']
    else:
        paramlist = ['U', 'V']
    follicles = []
    for i in range(nb):
        surfaceshape = tbx.getShape(surface)[0]
        if not mc.nodeType(surfaceshape) == 'nurbsSurface':
            continue
        follicleshape = mc.createNode('follicle', n=surface+'_follicleShape#')
        follicle = mc.listRelatives(follicleshape, p=True)[0]
        follicle = mc.rename(follicle, surface+'_follicle', ignoreShape=True)
        follicles.append(follicle)
        mc.connectAttr(surfaceshape+'.local', follicleshape+'.inputSurface', f=True)
        mc.connectAttr(surfaceshape+'.worldMatrix[0]', follicleshape+'.inputWorldMatrix', f=True)
        mc.connectAttr(follicleshape+'.outRotate', follicle+'.rotate', f=True)
        mc.connectAttr(follicleshape+'.outTranslate', follicle+'.translate', f=True)
        for manip in 'tr':
            for axis in 'xyz':
                mc.setAttr(follicle+'.'+manip+axis, lock=True)
        mc.setAttr(follicleshape+'.parameter'+paramlist[0], pos)
        pos += dif
        mc.setAttr(follicleshape+'.parameter'+paramlist[1], 0.5)

    return follicles
