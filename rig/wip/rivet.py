import maya.cmds as mc
import follicle as f
from tbx import getShape as gs

# todo : congious edges sorter


def do_rivet(edges=False):

    if not edges or len(edges) < 2:
        mc.warning('Please select at least two edges')
        return

    crvs = []
    for i in edges:
        mc.select(i, r=True)
        crvs.append(mc.polyToCurve(form=2, degree=1, n='rvt_crv_#')[0])
    for crv in crvs:
        mc.rebuildCurve(crv, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=False, kep=True, kt=False, s=0, d=3, tol=0.01)
    surf = mc.loft(crvs, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0, rsn=False, n='rvt_surf#')[0]

    rvt = f.do_follicle(surface=surf)[0]
    grp = mc.group(surf, rvt, n='rvtgrp#')
    print surf
    print rvt
    mc.setAttr(surf+'.inheritsTransform', 0)
    mc.setAttr(rvt+'.inheritsTransform', 0)

    for crv in crvs:
        print crv
        mc.setAttr(crv+'.inheritsTransform', 0)
        mc.parent(crv, grp)

    return rvt
