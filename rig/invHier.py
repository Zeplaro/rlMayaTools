import maya.cmds as mc


def do_invHier(objs=None):

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

    grandC = mc.listRelatives(son, c=True) or []
    grandD = mc.listRelatives(dad, p=True) or []
    temp = []
    if grandC:
        temp = mc.group(em=True, w=True, n='tempGrp#')
        mc.parent(grandC, temp)
    if grandD:
        mc.parent(dad, w=True)

    ad = mc.listRelatives(dad, ad=True)[::-1]
    for c in ad:
        mc.parent(c, w=True)
    for c in range(len(ad)-1):
        mc.parent(ad[c], ad[c+1])
    mc.parent(dad, ad[:-1])
    if grandD:
        mc.parent(son, grandD)
    if grandC:
        mc.parent(grandC, dad)
    if temp:
        mc.delete(temp)
