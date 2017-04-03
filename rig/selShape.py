import maya.cmds as mc


def do_selShape(q=False, objs=[]):
    childs = []
    if q:
        if isinstance(objs, str):
            objs = [objs]
    else:
        objs = mc.ls(sl=1)

    for obj in objs:
        if mc.objectType(obj, isa='shape'):
            childs += [obj]
            continue
        child = mc.listRelatives(obj, c=1, typ='shape') or []
        child = [shape for shape in child if 'Orig' not in shape]
        childs += child

    shapes = []
    [shapes.append(i) for i in childs if i not in shapes]

    if not q:
        mc.select(shapes,r=1)
    return shapes
