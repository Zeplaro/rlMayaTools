import maya.cmds as mc
import follicle as f
from tbx import getShape

# todo : contiguous edges sorter or step by step edges selection interface


def do_rivet(edges=False):

    if not edges:
        edges = mc.ls(sl=True, fl=True)
    if not edges or len(edges) < 2:
        mc.warning('Please select at least two edges')
        return

    crvs = []
    for edge in edges:
        mc.select(edge, r=True)
        crvs.append(mc.polyToCurve(form=2, degree=1, n='rvt_crv_#')[0])
    for crv in crvs:
        mc.rebuildCurve(crv, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=False, kep=True, kt=False, s=0, d=3, tol=0.01)
    surf = mc.loft(crvs, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0, rsn=False, n='rvt_surf#')[0]
    rvt = f.do_follicle(surface=surf)[0]

    rvtshape = getShape(rvt)[0]
    mc.setAttr(rvt+'.inheritsTransform', 0)
    mc.setAttr(rvtshape+'.visibility', 0)
    loc = mc.spaceLocator(n='rvtloc#')[0]
    locshape = getShape(loc)
    for axe in 'XYZ':
        mc.setAttr(loc+'.localScale'+axe, 0.1)
    mc.parent(locshape, rvt, r=True, s=True)

    grpW = mc.group(em=True, n='rvtWorld#')
    mc.setAttr(grpW+'.inheritsTransform', 0)
    mc.setAttr(grpW+'.visibility', 0)
    mc.parent(getShape(surf), grpW, r=True, s=True)
    mc.delete(surf, loc)
    for crv in crvs:
        mc.parent(getShape(crv), grpW, r=True, s=True)
        mc.delete(crv)
    for i in 'trs':
        for axe in 'xyz':
            mc.setAttr(grpW+'.'+i+axe, lock=True)
    mc.group(rvt, grpW, n='rvtGrp_#')
    rvt = mc.rename(rvt, 'rivet_#')
    mc.reorder(locshape, front=True)

    return rvt
