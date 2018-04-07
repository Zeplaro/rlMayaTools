import maya.cmds as mc
import maya.OpenMayaUI as mui
from functools import partial
import maya.mel as mel
qtVersion = mc.about(qtVersion=True)  # import pyside, do qt version check for maya 2017 >
if qtVersion.startswith('4'):
    from PySide.QtGui import *
    from PySide.QtCore import *
    import shiboken
else:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    import shiboken2 as shiboken


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
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.obj = self.get_selection()
        self.attributes = self.get_attributes()
        if not self.attributes:
            self.attributes = []

        self.reloadSel_button = QPushButton('Reload selected')
        self.main_layout.addWidget(self.reloadSel_button)
        self.reloadSel_button.clicked.connect(self.reload_ui)

        if not self.obj:
            mc.warning('Nothing selected')
        if self.obj:
            if not self.attributes:
                mc.warning('No attributes in selection')

            # Main separator
            self.main_frame = QFrame()
            self.main_frame.setFrameShape(QFrame.HLine)
            self.main_layout.addWidget(self.main_frame)

            self.attrs_all_layout = QHBoxLayout()
            self.main_layout.addLayout(self.attrs_all_layout)

        if self.attributes:
            # Move arrow layout
            self.moveArrow_layout = QVBoxLayout()
            self.moveUp_toolButton = QToolButton()
            self.moveUp_toolButton.setArrowType(Qt.UpArrow)
            self.moveArrow_layout.addWidget(self.moveUp_toolButton)
            self.moveDown_toolButton = QToolButton()
            self.moveDown_toolButton.setArrowType(Qt.DownArrow)
            self.moveArrow_layout.addWidget(self.moveDown_toolButton)
            self.attrs_all_layout.addLayout(self.moveArrow_layout)

            # ATTRIBUTES-------------------------------------------
            # Attributes VLayout
            self.attrs_layout = QVBoxLayout()
            self.attrs_all_layout.addLayout(self.attrs_layout)

            self.attr_move_buttonGrp = QButtonGroup()

        for i, attr in enumerate(self.attributes):

            attr_infos = self.get_attr_infos(attr)
            print(attr_infos)

            # Attribute HLayout
            self.attr_all_layoutH = QHBoxLayout()
            self.attr_all_layoutH.setObjectName('attr_all_layoutH')
            self.attrs_layout.addLayout(self.attr_all_layoutH)

            # Attribute choice radioButton
            self.attr_move_radioButton = QRadioButton()
            self.attr_move_radioButton.setObjectName('attr_{}_move_radioButton'.format(i))
            # if i == self.choice:
            #     self.attr_move_radioButton.setChecked(True)
            self.attr_move_buttonGrp.addButton(self.attr_move_radioButton)
            self.attr_all_layoutH.addWidget(self.attr_move_radioButton)
            # Attribute choice separator
            self.attr_all_frame = QFrame()
            self.attr_all_frame.setFrameShape(QFrame.VLine)
            self.attr_all_layoutH.addWidget(self.attr_all_frame)

            # Frame border line
            self.attr_all_border_frame = QFrame()
            self.attr_all_border_frame.setObjectName('attr_all_border_frame')
            self.attr_all_border_frame.setStyleSheet('QFrame#attr_all_border_frame { background-color : #4b4b4b }')
            self.attr_all_layoutH.addWidget(self.attr_all_border_frame)
            # Attribute VLayout
            self.attr_all_layoutV = QVBoxLayout()
            self.attr_all_border_frame.setLayout(self.attr_all_layoutV)
            self.attr_layout = QHBoxLayout()
            self.attr_all_layoutV.addLayout(self.attr_layout)
            # Attribute hide button
            self.attr_hide_toolButton = QToolButton()
            self.attr_hide_toolButton.setObjectName('attr_{}_hide_toolButton'.format(i))
            self.attr_hide_toolButton.setArrowType(Qt.RightArrow)
            self.attr_hide_toolButton.setFixedSize(20, 20)
            self.attr_layout.addWidget(self.attr_hide_toolButton)
            # Attribute name lineEdit
            self.attr_lineEdit = QLineEdit(attr)
            self.attr_lineEdit.setObjectName('attr_{}_lineEdit'.format(i))
            self.attr_layout.addWidget(self.attr_lineEdit)

            # Apply update button
            self.attr_apply_button = QPushButton('Apply')
            self.attr_apply_button.setObjectName('attr_{}_apply_button'.format(i))
            self.attr_apply_button.setFixedWidth(50)
            self.attr_apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.attr_all_layoutH.addWidget(self.attr_apply_button)

            # Attribute EDITS------------
            # Attribute edits Widget
            self.attr_edits_widget = QWidget()
            self.attr_edits_widget.setObjectName('attr_{}_edits_widget'.format(i))
            # self.attr_edits_widget.hide()
            self.attr_all_layoutV.addWidget(self.attr_edits_widget)
            # Attribute Edits layout
            self.attr_edits_layout = QVBoxLayout()
            self.attr_edits_layout.setObjectName('attr_{}_edits_layout'.format(i))
            self.attr_edits_widget.setLayout(self.attr_edits_layout)

            # Attribute nice Name
            self.attr_niceName_layout = QHBoxLayout()
            self.attr_edits_layout.addLayout(self.attr_niceName_layout)
            self.attr_niceName_checkBox = QCheckBox('Nice Name')
            self.attr_niceName_checkBox.setObjectName('attr_{}_niceName_checkBox'.format(i))
            self.attr_niceName_checkBox.setChecked(attr_infos['niceNameStatus'])
            self.attr_niceName_layout.addWidget(self.attr_niceName_checkBox)
            self.attr_niceName_lineEdit = QLineEdit(attr_infos['niceName'])
            self.attr_niceName_lineEdit.setObjectName('attr_{}_niceName_lineEdit'.format(i))
            self.attr_niceName_layout.addWidget(self.attr_niceName_lineEdit)

            # Attribute status
            self.attr_status_buttonGrp = QButtonGroup()
            self.attr_status_buttonGrp.setObjectName('{}_status_buttonGrp'.format(self.attributes[i]))
            self.attr_status_layout = QHBoxLayout()
            self.attr_edits_layout.addLayout(self.attr_status_layout)
            self.attr_keyable_radioButton = QRadioButton('Keyable')
            self.attr_keyable_radioButton.setObjectName('attr_{}_keyable_radioButton'.format(i))
            self.attr_status_buttonGrp.addButton(self.attr_keyable_radioButton)
            if attr_infos['status'] == 'keyable':
                self.attr_keyable_radioButton.setChecked(True)
            self.attr_status_layout.addWidget(self.attr_keyable_radioButton)
            self.attr_displayable_radioButton = QRadioButton('Displayable')
            self.attr_displayable_radioButton.setObjectName('attr_{}_displayable_radioButton'.format(i))
            self.attr_status_buttonGrp.addButton(self.attr_displayable_radioButton)
            if attr_infos['status'] == 'displayable':
                self.attr_displayable_radioButton.setChecked(True)
            self.attr_status_layout.addWidget(self.attr_displayable_radioButton)
            self.attr_hidden_radioButton = QRadioButton('Hidden')
            self.attr_hidden_radioButton.setObjectName('attr_{}_hidden_radioButton'.format(i))
            self.attr_status_buttonGrp.addButton(self.attr_hidden_radioButton)
            if attr_infos['status'] == 'hidden':
                self.attr_hidden_radioButton.setChecked(True)
            self.attr_status_layout.addWidget(self.attr_hidden_radioButton)
            self.attr_locked_checkBox = QCheckBox('Locked')
            self.attr_locked_checkBox.setObjectName('attr_{}_locked_checkBox'.format(i))
            self.attr_locked_checkBox.setChecked(attr_infos['locked'])
            self.attr_status_layout.addWidget(self.attr_locked_checkBox)

            # INT / FLOAT-----------------------------------------------------------------------------------------------
            print('attr is {}'.format(attr_infos['type']))
            if (attr_infos['type'] == 'long') or (attr_infos['type'] == 'double'):
                # Attribute min max
                # Min
                self.attr_minMax_layout = QHBoxLayout()
                self.attr_edits_layout.addLayout(self.attr_minMax_layout)
                self.attr_min_checkBox = QCheckBox('Min')
                self.attr_min_checkBox.setObjectName('attr_{}_min_checkBox'.format(i))
                self.attr_min_checkBox.setChecked(attr_infos['minStatus'])
                self.attr_minMax_layout.addWidget(self.attr_min_checkBox)
                self.attr_min_lineEdit = QLineEdit()
                self.attr_min_lineEdit.setObjectName('attr_{}_min_lineEdit'.format(i))
                self.attr_min_lineEdit.setText(str(attr_infos['minValue']))
                self.attr_min_lineEdit.setValidator(QRegExpValidator(QRegExp('[\d]{1,9}[.][\d]{0,3}')))
                self.attr_minMax_layout.addWidget(self.attr_min_lineEdit)
                # Separator
                self.attr_minMaxSep_frame = QFrame()
                self.attr_minMaxSep_frame.setFrameShape(QFrame.VLine)
                self.attr_minMaxSep_frame.setFrameShadow(QFrame.Sunken)
                self.attr_minMax_layout.addWidget(self.attr_minMaxSep_frame)
                # Max
                self.attr_max_checkBox = QCheckBox('Max')
                self.attr_max_checkBox.setObjectName('attr_{}_max_checkBox'.format(i))
                self.attr_max_checkBox.setChecked(attr_infos['maxStatus'])
                self.attr_minMax_layout.addWidget(self.attr_max_checkBox)
                self.attr_max_lineEdit = QLineEdit()
                self.attr_max_lineEdit.setObjectName('attr_{}_max_lineEdit'.format(i))
                self.attr_max_lineEdit.setText(str(attr_infos['maxValue']))
                self.attr_max_lineEdit.setValidator(QRegExpValidator(QRegExp('[\d]{1,9}[.][\d]{0,3}')))
                self.attr_minMax_layout.addWidget(self.attr_max_lineEdit)

                # Default Value
                self.attr_dValue_layout = QHBoxLayout()
                self.attr_edits_layout.addLayout(self.attr_dValue_layout)
                self.attr_dValue_label = QLabel('Default value')
                self.attr_dValue_layout.addWidget(self.attr_dValue_label)
                self.attr_dValue_lineEdit = QLineEdit()
                self.attr_dValue_lineEdit.setObjectName('attr_{}_dValue_lineEdit'.format(i))
                self.attr_dValue_lineEdit.setText(str(attr_infos['dValue']))
                self.attr_dValue_lineEdit.setValidator(QRegExpValidator(QRegExp('[\d]{1,9}[.][\d]{0,3}')))
                self.attr_dValue_layout.addWidget(self.attr_dValue_lineEdit)

            # BOOL------------------------------------------------------------------------------------------------------
            if attr_infos['type'] == 'bool':
                # Default Value
                self.attr_dValue_layout = QHBoxLayout()
                self.attr_edits_layout.addLayout(self.attr_dValue_layout)
                self.attr_dValue_label = QLabel('Default value')
                self.attr_dValue_layout.addWidget(self.attr_dValue_label)

                self.attr_dValue_buttonGrp = QButtonGroup()
                self.attr_dValue_buttonGrp.setObjectName('{}_dValue_buttonGrp'.format(self.attributes[i]))

                self.attr_dValue_true_radioButton = QRadioButton('True')
                self.attr_dValue_buttonGrp.addButton(self.attr_dValue_true_radioButton)
                self.attr_dValue_layout.addWidget(self.attr_dValue_true_radioButton)
                self.attr_dValue_false_radioButton = QRadioButton('False')
                self.attr_dValue_buttonGrp.addButton(self.attr_dValue_false_radioButton)
                self.attr_dValue_layout.addWidget(self.attr_dValue_false_radioButton)

        if self.obj:
            # Add attribute------------------------------
            self.add_attr_button = QPushButton('Add Attribute')
            self.main_layout.addWidget(self.add_attr_button)

        # --------------Launch UI connections-------------
        self.ui_connection()

    def ui_connection(self):
        # Move button
        if self.attributes:
            self.moveUp_toolButton.clicked.connect(partial(self.move_attr, 'up'))
            self.moveDown_toolButton.clicked.connect(partial(self.move_attr, 'down'))
        for i, attr in enumerate(self.attributes):
            # Apply Button
            apply_button = self.findChild(QPushButton, 'attr_{}_apply_button'.format(i))
            apply_button.clicked.connect(partial(self.apply_changes, i))
            # Hide button
            hide_button = self.findChild(QToolButton, 'attr_{}_hide_toolButton'.format(i))
            hide_button.clicked.connect(partial(self.hide_attrEdits, i))
        # Add attribute button
        self.add_attr_button.clicked.connect(self.add_attr)

    def reload_ui(self):
        launch_ui()
        return

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

    def get_move_radioButton(self):
        for i, attr in enumerate(self.attributes):
            attr_radioButton = self.findChild(QRadioButton, 'attr_{}_move_radioButton'.format(i))
            if attr_radioButton.isChecked():
                return i
        print('No radio Button checked')
        return None

    def move_attr(self, way):
        attrIndex = self.get_move_radioButton()
        if way == 'up':
            if attrIndex > 0:
                newIndex = attrIndex-1
            else:
                return
        else:
            newIndex = attrIndex+1

        new_attributes = list(self.attributes)
        new_attributes.pop(attrIndex)
        new_attributes.insert(newIndex, self.attributes[attrIndex])
        print(new_attributes)

        for attribute in new_attributes:
            if mc.getAttr('{}.{}'.format(self.obj, attribute), lock=True):
                lock = True
                mc.setAttr('{}.{}'.format(self.obj, attribute), lock=False)
            else:
                lock = False
            mc.deleteAttr('{}.{}'.format(self.obj, attribute))
            mc.undo()
            if lock:
                mc.setAttr('{}.{}'.format(self.obj, attribute), lock=True)

        self.reload_ui()
        return

    def hide_attrEdits(self, index):
        hide_toolButton = self.findChild(QToolButton, 'attr_{}_hide_toolButton'.format(index))
        hide_widget = self.findChild(QWidget, 'attr_{}_edits_widget'.format(index))
        apply_button = self.findChild(QPushButton, 'attr_{}_apply_button'.format(index))

        if hide_toolButton.arrowType() == Qt.DownArrow:
            hide_widget.hide()
            hide_toolButton.setArrowType(Qt.RightArrow)
            apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            hide_toolButton.setArrowType(Qt.DownArrow)
            apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            hide_widget.show()

        self.adjustSize()

    def apply_changes(self, attrIndex):
        self.attributes = self.get_attributes()
        self.rename_attribute(attrIndex)
        self.set_niceName(attrIndex)
        self.set_status(attrIndex)
        self.set_locked(attrIndex)
        self.set_min(attrIndex)
        self.set_max(attrIndex)
        self.set_dValue(attrIndex)

    def rename_attribute(self, attrIndex):
        attr_lineEdit = self.findChild(QLineEdit, 'attr_{}_lineEdit'.format(attrIndex))
        newName = attr_lineEdit.text()

        if newName == self.attributes[attrIndex]:
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

    def set_niceName(self, attrIndex):
        niceName_checkBox = self.findChild(QCheckBox, 'attr_{}_niceName_checkBox'.format(attrIndex))
        niceName_checkBox_status = niceName_checkBox.isChecked()
        niceName_lineEdit = self.findChild(QLineEdit, 'attr_{}_niceName_lineEdit'.format(attrIndex))
        niceName_lineEdit_text = niceName_lineEdit.text()
        if niceName_checkBox_status:
            newNiceName = niceName_lineEdit_text
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, niceName=newNiceName)
        else:
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, niceName='')
            newNiceName = self.get_niceName_info(self.attributes[attrIndex])[1]
            niceName_lineEdit.setText(newNiceName)
        self.refresh_sel()
        return

    def get_status(self, attr):
        keyable = mc.getAttr('{}.{}'.format(self.obj, attr), keyable=True)
        displayable = mc.getAttr('{}.{}'.format(self.obj, attr), channelBox=True)

        if keyable:
            return 'keyable'
        elif displayable:
            return 'displayable'
        else:
            return 'hidden'

    def get_checked_status_radioButton(self, attrIndex):
        for i, status in enumerate(('keyable', 'displayable', 'hidden')):
            attr_radioButton = self.findChild(QRadioButton, 'attr_{}_{}_radioButton'.format(attrIndex, status))
            attr_radioButton_status = attr_radioButton.isChecked()
            if attr_radioButton_status:
                return attr_radioButton.text()
        print('No radio Button checked')
        return None

    def set_status(self, attrIndex):
        attr_radioButton_status = self.get_checked_status_radioButton(attrIndex)
        if attr_radioButton_status == 'Keyable':
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), keyable=True)
        elif attr_radioButton_status == 'Displayable':
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), channelBox=True)
        else:
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), keyable=False)
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), channelBox=False)
        return

    def get_locked(self, attr):
        locked = mc.getAttr('{}.{}'.format(self.obj, attr), lock=True)
        return locked

    def set_locked(self, attrIndex):
        attr_locked_status = mc.getAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), lock=True)
        attr_locked_checkBox = self.findChild(QCheckBox, 'attr_{}_locked_checkBox'.format(attrIndex))
        attr_locked_checkBox_status = attr_locked_checkBox.isChecked()

        if attr_locked_checkBox_status != attr_locked_status:
            mc.setAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), lock=attr_locked_checkBox_status)
        else:
            return
        return

    def get_min_info(self, attr):
        min_status = mc.attributeQuery(attr, node=self.obj, minExists=True)
        if min_status:
            min_value = mc.attributeQuery(attr, node=self.obj, minimum=True)[0]
            return min_status, min_value
        else:
            return min_status, 0.0

    def get_max_info(self, attr):
        max_status = mc.attributeQuery(attr, node=self.obj, maxExists=True)
        if max_status:
            max_value = mc.attributeQuery(attr, node=self.obj, maximum=True)[0]
            return max_status, max_value
        else:
            return max_status, 0.0

    def set_min(self, attrIndex):
        '''
        Maya can only toggle between having minValue enabled or not, and can not set it to a certain state, which
        implies the following over complicated way of setting it.
        '''
        attr_min_checkbox = self.findChild(QCheckBox, 'attr_{}_min_checkBox'.format(attrIndex))
        attr_min_checkbox_status = attr_min_checkbox.isChecked()
        attr_min_status = self.get_min_info(self.attributes[attrIndex])[0]
        attr_min_lineEdit = self.findChild(QLineEdit, 'attr_{}_min_lineEdit'.format(attrIndex))
        attr_min_lineEdit_text = attr_min_lineEdit.text()

        if attr_min_checkbox_status != attr_min_status:
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), edit=True, hasMinValue=False)
            if attr_min_checkbox_status:
                mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, minValue=float(attr_min_lineEdit_text))
            else:
                return
        else:
            if attr_min_checkbox_status:
                mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, minValue=float(attr_min_lineEdit_text))
            else:
                return

    def set_max(self, attrIndex):
        '''
        Maya can only toggle between having maxValue enabled or not, and can not set it to a certain state, which
        implies the following over complicated way of setting it.
        '''
        attr_max_checkbox = self.findChild(QCheckBox, 'attr_{}_max_checkBox'.format(attrIndex))
        attr_max_checkbox_status = attr_max_checkbox.isChecked()
        attr_max_status = self.get_max_info(self.attributes[attrIndex])[0]
        attr_max_lineEdit = self.findChild(QLineEdit, 'attr_{}_max_lineEdit'.format(attrIndex))
        attr_max_lineEdit_text = attr_max_lineEdit.text()

        if attr_max_checkbox_status != attr_max_status:
            mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), edit=True, hasMaxValue=False)
            if attr_max_checkbox_status:
                mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, maxValue=float(attr_max_lineEdit_text))
            else:
                return
        else:
            if attr_max_checkbox_status:
                mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, maxValue=float(attr_max_lineEdit_text))
            else:
                return

    def get_dValue(self, attr):
        dv = mc.addAttr('{}.{}'.format(self.obj, attr), q=True, defaultValue=True)
        return dv

    def set_dValue(self, attrIndex):
        attr_lineEdit = self.findChild(QLineEdit, 'attr_{}_dValue_lineEdit'.format(attrIndex))
        attr_lineEdit_text = attr_lineEdit.text()
        if not attr_lineEdit_text:
            attr_lineEdit_text = '0.0'
        mc.addAttr('{}.{}'.format(self.obj, self.attributes[attrIndex]), e=True, defaultValue=float(attr_lineEdit_text))
        return

    def get_type(self, attr):
        print('attributes = {}.{}'.format(self.obj, attr))
        attr_type = mc.getAttr('{}.{}'.format(self.obj, attr), type=True)
        print(attr_type)
        return str(attr_type)

    @staticmethod
    def add_attr():
        mel.eval('AddAttribute;')

    #Dict attr
    def get_attr_infos(self, attr):
        attr_infos = {'niceNameStatus': self.get_niceName_info(attr)[0],
                      'niceName': self.get_niceName_info(attr)[1],
                      'status': self.get_status(attr),
                      'locked': self.get_locked(attr),
                      'dValue': self.get_dValue(attr),
                      'type': self.get_type(attr)}
        if (attr_infos['type'] == 'long') or (attr_infos['type'] == 'double'):  # if integer or float
            attr_infos['minStatus'] = self.get_min_info(attr)[0]
            attr_infos['minValue'] = self.get_min_info(attr)[1]
            attr_infos['maxStatus'] = self.get_max_info(attr)[0]
            attr_infos['maxValue'] = self.get_max_info(attr)[1]
        elif attr_infos['type'] == 'enum':
            # todo : add enum attributes support
            pass
        return attr_infos
