import maya.cmds as mc


def do_selShape(objs=None):

    sel = False
    if not objs:
        objs = mc.ls(sl=True, fl=True)
        sel = True
    shapes = []
    for obj in objs:
        [shapes.append(shape) for shape in mc.listRelatives(obj, s=True) or [] if 'Orig' not in shape]
    if sel:
        mc.select(shapes, r=True)
    print(shapes)
    return shapes
