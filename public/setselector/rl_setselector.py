# coding: utf-8

"""
Selection manager tool for maya. Stores multiple selection data in different tab for easy selection modification and
recovery.

For it to work you need to have Marcus Ottosson's Qt.py installed.
You can find it here https://github.com/mottosso/Qt.py

To launch run :

from setselector import rl_setselector
rl_setselector.launch_ui()

"""

__author__ = "Robin Lavigne"
__version__ = "2.0"
__email__ = "contact@robinlavigne.com"

import os
import sys
import json
from functools import partial
import maya.OpenMayaUI as omui
from maya import cmds

_pyversion = sys.version_info[0]
if _pyversion == 3:
    long = int

from Qt import QtGui, QtCore, QtWidgets, QtCompat


empty_data = {'tabs': ['Main'],
              'tabs_data': {'Main': {'sets': [],
                                     'members': {}
                                     }
                            }
              }


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


def launch_ui():
    """Launch the Renamer ui"""
    ui_title = 'rl Set Selector'
    close_existing(ui_title)
    ui = MainUI(parent=get_maya_window(), title=ui_title)
    ui.show()
    return ui


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None, title='rl Set Selector'):
        super(MainUI, self).__init__(parent=parent)
        QtCompat.loadUi(os.path.split(__file__)[0] + "/rl_setselector.ui", self)  # Loading the .ui file
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        self.data = SelData(get_scene_data())

        self.ui_layout()

        self.ui_connections()

    def ui_layout(self):
        # top
        self.resetdata_action = self.findChild(QtWidgets.QAction, 'resetdata_action')
        self.setname_line = self.findChild(QtWidgets.QLineEdit, 'setname_line')
        self.setname_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'([a-zA-Z]|_){1}(\w|_|0-9| )+')))
        self.addset_button = self.findChild(QtWidgets.QPushButton, 'addset_button')
        self.deleteset_button = self.findChild(QtWidgets.QPushButton, 'deleteset_button')

        # move
        self.up_button = self.findChild(QtWidgets.QToolButton, 'up_button')
        self.down_button = self.findChild(QtWidgets.QToolButton, 'down_button')

        # tabs
        tabs_layout = self.findChild(QtWidgets.QVBoxLayout, 'tabs_layout')
        self.tab_widget = TabBarWidget(self)
        tabs_layout.addWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("QTabBar { background-color: #373737 }")
        # list
        self.list_view = SetListView(self, self.data)
        tabs_layout.addWidget(self.list_view)

        # update
        self.plus_button = self.findChild(QtWidgets.QPushButton, 'plus_button')
        self.replace_button = self.findChild(QtWidgets.QPushButton, 'replace_button')
        self.minus_button = self.findChild(QtWidgets.QPushButton, 'minus_button')

        # Replace
        self.replace_group = self.findChild(QtWidgets.QGroupBox, 'replace_group')
        self.replace_widget = self.findChild(QtWidgets.QWidget, 'replace_widget')
        self.replace_widget.setVisible(False)
        self.replace_line = self.findChild(QtWidgets.QLineEdit, 'replace_line')
        self.replaceby_line = self.findChild(QtWidgets.QLineEdit, 'replaceby_line')

        # bottom
        self.select_button = self.findChild(QtWidgets.QPushButton, 'select_button')
        self.add_check = self.findChild(QtWidgets.QCheckBox, 'add_check')
        self.createset_button = self.findChild(QtWidgets.QPushButton, 'createset_button')
        self.refresh_button = self.findChild(QtWidgets.QPushButton, 'refresh_button')

    def ui_connections(self):
        self.resetdata_action.triggered.connect(self.reset_data)
        self.addset_button.clicked.connect(self.add_set)
        self.deleteset_button.clicked.connect(self.delete_sets)
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.plus_button.clicked.connect(self.add_members)
        self.replace_button.clicked.connect(self.replace_members)
        self.minus_button.clicked.connect(self.remove_members)
        self.replace_group.toggled.connect(self.refresh_replace)
        self.select_button.clicked.connect(self.select_members)
        self.createset_button.clicked.connect(self.create_scene_sets)
        self.refresh_button.clicked.connect(self.refresh_data)

    def reset_data(self):
        self.data.replace_data(empty_data)
        self.save_data()
        self.refresh_data()

    def refresh_list(self):
        self.list_view.model().layoutChanged.emit()

    def refresh_replace(self, state):
        """Refreshes the groupBox visibility when checked/unchecked"""
        self.replace_widget.setVisible(state)

    def add_set(self):
        name = self.setname_line.text()
        if name in self.data.current_sets:
            a = QtWidgets.QMessageBox.question(self, 'Set already existing',
                                               'The given name already exists in the sets list.\n'
                                               'Do you want to overwrite it ?')
            if str(a).split('.')[-1] == 'Yes':
                self.data.current_sets[name] = cmds.ls(os=True, fl=True)
        else:
            self.data.current_sets.append(name)
            self.data.current_members[name] = cmds.ls(os=True, fl=True)
        self.refresh_list()
        self.save_data()

    def delete_sets(self):
        indexes = [x.row() for x in self.list_view.selectedIndexes()]
        for index in sorted(indexes, reverse=True):
            del self.data.current_members[self.data.current_sets[index]]
            self.data.current_sets.pop(index)
        self.refresh_list()
        self.save_data()

    def move_up(self):
        indexes = self.list_view.selectedIndexes()
        if indexes:
            indexes.sort(key=lambda x: x.row())
            for index in indexes:
                if index.row() == 0:
                    continue
                item = self.data.current_sets.pop(index.row())
                self.data.current_sets.insert(index.row()-1, item)
            self.refresh_list()
            index = self.list_view.model().index(indexes[0].row()-1)
            if -1 < index.row() < len(self.data.current_sets):
                self.list_view.setCurrentIndex(index)
        else:
            cmds.warning("No set selected. Select one or more set  to move them up the list")

    def move_down(self):
        indexes = self.list_view.selectedIndexes()
        if indexes:
            indexes.sort(key=lambda x: x.row())
            for index in indexes[::-1]:
                if index.row() == len(self.data.current_sets)-1:
                    continue
                item = self.data.current_sets.pop(index.row())
                self.data.current_sets.insert(index.row()+1, item)
            self.refresh_list()
            index = self.list_view.model().index(indexes[0].row()+1)
            if -1 < index.row() < len(self.data.current_sets):
                self.list_view.setCurrentIndex(index)
        else:
            cmds.warning("No set selected. Select one or more set  to move them down the list")

    def select_members(self):
        add = self.add_check.isChecked()
        indexes = self.list_view.selectedIndexes()
        members = []
        for index in indexes:
            members += self.data.current_members[self.data.current_sets[index.row()]]

        existing = []
        replace = self.replace_group.isChecked()
        replace_text = self.replace_line.text()
        by_text = self.replaceby_line.text()
        for member in members:
            if replace:
                member = member.replace(replace_text, by_text)
            if cmds.objExists(member):
                existing.append(member)

        cmds.select(existing, add=add)
        missing = len(members) - len(existing)
        if missing:
            print("{} members are missing from the scene".format(missing))

    def save_data(self):
        self.data.save_data()

    def refresh_data(self):
        new = get_scene_data()
        self.data.replace_data(new)
        self.tab_widget.refresh_data()
        self.refresh_list()

    def create_scene_sets(self):
        sel = cmds.ls(sl=True, fl=True)
        cmds.select(clear=True)
        for index in self.list_view.selectedIndexes():
            setsel = self.data.current_sets[index.row()]
            members = self.data.current_members[setsel]
            existing = [x for x in members if cmds.objExists(x)]
            if existing:
                cmds.sets(*existing, name=setsel)
            else:
                cmds.warning("'{}' not created, no members found in current scene.".format(setsel))
        cmds.select(sel)

    def add_members(self):
        sel = cmds.ls(sl=True, fl=True)
        for index in self.list_view.selectedIndexes():
            setsel = self.data.current_sets[index.row()]
            members = self.data.current_members[setsel]
            for i in sel:
                if i not in members:
                    members.append(i)
        self.save_data()

    def remove_members(self):
        sel = cmds.ls(sl=True, fl=True)
        for index in self.list_view.selectedIndexes():
            setsel = self.data.current_sets[index.row()]
            members = self.data.current_members[setsel]
            for i in sel:
                if i in members:
                    members.remove(i)
        self.save_data()

    def replace_members(self):
        sel = cmds.ls(sl=True, fl=True)
        for index in self.list_view.selectedIndexes():
            setsel = self.data.current_sets[index.row()]
            self.data.current_members[setsel] = sel
        self.save_data()

    def move_to_tab(self, setsels, tab):
        for setsel in setsels:
            if setsel in self.data.data[tab]['sets']:
                cmds.warning("'{}' set already exists in '{}' tab".format(setsel, tab))
                continue
            self.data.data[tab]['sets'].append(setsel)
            self.data.data[tab]['members'][setsel] = self.data.current_members[setsel]
            self.data.current_sets.remove(setsel)
            del self.data.current_members[setsel]
        self.save_data()


