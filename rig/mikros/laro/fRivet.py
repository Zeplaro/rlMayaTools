import maya.cmds as mc

"""
import mayaRigTools_sk.sandBox.laro.fRivet as fr
reload(fr)
fr.do_fRivet()
"""


def do_fRivet(*args):
    """
    :param args: if more than two edges, input edges (number or full name) list, e.g.: [12,13], [21,22], [33,34] and
                input or select a mesh
    :return: the rivet transform node.
    """

    if args:

        # Getting mesh if one
        mesh = [arg for arg in args if isinstance(arg, basestring) and '.' not in arg]
        if not mesh:
            mesh = mc.ls(sl=1, type='transform')
        if not mesh:
            mc.warning('Please select a mesh')
            return

        # Getting edges
        edges = [arg for arg in args if arg not in mesh]
        if not edges:
            mc.warning('No edges given')
            return

        # if edges are given as integer converting them to real edges name string
        if type(edges[0]) is int:
            edges = convertIntEdges(mesh[0], edges)
        # elif edges are given as list of integer converting them to real edges name string
        elif type(edges[0]) is list or type(edges[0]) is tuple:
            for i, edge in enumerate(edges):
                if type(edge[0]) is int:
                    edges[i] = convertIntEdges(mesh[0], edge)

    else:
        edges = [edge for edge in mc.ls(sl=True, fl=True) if '.' in edge]

    if len(edges) < 2:
        mc.warning('Please select at least two edges')
        return

    crvs = []
    for edge in edges:
        mc.select(edge, r=True)
        crvs.append(mc.polyToCurve(form=2, degree=1, n='rvt_crv_#')[0])
    for crv in crvs:
        mc.rebuildCurve(crv, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=False, kep=True, kt=False, s=0, d=3, tol=0.01)
    surf = mc.loft(crvs, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0, rsn=False, n='rvt_surf#')[0]
    rvt = do_follicle(surface=surf)[0]

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


def convertIntEdges(mesh, edges):
    for i, edge in enumerate(edges):
        edges[i] = mesh + '.e[' + str(edge) + ']'
    return edges


def getShape(objs=None):

    shapes = [shape for shape in mc.listRelatives(objs, s=True, pa=1) or [] if 'Orig' not in shape]
    return shapes


def do_follicle(nb=1, param='U', surface=None):

    if not surface:
        surface = mc.ls(sl=True, fl=True)
    if not surface:
        mc.warning('Select a nurbs surface')
        return
    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0/(nb-1)
        pos = 0.0
    if not param == 'U':
        paramlist = ['V', 'U']
    else:
        paramlist = ['U', 'V']
    follicles = []
    for i in range(nb):
        surfaceshape = getShape(surface)[0]
        if not mc.nodeType(surfaceshape) == 'nurbsSurface':
            continue
        follicleshape = mc.createNode('follicle', n=surface+'_follicleShape#')
        follicle = mc.listRelatives(follicleshape, p=True)[0]
        follicle = mc.rename(follicle, surface+'_follicle', ignoreShape=True)
        follicles.append(follicle)
        mc.connectAttr(surfaceshape+'.local', follicleshape+'.inputSurface', f=True)
        mc.connectAttr(surfaceshape+'.worldMatrix[0]', follicleshape+'.inputWorldMatrix', f=True)
        mc.connectAttr(follicleshape+'.outRotate', follicle+'.rotate', f=True)
        mc.connectAttr(follicleshape+'.outTranslate', follicle+'.translate', f=True)
        for manip in 'tr':
            for axis in 'xyz':
                mc.setAttr(follicle+'.'+manip+axis, lock=True)
        mc.setAttr(follicleshape+'.parameter'+paramlist[0], pos)
        pos += dif
        mc.setAttr(follicleshape+'.parameter'+paramlist[1], 0.5)

    return follicles
