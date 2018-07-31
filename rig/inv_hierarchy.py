import maya.cmds as mc


def inv_hierarchy(*objs):

    if not objs:
        objs = mc.ls(sl=True, fl=True)
    if len(objs) < 2:
        mc.warning('Not enough objects')
        return

    dad = objs[0]
    son = objs[1]

    if son not in mc.listRelatives(dad, ad=True):
        mc.warning('First object not parented to the second')
        return

    grand_c = mc.listRelatives(son, c=True) or []
    grand_d = mc.listRelatives(dad, p=True) or []
    temp = []
    if grand_c:
        temp = mc.group(em=True, w=True, n='tempGrp#')
        mc.parent(grand_c, temp)
    if grand_d:
        mc.parent(dad, w=True)

    ad = mc.listRelatives(dad, ad=True)[::-1]
    for c in ad:
        mc.parent(c, w=True)
    for c in range(len(ad)-1):
        mc.parent(ad[c], ad[c+1])
    mc.parent(dad, ad[:-1])
    if grand_d:
        mc.parent(son, grand_d)
    if grand_c:
        mc.parent(grand_c, dad)
    if temp:
        mc.delete(temp)
