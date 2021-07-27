#!/usr/bin/env python
# coding:utf-8

""" Attribute Manager for Maya 2017 and up.

The Attribute Manager will also work on 2016 and below if the user has Qt.py available.
The Attribute Manager allows you to quickly manage your custom attributes properties with a simple interface.
Supported attribute type are: bool, double, double3, long, enum, string

run command:
import rl_attr_manager
rl_attr_manager.launch_ui()

"""

from collections import OrderedDict
from functools import partial
import maya.cmds as mc
import maya.OpenMayaUI as mui
import maya.mel as mel
try:
    from Qt import QtGui, QtCore, QtWidgets, QtCompat
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as QtCompat

__author__ = "Robin Lavigne"
__version__ = "1.0"
__email__ = "contact@robinlavigne.com"


def launch_ui():
    if mc.window('rl_attr_manager', exists=True):
        mc.deleteUI('rl_attr_manager')
    ui = MainUI()
    ui.show()
    return ui


def get_maya_win():
    pointer = mui.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)


class MainUI(QtWidgets.QDialog, object):
    def __init__(self, parent=get_maya_win()):
        super(MainUI, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle('Attribute Manager')
        self.setObjectName('rl_attr_manager')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(225, 300)

        self.obj = get_sel()
        self.attributes = OrderedDict([(x, None) for x in get_attributes(self.obj)
                                       if not AttrData(x, self.obj).parent])
        print(list(self.attributes))
        if not self.attributes:
            mc.warning('No attributes on selection')
        if not self.obj:
            mc.warning('Nothing selected')
        self.ui_layout()
        self.ui_connections()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(7)
        main_layout.setContentsMargins(6, 8, 6, 6)
        self.setLayout(main_layout)

        reload_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(reload_layout)

        self.reloadSel_button = QtWidgets.QPushButton('Reload selected')
        reload_layout.addWidget(self.reloadSel_button)
        # Add attribute
        self.addAttr_button = QtWidgets.QPushButton('Add Attribute')
        self.addAttr_button.setFixedWidth(85)
        reload_layout.addWidget(self.addAttr_button)
        # Main separator
        main_frame = QtWidgets.QFrame()
        main_frame.setFrameShape(QtWidgets.QFrame.HLine)
        main_layout.addWidget(main_frame)

        self.sec_layout = QtWidgets.QHBoxLayout()
        self.sec_layout.setSpacing(0)
        self.sec_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(self.sec_layout)

        # Move arrow layout
        move_arrow_layout = QtWidgets.QVBoxLayout()
        move_arrow_layout.setContentsMargins(0, 0, 0, 0)
        self.moveUp_toolButton = QtWidgets.QToolButton()
        self.moveUp_toolButton.setArrowType(QtCore.Qt.UpArrow)
        self.moveUp_toolButton.setFixedWidth(22)
        move_arrow_layout.addWidget(self.moveUp_toolButton)
        self.moveDown_toolButton = QtWidgets.QToolButton()
        self.moveDown_toolButton.setArrowType(QtCore.Qt.DownArrow)
        self.moveDown_toolButton.setFixedWidth(22)
        move_arrow_layout.addWidget(self.moveDown_toolButton)
        self.sec_layout.addLayout(move_arrow_layout)

        # Advanced
        advance_layout = QtWidgets.QHBoxLayout()
        advance_layout.setAlignment(QtCore.Qt.AlignLeft)
        main_layout.addLayout(advance_layout)
        self.advance_checkbox = QtWidgets.QCheckBox('Advance mode')
        self.advance_checkbox.setFixedWidth(100)
        advance_layout.addWidget(self.advance_checkbox)
        self.applyAll_button = QtWidgets.QPushButton('Apply all')
        self.applyAll_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        advance_layout.addWidget(self.applyAll_button)
        self.applyAll_button.hide()

        # Attributes Group
        self.group_layout()

    def group_layout(self):
        self.attrs_group = QtWidgets.QGroupBox('Attributes')
        self.attrs_group.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.sec_layout.addWidget(self.attrs_group)
        group_layout = QtWidgets.QVBoxLayout()
        group_layout.setSpacing(0)
        group_layout.setContentsMargins(0, 0, 0, 0)
        self.attrs_group.setLayout(group_layout)

        self.attrs_groupButton = QtWidgets.QButtonGroup()

        scroll = QtWidgets.QScrollArea()
        group_layout.addWidget(scroll)
        container = QtWidgets.QWidget()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        self.attrs_layout = QtWidgets.QVBoxLayout()
        self.attrs_layout.setAlignment(QtCore.Qt.AlignTop)
        container.setLayout(self.attrs_layout)
        self.attrs_layout.setSpacing(0)
        self.attrs_layout.setContentsMargins(0, 0, 0, 0)

        for attribute in self.attributes:
            ui = AttrUI(parent=self, attr=attribute, advance=self.advance_checkbox.isChecked())
            self.attributes[attribute] = ui
            self.attrs_layout.addWidget(ui)

    def ui_connections(self):
        self.reloadSel_button.clicked.connect(self.reload_ui)
        self.addAttr_button.clicked.connect(partial(add_attr_maya, self.obj))
        self.moveDown_toolButton.clicked.connect(partial(self.move_attr, 'down'))
        self.moveUp_toolButton.clicked.connect(partial(self.move_attr, 'up'))
        self.advance_checkbox.clicked.connect(self.reload_ui)
        self.applyAll_button.clicked.connect(self.apply_all)

    def reload_ui(self):
        try:
            self.attrs_group.close()
        except:
            pass
        self.obj = get_sel()
        if self.obj:
            self.attributes = OrderedDict([(x, None) for x in get_attributes(self.obj)
                                           if not AttrData(x, self.obj).parent])
            self.group_layout()
        else:
            mc.warning('Select an object')

    @property
    def selected(self):
        for i, attr in enumerate(self.attributes):
            if self.attributes[attr].selected_status:
                return i, attr

    @selected.setter
    def selected(self, attr):
        self.attributes[attr].select_radioButton.setChecked(True)

    def move_attr(self, way):
        index, attr = self.selected
        if index is None:
            return

        if way == 'up':
            if index == 0:
                return
            new_index = index - 1
        else:
            new_index = index + 1

        # Creating a new list with the new attributes order
        attributes = list(self.attributes)
        new_attributes = list(self.attributes)
        new_attributes.pop(index)
        new_attributes.insert(new_index, attributes[index])

        # Deleting and undeleting attributes to reorder them
        for attribute in new_attributes:
            real_name = self.attributes[attribute].data.name
            if mc.getAttr('{}.{}'.format(self.obj, real_name), lock=True):  # If the attr is locked : unlock it
                lock = True
                mc.setAttr('{}.{}'.format(self.obj, real_name), lock=False)
            else:
                lock = False
            mc.deleteAttr('{}.{}'.format(self.obj, real_name))
            mc.undo()
            mc.setAttr('{}.{}'.format(self.obj, real_name), lock=lock)
        real_name = self.attributes[attr].data.name
        self.reload_ui()
        self.selected = real_name

    def apply_all(self):
        for attr, ui in self.attributes.items():
            ui.apply_changes()


class AttrUI(QtWidgets.QWidget, object):
    def __init__(self, parent, attr, advance):
        super(AttrUI, self).__init__(parent)
        self.parent = parent
        self.obj = parent.obj
        self.data = AttrData(attr, self.obj)
        self.children = None
        if self.data.children:
            self.children = OrderedDict()
            for child in self.data.children:
                self.children[child] = AttrUI(parent=parent, attr=child, advance=parent.advance_checkbox.isChecked())
        if advance:
            self.advance_layout()
        else:
            self.simple_layout()

    def simple_layout(self):
        self.parent.applyAll_button.hide()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(4, 6, 4, 2)
        self.setLayout(self.main_layout)
        self.selection_layout()

        self.name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.name_layout)
        self.name_lineEdit = QtWidgets.QLineEdit(self.data.name)
        self.main_layout.addWidget(self.name_lineEdit)

        if self.children:
            self.children_layout()

        self.simple_connection()
        mc.refresh()
        self.parent.adjustSize()

    def simple_connection(self):
        self.name_lineEdit.editingFinished.connect(partial(self.apply_changes, True))

    def advance_layout(self):
        self.parent.setMinimumSize(600, 500)
        self.parent.applyAll_button.show()

        # self.setMaximumHeight(150)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 4, 4, 8)
        self.setLayout(self.main_layout)
        if not self.data.parent:
            self.selection_layout()

        # Frame border box
        self.border_frame = QtWidgets.QFrame()
        self.border_frame.setObjectName('border_frame')
        self.border_frame.setStyleSheet('QFrame#border_frame { background-color : #4b4b4b }')
        self.main_layout.addWidget(self.border_frame)
        # Data Layout
        self.attr_layout = QtWidgets.QVBoxLayout()
        self.border_frame.setLayout(self.attr_layout)
        # Name line Layout
        self.name_layout = QtWidgets.QHBoxLayout()
        self.attr_layout.addLayout(self.name_layout)
        # Name label
        self.name_label = QtWidgets.QLabel('Name ')
        self.name_layout.addWidget(self.name_label)
        # Attribute name lineEdit
        self.name_lineEdit = QtWidgets.QLineEdit(self.data.name)
        self.name_lineEdit.setMinimumWidth(120)
        self.name_layout.addWidget(self.name_lineEdit)

        if not self.data.parent:
            self.apply_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addLayout(self.apply_layout)
            # Apply apply button
            self.apply_button = QtWidgets.QPushButton('Apply')
            self.apply_button.setFixedWidth(50)
            self.apply_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
            self.apply_layout.addWidget(self.apply_button)
            self.delete_button = QtWidgets.QPushButton('Delete')
            self.delete_button.setFixedWidth(50)
            self.apply_layout.addWidget(self.delete_button)

        # Attribute data------------
        # Attribute data Widget
        self.data_widget = QtWidgets.QWidget()
        self.attr_layout.addWidget(self.data_widget)
        # Attribute data layout
        self.data_layout = QtWidgets.QVBoxLayout()
        self.data_layout.setSpacing(6)
        self.data_layout.setContentsMargins(0, 6, 0, 0)
        self.data_widget.setLayout(self.data_layout)

        # Attribute nice Name
        self.niceName_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.niceName_layout)
        self.niceName_checkBox = QtWidgets.QCheckBox('Nice Name')
        if self.data.niceName_status:
            self.niceName_checkBox.setChecked(True)
        self.niceName_layout.addWidget(self.niceName_checkBox)
        self.niceName_lineEdit = QtWidgets.QLineEdit(self.data.niceName)
        self.niceName_layout.addWidget(self.niceName_lineEdit)

        # Attribute status
        self.status_buttonGrp = QtWidgets.QButtonGroup()
        self.status_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.status_layout)
        self.keyable_radioButton = QtWidgets.QRadioButton('Keyable')
        self.status_buttonGrp.addButton(self.keyable_radioButton)
        if self.data.status == 'keyable':
            self.keyable_radioButton.setChecked(True)
        self.status_layout.addWidget(self.keyable_radioButton)
        self.displayable_radioButton = QtWidgets.QRadioButton('Displayable')
        self.status_buttonGrp.addButton(self.displayable_radioButton)
        if self.data.status == 'displayable':
            self.displayable_radioButton.setChecked(True)
        self.status_layout.addWidget(self.displayable_radioButton)
        self.hidden_radioButton = QtWidgets.QRadioButton('Hidden')
        self.status_buttonGrp.addButton(self.hidden_radioButton)
        if self.data.status == 'hidden':
            self.hidden_radioButton.setChecked(True)
        self.status_layout.addWidget(self.hidden_radioButton)
        self.locked_checkBox = QtWidgets.QCheckBox('Locked')
        self.locked_checkBox.setChecked(self.data.locked)
        self.status_layout.addWidget(self.locked_checkBox)

        extra_data = getattr(self, '{}_layout'.format(self.data.type))
        extra_data()

        if not self.data.parent:
            self.advance_connections()

    def selection_layout(self):
        # Attribute choice radioButton
        self.select_radioButton = QtWidgets.QRadioButton()
        self.parent.attrs_groupButton.addButton(self.select_radioButton)
        self.main_layout.addWidget(self.select_radioButton)

    def children_layout(self):
        for child, ui in self.children.items():
            self.main_layout.addWidget(ui)


    @property
    def selected_status(self):
        return self.select_radioButton.isChecked()

    def double_layout(self):
        self.minMax_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.minMax_layout)
        self.min_checkBox = QtWidgets.QCheckBox('Min')
        self.min_checkBox.setChecked(self.data.min_status)
        self.minMax_layout.addWidget(self.min_checkBox)
        self.min_lineEdit = QtWidgets.QLineEdit()
        if self.data.min_status:
            min_value = str(self.data.min)
        else:
            min_value = '0.0'
        self.min_lineEdit.setText(min_value)
        self.min_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,9}[.][\d]{0,3}')))
        self.minMax_layout.addWidget(self.min_lineEdit)
        # Separator
        self.minMaxSep_frame = QtWidgets.QFrame()
        self.minMaxSep_frame.setFrameShape(QtWidgets.QFrame.VLine)
        self.minMaxSep_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.minMax_layout.addWidget(self.minMaxSep_frame)
        # Max
        self.max_checkBox = QtWidgets.QCheckBox('Max')
        self.max_checkBox.setChecked(self.data.max_status)
        self.minMax_layout.addWidget(self.max_checkBox)
        self.max_lineEdit = QtWidgets.QLineEdit()
        if self.data.max_status:
            max_value = str(self.data.max)
        else:
            max_value = '0.0'
        self.max_lineEdit.setText(max_value)
        self.max_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,9}[.][\d]{0,3}')))
        self.minMax_layout.addWidget(self.max_lineEdit)

        # Default Value
        self.defaultValue_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.defaultValue_layout)
        self.defaultValue_label = QtWidgets.QLabel('Default value')
        self.defaultValue_layout.addWidget(self.defaultValue_label)
        self.defaultValue_lineEdit = QtWidgets.QLineEdit()
        self.defaultValue_lineEdit.setText(str(self.data.defaultValue))
        self.defaultValue_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,9}[.][\d]{0,3}')))
        self.defaultValue_layout.addWidget(self.defaultValue_lineEdit)

    def long_layout(self):
        self.double_layout()

    def bool_layout(self):
        # Default Value
        self.defaultValue_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.defaultValue_layout)
        self.defaultValue_label = QtWidgets.QLabel('Default value')
        self.defaultValue_layout.addWidget(self.defaultValue_label)

        self.defaultValue_buttonGrp = QtWidgets.QButtonGroup()

        self.defaultValueTrue_radioButton = QtWidgets.QRadioButton('True')
        self.defaultValue_buttonGrp.addButton(self.defaultValueTrue_radioButton)
        self.defaultValueTrue_radioButton.setChecked(self.data.defaultValue)
        self.defaultValue_layout.addWidget(self.defaultValueTrue_radioButton)

        self.defaultValueFalse_radioButton = QtWidgets.QRadioButton('False')
        self.defaultValue_buttonGrp.addButton(self.defaultValueFalse_radioButton)
        self.defaultValueFalse_radioButton.setChecked(not self.data.defaultValue)
        self.defaultValue_layout.addWidget(self.defaultValueFalse_radioButton)

    def enum_layout(self):
        self.enum_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.enum_layout)

        self.enum_label = QtWidgets.QLabel('Enum names')
        self.enum_layout.addWidget(self.enum_label)

        self.enum_listWidget = QtWidgets.QListWidget()
        self.enum_listWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.enum_layout.addWidget(self.enum_listWidget)
        enum_list = self.data.enum_list
        self.enum_listWidget.setFixedHeight(16 * (len(enum_list) + 1))
        self.enum_listWidget.setMaximumWidth(140)
        for enum in enum_list:
            item = QtWidgets.QListWidgetItem(enum)
            self.enum_listWidget.addItem(item)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item = QtWidgets.QListWidgetItem('')
        self.enum_listWidget.addItem(item)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        # Default Value
        self.defaultValue_layout = QtWidgets.QHBoxLayout()
        self.enum_layout.addLayout(self.defaultValue_layout)
        self.defaultValue_label = QtWidgets.QLabel('Default index')
        self.defaultValue_layout.addWidget(self.defaultValue_label)
        self.defaultValue_lineEdit = QtWidgets.QLineEdit()
        self.defaultValue_lineEdit.setText(str(self.data.defaultValue))
        self.defaultValue_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]+')))
        self.defaultValue_lineEdit.setMaximumWidth(20)
        self.defaultValue_layout.addWidget(self.defaultValue_lineEdit)

    def string_layout(self):
        self.string_layout = QtWidgets.QHBoxLayout()
        self.data_layout.addLayout(self.string_layout)
        self.value_label = QtWidgets.QLabel('Value')
        self.string_layout.addWidget(self.value_label)
        self.value_lineEdit = QtWidgets.QLineEdit(self.data.value)
        self.string_layout.addWidget(self.value_lineEdit)

    def double3_layout(self):
        for child, ui in self.children.items():
            self.data_layout.addWidget(ui)

    def advance_connections(self):
        # Apply Button
        self.apply_button.clicked.connect(self.apply_changes)
        self.delete_button.clicked.connect(self.delete_attr)

    def delete_attr(self):
        mc.deleteAttr(self.obj, attribute=self.data.name)
        self.parent.reload_ui()

    def apply_changes(self, simple=False, *args):
        if not simple:
            for attr, value in self.widget_data.items():
                setattr(self.data, attr, value)
            self.widget_data = dict(self.data)
            if self.children:
                for child, ui in self.children.items():
                    ui.apply_changes()
        else:
            self.data.name = self.name_lineEdit.text()
            self.name_lineEdit.setText(self.data.name)
        refresh_channel_box()

    @property
    def widget_data(self):
        data = OrderedDict()
        data['name'] = self.name_lineEdit.text()
        data['niceName'] = self.niceName_lineEdit.text()
        data['niceName_status'] = self.niceName_checkBox.isChecked()
        data['locked'] = self.locked_checkBox.isChecked()
        if self.hidden_radioButton.isChecked():
            data['status'] = 'hidden'
        elif self.displayable_radioButton.isChecked():
            data['status'] = 'displayable'
        else:
            data['status'] = 'keyable'
        if self.data.type == 'double' or self.data.type == 'long':
            data['min'] = self.min_lineEdit.text()
            data['min_status'] = self.min_checkBox.isChecked()
            data['max'] = self.max_lineEdit.text()
            data['max_status'] = self.max_checkBox.isChecked()
            data['defaultValue'] = self.defaultValue_lineEdit.text()
        elif self.data.type == 'bool':
            data['defaultValue'] = self.defaultValueTrue_radioButton.isChecked()
        elif self.data.type == 'enum':
            data['enum_list'] = self.enum_list
            data['defaultValue'] = self.defaultValue_lineEdit.text()
        elif self.data.type == 'string':
            data['value'] = self.value_lineEdit.text()
        return data

    @widget_data.setter
    def widget_data(self, data):
        self.name_lineEdit.setText(data['name'])
        self.niceName_lineEdit.setText(data['niceName'])
        self.niceName_checkBox.setChecked(data['niceName_status'])
        self.locked_checkBox.setChecked(data['locked'])
        if data['status'] == 'hidden':
            self.hidden_radioButton.setChecked(True)
        elif data['status'] == 'displayable':
            self.displayable_radioButton.setChecked(True)
        else:
            self.keyable_radioButton.setChecked(True)
        if self.data.type == 'double' or self.data.type == 'long':
            self.min_lineEdit.setText(str(data['min']))
            self.min_checkBox.setChecked(data['min_status'])
            self.max_lineEdit.setText(str(data['max']))
            self.max_checkBox.setChecked(data['max_status'])
            data['defaultValue'] = self.defaultValue_lineEdit.text()
        elif self.data.type == 'bool':
            self.defaultValueTrue_radioButton.setChecked(data['defaultValue'])
        elif self.data.type == 'enum':
            self.enum_list = data['enum_list']
            data['defaultValue'] = self.defaultValue_lineEdit.setText(str(data['defaultValue']))
        elif self.data.type == 'string':
            self.value_lineEdit.setText(data['value'])

    @property
    def enum_list(self):
        items = []
        i = 0
        while True:
            item = self.enum_listWidget.item(i)
            if item:
                text = item.text()
                if text:
                    items.append(text)
                i += 1
            else:
                break
        return items

    @enum_list.setter
    def enum_list(self, value):
        self.enum_listWidget.close()
        self.enum_listWidget = QtWidgets.QListWidget()
        self.enum_listWidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.enum_layout.insertWidget(1, self.enum_listWidget)
        enum_list = value
        self.enum_listWidget.setFixedHeight(16 * (len(enum_list) + 1))
        self.enum_listWidget.setMaximumWidth(140)
        for enum in enum_list:
            item = QtWidgets.QListWidgetItem(enum)
            self.enum_listWidget.addItem(item)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item = QtWidgets.QListWidgetItem('')
        self.enum_listWidget.addItem(item)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)