class TabBarWidget(QtWidgets.QTabBar):
    def __init__(self, ui):
        super(TabBarWidget, self).__init__()
        self.setMovable(True)
        self.ui = ui
        self.data = ui.data
        self.refresh_data()
        self.data.current_tab_func = self.currentIndex
        self.currentChanged.connect(self.ui.refresh_list)
        self.tabMoved.connect(self.tab_moved)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(parent=self)
        menu.addAction('Add tab', self.add_tab)
        menu.addAction('Close tab', self.close_tab)
        menu.addAction('Rename tab', self.rename_tab)
        menu.exec_(event.globalPos())
        return menu

    def add_tab(self):
        name, do = QtWidgets.QInputDialog.getText(self, 'New tab', 'New tab name?')
        if not do or not name:
            return
        name = str(name)
        if name in self.data.tabs:
            QtWidgets.QMessageBox.warning(self, 'Tab name already existing',
                                          'The given name already exists in the tabs list.')
            return
        self.data.tabs.append(name)
        self.data.data[name] = {'sets': [], 'members': {}}
        self.refresh_data()
        self.ui.save_data()
        self.setCurrentIndex(self.count()-1)

    def close_tab(self):
        index = self.currentIndex()
        del self.data.data[self.data.tabs[index]]
        self.data.tabs.pop(index)
        self.removeTab(index)
        if not self.count():
            self.data.replace_data(empty_data)
            self.ui.save_data()
            self.ui.refresh_data()
        else:
            self.ui.save_data()

    def rename_tab(self):
        current_index = self.currentIndex()
        old_name = self.data.tabs[current_index]
        name, do = QtWidgets.QInputDialog.getText(self, 'Rename tab', 'New name?')
        if do and name:
            if name in self.data.tabs:
                QtWidgets.QMessageBox.warning(self, 'Tab name already existing',
                                              'The given name already exists in the tabs list.')
                return
            self.data.tabs[current_index] = name
            self.data.data[name] = self.data.data[old_name]
            del self.data.data[old_name]
            self.setTabText(current_index, name)
            self.ui.save_data()

    def tab_moved(self):
        self.data.tabs = [self.tabText(i) for i in range(self.count())]
        self.ui.save_data()

    def refresh_data(self):
        self.clear_tabs()
        for tab in self.data.tabs:
            self.addTab(tab)

    def clear_tabs(self):
        while self.count():
            self.removeTab(0)


