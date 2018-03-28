import maya.cmds as mc
qtVersion = mc.about(qtVersion=True)  # import pyside, do qt version check for maya 2017 >
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
from functools import partial


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
        self.ui_connection()
            
    def ui_layout(self):
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # Move arrow layout
        self.moveArrow_layout = QVBoxLayout()
        self.moveUp_toolButton = QToolButton()
        self.moveUp_toolButton.setArrowType(Qt.UpArrow)
        self.moveArrow_layout.addWidget(self.moveUp_toolButton)
        self.moveDown_toolButton = QToolButton()
        self.moveDown_toolButton.setArrowType(Qt.DownArrow)
        self.moveArrow_layout.addWidget(self.moveDown_toolButton)
        self.main_layout.addLayout(self.moveArrow_layout)

        # ATTRIBUTES-------------------------------------------
        # Attributes VLayout
        self.attributes_layout = QVBoxLayout()
        self.main_layout.addLayout(self.attributes_layout)

        self.attributeChoice_buttonGrp = QButtonGroup()

        self.obj = self.get_selection()
        self.attributes = self.get_attributes()

        for i, attr in enumerate(self.attributes):
            # Attribute HLayout
            self.attributeAll_layoutH = QHBoxLayout()
            self.attributeAll_layoutH.setObjectName('attributeAll_layoutH')
            self.attributes_layout.addLayout(self.attributeAll_layoutH)

            # Attribute choice radioButton
            self.attributeAll_radioButton = QRadioButton()
            self.main_layout.setObjectName("attributeAll_radioButton")
            self.attributeAll_layoutH.addWidget(self.attributeAll_radioButton)
            self.attributeChoice_buttonGrp.addButton(self.attributeAll_radioButton)

            # Attribute choice separator
            self.attributeAll_line = QFrame()
            self.attributeAll_line.setFrameShape(QFrame.VLine)
            self.attributeAll_line.setFrameShadow(QFrame.Sunken)
            self.attributeAll_layoutH.addWidget(self.attributeAll_line)

            # Attribute VLayout
            self.attributeAll_layoutV = QVBoxLayout()
            self.attributeAll_layoutH.addLayout(self.attributeAll_layoutV)
            self.attribute_layout = QHBoxLayout()
            self.attributeAll_layoutV.addLayout(self.attribute_layout)
            # Attribute hide button
            self.attributeHide_toolButton = QToolButton()
            self.attributeHide_toolButton.setObjectName('attr_{}_hide_toolButton'.format(i))
            self.attributeHide_toolButton.setArrowType(Qt.RightArrow)
            self.attributeHide_toolButton.setFixedSize(20, 20)
            self.attribute_layout.addWidget(self.attributeHide_toolButton)
            # Attribute name lineEdit
            self.attribute_lineEdit = QLineEdit(attr)
            self.attribute_lineEdit.setObjectName('attr_{}_lineEdit'.format(i))
            self.attribute_layout.addWidget(self.attribute_lineEdit)
            # Apply update button
            self.attribute_apply_button = QPushButton('Apply')
            self.attribute_apply_button.setObjectName('attr_{}_apply_button'.format(i))
            self.attribute_apply_button.setFixedWidth(50)
            self.attribute_apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.attributeAll_layoutH.addWidget(self.attribute_apply_button)

            # Attribute EDITS---------------------------
            # Attribute edits Widget
            self.attributeEdits_widget = QWidget()
            self.attributeEdits_widget.setObjectName('attr_{}_edits_widget'.format(i))
            # self.attributeEdits_widget.hide()
            self.attributeAll_layoutV.addWidget(self.attributeEdits_widget)
            # Attribute Edits layout
            self.attributeEdits_layout = QVBoxLayout()
            self.attributeEdits_layout.setObjectName('attr_{}_edits_layout'.format(i))
            self.attributeEdits_widget.setLayout(self.attributeEdits_layout)

            # Attribute nice Name
            self.attributeNiceName_layout = QHBoxLayout()
            self.attributeEdits_layout.addLayout(self.attributeNiceName_layout)
            self.attributeNiceName_checkBox = QCheckBox('Nice Name')
            self.attributeNiceName_checkBox.setObjectName('attr_{}_niceName_checkBox'.format(i))
            niceName_staus = self.get_niceName_info(attr)[0]
            self.attributeNiceName_checkBox.setChecked(niceName_staus)
            self.attributeNiceName_layout.addWidget(self.attributeNiceName_checkBox)
            niceName = self.get_niceName_info(attr)[1]
            self.attributeNiceName_lineEdit = QLineEdit(niceName)
            self.attributeNiceName_lineEdit.setObjectName('attr_{}_niceName_lineEdit'.format(i))
            self.attributeNiceName_layout.addWidget(self.attributeNiceName_lineEdit)

            # Attribute status
            self.attributeStatus_layout = QHBoxLayout()
            self.attributeEdits_layout.addLayout(self.attributeStatus_layout)
            attr_status = self.get_attr_status_radioButton(i)
            self.attributeKeyable_radioButton = QRadioButton('Keyable')
            self.attributeKeyable_radioButton.setObjectName('attr_{}_keyable_radioButton'.format(i))
            if attr_status == 'keyable':
                self.attributeKeyable_radioButton.setChecked(True)
            self.attributeStatus_layout.addWidget(self.attributeKeyable_radioButton)
            self.attributeDisplayable_radioButton = QRadioButton('Displayable')
            self.attributeDisplayable_radioButton.setObjectName('attr_{}_displayable_radioButton'.format(i))
            if attr_status == 'displayable':
                self.attributeDisplayable_radioButton.setChecked(True)
            self.attributeStatus_layout.addWidget(self.attributeDisplayable_radioButton)
            self.attributeHidden_radioButton = QRadioButton('Hidden')
            self.attributeHidden_radioButton.setObjectName('attr_{}_hidden_radioButton'.format(i))
            if attr_status == 'hidden':
                self.attributeHidden_radioButton.setChecked(True)
            self.attributeStatus_layout.addWidget(self.attributeHidden_radioButton)
            self.attributeLocked_checkBox = QCheckBox('Locked')
            self.attributeLocked_checkBox.setObjectName('attr_{}_locked_checkBox'.format(i))
            locked_status = mc.getAttr('{}.{}'.format(self.obj, attr), lock=True)
            self.attributeLocked_checkBox.setChecked(locked_status)
            self.attributeStatus_layout.addWidget(self.attributeLocked_checkBox)

            # self.attributeMinMax_layout = QHBoxLayout()
            # self.attributeMinMax_layout.setObjectName("attributeMinMax_layout")
            # self.attributeMin_checkBox = QCheckBox('Min')
            # self.attributeMin_checkBox.setObjectName("attributeMin_checkBox")
            # self.attributeMinMax_layout.addWidget(self.attributeMin_checkBox)
            # self.attributeMin_lineEdit = QLineEdit()
            # self.attributeMin_lineEdit.setObjectName("attributeMin_lineEdit")
            # self.attributeMinMax_layout.addWidget(self.attributeMin_lineEdit)
            # self.attributeMinMaxSep_line = QFrame()
            # self.attributeMinMaxSep_line.setFrameShape(QFrame.VLine)
            # self.attributeMinMaxSep_line.setFrameShadow(QFrame.Sunken)
            # self.attributeMinMaxSep_line.setObjectName("attributeMinMaxSep_line")
            # self.attributeMinMax_layout.addWidget(self.attributeMinMaxSep_line)
            # self.attributeMax_checkBox = QCheckBox('Max')
            # self.attributeMax_checkBox.setObjectName("attributeMax_checkBox")
            # self.attributeMinMax_layout.addWidget(self.attributeMax_checkBox)
            # self.attributeMax_lineEdit = QLineEdit()
            # self.attributeMax_lineEdit.setObjectName("attributeMax_lineEdit")
            # self.attributeMinMax_layout.addWidget(self.attributeMax_lineEdit)
            # self.attributeEdits_layout.addLayout(self.attributeMinMax_layout)
            # self.attributeDValue_layout = QHBoxLayout()
            # self.attributeDValue_layout.setObjectName("attributeDValue_layout")
            # self.attributeDValue_label = QLabel('Default value')
            # self.attributeDValue_label.setObjectName("attributeDValue_label")
            # self.attributeDValue_layout.addWidget(self.attributeDValue_label)
            # self.attributeDValue_lineEdit = QLineEdit()
            # self.attributeDValue_lineEdit.setObjectName("attributeDValue_lineEdit")
            # self.attributeDValue_layout.addWidget(self.attributeDValue_lineEdit)
            # self.attributeEdits_layout.addLayout(self.attributeDValue_layout)

    def ui_connection(self):
        for i, attr in enumerate(self.attributes):
            # Apply Button
            apply_button = self.findChild(QPushButton, 'attr_{}_apply_button'.format(i))
            apply_button.clicked.connect(partial(self.apply_changes, i))
            # Hide button
            hide_button = self.findChild(QToolButton, 'attr_{}_hide_toolButton'.format(i))
            hide_button.clicked.connect(partial(self.hide_attrEdits, i))

    @staticmethod
    def get_selection():
        sel = mc.ls(sl=True, fl=True)
        if not sel:
            mc.warning('Select an object')
            return None
        return sel[0]

    def get_attributes(self):
        if not self.obj:
            return []
        attrs = mc.listAttr(self.obj, ud=True, visible=True)
        return attrs

    def refresh_sel(self):
        mc.select(clear=True)
        mc.select(self.obj)
        return

    def hide_attrEdits(self, index):
        editsArrow_toolButton_object = self.findChild(QToolButton, 'attr_{}_hide_toolButton'.format(index))
        editsArrow_widget_object = self.findChild(QWidget, 'attr_{}_edits_widget'.format(index))
        apply_button_object = self.findChild(QPushButton, 'attr_{}_apply_button'.format(index))
        if editsArrow_toolButton_object.arrowType() == Qt.DownArrow:
            editsArrow_widget_object.hide()
            editsArrow_toolButton_object.setArrowType(Qt.RightArrow)
            apply_button_object.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.adjustSize()
        else:
            editsArrow_toolButton_object.setArrowType(Qt.DownArrow)
            apply_button_object.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            editsArrow_widget_object.show()

    def apply_changes(self, attrIndex):
        self.attributes = self.get_attributes()
        self.rename_attribute(attrIndex)
        self.edit_niceName(attrIndex)
        self.edit_status(attrIndex)
        self.edit_locked_status(attrIndex)

    def rename_attribute(self, attrIndex):
        attr_lineEdit = self.findChild(QLineEdit, 'attr_{}_lineEdit'.format(attrIndex))
        newName = attr_lineEdit.text()

        if newName == self.attributes[attrIndex]:
            print('Name unchanged')
            return
        try:
            mc.renameAttr(self.obj + '.' + self.attributes[attrIndex], newName)
        except:
            mc.warning('New attribute name invalid or already used')
            attr_lineEdit.setText(self.attributes[attrIndex])
            return
        self.refresh_sel()
        self.attributes = self.get_attributes()

    def get_niceName_info(self, attr):
        if mc.addAttr('{}.{}'.format(self.obj, attr), q=True, niceName=True):
            niceName_status = True
        else:
            niceName_status = False
        niceName = mc.attributeQuery(attr, node=self.obj, niceName=True)
        return niceName_status, niceName

    def edit_niceName(self, attrIndex):
        niceName_checkBox_object = self.findChild(QCheckBox, 'attr_{}_niceName_checkBox'.format(attrIndex))
        niceName_checkBox_status = niceName_checkBox_object.isChecked()
        niceName_lineEdit_object = self.findChild(QLineEdit, 'attr_{}_niceName_lineEdit'.format(attrIndex))
        niceName_lineEdit_text = niceName_lineEdit_object.text()
        if niceName_checkBox_status:
            newNiceName = niceName_lineEdit_text
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, niceName=newNiceName)
        else:
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, niceName='')
            newNiceName = self.get_niceName_info(self.attributes[attrIndex])[1]
            niceName_lineEdit_object.setText(newNiceName)
        self.refresh_sel()
        return

    def get_checked_radioButton(self, attrIndex):
        for i, status in enumerate(('keyable', 'displayable', 'hidden')):
            attr_radioButton_object = self.findChild(QRadioButton, 'attr_{}_{}_radioButton'.format(attrIndex, status))
            attr_radioButton_status = attr_radioButton_object.isChecked()
            if attr_radioButton_status:
                return attr_radioButton_object.text()
        print('No radio Button checked')
        return None

    def get_attr_status_radioButton(self, attrIndex):
        keyable = mc.getAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), keyable=True)
        displayable = mc.getAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), channelBox=True)

        if keyable:
            return 'keyable'
        elif displayable:
            return 'displayable'
        else:
            return 'hidden'

    def edit_status(self, attrIndex):
        attr_radioButton_status = self.get_checked_radioButton(attrIndex)
        print(attr_radioButton_status)
        if attr_radioButton_status == 'Keyable':
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), keyable=True)
        elif attr_radioButton_status == 'Displayable':
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), channelBox=True)
        else:
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), keyable=False)
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), channelBox=False)
        return

    def edit_locked_status(self, attrIndex):
        attr_locked_status = mc.getAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), lock=True)
        attr_locked_checkBox_object = self.findChild(QCheckBox, 'attr_{}_locked_checkBox'.format(attrIndex))
        attr_locked_checkBox_status = attr_locked_checkBox_object.isChecked()

        if attr_locked_checkBox_status != attr_locked_status:
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), lock=attr_locked_checkBox_status)
        else:
            return
        return

    def get_lineEdit_text(self, lineObject_name):
        lineObject = self.findChild(QLineEdit, lineObject_name)
        lineObject_text = lineObject.text()
        return lineObject_text
