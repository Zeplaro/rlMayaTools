# coding: utf-8

"""
Advanced node renaming tool for maya.

For it to work you need to have Marcus Ottosson's Qt.py installed.
You can find it here https://github.com/mottosso/Qt.py

To launch run :

from renamer import rl_renamer
rl_renamer.launch_ui()

"""

__author__ = "Robin Lavigne"
__version__ = "1.0"
__email__ = "contact@robinlavigne.com"

import os
import re
import sys
from functools import partial

_pyversion = sys.version_info[0]
if _pyversion == 3:
    basestring = str
    long = int

from Qt import QtGui, QtCore, QtWidgets, QtCompat

import maya.OpenMayaUI as omui
from maya import cmds
import maya.api.OpenMaya as om


def get_maya_window():
    """Getting maya's window"""
    ptr = omui.MQtUtil.mainWindow()
    parent = QtCompat.wrapInstance(long(ptr), QtWidgets.QMainWindow)
    return parent


def close_existing(target_title):
    """Close existing Renamer is already openned"""
    parent = get_maya_window()
    children = parent.children()
    for child in children:
        try:
            title = child.windowTitle()
        except:
            title = ''
        if title == target_title:
            try:
                child.close()
            except ValueError:
                print("failed to close '{}'".format(target_title))


def center_ui(ui):
    cursor_pos = QtGui.QCursor.pos()
    screen_index = QtWidgets.QApplication.desktop().screenNumber(cursor_pos)
    ui_center = QtCore.QPoint(ui.frameSize().height() / 2, ui.frameSize().width() / 2)
    screen_center = QtWidgets.QApplication.screens()[screen_index].geometry().center()
    center_pos = screen_center - ui_center
    ui.move(center_pos)


