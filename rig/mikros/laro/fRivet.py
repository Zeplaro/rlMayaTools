import maya.cmds as mc
from functools import partial

"""
import mayaRigTools_sk.sandBox.laro.fRivet as fr
reload(fr)
fr.launch_ui()
"""


def launch_ui():
    if mc.window('rvtUI', exists=True):
        mc.deleteUI('rvtUI')
    FRivet_ui()


class FRivet_ui:
    nbOfColumn = 0
    width = 30

    def __init__(self):
        self.ui_layout()
        mc.showWindow('rvtUI')

    def ui_layout(self):

        mc.window('rvtUI', title='Follicle Rivet creator', w=self.width, s=False, rtf=True)

        mc.columnLayout('columnMain', w=self.width)
        mc.rowLayout('rowEdges', nc=100)
        mc.columnLayout('columnAddDel', cal='center')
        mc.button('+', w=20, command=self.add_column)
        mc.button('-', w=20, command=self.del_column)
        mc.setParent('..')
        self.add_column()
        self.add_column()
        mc.setParent('..')
        mc.setParent('..')
        mc.intSliderGrp('nb', l='Number of rivet', cw=(1, 90), cl3=('center', 'center', 'center'), value=1, min=1,
                        max=10, field=True, fieldMinValue=1, fieldMaxValue=1000, w=self.width)
        mc.button('Create Rivet', command=self.launch_fRivet, w=self.width)

    @staticmethod
    def update_edges(*args):
        name = 'edges' + str(args[0])
        mc.textScrollList(name, e=True, ra=True)
        edges = [x for x in mc.ls(sl=True, fl=True) if '.e' in x]
        mc.textScrollList(name, e=True, append=edges)

    @classmethod
    def add_column(cls, *args):
        cls.nbOfColumn += 1
        cls.width += 204
        mc.columnLayout('columnEdges{}'.format(cls.nbOfColumn), cal='center', parent='rowEdges')
        mc.text(label='Edges', align='center', w=200)
        mc.textScrollList('edges{}'.format(cls.nbOfColumn), w=200, h=100, allowMultiSelection=True)
        mc.button('upSel{}'.format(cls.nbOfColumn), label='Update from selection', w=200,
                  command=partial(cls.update_edges, cls.nbOfColumn))
        if cls.nbOfColumn > 2:
            mc.intSliderGrp('nb', e=True, w=cls.width)
            mc.button('Create_Rivet', e=True, w=cls.width)
        mc.columnLayout('columnMain', e=True, w=cls.width)

    @classmethod
    def del_column(cls, *args):
        if cls.nbOfColumn > 2:
            mc.deleteUI('columnEdges{}'.format(cls.nbOfColumn))
            cls.nbOfColumn -= 1
            cls.width -= 204
            mc.intSliderGrp('nb', e=True, w=cls.width)
            mc.button('Create_Rivet', e=True, w=cls.width)
            mc.window('rvtUI', e=True, w=cls.width)

    def launch_fRivet(self, *args):
        while not mc.textScrollList('edges' + str(self.nbOfColumn), q=True, ai=True) and self.nbOfColumn > 2:
            self.del_column()
        edges = []
        for i in range(self.nbOfColumn):
            edges.append(mc.textScrollList('edges' + str(i + 1), q=True, ai=True))
        nb = mc.intSliderGrp('nb', q=True, value=True)
        do_fRivet(edges=edges, nb=nb)


