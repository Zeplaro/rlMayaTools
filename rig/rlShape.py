import maya.cmds as mc
from PySide import QtGui
from PySide import QtCore
import maya.OpenMayaUI as mui
import shiboken

from functools import partial
from math import sqrt, ceil
import shapeMirror
from tbx import get_shape


def getMayaWin():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(pointer), QtGui.QWidget)


class rlShape_ui(QtGui.QDialog):

    choosenColor = (255, 255, 0)

    def __init__(self, parent=getMayaWin()):
        super(rlShape_ui, self).__init__(parent)

        self.setWindowTitle('rlShape Creator')
        self.setObjectName('rlShapeCreator')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.ui_layout()
        self.ui_connection()

    def ui_layout(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # Shapes groupBox
        self.shapeGroupBox = QtGui.QGroupBox('Shapes')
        self.shapeGroupBox.setAlignment(4)
        self.mainLayout.addWidget(self.shapeGroupBox)

        # Shapes buttons Layout
        shapeLayout = QtGui.QGridLayout()
        self.shapeGroupBox.setLayout(shapeLayout)
        row = 0
        column = 0
        shapeDone = 0
        while shapeDone < len(Shapes.shapesList):
            if column < ceil(sqrt(len(Shapes.shapesList))):
                self.shapeButton = QtGui.QPushButton(Shapes.shapesList[shapeDone])
                self.shapeButton.setObjectName('btn_'+Shapes.shapesList[shapeDone])
                self.shapeButton.setFixedSize(55, 55)
                shapeLayout.addWidget(self.shapeButton, row, column)
                column += 1
                shapeDone += 1
            else:
                column = 0
                row += 1

        # Shape Options
        self.shapeOptionLayout = QtGui.QHBoxLayout()
        self.shapeOptionLayout.setAlignment(4)
        self.mainLayout.addLayout(self.shapeOptionLayout)
        # Replace checkbox
        self.replaceCheckBox = QtGui.QCheckBox('Replace')
        self.replaceCheckBox.setChecked(True)
        self.shapeOptionLayout.addWidget(self.replaceCheckBox)
        # Separator
        self.optionSeparator = QtGui.QLabel()
        self.optionSeparator.setMaximumWidth(1)
        self.optionSeparator.setStyleSheet("background-color: #292929")
        self.shapeOptionLayout.addWidget(self.optionSeparator)
        # Color Picker
        self.colorLabel = QtGui.QLabel(' Color  :')
        self.shapeOptionLayout.addWidget(self.colorLabel)
        self.colorButton = QtGui.QPushButton()
        self.colorButton.setStyleSheet('background-color: rgb' + str(tuple(self.choosenColor)))
        self.colorButton.setFixedSize(50, 20)
        self.shapeOptionLayout.addWidget(self.colorButton)
        # Apply Color button
        self.applyColorButton = QtGui.QPushButton('Apply Color')
        self.shapeOptionLayout.addWidget(self.applyColorButton)

        # Separator line
        # to do : replace with QFrame(QHLine)
        self.separator = QtGui.QLabel()
        self.separator.setMaximumHeight(1)
        self.separator.setStyleSheet("background-color: #292929")
        self.mainLayout.addWidget(self.separator)

        # Mirror button Layout
        self.mirrorLayout = QtGui.QHBoxLayout()
        self.mirrorLayout.setAlignment(4)
        self.mainLayout.addLayout(self.mirrorLayout)
        self.mirrorLabel = QtGui.QLabel('Mirror :')
        self.mirrorLayout.addWidget(self.mirrorLabel)
        for axe in 'XYZ':
            self.mirrorButton = QtGui.QPushButton(axe)
            self.mirrorButton.setObjectName('mirrorButton{}'.format(axe))
            self.mirrorButton.setFixedSize(20, 20)
            self.mirrorLayout.addWidget(self.mirrorButton)
        self.spaceCheckBox = QtGui.QCheckBox('Object space')
        self.spaceCheckBox.setObjectName('objectSpace')
        self.spaceCheckBox.setChecked(True)
        self.mirrorLayout.addWidget(self.spaceCheckBox)

        # Mirror other side
        self.sideMirror = QtGui.QPushButton('Mirror other side')
        self.mainLayout.addWidget(self.sideMirror)

        # Parent and copy layout
        self.parentCopyLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.parentCopyLayout)
        # Parent shape button
        self.parentButton = QtGui.QPushButton('Parent Shapes')
        self.parentCopyLayout.addWidget(self.parentButton)

        # Copy shape button
        self.copyButton = QtGui.QPushButton('Copy Shapes')
        self.parentCopyLayout.addWidget(self.copyButton)

    def ui_connection(self):
        self.colorButton.clicked.connect(self.get_color)
        self.applyColorButton.clicked.connect(apply_color)

        # Mirror buttons
        self.mirbutt = self.findChild(QtGui.QPushButton, 'mirrorButtonX')
        self.mirbutt.clicked.connect(partial(self.mirror_signal, 'x'))
        self.mirbutt = self.findChild(QtGui.QPushButton, 'mirrorButtonY')
        self.mirbutt.clicked.connect(partial(self.mirror_signal, 'y'))
        self.mirbutt = self.findChild(QtGui.QPushButton, 'mirrorButtonZ')
        self.mirbutt.clicked.connect(partial(self.mirror_signal, 'z'))

        self.sideMirror.clicked.connect(shapeMirror.do_shapeMirror)
        self.parentButton.clicked.connect(parent_shape)
        self.copyButton.clicked.connect(partial(shapeMirror.do_shapeMirror, copy=True))

    def mirror_signal(self, axis):
        space = self.findChild(QtGui.QCheckBox, 'objectSpace')
        ws = not space.isChecked()
        shapeMirror.do_shapeMirror(miraxis=axis, ws=ws, solo=True)

    def get_color(self):
        self.colorItem = QtGui.QColor()
        self.colorItem.setRgb(*self.choosenColor)
        self.colorPicker = QtGui.QColorDialog()
        self.colorItem = self.colorPicker.getColor(self.colorItem)
        if self.colorItem.isValid():
            rlShape_ui.choosenColor = self.colorItem.getRgb()
            self.colorButton.setStyleSheet('background-color: rgb' + str(tuple(self.choosenColor)))