def get_sel():
    obj = mc.ls(sl=True)
    if not obj:
        return []
    return obj[0]


def get_attributes(obj):
    if obj:
        attrs = mc.listAttr(obj, ud=True, visible=True)
        if attrs:
            return attrs
    return []


def add_attr_maya(obj):
    if obj:
        mc.select(obj)
        mel.eval('AddAttribute;')


def refresh_channel_box():
    mc.select(mc.ls(sl=True))


class AttrData(object):
    def __init__(self, name, obj):
        self.__name = name
        self.obj = obj

    def __iter__(self):
        methods = dir(self)
        for method in methods:
            if '__' not in method:
                attr = getattr(self, method)
                if attr is not None:
                    yield method, attr

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not value == '':
            try:
                mc.renameAttr('{}.{}'.format(self.obj, self.name), value)
                self.__name = value
            except RuntimeError:
                pass

    @property
    def niceName_status(self):
        if mc.addAttr('{}.{}'.format(self.obj, self.name), q=True, niceName=True):
            return True
        return False

    @niceName_status.setter
    def niceName_status(self, value):
        if not value:
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, niceName='')

    @property
    def niceName(self):
        return mc.attributeQuery(self.name, node=self.obj, niceName=True)

    @niceName.setter
    def niceName(self, value):
        mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, niceName=value)

    @property
    def status(self):
        keyable = mc.getAttr('{}.{}'.format(self.obj, self.name), keyable=True)
        displayable = mc.getAttr('{}.{}'.format(self.obj, self.name), channelBox=True)
        if keyable:
            return 'keyable'
        elif displayable:
            return 'displayable'
        else:
            return 'hidden'

    @status.setter
    def status(self, value):
        if value == 'hidden':
            mc.setAttr('{}.{}'.format(self.obj, self.name), keyable=False)
            mc.setAttr('{}.{}'.format(self.obj, self.name), channelBox=False)
        elif value == 'displayable':
            mc.setAttr('{}.{}'.format(self.obj, self.name), channelBox=True)
        else:
            mc.setAttr('{}.{}'.format(self.obj, self.name), keyable=True)

    @property
    def locked(self):
        locked = mc.getAttr('{}.{}'.format(self.obj, self.name), lock=True)
        return locked

    @locked.setter
    def locked(self, value):
        mc.setAttr('{}.{}'.format(self.obj, self.name), lock=value)

    @property
    def type(self):
        return mc.getAttr('{}.{}'.format(self.obj, self.name), type=True)

    @property
    def min_status(self):
        if self.type == 'double' or self.type == 'long':
            return mc.attributeQuery(self.name, node=self.obj, minExists=True)

    @min_status.setter
    def min_status(self, value):
        """
        Maya can only toggle the minValue and can not set it to a certain state, regardless of passing True or False,
         which implies the following way of setting it.
        """
        if not bool(value) == self.min_status:
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, hasMinValue=value)

    @property
    def min(self):
        if self.type == 'double' or self.type == 'long':
            if not self.min_status:
                return 0.0
            return mc.attributeQuery(self.name, node=self.obj, minimum=True)[0]

    @min.setter
    def min(self, value):
        mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, minValue=float(value))

    @property
    def max_status(self):
        if self.type == 'double' or self.type == 'long':
            return mc.attributeQuery(self.name, node=self.obj, maxExists=True)

    @max_status.setter
    def max_status(self, value):
        """
        Maya can only toggle the maxValue and can not set it to a certain state, regardless of passing True or False,
         which implies the following of setting it.
        """
        if not bool(value) == self.max_status:
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, hasMaxValue=value)

    @property
    def max(self):
        if self.type == 'double' or self.type == 'long':
            if not self.max_status:
                return 0.0
            return mc.attributeQuery(self.name, node=self.obj, maximum=True)[0]

    @max.setter
    def max(self, value):
        mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, maxValue=float(value))

    @property
    def defaultValue(self):
        if self.children:
            return
        default_value = mc.addAttr('{}.{}'.format(self.obj, self.name), q=True, defaultValue=True)
        if self.type == 'bool':
            return bool(default_value)
        elif self.type == 'enum':
            return int(default_value)
        return default_value

    @defaultValue.setter
    def defaultValue(self, value):
        if self.children:
            return
        if self.type == 'bool':
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, defaultValue=bool(value))
        elif self.type == 'enum':
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, defaultValue=int(value))
        else:
            mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, defaultValue=float(value))

    @property
    def enum_list(self):
        if self.type == 'enum':
            enums = mc.addAttr('{}.{}'.format(self.obj, self.name), q=True, enumName=True)
            if enums:
                enums = enums.split(':')
                return enums
            else:
                return []

    @enum_list.setter
    def enum_list(self, value):
        mc.addAttr('{}.{}'.format(self.obj, self.name), e=True, enumName=':'.join(value))

    @property
    def parent(self):
        """
        gets the parent attribute if any. e.g. for a double3 type sub attributes
        :return: the parent attribute name
        """
        return mc.attributeQuery(self.name, node=self.obj, listParent=True)

    @property
    def children(self):
        """
        gets the children attributes list if any. e.g. for a double3 type attribute
        :return: the children attribute list
        """
        return mc.attributeQuery(self.name, node=self.obj, listChildren=True)

    @property
    def value(self):
        return mc.getAttr('{}.{}'.format(self.obj, self.name))

    @value.setter
    def value(self, value):
        if self.type == 'string':
            mc.setAttr('{}.{}'.format(self.obj, self.name), value, type='string')
        else:
            mc.setAttr('{}.{}'.format(self.obj, self.name), value)


if __name__ == '__main__':
    launch_ui()
