import maya.cmds as mc
from tbx import getShape

# todo : contiguous edges sorter or step by step edges selection interface

########################################################################################################################
nbOfColumn = 0
width = 30

def ui():


    winID = 'rvtUI'
    if mc.window(winID, exists=True):
        mc.deleteUI(winID)
    mc.window(winID, title='Follicle Rivet creator', w=width, s=False, rtf=True)

    mc.columnLayout('columnMain', w=width)
    mc.rowLayout('rowEdges', nc=100)
    mc.columnLayout('columnAddDel', cal='center')
    mc.button('+', w=20, command=addColumn)
    mc.button('-', w=20, command=delColumn)
    mc.setParent('..')
    addColumn()
    addColumn()
    mc.setParent('..')
    mc.setParent('..')
    mc.intSliderGrp('nb', l='Number of rivet', cw=(1, 90), cl3=('center', 'center', 'center'), value=1, min=1, max=10, field=True, fieldMinValue=1, fieldMaxValue=1000, w=width)
    mc.button('Create fRivet', command=createFRivet, w=width)
    mc.showWindow()


def upEdges(*args):
    name = 'edges'+str(args[0])
    mc.textScrollList(name, e=True, ra=True)
    edges = [x for x in mc.ls(sl=True, fl=True) if '.e' in x]
    mc.textScrollList(name, e=True, append=edges)


def addColumn(*args):
    global nbOfColumn
    nbOfColumn += 1
    global width
    width += 204
    nbr = str(nbOfColumn)
    mc.columnLayout('columnEdges'+nbr, cal='center', parent='rowEdges')
    mc.text(label='Edges', align='center', w=200)
    mc.textScrollList('edges'+nbr, w=200, h=100, allowMultiSelection=True)
    mc.button('upSel'+nbr, label='Update selection', w=200, command=lambda x: upEdges(nbr))
    mc.columnLayout('columnMain', e=True, w=width)


def delColumn(*args):
    global nbOfColumn
    global width
    nbr = str(nbOfColumn)
    if nbOfColumn > 2:
        mc.deleteUI('columnEdges'+nbr)
        nbOfColumn -= 1
        width -= 204
        mc.window('rvtUI', e=True, w=width)


def createFRivet(*args):
    edges = []
    for i in range(nbOfColumn):
        edges.append(mc.textScrollList('edges'+str(i+1), q=True, ai=True))
    nb = mc.intSliderGrp('nb', q=True, value=True)
    do_fRivet(edges, nb)
########################################################################################################################


def do_fRivet(edges, nb=1, param='U', mesh=None):
    """
    :param edges: input edges (number or full name) list, e.g.: [[12,13], [21,22], [33,34]]
    :param mesh: input or select a mesh
    :param nb: number of rivet wanted
    :param param: 'U' or 'V' param of the follicle
    :return: the rivet transform node.
    """

    if edges:

        # Getting mesh if one
        if not mesh:
            mesh = mc.ls(sl=True, type='transform')

        # Getting edges
        edges = [arg for arg in edges if arg not in mesh]
        if not edges or len(edges) < 2 or not edges[0] or not edges[1]:
            mc.warning('Not enough or no edges given')
            return

        # if edges are given as integer converting them to real edges name string
        edgesType = type(edges[0])
        if edgesType is int:
            if not mesh:
                mc.warning('Please select a mesh')
                return
            edges = convertIntEdges(mesh[0], edges)
        # elif edges are given as list of integer converting them to real edges name string
        elif edgesType is list or edgesType is tuple:
            for i, edge in enumerate(edges):
                if type(edge[0]) is int:
                    if not mesh:
                        mc.warning('Please select a mesh')
                        return
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

    rvtGrp = mc.group(em=True, n='rvtGrp_#')
    mc.parent(grpW, rvtGrp)

    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0/(nb-1)
        pos = 0.0

    surf = grpW
    rvts = []
    for i in range(nb):
        rvt = do_follicle(surface=surf, pos=pos, param=param)
        pos += dif

    # adding a locactor shape
        loc = mc.spaceLocator(n='rivetloc_#')[0]
        locshape = getShape(loc)
        mc.parent(locshape, rvt, r=True, s=True)
        mc.delete(loc)
        rvt = mc.rename(rvt, 'rivet_#')
        rvtshape = getShape(rvt)[0]
        mc.setAttr(rvtshape+'.visibility', 0)
        mc.reorder(locshape, front=True)
        mc.parent(rvt, rvtGrp)

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
        rvts.append(rvt)

    return rvts


def convertIntEdges(mesh, edges):
    for i, edge in enumerate(edges):
        edges[i] = mesh + '.e[' + str(edge) + ']'
    return edges


def do_follicle(surface=None, pos=0.5, param='U'):

    if not surface:
        surface = mc.ls(sl=True, fl=True)
    if not surface:
        mc.warning('Select a nurbs surface')
        return
    if not param == 'U':
        paramlist = ['V', 'U']
    else:
        paramlist = ['U', 'V']

    surfaceshape = getShape(surface)[0]
    if not mc.nodeType(surfaceshape) == 'nurbsSurface':
        mc.warning('No nurbs surface given')
        return

    follicleshape = mc.createNode('follicle', n=surface+'_follicleShape#')
    follicle = mc.listRelatives(follicleshape, p=True)[0]
    follicle = mc.rename(follicle, surface+'_follicle', ignoreShape=True)
    mc.connectAttr(surfaceshape+'.local', follicleshape+'.inputSurface', f=True)
    mc.connectAttr(surfaceshape+'.worldMatrix[0]', follicleshape+'.inputWorldMatrix', f=True)
    mc.connectAttr(follicleshape+'.outRotate', follicle+'.rotate', f=True)
    mc.connectAttr(follicleshape+'.outTranslate', follicle+'.translate', f=True)
    for manip in 'tr':
        for axis in 'xyz':
            mc.setAttr(follicle+'.'+manip+axis, lock=True)
    mc.setAttr(follicleshape+'.parameter'+paramlist[0], pos)
    mc.setAttr(follicleshape+'.parameter'+paramlist[1], 0.5)

    return follicle

"""
# WIP
def edgesSort(edges=None):

    sort = []
    poly = edges[0].split('.')[0]
    edgesNum = [int(a.split('[')[-1].split(']')[0]) for a in edges]
    print(edgesNum)in

    for i, edge in enumerate(edgesNum):
        if i+1 == len(edgesNum):
            break
        if mc.polySelect(poly, elp=(edge, edgesNum[i+1])):
            print('loop')
        else:
            print('not loop')
    mc.select(edges, r=True)


# TO TEST

edges = {edge: [edgesInLoop], ...}
liste = []
for each in edges:
    for j in edges:
        if each in j:
            liste[jIndexInedges].append(each)
"""