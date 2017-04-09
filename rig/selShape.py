import maya.cmds as mc


def do_selShape(objs=None):

    if objs:
        if isinstance(objs, str) or isinstance(objs, unicode):  # if a string is given converts it in a list
            objs = [objs]
        sel = False
    else:
        objs = mc.ls(sl=1)
        sel = True

    childs = []
    for obj in objs:
        if mc.objectType(obj, isa='shape'):  # if selection is already a shape add it and continue
            childs += [obj]
            continue
        child = mc.listRelatives(obj, c=1, typ='shape') or []
        child = [shape for shape in child if 'Orig' not in shape]
        childs += child

    # Removing doublon in case shape was already selected
    shapes = []
    [shapes.append(i) for i in childs if i not in shapes]

    if sel:
        mc.select(shapes, r=1)
    return shapes
