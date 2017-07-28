import maya.cmds as mc
from PySide import QtGui
from PySide import QtCore
import maya.OpenMayaUI as mui
import shiboken

from functools import partial
from math import sqrt, ceil
import shapeMirror
from tbx import get_shape


"""
todo: quad_round_arrow, cube, sphere, cylinder, locator, half_circle, simple_arrow, octo_arrown, double_arrow,
      quad_bent_arrow, double_bent_arrow, fly, line, pyramide, double_pyramide, half_sphere, wobbly_circle, eye, foot,
      pin_sphere, pin_cube, pin_pyramide, pin_double_pyramide, pin_circle_crossed, star, circle_cross,
      double_pin_circle_crossed, u_turn_arrow, pin_arrow, cross_axis, sparkle
"""


def launch_ui():

    if mc.window('rlShapeCreator', exists=True):
        mc.deleteUI('rlShapeCreator')
    ui = RlShape_ui()
    ui.show()


def getMayaWin():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(pointer), QtGui.QWidget)


class RlShape_ui(QtGui.QDialog):

    choosenColor = (255, 255, 0)

    shapesList = ['circle', 'square', 'cube', 'sphere', 'quad_arrow', 'cross', 'arrow_head']
    shapesDict = {'square': [(0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5)],
                  'quad_arrow': [(0, 0, -0.5), (0.2, 0, -0.3), (0.1, 0, -0.3), (0.1, 0, -0.1), (0.3, 0, -0.1), (0.3, 0, -0.2), (0.5, 0, 0), (0.3, 0, 0.2), (0.3, 0, 0.1), (0.1, 0, 0.1), (0.1, 0, 0.3), (0.2, 0, 0.3), (0, 0, 0.5), (-0.2, 0, 0.3), (-0.1, 0, 0.3), (-0.1, 0, 0.1), (-0.3, 0, 0.1), (-0.3, 0, 0.2), (-0.5, 0, 0), (-0.3, 0, -0.2), (-0.3, 0, -0.1), (-0.1, 0, -0.1), (-0.1, 0, -0.3), (-0.2, 0, -0.3), (0, 0, -0.5)],
                  'cross': [(0.25, 0, -0.25), (0.5, 0, -0.25), (0.5, 0, 0.25), (0.25, 0, 0.25), (0.25, 0, 0.5), (-0.25, 0, 0.5), (-0.25, 0, 0.25), (-0.5, 0, 0.25), (-0.5, 0, -0.25), (-0.25, 0, -0.25), (-0.25, 0, -0.5), (0.25, 0, -0.5), (0.25, 0, -0.25)],
                  'arrow_head': [(0, 0, 0), (0, 1.5, 0.5), (0, 1.5, -0.5), (0, 0, 0), (-0.5, 1.5, 0), (0, 1.5, 0), (0.5, 1.5, 0), (0, 0, 0)],
                  'cube': [(-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5)],
                  'sphere': [(0, 0.5, 0), (0, 0.46194, 0.1913415), (0, (sqrt(2)/2)/2, (sqrt(2)/2)/2), (0, 0.1913415, 0.46194), (0, 0, 0.5), (0, -0.1913415, 0.46194), (0, -((sqrt(2)/2)/2), (sqrt(2)/2)/2), (0, -0.46194, 0.1913415), (0, -0.5, 0), (0, -0.46194, -0.1913415), (0, -((sqrt(2)/2)/2), -((sqrt(2)/2)/2)), (0, -0.1913415, -0.46194), (0, 0, -0.5), (0, 0.1913415, -0.46194), (0, (sqrt(2)/2)/2, -((sqrt(2)/2)/2)), (0, 0.46194, -0.1913415), (0, 0.5, 0), (0.1913415, 0.46194, 0), ((sqrt(2)/2)/2, (sqrt(2)/2)/2, 0), (0.46194, 0.1913415, 0), (0.5, 0, 0), (0.46194, -0.1913415, 0), ((sqrt(2)/2)/2, -((sqrt(2)/2)/2), 0), (0.1913415, -0.46194, 0), (0, -0.5, 0), (-0.1913415, -0.46194, 0), (-((sqrt(2)/2)/2), -((sqrt(2)/2)/2), 0), (-0.46194, -0.1913415, 0), (-0.5, 0, 0), (-0.46194, 0.1913415, 0), (-((sqrt(2)/2)/2), (sqrt(2)/2)/2, 0), (-0.1913415, 0.46194, 0), (0, 0.5, 0), (0, 0.46194, -0.1913415), (0, (sqrt(2)/2)/2, -((sqrt(2)/2)/2)), (0, 0.1913415, -0.46194), (0, 0, -0.5), (-0.1913415, 0, -0.46194), (-((sqrt(2)/2)/2), 0, -((sqrt(2)/2)/2)), (-0.46194, 0, -0.1913415), (-0.5, 0, 0), (-0.46194, 0, 0.1913415), (-((sqrt(2)/2)/2), 0, (sqrt(2)/2)/2), (-0.1913415, 0, 0.46194), (0, 0, 0.5), (0.1913415, 0, 0.46194), ((sqrt(2)/2)/2, 0, (sqrt(2)/2)/2), (0.46194, 0, 0.1913415), (0.5, 0, 0), (0.46194, 0, -0.1913415), ((sqrt(2)/2)/2, 0, -((sqrt(2)/2)/2)), (0.1913415, 0, -0.46194), (0, 0, -0.5)]}

    def __init__(self, parent=getMayaWin()):
        super(RlShape_ui, self).__init__(parent)

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
        self.shapeGroupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addWidget(self.shapeGroupBox)

        # Shapes buttons Layout
        shapeLayout = QtGui.QGridLayout()
        self.shapeGroupBox.setLayout(shapeLayout)
        row = 0
        column = 0
        shapeDone = 0
        while shapeDone < len(self.shapesList):
            if column < ceil(sqrt(len(self.shapesList))):
                self.shapeButton = QtGui.QPushButton(self.shapesList[shapeDone])
                self.shapeButton.setObjectName('btn_'+self.shapesList[shapeDone])
                self.shapeButton.setFixedSize(55, 55)
                shapeLayout.addWidget(self.shapeButton, row, column)
                column += 1
                shapeDone += 1
            else:
                column = 0
                row += 1

        # Size Layout
        self.sizeLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.sizeLayout)
        # Size Label
        self.sizeLabel = QtGui.QLabel(' Size :')
        self.sizeLayout.addWidget(self.sizeLabel)
        # Size Value
        self.sizeLineEdit = QtGui.QLineEdit('2')
        self.sizeLineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
        self.sizeLineEdit.setMaximumWidth(40)
        self.sizeLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.sizeLayout.addWidget(self.sizeLineEdit)
        # Size Slider
        self.sizeSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sizeSlider.setValue(2)
        self.sizeSlider.setMaximum(10)
        self.sizeSlider.setMinimum(1)
        self.sizeLayout.addWidget(self.sizeSlider)
        # Shape Options
        self.shapeOptionLayout = QtGui.QHBoxLayout()
        self.shapeOptionLayout.setAlignment(QtCore.Qt.AlignCenter)
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
        self.mirrorLayout.setAlignment(QtCore.Qt.AlignCenter)
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
        # Shapes
        for buttonIndex in range(len(self.shapesList)):
            shape = self.shapesList[buttonIndex]
            self.shapeButton = self.findChild(QtGui.QPushButton, 'btn_'+shape)
            self.shapeButton.clicked.connect(partial(self.do_shape, shape))

        # Scale Slider
        self.sizeSlider.valueChanged.connect(self.sizeSlider_update)
        # Scale LineEdit
        self.sizeLineEdit.textEdited.connect(self.sizeLineEdit_update)
        # Shape option
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
            RlShape_ui.choosenColor = self.colorItem.getRgb()
            self.colorButton.setStyleSheet('background-color: rgb' + str(tuple(self.choosenColor)))

    def sizeSlider_update(self):
        value = self.sizeSlider.value()
        self.sizeLineEdit.setText(str(value))

    def sizeLineEdit_update(self):
        value = self.sizeLineEdit.text()
        if float(value) > 10:
            if float(value) < 500:
                self.sizeSlider.setMaximum(float(value)*2)
            else:
                self.sizeSlider.setMaximum(1000)
        else:
            self.sizeSlider.setMaximum(10)
        self.sizeSlider.setValue(float(value))

    def do_shape(self, shape):
        size = float(self.sizeLineEdit.text())
        if shape == 'circle':
            crv = mc.circle(nr=(0, 1, 0), r=size/2.0, ch=False)
            apply_color([crv])
            return crv
        p = self.shapesDict[shape]
        p = [(x * size, y * size, z * size) for x, y, z in p]
        crv = mc.curve(d=1, p=p)
        apply_color([crv])
        return crv


def apply_color(crvs=None):
    def do(shape, color):
        mc.setAttr(shape + '.overrideEnabled', True)
        mc.setAttr(shape + '.overrideRGBColors', True)
        mc.setAttr(shape + '.overrideColorRGB', *color)

    if not crvs:
        crvs = mc.ls(sl=True)
    color = RlShape_ui.choosenColor
    color = [x/255.0 for x in color]
    for crv in crvs:
        if mc.nodeType(crv) == 'nurbsCurve':
            do(crv, color)
        else:
            shapes = get_shape(crv)
            for shape in shapes:
                if mc.nodeType(shape) == 'nurbsCurve':
                    do(shape, color[:3])


def parent_shape(parent=None, childs=None, freeze=False):

    sel = mc.ls(sl=True)
    if not parent or not childs:
        if len(sel) < 2:
            mc.warning('Select a shape and a parent transform')
            return
        childs = sel[:-1]
        parent = sel[-1]
    for child in childs:
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
