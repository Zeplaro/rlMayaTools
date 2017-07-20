import maya.cmds as mc


class Launch_ui:

    winID = 'rlShapeUI'

    def __init__(self):
        self.ui_layout()
        mc.showWindow(self.winID)

    def ui_layout(self):
        if mc.window(self.winID, exists=True):
            mc.deleteUI(self.winID)
        mc.window(self.winID, title='rl Shape creator', s=True, rtf=True)

        mc.



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

"""
todo: quad_round_arrow, cube, sphere, cylinder, locator, cross, half_circle, simple_arrow, octo_arrown, double_arrow,
      quad_bent_arrow, double_bent_arrow, fly, line, pyramide, double_pyramide, half_sphere, wobbly_circle, eye, foot,
      pin_sphere, pin_cube, pin_pyramide, pin_double_pyramide, pin_circle_crossed, star, circle_cross,
      double_pin_circle_crossed, u_turn_arrow, pin_arrow, cross_axis, sparkle
"""
class Shapes():

    @staticmethod
    def scale(p, scale=1):
        return [(x * scale, y * scale, z * scale) for x, y, z in p]

    @staticmethod
    def circle(scale=1):
        crv = mc.circle(nr=(0, 1, 0), r=scale, ch=False)
        return crv

    def square(self, scale=1):
        p = [(1, 0, 1), (-1, 0, 1), (-1, 0, -1), (1, 0, -1)]
        p = self.scale(p, scale)
        crv = mc.curve(d=1, p=p)
        return crv

    def quad_arrow(self, scale=1):
        p = [(0, 0, -5), (2, 0, -3), (1, 0, -3), (1, 0, -1), (3, 0, -1), (3, 0, -2), (5, 0, 0), (3, 0, 2),
             (3, 0, 1), (1, 0, 1), (1, 0, 3), (2, 0, 3), (0, 0, 5), (-2, 0, 3), (-1, 0, 3), (-1, 0, 1), (-3, 0, 1),
             (-3, 0, 2), (-5, 0, 0), (-3, 0, -2), (-3, 0, -1), (-1, 0, -1), (-1, 0, -3), (-2, 0, -3), (0, 0, -5)]
        p = self.scale(p, scale)
        crv = mc.curve(d=1, p=p)
        return crv
