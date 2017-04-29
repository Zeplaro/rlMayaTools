import maya.cmds as mc


def do_selShape(objs=None):

    sel = False
    if not objs:
        objs = mc.ls(sl=True, fl=True)[0]
        sel = True
    shapes = []
    [shapes.append(shape) for shape in mc.listRelatives(objs, s=True, pa=1) or [] if 'Orig' not in shape]
    if sel:
        mc.select(shapes, r=True)
    return shapes