class SetListView(QtWidgets.QListView):
    def __init__(self, ui, data):
        super(SetListView, self).__init__()
        self.data = data
        self.ui = ui
        self.setModel(ItemsListModel(ui, data))
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def contextMenuEvent(self, event):
        setsels = [self.data.current_sets[index.row()] for index in self.selectedIndexes()]
        if not setsels:
            return
        menu = QtWidgets.QMenu(parent=self)
        move_menu = menu.addMenu('Move to tab...')
        for tab in self.data.tabs:
            if tab != self.data.current_tab():
                move_menu.addAction(tab, partial(self.ui.move_to_tab, setsels, tab))
        menu.exec_(event.globalPos())


class ItemsListModel(QtCore.QAbstractListModel):
    def __init__(self, ui, data):
        super(ItemsListModel, self).__init__()
        self.sel_data = data
        self.ui = ui

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.sel_data.current_sets[index.row()]

    def rowCount(self, index):
        return len(self.sel_data.current_sets)

    def flags(self, index):
        return super(ItemsListModel, self).flags(index) | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole and value:
            if value in self.sel_data.current_sets:
                cmds.warning("'{}' set already exists in the list")
            row = index.row()
            old_name = self.sel_data.current_sets[row]
            self.sel_data.current_sets.pop(row)
            self.sel_data.current_sets.insert(row, value)
            self.sel_data.current_members[value] = self.sel_data.current_members[old_name]
            del self.sel_data.current_members[old_name]
            self.ui.save_data()
            return True
        return False


class SelData(object):
    def __init__(self, data):
        super(SelData, self).__init__()
        self.tabs = data['tabs']
        self.data = data['tabs_data']
        self.current_tab_func = None

    def __str__(self):
        return self.full_data()

    def full_data(self):
        return {'tabs': self.tabs, 'tabs_data': self.data}

    def replace_data(self, data):
        self.tabs = data['tabs']
        self.data = data['tabs_data']

    def current_tab(self):
        if self.current_tab_func:
            current_tab = self.current_tab_func()
            if current_tab > -1:
                return self.tabs[current_tab]

    @property
    def current_sets(self):
        current_tab = self.current_tab()
        if current_tab:
            return self.data[current_tab]['sets']
        return []

    @property
    def current_members(self):
        current_tab = self.current_tab()
        if current_tab:
            return self.data[current_tab]['members']

    def save_data(self):
        save_data(self.full_data())


def get_scene_data():
    file_path = get_file_path()
    if os.path.exists(file_path):
        with open(file_path, 'r') as data:
            return json.loads(data.read())
    return empty_data


def save_data(data):
    file_path = get_file_path()
    with open(file_path, 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))


def get_file_path():
    full_path = os.path.split(__file__)[0]
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    return '{}/rl_setselector_data.json'.format(full_path)


if __name__ == '__main__':
    launch_ui()
