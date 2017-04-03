import maya.cmds as mc
'''
To do : check if already shape
'''


def do_selShape(q=False, objs=[]):
    childs = []
    if q:
        if isinstance(objs, str):
            objs = [objs]
    else:
        objs = mc.ls(sl=1)

    for obj in objs:
        child = mc.listRelatives(obj,c=1,typ='shape')
        child = [shape for shape in child if 'Orig' not in shape]
        childs += child
    if not q:
        mc.select(childs,r=1)
    return childs