def apply_color():
    def do(shape, color):
        mc.setAttr(shape + '.overrideEnabled', True)
        mc.setAttr(shape + '.overrideRGBColors', True)
        mc.setAttr(shape + '.overrideColorRGB', *color)

    color = rlShape_ui.choosenColor
    crvs = mc.ls(sl=True)
    color = [x/255.0 for x in color]
    for crv in crvs:
        if mc.nodeType(crv) == 'nurbsCurve':
            do(crv, color)
        else:
            shapes = get_shape(crv)
            for shape in shapes:
                if mc.nodeType(shape) == 'nurbsCurve':
                    do(shape, color[:3])


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
todo: quad_round_arrow, cube, sphere, cylinder, locator, half_circle, simple_arrow, octo_arrown, double_arrow,
      quad_bent_arrow, double_bent_arrow, fly, line, pyramide, double_pyramide, half_sphere, wobbly_circle, eye, foot,
      pin_sphere, pin_cube, pin_pyramide, pin_double_pyramide, pin_circle_crossed, star, circle_cross,
      double_pin_circle_crossed, u_turn_arrow, pin_arrow, cross_axis, sparkle
"""
class Shapes():

    shapesList = ['circle', 'square', 'quad_arrow', 'cross', 'shape1', 'shape2', '2', '5', '5sd', '568', '1', '2']

    @staticmethod
    def scaleConfo(p, scale=1):
        scale = float(scale)
        return [(x * scale, y * scale, z * scale) for x, y, z in p]

    def circle(self, scale=1):
        crv = mc.circle(nr=(0, 1, 0), r=scale/2.0, ch=False)
        return crv

    def square(self, scale=1):
        p = [(0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0.5, 0, -0.5)]
        p = self.scaleConfo(p, scale)
        crv = mc.curve(d=1, p=p)
        return crv

    def quad_arrow(self, scale=1):
        p = [(0, 0, -2.5), (1, 0, -1.5), (0.5, 0, -1.5), (0.5, 0, -0.5), (1.5, 0, -0.5), (1.5, 0, -1), (2.5, 0, 0),
             (1.5, 0, 1), (1.5, 0, 0.5), (0.5, 0, 0.5), (0.5, 0, 1.5), (1, 0, 1.5), (0, 0, 2.5), (-1, 0, 1.5),
             (-0.5, 0, 1.5), (-0.5, 0, 0.5), (-1.5, 0, 0.5), (-1.5, 0, 1), (-2.5, 0, 0), (-1.5, 0, -1), (-1.5, 0, -0.5),
             (-0.5, 0, -0.5), (-0.5, 0, -1.5), (-1, 0, -1.5), (0, 0, -2.5)]
        p = self.scaleConfo(p, scale)
        crv = mc.curve(d=1, p=p)
        return crv

    def cross(self, scale=1):
        p = [(0.25, 0, -0.25), (0.5, 0, -0.25), (0.5, 0, 0.25), (0.25, 0, 0.25), (0.25, 0, 0.5), (-0.25, 0, 0.5),
             (-0.25, 0, 0.25), (-0.5, 0, 0.25), (-0.5, 0, -0.25), (-0.25, 0, -0.25), (-0.25, 0, -0.5), (0.25, 0, -0.5),
             (0.25, 0, -0.25)]
        p = self.scaleConfo(p, scale)
        crv = mc.curve(d=1, p=p)
        return crv

def launch_ui():

    if mc.window('rlShapeCreator', exists=True):
        mc.deleteUI('rlShapeCreator')
    ui = rlShape_ui()
    ui.show()