def launch_ui():
    """Launch the Renamer ui"""
    ui_title = 'rl Renamer'
    close_existing(ui_title)
    ui = MainUI(parent=get_maya_window(), title=ui_title)
    ui.show()
    center_ui(ui.window())
    return ui


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, title='rl Renamer', parent=None):
        super(MainUI, self).__init__(parent)
        QtCompat.loadUi(os.path.split(__file__)[0] + "/rl_renamer.ui", self)  # Loading the .ui file
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)

        self.model = NameModel(self)

        self.name_table = self.findChild(QtWidgets.QTableView, 'name_table')
        self.name_table.setModel(self.model)
        self.name_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # lineEdit regex validator for maya allowed characters
        reg_ex = QtCore.QRegExp("([a-zA-Z0-9]|_)+")

        self.reload_button = self.findChild(QtWidgets.QPushButton, 'reload_button')
        # rename group
        self.rename_group = self.findChild(QtWidgets.QGroupBox, 'rename_group')
        self.rename_widget = self.findChild(QtWidgets.QWidget, 'rename_widget')
        self.rename_line = self.findChild(QtWidgets.QLineEdit, 'rename_line')
        # replace group
        self.replace_group = self.findChild(QtWidgets.QGroupBox, 'replace_group')
        self.replace_widget = self.findChild(QtWidgets.QWidget, 'replace_widget')
        self.replace_line = self.findChild(QtWidgets.QLineEdit, 'replace_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.replace_line)
        self.replace_line.setValidator(input_validator)
        self.replacewith_line = self.findChild(QtWidgets.QLineEdit, 'replacewith_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.replacewith_line)
        self.replacewith_line.setValidator(input_validator)
        self.matchcase_checkbox = self.findChild(QtWidgets.QCheckBox, 'matchcase_checkbox')
        # remove group
        self.remove_group = self.findChild(QtWidgets.QGroupBox, 'remove_group')
        self.remove_widget = self.findChild(QtWidgets.QWidget, 'remove_widget')
        self.first_spin = self.findChild(QtWidgets.QSpinBox, 'first_spin')
        self.last_spin = self.findChild(QtWidgets.QSpinBox, 'last_spin')
        self.from_spin = self.findChild(QtWidgets.QSpinBox, 'from_spin')
        self.to_spin = self.findChild(QtWidgets.QSpinBox, 'to_spin')
        # add group
        self.add_group = self.findChild(QtWidgets.QGroupBox, 'add_group')
        self.add_widget = self.findChild(QtWidgets.QWidget, 'add_widget')
        self.prefix_line = self.findChild(QtWidgets.QLineEdit, 'prefix_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.prefix_line)
        self.prefix_line.setValidator(input_validator)
        self.insert_line = self.findChild(QtWidgets.QLineEdit, 'insert_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.insert_line)
        self.insert_line.setValidator(input_validator)
        self.insertat_spin = self.findChild(QtWidgets.QSpinBox, 'insertat_spin')
        self.suffix_line = self.findChild(QtWidgets.QLineEdit, 'suffix_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.suffix_line)
        self.suffix_line.setValidator(input_validator)
        # numbering group
        self.numbering_group = self.findChild(QtWidgets.QGroupBox, 'numbering_group')
        self.numbering_widget = self.findChild(QtWidgets.QWidget, 'numbering_widget')
        self.mode_combo = self.findChild(QtWidgets.QComboBox, 'mode_combo')
        self.type_combo = self.findChild(QtWidgets.QComboBox, 'type_combo')
        self.start_spin = self.findChild(QtWidgets.QSpinBox, 'start_spin')
        self.step_spin = self.findChild(QtWidgets.QSpinBox, 'step_spin')
        self.numberinginsertat_label = self.findChild(QtWidgets.QLabel, 'numberinginsertat_label')
        self.numberinginsertat_spin = self.findChild(QtWidgets.QSpinBox, 'numberinginsertat_spin')
        self.padding_label = self.findChild(QtWidgets.QLabel, 'padding_label')
        self.padding_spin = self.findChild(QtWidgets.QSpinBox, 'padding_spin')
        self.sep_line = self.findChild(QtWidgets.QLineEdit, 'sep_line')
        input_validator = QtGui.QRegExpValidator(reg_ex, self.sep_line)
        self.sep_line.setValidator(input_validator)

        self.rename_button = self.findChild(QtWidgets.QPushButton, 'rename_button')

        self.ui_connections()
        self.rename_group.setChecked(False)
        self.replace_group.setChecked(False)
        self.remove_group.setChecked(False)
        self.add_group.setChecked(False)
        self.numbering_group.setChecked(False)

        self.reload_selection()

    def ui_connections(self):
        """Sets the signal connections"""
        self.reload_button.clicked.connect(self.reload_selection)
        # rename group
        self.rename_group.toggled.connect(partial(self.refresh_group, self.rename_widget))
        self.rename_line.textChanged.connect(self.refresh_newnames)
        # replace group
        self.replace_group.toggled.connect(partial(self.refresh_group, self.replace_widget))
        self.replace_line.textChanged.connect(self.refresh_newnames)
        self.replacewith_line.textChanged.connect(self.refresh_newnames)
        self.matchcase_checkbox.stateChanged.connect(self.refresh_newnames)
        # remove group
        self.remove_group.toggled.connect(partial(self.refresh_group, self.remove_widget))
        self.first_spin.valueChanged.connect(self.refresh_newnames)
        self.last_spin.valueChanged.connect(self.refresh_newnames)
        self.from_spin.valueChanged.connect(self.fromspin_changed)
        self.to_spin.valueChanged.connect(self.tospin_changed)
        # add group
        self.add_group.toggled.connect(partial(self.refresh_group, self.add_widget))
        self.prefix_line.textChanged.connect(self.refresh_newnames)
        self.insert_line.textChanged.connect(self.refresh_newnames)
        self.insertat_spin.valueChanged.connect(self.refresh_newnames)
        self.suffix_line.textChanged.connect(self.refresh_newnames)
        # numbering group
        self.numbering_group.toggled.connect(partial(self.refresh_group, self.numbering_widget))
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)
        self.type_combo.currentIndexChanged.connect(self.type_changed)
        self.start_spin.valueChanged.connect(self.refresh_newnames)
        self.step_spin.valueChanged.connect(self.refresh_newnames)
        self.numberinginsertat_spin.valueChanged.connect(self.refresh_newnames)
        self.padding_spin.valueChanged.connect(self.refresh_newnames)
        self.sep_line.textChanged.connect(self.refresh_newnames)
        self.rename_button.clicked.connect(self.do_rename)

    def refresh_group(self, widget, state):
        """Refreshes the groupBox visibility when checked/unchecked"""
        widget.setVisible(state)
        self.refresh_newnames()

    def reload_selection(self):
        """Reloads objects list from current selection"""
        self.model.maya_nodes = get_selection()
        self.refresh_newnames()

    def refresh_newnames(self):
        """Refreshes the new names in the table"""
        self.refresh_numbering_range()
        self.model.layoutChanged.emit()

    def get_new_name(self, name, index):
        """Gets the new name passing through all the checked 'modifiers', leaving out the parents if in the name"""
        split = name.split('|')
        name = split.pop(-1)
        if self.rename_group.isChecked():
            name = self.rename(name)
        if self.replace_group.isChecked():
            name = self.replace(name)
        if self.remove_group.isChecked():
            name = self.remove(name)
        if self.add_group.isChecked():
            name = self.add(name)
        if self.numbering_group.isChecked():
            name = self.numbering(name, index)
        return name

    def rename(self, name):
        rename_text = self.rename_line.text()
        if rename_text:
            name = rename_text
        return name

    def replace(self, name):
        if self.matchcase_checkbox.isChecked():
            name = name.replace(self.replace_line.text(), self.replacewith_line.text())
        else:
            pattern = re.compile(re.escape(self.replace_line.text()), re.IGNORECASE)
            name = pattern.sub(self.replacewith_line.text(), name)
        return name

    def remove(self, name):
        first = self.first_spin.value()
        name = name[first:]
        last = self.last_spin.value()
        if last:
            name = name[:-last]

        from_value = self.from_spin.value()
        to_value = self.to_spin.value()
        if from_value:
            name = name[:from_value-1] + name[to_value:]

        return name

    def add(self, name):
        name = self.prefix_line.text() + name
        insertat_value = self.insertat_spin.value()
        if insertat_value == -1:
            name += self.insert_line.text()
        elif insertat_value < 0:
            name = name[:insertat_value+1] + self.insert_line.text() + name[insertat_value+1:]
        else:
            name = name[:insertat_value] + self.insert_line.text() + name[insertat_value:]
        name += self.suffix_line.text()
        return name

    def numbering(self, name, index):
        mode = self.mode_combo.currentText()
        numtype = self.type_combo.currentText()
        insertat = self.numberinginsertat_spin.value()
        padding = self.padding_spin.value()
        separator = self.sep_line.text()

        if numtype == 'Decimal':
            num_string = str(self.numbering_range[index]).zfill(padding)
        elif numtype == 'Alphabetical (upper)':
            num_string = self.numbering_range[index].upper()
        elif numtype == 'Alphabetical (lower)':
            num_string = self.numbering_range[index]
        elif numtype == 'Hexadecimal (upper)':
            num_string = str(hex(self.numbering_range[index]))[2:].zfill(padding).upper()
        elif numtype == 'Hexadecimal (lower)':
            num_string = str(hex(self.numbering_range[index]))[2:].zfill(padding)
        elif numtype == 'Octal':
            num_string = str(oct(self.numbering_range[index]))[2:].zfill(padding) or '0'.zfill(padding)
        elif numtype == 'Binary':
            num_string = str(bin(self.numbering_range[index]))[2:].zfill(padding)
        elif numtype == 'Roman':
            num_string = decimal_to_roman(self.numbering_range[index])
        else:
            num_string = ''

        if mode == 'Suffix':
            name += separator + num_string
        elif mode == 'Prefix':
            name = num_string + separator + name
        elif mode == 'Insert':
            name = name[:insertat] + separator + num_string + separator + name[insertat:]
        return name

    def fromspin_changed(self):
        """Updates to_spin spinBox so that it's never lower than from_spin spinBox"""
        from_value = self.from_spin.value()
        to_value = self.to_spin.value()
        if to_value < from_value:
            self.to_spin.setValue(from_value)
        self.refresh_newnames()

    def tospin_changed(self):
        """Updates from_spin spinBox so that it's never higher than to_spin spinBox"""
        from_value = self.from_spin.value()
        to_value = self.to_spin.value()
        if from_value > to_value:
            self.from_spin.setValue(to_value)
        self.refresh_newnames()

    def mode_changed(self):
        """Updates insert spinBox and label to be disabled when 'Insert' mode is selected"""
        if self.mode_combo.currentText() == 'Insert':
            self.numberinginsertat_label.setEnabled(True)
            self.numberinginsertat_spin.setEnabled(True)
        else:
            self.numberinginsertat_label.setEnabled(False)
            self.numberinginsertat_spin.setEnabled(False)
        self.refresh_newnames()

    def type_changed(self):
        """Updates padding spinBox and label to be disabled when 'Alphabetical' mode is selected"""
        current_type = self.type_combo.currentText()
        if 'Alphabetical' in current_type:
            self.start_spin.setMinimum(0)
            self.padding_label.setEnabled(False)
            self.padding_spin.setEnabled(False)
        elif current_type == 'Roman':
            self.start_spin.setMinimum(1)
            self.padding_label.setEnabled(False)
            self.padding_spin.setEnabled(False)
        else:
            self.start_spin.setMinimum(0)
            self.padding_label.setEnabled(True)
            self.padding_spin.setEnabled(True)
        self.refresh_newnames()

    def refresh_numbering_range(self):
        current_type = self.type_combo.currentText()
        start = self.start_spin.value()
        step = self.step_spin.value()
        if 'Alphabetical' in current_type:
            self.numbering_range = [decimal_to_alpha(x) for x in range(start, len(self.model.maya_nodes) * step + start, step)]
        else:
            self.numbering_range = list(range(start, len(self.model.maya_nodes) * step + start, step))

    def do_rename(self):
        """Renames the objects in maya. Will fail if given invalid characters or trying to rename non renamable nodes"""
        cmds.undoInfo(openChunk=True)
        self.model.maya_nodes = get_selection()
        counter = 0
        for i, node in enumerate(self.model.maya_nodes):
            try:
                new_name = self.get_new_name(node.name, i)
                if node.name != new_name:
                    node.name = new_name
                counter += 1
            except RuntimeError as e:
                print("cannot rename node '{}' : {}".format(node.name, e))
        cmds.undoInfo(closeChunk=True)
        print("## Renamed {} nodes.".format(counter))
        self.refresh_newnames()


class NameModel(QtCore.QAbstractTableModel):
    def __init__(self, main_ui):
        super(NameModel, self).__init__()
        self.main_ui = main_ui
        self.maya_nodes = []

    def rowCount(self, index):
        return len(self.maya_nodes)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            name = self.maya_nodes[index.row()].name
            if index.column() == 0:
                return name
            else:
                return self.main_ui.get_new_name(name, index.row())
        elif role == QtCore.Qt.ForegroundRole:  # Sets the new names color if different than current name
            if index.column() == 1:
                name = self.maya_nodes[index.row()].name
                if self.main_ui.get_new_name(name, index.row()) != name:
                    return QtGui.QColor(95, 173, 136)

    def headerData(self, column, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if column == 0:
                    return "Current name"
                else:
                    return "New name"


def get_selection():
    """Returns OpenMaya MObject for current scene selection"""
    mSelectionList = om.MSelectionList()
    mObjects = []
    i = 0  # not using enumerate in case components are in selection
    for node in cmds.ls(os=True, fl=True):
        if '.' not in node:
            mSelectionList.add(node)
            mObjects.append(MayaNode(mSelectionList.getDependNode(i)))
            i += 1
    return mObjects


class MayaNode(object):
    """Manages maya nodes naming properly keeping track of each nodes MObject"""
    def __init__(self, mObject):
        self.mObject = mObject
        self.mFnDependencyNode = om.MFnDependencyNode(mObject)
        try:
            self.mFnDagNode = om.MFnDagNode(mObject)
        except RuntimeError:
            self.mFnDagNode = None

    def __str__(self):
        return self.name

    @property
    def name(self):
        """Gets the node name from its MObject"""
        try:
            return self.mFnDagNode.partialPathName()
        except RuntimeError:
            return self.mFnDependencyNode.name()

    @name.setter
    def name(self, newname):
        cmds.rename(self.name, newname)


def decimal_to_alpha(index):
    """Converts an int to an alphabetical index"""
    from string import ascii_lowercase
    alphanum = ''
    index += 1  # because alphabet hase no 0 and starts with 'a'
    while index:
        index -= 1  # 'a' needs to be used as next 'decimal' unit when reaching 'z':  ..., 'y', 'z', 'aa', 'ab', ...
        reste = index % 26
        index = index // 26
        alphanum = ascii_lowercase[reste] + alphanum
    return alphanum


def decimal_to_roman(index):
    """Converts an int to a roman numerical index"""
    if not isinstance(index, int):
        raise TypeError("Expected index to be int; got : {}, {}".format(index, type(index).__name__))
    if not index > 0:
        raise ValueError("Given index must be > 0; got : {}".format(index))
    roman = [(1000, 'M'), (900, 'CM'),
             (500, 'D'), (400, 'CD'),
             (100, 'C'), (90, 'XC'),
             (50, 'L'), (40, 'XL'),
             (10, 'X'), (9, 'IX'),
             (5, 'V'), (4, 'IV'),
             (1, 'I')]
    roman_num = ''
    while index:
        for value, num in roman:
            if index >= value:
                roman_num += num
                index -= value
                break
    return roman_num


if __name__ == '__main__':
    launch_ui()
