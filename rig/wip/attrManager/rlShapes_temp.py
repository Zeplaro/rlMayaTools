import maya.cmds as mc
# import pyside, do qt version check for maya 2017 >
qtVersion = mc.about(qtVersion=True)
if qtVersion.startswith("4"):
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken
import maya.OpenMayaUI as mui


def launch_ui():

    if mc.window('attrManager', exists=True):
        mc.deleteUI('attrManager')
    ui = attrManager_ui()
    ui.show()


def getMayaWin():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(pointer), QWidget)


class attrManager_ui(QDialog):

    def __init__(self, parent=getMayaWin()):
        super(attrManager_ui, self).__init__(parent)

        self.setWindowTitle('Attribute Manager')
        self.setObjectName('attrManager')
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.ui_layout()

    def ui_layout(self):
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        # Shapes Menu Tool Button
        self.shapesCollapseLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.shapesCollapseLayout)
        self.shapesCollapse = QToolButton()
        self.shapesCollapse.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.shapesCollapse.setArrowType(Qt.DownArrow)
        self.shapesCollapse.setText('Shapes')
        self.shapesCollapse.setMinimumWidth(300)
        self.shapesButtonFont = QFont()
        self.shapesButtonFont.setBold(True)
        self.shapesButtonFont.setPointSize(8)
        self.shapesCollapse.setFont(self.shapesButtonFont)
        self.shapesCollapseLayout.addWidget(self.shapesCollapse)
    #
    #     # Shapes buttons Layout Widget
    #     self.shapesLayoutWidget = QWidget()
    #     self.mainLayout.addWidget(self.shapesLayoutWidget)
    #
    #     # Shape Options
    #     self.replaceColorLayout = QHBoxLayout()
    #     self.replaceColorLayout.setAlignment(Qt.AlignCenter)
    #     self.mainLayout.addLayout(self.replaceColorLayout)
    #     # Replace checkbox
    #     self.replaceCheckBox = QCheckBox('Replace')
    #     self.replaceCheckBox.setChecked(True)
    #     self.replaceColorLayout.addWidget(self.replaceCheckBox)
    #     # Separator
    #     self.vSeparator = QLabel()
    #     self.vSeparator.setFrameStyle(QFrame.VLine)
    #     self.replaceColorLayout.addWidget(self.vSeparator)
    #     # Color Picker
    #     self.colorLabel = QLabel(' Color  :')
    #     self.replaceColorLayout.addWidget(self.colorLabel)
    #     self.colorButton = QPushButton()
    #     self.colorButton.setStyleSheet('background-color: rgb(255, 255, 0)')
    #     self.colorButton.setFixedSize(50, 20)
    #     self.replaceColorLayout.addWidget(self.colorButton)
    #     # Apply Color button
    #     self.applyColorButton = QPushButton('Apply Color')
    #     self.replaceColorLayout.addWidget(self.applyColorButton)
    #     # Get color button
    #     self.getColorButton = QPushButton('Get')
    #     self.getColorButton.setFixedWidth(30)
    #     self.getColorButton.setToolTip('Get the color of the selected curve')
    #     self.replaceColorLayout.addWidget(self.getColorButton)
    #
    #     # Size Layout
    #     self.sizeLayout = QHBoxLayout()
    #     self.mainLayout.addLayout(self.sizeLayout)
    #     # Size Label
    #     self.sizeLabel = QLabel(' Size :  ')
    #     self.sizeLayout.addWidget(self.sizeLabel)
    #     # Size Value
    #     self.sizeLineEdit = QLineEdit('2')
    #     self.sizeLineEdit.setValidator(QRegExpValidator(QRegExp('[\d]{1,3}[.][\d]{0,3}')))
    #     self.sizeLineEdit.setMaximumWidth(40)
    #     self.sizeLineEdit.setAlignment(Qt.AlignCenter)
    #     self.sizeLayout.addWidget(self.sizeLineEdit)
    #     # Size Slider
    #     self.sizeSlider = QSlider(Qt.Horizontal)
    #     self.sizeSlider.setValue(2)
    #     self.sizeSlider.setMaximum(10)
    #     self.sizeSlider.setMinimum(1)
    #     self.sizeLayout.addWidget(self.sizeSlider)
    #
    #     # Axis Twist layout
    #     self.axisTwistLayout = QHBoxLayout()
    #     self.axisTwistLayout.setAlignment(Qt.AlignCenter)
    #     self.mainLayout.addLayout(self.axisTwistLayout)
    #     # Axis Label
    #     self.axisLabel = QLabel('Axis :')
    #     self.axisLabel.setFixedWidth(35)
    #     self.axisTwistLayout.addWidget(self.axisLabel)
    #     # radio Buttons
    #     self.axisButtonGroup = QButtonGroup()
    #     for axis in 'xyz':
    #         self.radioButton = QRadioButton(axis)
    #         self.radioButton.setFixedWidth(35)
    #         if axis == 'y':
    #             self.radioButton.setChecked(True)
    #         self.axisTwistLayout.addWidget(self.radioButton)
    #         self.axisButtonGroup.addButton(self.radioButton)
    #     # reverse checkbox
    #     self.reverseCheckBox = QCheckBox('Reverse')
    #     self.reverseCheckBox.setFixedWidth(65)
    #     self.axisTwistLayout.addWidget(self.reverseCheckBox)
    #     # Separator
    #     self.vSeparator = QFrame()
    #     self.vSeparator.setFrameStyle(QFrame.VLine)
    #     self.vSeparator.setFixedWidth(10)
    #     self.axisTwistLayout.addWidget(self.vSeparator)
    #     # TwistLabel
    #     self.twistLabel = QLabel('Twist ')
    #     self.twistLabel.setFixedWidth(30)
    #     self.axisTwistLayout.addWidget(self.twistLabel)
    #     # Twist Value
    #     self.twistLineEdit = QLineEdit('0')
    #     self.twistLineEdit.setValidator(QRegExpValidator(QRegExp('[\d]{1,3}[.][\d]{0,3}')))
    #     self.twistLineEdit.setMaximumWidth(40)
    #     self.twistLineEdit.setAlignment(Qt.AlignCenter)
    #     self.axisTwistLayout.addWidget(self.twistLineEdit)
    #
    #     # Separator line
    #     self.hSeparator = QFrame()
    #     self.hSeparator.setFrameStyle(QFrame.HLine)
    #     self.mainLayout.addWidget(self.hSeparator)
    #
    #     # Main Mirror Layout
    #     self.mainMirrorLayout = QHBoxLayout()
    #     self.mainMirrorLayout.setAlignment(Qt.AlignCenter)
    #     self.mainLayout.addLayout(self.mainMirrorLayout)
    #     # Mirror buttons layout
    #     self.mirrorButtonsLayout = QVBoxLayout()
    #     self.mirrorButtonsLayout.setAlignment(Qt.AlignCenter)
    #     self.mainMirrorLayout.addLayout(self.mirrorButtonsLayout)
    #     # Mirror solo button Layout
    #     self.mirrorSoloLayout = QHBoxLayout()
    #     self.mirrorSoloLayout.setAlignment(Qt.AlignCenter)
    #     self.mirrorButtonsLayout.addLayout(self.mirrorSoloLayout)
    #     # Mirror Label
    #     self.mirrorLabel = QLabel('Mirror :')
    #     self.mirrorSoloLayout.addWidget(self.mirrorLabel)
    #     # Mirror button
    #     for axe in 'XYZ':
    #         self.mirrorButton = QPushButton(axe)
    #         self.mirrorButton.setObjectName('mirrorButton{}'.format(axe))
    #         self.mirrorButton.setFixedSize(25, 20)
    #         self.mirrorSoloLayout.addWidget(self.mirrorButton)
    #     # Mirror other side
    #     self.sideMirror = QPushButton('Mirror other side')
    #     self.sideMirror.setFixedWidth(145)
    #     self.mirrorButtonsLayout.addWidget(self.sideMirror)
    #     # Copy shape button
    #     self.copyButton = QPushButton('Copy Shapes')
    #     self.copyButton.setFixedWidth(145)
    #     self.mirrorButtonsLayout.addWidget(self.copyButton)
    #     # Separator Layout
    #     self.separatorLayout = QVBoxLayout()
    #     self.mainMirrorLayout.addLayout(self.separatorLayout)
    #     # Separator line
    #     for sep in range(6):
    #         self.hSeparator = QFrame()
    #         self.hSeparator.setFrameStyle(QFrame.VLine)
    #         self.separatorLayout.addWidget(self.hSeparator)
    #     # Mirror Space
    #     self.spaceCheckBox = QCheckBox('Object space')
    #     self.spaceCheckBox.setObjectName('objectSpace')
    #     self.spaceCheckBox.setChecked(True)
    #     self.spaceCheckBox.setFixedWidth(100)
    #     self.mainMirrorLayout.addWidget(self.spaceCheckBox)
    #
    #     # Separator line
    #     self.hSeparator = QFrame()
    #     self.hSeparator.setFrameStyle(QFrame.HLine)
    #     self.mainLayout.addWidget(self.hSeparator)
    #
    #     # Parent shape button
    #     self.parentButton = QPushButton('Parent Shapes')
    #     self.mainLayout.addWidget(self.parentButton)
    #
    # def shapes_hide(self):
    #     if self.shapesCollapse.arrowType() == Qt.DownArrow:
    #         self.shapesLayoutWidget.hide()
    #         self.shapesCollapse.setArrowType(Qt.RightArrow)
    #         self.adjustSize()
    #     else:
    #         self.shapesCollapse.setArrowType(Qt.DownArrow)
    #         self.shapesLayoutWidget.show()
    #
    # def sizeSlider_update(self):
    #     value = self.sizeSlider.value()
    #     self.sizeLineEdit.setText(str(value))
    #
    # def sizeLineEdit_update(self):
    #     value = self.sizeLineEdit.text()
    #     if float(value) > 10:
    #         if float(value) < 500:
    #             self.sizeSlider.setMaximum(float(value)*2)
    #         else:
    #             self.sizeSlider.setMaximum(1000)
    #     else:
    #         self.sizeSlider.setMaximum(10)
    #     self.sizeSlider.setValue(float(value))
    #
    # def widthSlider_update(self):
    #     value = self.widthSlider.value()
    #     self.widthLineEdit.setText(str(value))
    #
    # def widthLineEdit_update(self):
    #     value = self.widthLineEdit.text()
    #     if float(value) > 10:
    #         if float(value) < 500:
    #             self.widthSlider.setMaximum(float(value)*2)
    #         else:
    #             self.widthSlider.setMaximum(1000)
    #     else:
    #         self.widthSlider.setMaximum(10)
    #     self.widthSlider.setValue(float(value))