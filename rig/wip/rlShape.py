import maya.cmds as mc


def parent_shape(parent=None, child=None, freeze=False):

    sel = mc.ls(sl=True)
    if not parent or not child:
        if len(sel) < 2:
            mc.warning('Select a shape and a parent transform')
            return
        child = sel[0]
        parent = sel[1]
    if not mc.nodeType(parent) == 'transform':
        mc.warning('Select a shape and a parent transform')
        return
    if parent in (mc.listRelatives(child, parent=True) or []):
        mc.warning(child+' is already a child of '+parent)
        return
    if freeze:
        child_parent = mc.listRelatives(child, parent=True)[0]
        print(child_parent)
        child_grd_parent = mc.listRelatives(child_parent, parent=True) or []
        print(child_grd_parent)
        child_parent_t = mc.xform(child_parent, q=True, ws=True, t=True)
        child_parent_ro = mc.xform(child_parent, q=True, ws=True, ro=True)
        child_parent_s = mc.xform(child_parent, q=True, ws=True, s=True)
        grp_freeze = mc.group(n='grpfreeze#', em=True, w=True)
        mc.parent(grp_freeze, parent, r=True)
        mc.parent(child_parent, grp_freeze)
        mc.parent(grp_freeze, w=True)
        for j in 'xyz':
            for i in 'tr':
                mc.setAttr(grp_freeze+'.'+i+j, 0)
            mc.setAttr(grp_freeze+'.s'+j, 1)
        mc.makeIdentity(child_parent, a=True)

    mc.parent(child, parent, r=True, s=True)

    if freeze:
        if child_grd_parent:
            mc.parent(child_parent, child_grd_parent[0])
        else:
            mc.parent(child_parent, w=True)
        mc.delete(mc.parentConstraint(grp_freeze, child_parent, mo=False))
        mc.makeIdentity(child_parent, a=True)
        mc.xform(child_parent, ro=child_parent_ro, t=child_parent_t, s=child_parent_s, ws=True)
        mc.delete(grp_freeze)
