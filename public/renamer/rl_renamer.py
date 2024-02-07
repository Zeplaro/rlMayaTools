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
from functools import partial
from string import ascii_lowercase

from Qt import QtGui, QtCore, QtWidgets, QtCompat

import maya.OpenMayaUI as omui
from maya import cmds
import maya.api.OpenMaya as om


def get_maya_window():
    """Getting maya's window"""
    ptr = omui.MQtUtil.mainWindow()
    parent = QtCompat.wrapInstance(int(ptr), QtWidgets.QMainWindow)
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
    # Get the cursor position
    cursor_pos = QtGui.QCursor.pos()
    # Get the screen the cursor is on
    screen = QtWidgets.QApplication.screenAt(cursor_pos)
    # Get the center point of the screen
    screen_center = screen.geometry().center()
    # Get the center point of the UI
    ui_center = ui.frameGeometry().center()
    # Calculate the position to move the UI to the center of the screen
    center_pos = screen_center - ui_center
    # Move the UI to the calculated position
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
        self.ui = QtCompat.loadUi(os.path.split(__file__)[0] + "/rl_renamer.ui", self)  # Loading the .ui file
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)

        self.model = NameModel(self)

        self.ui.name_table.setModel(self.model)
        self.ui.name_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # lineEdit regex validator for maya allowed characters
        reg_ex = QtCore.QRegExp("([a-zA-Z0-9]|_)+")
        input_validator = QtGui.QRegExpValidator(reg_ex)

        self.ui.rename_line.setValidator(input_validator)
        self.ui.replace_line.setValidator(input_validator)
        self.ui.replacewith_line.setValidator(input_validator)
        self.ui.prefix_line.setValidator(input_validator)
        self.ui.insert_line.setValidator(input_validator)
        self.ui.suffix_line.setValidator(input_validator)
        self.ui.sep_line.setValidator(input_validator)

        self.ui_connections()
        self.ui.rename_group.setChecked(False)
        self.ui.replace_group.setChecked(False)
        self.ui.remove_group.setChecked(False)
        self.ui.add_group.setChecked(False)
        self.ui.numbering_group.setChecked(False)

        self.reload_selection()

    def ui_connections(self):
        """Sets the signal connections"""
        self.ui.reload_button.clicked.connect(self.reload_selection)
        # rename group
        self.ui.rename_group.toggled.connect(partial(self.refresh_group, self.rename_widget))
        self.ui.rename_line.textChanged.connect(self.refresh_newnames)
        # replace group
        self.ui.replace_group.toggled.connect(partial(self.refresh_group, self.replace_widget))
        self.ui.replace_line.textChanged.connect(self.refresh_newnames)
        self.ui.replacewith_line.textChanged.connect(self.refresh_newnames)
        self.ui.matchcase_checkbox.stateChanged.connect(self.refresh_newnames)
        # remove group
        self.ui.remove_group.toggled.connect(partial(self.refresh_group, self.remove_widget))
        self.ui.first_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.last_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.from_spin.valueChanged.connect(self.fromspin_changed)
        self.ui.to_spin.valueChanged.connect(self.tospin_changed)
        # add group
        self.ui.add_group.toggled.connect(partial(self.refresh_group, self.add_widget))
        self.ui.prefix_line.textChanged.connect(self.refresh_newnames)
        self.ui.insert_line.textChanged.connect(self.refresh_newnames)
        self.ui.insertat_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.suffix_line.textChanged.connect(self.refresh_newnames)
        # numbering group
        self.ui.numbering_group.toggled.connect(partial(self.refresh_group, self.numbering_widget))
        self.ui.mode_combo.currentIndexChanged.connect(self.mode_changed)
        self.ui.type_combo.currentIndexChanged.connect(self.type_changed)
        self.ui.start_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.step_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.numberinginsertat_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.padding_spin.valueChanged.connect(self.refresh_newnames)
        self.ui.sep_line.textChanged.connect(self.refresh_newnames)
        self.ui.rename_button.clicked.connect(self.do_rename)

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
        if self.ui.rename_group.isChecked():
            name = self.rename(name)
        if self.ui.replace_group.isChecked():
            name = self.replace(name)
        if self.ui.remove_group.isChecked():
            name = self.remove(name)
        if self.ui.add_group.isChecked():
            name = self.add(name)
        if self.ui.numbering_group.isChecked():
            name = self.numbering(name, index)
        return name

    def rename(self, name):
        rename_text = self.ui.rename_line.text()
        if rename_text:
            name = rename_text
        return name

    def replace(self, name):
        if self.ui.matchcase_checkbox.isChecked():
            name = name.replace(self.ui.replace_line.text(), self.ui.replacewith_line.text())
        else:
            pattern = re.compile(re.escape(self.ui.replace_line.text()), re.IGNORECASE)
            name = pattern.sub(self.ui.replacewith_line.text(), name)
        return name

    def remove(self, name):
        first = self.ui.first_spin.value()
        name = name[first:]
        last = self.ui.last_spin.value()
        if last:
            name = name[:-last]

        from_value = self.ui.from_spin.value()
        to_value = self.ui.to_spin.value()
        if from_value:
            name = name[:from_value-1] + name[to_value:]

        return name

    def add(self, name):
        name = self.ui.prefix_line.text() + name
        insertat_value = self.ui.insertat_spin.value()
        if insertat_value == -1:
            name += self.ui.insert_line.text()
        elif insertat_value < 0:
            name = name[:insertat_value+1] + self.ui.insert_line.text() + name[insertat_value+1:]
        else:
            name = name[:insertat_value] + self.ui.insert_line.text() + name[insertat_value:]
        name += self.ui.suffix_line.text()
        return name

    def numbering(self, name, index):
        mode = self.ui.mode_combo.currentText()
        numtype = self.ui.type_combo.currentText()
        insertat = self.ui.numberinginsertat_spin.value()
        padding = self.ui.padding_spin.value()
        separator = self.ui.sep_line.text()

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
        from_value = self.ui.from_spin.value()
        to_value = self.ui.to_spin.value()
        if to_value < from_value:
            self.ui.to_spin.setValue(from_value)
        self.refresh_newnames()

    def tospin_changed(self):
        """Updates from_spin spinBox so that it's never higher than to_spin spinBox"""
        from_value = self.ui.from_spin.value()
        to_value = self.ui.to_spin.value()
        if from_value > to_value:
            self.ui.from_spin.setValue(to_value)
        self.refresh_newnames()

    def mode_changed(self):
        """Updates insert spinBox and label to be disabled when 'Insert' mode is selected"""
        if self.ui.mode_combo.currentText() == 'Insert':
            self.ui.numberinginsertat_label.setEnabled(True)
            self.ui.numberinginsertat_spin.setEnabled(True)
        else:
            self.ui.numberinginsertat_label.setEnabled(False)
            self.ui.numberinginsertat_spin.setEnabled(False)
        self.refresh_newnames()

    def type_changed(self):
        """Updates padding spinBox and label to be disabled when 'Alphabetical' mode is selected"""
        current_type = self.ui.type_combo.currentText()
        if 'Alphabetical' in current_type:
            self.ui.start_spin.setMinimum(0)
            self.ui.padding_label.setEnabled(False)
            self.ui.padding_spin.setEnabled(False)
        elif current_type == 'Roman':
            self.ui.start_spin.setMinimum(1)
            self.ui.padding_label.setEnabled(False)
            self.ui.padding_spin.setEnabled(False)
        else:
            self.ui.start_spin.setMinimum(0)
            self.ui.padding_label.setEnabled(True)
            self.ui.padding_spin.setEnabled(True)
        self.refresh_newnames()

    def refresh_numbering_range(self):
        current_type = self.ui.type_combo.currentText()
        start = self.ui.start_spin.value()
        step = self.ui.step_spin.value()
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
        elif role == QtCore.Qt.ForegroundRole:  # Sets the new names color if different from current name
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
    def __init__(self, MObject):
        self.MObject = MObject
        self.MFn = om.MFnDependencyNode(MObject)
        try:
            self.MFnDagNode = om.MFnDagNode(MObject)
        except RuntimeError:
            self.MFnDagNode = None

    def __str__(self):
        return self.name

    @property
    def name(self):
        """Gets the node name from its MObject"""
        try:
            return self.MFnDagNode.partialPathName()
        except RuntimeError:
            return self.MFn.name()

    @name.setter
    def name(self, newname):
        cmds.rename(self.name, newname)


def decimal_to_alpha(index):
    """Converts an int to an alphabetical index"""
    alphanum = ''
    index += 1  # because alphabet hase no 0 and starts with 'a'
    while index:
        index -= 1  # 'a' needs to be used as next 'decimal' unit when reaching 'z':  ..., 'y', 'z', 'aa', 'ab', ...
        reste = index % 26
        index = index // 26
        alphanum = ascii_lowercase[reste] + alphanum
    return alphanum


ROMAN = ((1000, 'M'), (900, 'CM'),
         (500, 'D'), (400, 'CD'),
         (100, 'C'), (90, 'XC'),
         (50, 'L'), (40, 'XL'),
         (10, 'X'), (9, 'IX'),
         (5, 'V'), (4, 'IV'),
         (1, 'I'))


def decimal_to_roman(index):
    """Converts an int to a roman numerical index"""
    if not isinstance(index, int):
        raise TypeError("Expected index to be int; got : {}, {}".format(index, type(index).__name__))
    if not index > 0:
        raise ValueError("Given index must be > 0; got : {}".format(index))
    roman_num = ''
    while index:
        for value, num in ROMAN:
            if index >= value:
                roman_num += num
                index -= value
                break
    return roman_num


if __name__ == '__main__':
    launch_ui()