def do_fRivet(edges=None, nb=1, param='U', mesh=None):
    """
    :param edges: input edges (number or full name) list, e.g.: [[12,13], [21,22], [33,34]]
    :param nb: number of rivet wanted
    :param param: 'U' or 'V' param of the follicle
    :param mesh: input or select a mesh
    :return: the rivet transform node.
    """

    if edges:

        # Getting mesh if one
        if not mesh:
            mesh = mc.ls(sl=True, type='transform')

        # Getting edges
        edges = [arg for arg in edges if arg not in mesh]
        if not edges or len(edges) < 2 or not edges[0] or not edges[1] or None in edges:
            mc.warning('Not enough or no edges given')
            return

        # if edges are given as integer converting them to real edges name string
        edges_type = type(edges[0])
        if edges_type is int:
            if not mesh:
                mc.warning('Please select a mesh')
                return
            edges = convert_int_edges(mesh[0], edges)
        # elif edges are given as list of integer converting them to real edges name string
        elif edges_type is list or edges_type is tuple:
            for i, edge in enumerate(edges):
                if type(edge[0]) is int:
                    if not mesh:
                        mc.warning('Please select a mesh')
                        return
                    edges[i] = convert_int_edges(mesh[0], edge)

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
    surface = mc.loft(crvs, ch=True, u=True, c=False, ar=True, d=3, ss=1, rn=False, po=0, rsn=False, n='rvt_surf#')[0]

    # grpWorld with curves and surface to clean
    grp_w = mc.group(em=True, n='rvtWorld#')
    mc.setAttr(grp_w + '.inheritsTransform', 0)
    mc.setAttr(grp_w + '.visibility', 0)
    mc.parent(get_shape(surface), grp_w, r=True, s=True)
    mc.delete(surface)
    for crv in crvs:
        mc.parent(get_shape(crv), grp_w, r=True, s=True)
        mc.delete(crv)
    for i in 'trs':
        for axe in 'xyz':
            mc.setAttr(grp_w + '.' + i + axe, lock=True)

    rvt_grp = mc.group(em=True, n='rvtGrp_#')
    mc.parent(grp_w, rvt_grp)

    if nb < 2:
        pos = 0.5
        dif = 0
    else:
        dif = 1.0 / (nb - 1)
        pos = 0.0

    surface = grp_w
    rvts = []
    for i in range(nb):
        rvt = do_follicle(surface=surface, pos=pos, param=param)
        pos += dif

        # adding a locactor shape
        loc = mc.spaceLocator(n='rivetloc_#')[0]
        locshape = get_shape(loc)
        mc.parent(locshape, rvt, r=True, s=True)
        mc.delete(loc)
        rvt = mc.rename(rvt, 'rivet_#')
        rvtshape = get_shape(rvt)[0]
        mc.setAttr(rvtshape + '.visibility', 0)
        mc.reorder(locshape, front=True)
        mc.parent(rvt, rvt_grp)
        rvts.append(rvt)

    return rvts


def convert_int_edges(mesh, edges):
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

    surfaceshape = get_shape(surface)[0]
    if not mc.nodeType(surfaceshape) == 'nurbsSurface':
        mc.warning('No nurbs surface given')
        return

    follicleshape = mc.createNode('follicle', n=surface + '_follicleShape#')
    follicle = mc.listRelatives(follicleshape, p=True)[0]
    follicle = mc.rename(follicle, surface + '_follicle', ignoreShape=True)
    mc.connectAttr(surfaceshape + '.local', follicleshape + '.inputSurface', f=True)
    mc.connectAttr(surfaceshape + '.worldMatrix[0]', follicleshape + '.inputWorldMatrix', f=True)
    mc.connectAttr(follicleshape + '.outRotate', follicle + '.rotate', f=True)
    mc.connectAttr(follicleshape + '.outTranslate', follicle + '.translate', f=True)

    # creating a stronger follicle position to be able to group it
    cmx = mc.createNode('composeMatrix', n='cmx_rvt#')
    mmx = mc.createNode('multMatrix', n='mmx_rvt#')
    dmx = mc.createNode('decomposeMatrix', n='dmx_rvt#')
    mc.connectAttr(follicleshape + '.outRotate', cmx + '.inputRotate')
    mc.connectAttr(follicleshape + '.outTranslate', cmx + '.inputTranslate')
    mc.connectAttr(cmx + '.outputMatrix', mmx + '.matrixIn[0]')
    mc.connectAttr(follicle + '.parentInverseMatrix', mmx + '.matrixIn[1]')
    mc.connectAttr(mmx + '.matrixSum', dmx + '.inputMatrix')
    mc.connectAttr(dmx + '.outputTranslate', follicle + '.translate', f=True)
    mc.connectAttr(dmx + '.outputRotate', follicle + '.rotate', f=True)

    for manip in 'tr':
        for axis in 'xyz':
            mc.setAttr(follicle + '.' + manip + axis, lock=True)
    mc.setAttr(follicleshape + '.parameter' + paramlist[0], pos)
    mc.setAttr(follicleshape + '.parameter' + paramlist[1], 0.5)

    return follicle


def get_shape(objs=None):
    shapes = mc.listRelatives(objs, s=True, pa=1, ni=True) or []
    return shapes
