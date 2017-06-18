import maya.cmds as mc
import follicle as f
from tbx import getShape

# todo : contiguous edges sorter or step by step edges selection interface


def do_rivet(edges=None):

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

    # grpWorld with curves and surface to clean
    grpW = mc.group(em=True, n='rvtWorld#')
    mc.setAttr(grpW+'.inheritsTransform', 0)
    mc.setAttr(grpW+'.visibility', 0)
    mc.parent(getShape(surf), grpW, r=True, s=True)
    mc.delete(surf)
    for crv in crvs:
        mc.parent(getShape(crv), grpW, r=True, s=True)
        mc.delete(crv)
    for i in 'trs':
        for axe in 'xyz':
            mc.setAttr(grpW+'.'+i+axe, lock=True)

    # adding a locactor shape
    loc = mc.spaceLocator(n='rivetloc_#')[0]
    locshape = getShape(loc)
    mc.parent(locshape, rvt, r=True, s=True)
    mc.delete(loc)
    rvt = mc.rename(rvt, 'rivet_#')
    rvtshape = getShape(rvt)[0]
    mc.setAttr(rvtshape+'.visibility', 0)
    mc.reorder(locshape, front=True)

    # grouping it all
    rvtGrp = mc.group(em=True, n='rvtGrp_#')
    mc.xform(rvtGrp, ws=True, ro=mc.xform(rvt, q=True, ws=True, ro=True), t=mc.xform(rvt, q=True, ws=True, t=True))
    mc.parent(rvt, grpW, rvtGrp)

    # creating a stronger rivet position to be able to group it
    cmx = mc.createNode('composeMatrix', n='cmx_rvt#')
    mmx = mc.createNode('multMatrix', n='mmx_rvt#')
    dmx = mc.createNode('decomposeMatrix', n='dmx_rvt#')
    mc.connectAttr(rvtshape+'.outRotate', cmx+'.inputRotate')
    mc.connectAttr(rvtshape+'.outTranslate', cmx+'.inputTranslate')
    mc.connectAttr(cmx+'.outputMatrix', mmx+'.matrixIn[0]')
    mc.connectAttr(rvt+'.parentInverseMatrix', mmx+'.matrixIn[1]')
    mc.connectAttr(mmx+'.matrixSum', dmx+'.inputMatrix')
    mc.connectAttr(dmx+'.outputTranslate', rvt+'.translate', f=True)
    mc.connectAttr(dmx+'.outputRotate', rvt+'.rotate', f=True)

    return rvt

# WIP
def edgesSort(edges=None):

    sort = []
    poly = edges[0].split('.')[0]
    edgesNum = [int(a.split('[')[-1].split(']')[0]) for a in edges]
    print(edgesNum)

    for i, edge in enumerate(edgesNum):
        if i+1 == len(edgesNum):
            break
        if mc.polySelect(poly, elp=(edge, edgesNum[i+1])):
            print('loop')
        else:
            print('not loop')
    mc.select(edges, r=True)
