import maya.cmds as mc
import follicle as f
from tbx import getShape

# todo : contiguous edges sorter or step by step edges selection interface

nbOfColumn = 2
width = 440


def ui():

    # TODO : ranger en collumn au lieu de row

    winID = 'rvtUI'
    if mc.window(winID, exists=True):
        mc.deleteUI(winID)
    mc.window(winID, title='Follicle Rivet creator', s=False, rtf=True)

    mc.columnLayout('columnMain', w=width)
    mc.rowLayout('rowTitle', nc=3)
    mc.separator(style='none', w=21)
    mc.text(label='Edges', align='center', w=200)
    mc.text(label='Edges', align='center', w=200)
    mc.setParent('..')
    mc.rowLayout('rowEdges', nc=100)
    mc.columnLayout('columnAddDel')
    mc.button('+', w=20, command=addColumn)
    mc.button('-', w=20, command=delColumn)
    mc.setParent('..')
    mc.columnLayout('columnEdges1')
    mc.textScrollList('edges1', w=200, h=100, allowMultiSelection=True)
    mc.button('upSel1', label='Update selection', w=200, command=lambda x: upEdges(1))
    mc.setParent('..')
    mc.columnLayout('columnEdges2')
    mc.textScrollList('edges2', w=200, h=100, allowMultiSelection=True)
    mc.button('upSel2', label='Update selection', w=200, command=lambda x: upEdges(2))
    mc.setParent('..')
    mc.setParent('..')
    mc.button('Create fRivet', command=createFRivet)
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
    mc.columnLayout('columnEdges'+nbr, parent='rowEdges')
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
        mc.columnLayout('columnMain', e=True, w=width)


def createFRivet(*args):
    edges = []
    for i in range(nbOfColumn):
        edges.append(mc.textScrollList('edges'+str(i+1), q=True, ai=True))
        print edges


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
        if not edges or len(edges) < 2:
            mc.warning('Not enough or no edges given')
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


def convertIntEdges(mesh, edges):
    for i, edge in enumerate(edges):
        edges[i] = mesh + '.e[' + str(edge) + ']'
    return edges

"""
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


# TO TEST

edges = {edge: [edgesInLoop], ...}
liste = []
for each in edges:
    for j in edges:
        if each in j:
            liste[jIndexInedges].append(each)
"""