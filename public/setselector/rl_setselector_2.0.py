# coding: utf-8

"""
Selection manager tool for maya. Stores multiple selection data in different tab for easy selection modification and
recovery.
This is version 2.0 :
Wrote with Python 3.4
Each tab now has its own file which prevents having to load and save all the data from all the tabs at every
modification of the data.

For it to work you need to have Marcus Ottosson's Qt.py installed.
You can find it here https://github.com/mottosso/Qt.py

To launch run :

from setselector import setselector_2.0
setselector_2.0.launch_ui()

"""

__author__ = "Robin Lavigne"
__version__ = "2.0"
__email__ = "contact@robinlavigne.com"

import os
import json
from pathlib import Path
from functools import partial
from pprint import pprint
import maya.OpenMayaUI as omui
from maya import cmds

from Qt import QtGui, QtCore, QtWidgets, QtCompat

BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / 'setselector_data'
TABS_FILE_PATH = DATA_PATH / 'tabs.setsel'


def get_maya_window():
    """Getting maya's window"""
    ptr = omui.MQtUtil.mainWindow()
    parent = QtCompat.wrapInstance(int(ptr), QtWidgets.QMainWindow)
    return parent


def close_existing(target_title):
    parent = get_maya_window()
    children = parent.children()
    for child in children:
        try:
            title = child.windowTitle()
        except AttributeError:
            title = ''
        if title == target_title:
            try:
                child.close()
            except ValueError:
                print(f"failed to close '{target_title}'")


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
    ui_title = 'rl Set Selector V2'
    close_existing(ui_title)
    ui = MainUI(parent=get_maya_window(), title=ui_title)
    ui.show()
    center_ui(ui.window())
    return ui


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None, title='rl Set Selector'):
        super(MainUI, self).__init__(parent=parent)
        QtCompat.loadUi(str(BASE_PATH / "setselector_v2.ui"), self)  # Loading the .ui file
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        self.data = SelData()

        # UI LAYOUT
        # top
        self.clearalldata_action = self.findChild(QtWidgets.QAction, 'clearalldata_action')
        self.setname_line = self.findChild(QtWidgets.QLineEdit, 'setname_line')
        self.setname_line.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r'([a-zA-Z]|_){1}(\w|_|0-9| )+')))
        self.addset_button = self.findChild(QtWidgets.QPushButton, 'addset_button')

        # move
        self.up_button = self.findChild(QtWidgets.QToolButton, 'up_button')
        self.down_button = self.findChild(QtWidgets.QToolButton, 'down_button')

        # tabs
        tabs_layout = self.findChild(QtWidgets.QVBoxLayout, 'tabs_layout')
        self.tab_widget = TabBarWidget(self)
        tabs_layout.addWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("QTabBar { background-color: #373737 }")
        # list
        self.list_view = SetListView(self.data)
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
        self.remove_check = self.findChild(QtWidgets.QCheckBox, 'remove_check')
        self.createset_button = self.findChild(QtWidgets.QPushButton, 'createset_button')
        self.refresh_button = self.findChild(QtWidgets.QPushButton, 'refresh_button')

        self.ui_connections()

    def ui_connections(self):
        self.clearalldata_action.triggered.connect(self.clear_all_data)
        self.addset_button.clicked.connect(self.add_set)
        self.up_button.clicked.connect(self.list_view.move_up)
        self.down_button.clicked.connect(self.list_view.move_down)
        self.plus_button.clicked.connect(self.add_members)
        self.replace_button.clicked.connect(self.replace_members)
        self.minus_button.clicked.connect(self.remove_members)
        self.replace_group.toggled.connect(self.refresh_replace)
        self.select_button.clicked.connect(self.select_members)
        self.add_check.stateChanged.connect(partial(self.add_remove_toggle, self.add_check))
        self.remove_check.stateChanged.connect(partial(self.add_remove_toggle, self.remove_check))
        self.createset_button.clicked.connect(self.create_scene_sets)
        self.refresh_button.clicked.connect(self.reload_data)

    def add_remove_toggle(self, button, state):
        if state:
            if button is self.add_check:
                self.remove_check.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                self.add_check.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def clear_all_data(self):
        answer = QtWidgets.QMessageBox.question(self, 'Clear all Data',
                                                'This action will clear all set data files.\n'
                                                'Are you sure you want to continue ?')
        if answer == QtWidgets.QMessageBox.StandardButton.Yes:
            clear_all_data()
            self.data.reset()

    def refresh_replace(self, state):
        """Refreshes the groupBox visibility when checked/unchecked"""
        self.replace_widget.setVisible(state)

    def add_set(self):
        name = self.setname_line.text()
        if not name:
            cmds.error('Set name cannot be empty', noContext=True)
            return
        if name in self.data.sets:
            answer = QtWidgets.QMessageBox.question(self, 'Set already existing',
                                                    'The given name already exists in the sets list.\n'
                                                    'Do you want to overwrite it ?')
            if answer != QtWidgets.QMessageBox.StandardButton.Yes:
                return
        self.data.add_set(name, get_selected())
        self.list_view.refresh()

    def select_members(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        add = self.add_check.isChecked()
        indexes = self.list_view.selectedIndexes()
        members = []
        for index in indexes:
            members += self.data.members[self.data.sets[index.row()]]

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
            print(f"{missing} members are missing from the scene")
        QtWidgets.QApplication.restoreOverrideCursor()

    def reload_data(self):
        self.data.reload_data()
        self.tab_widget.refresh_tabs()
        self.list_view.refresh()

    def create_scene_sets(self):
        sel = get_selected()
        cmds.select(clear=True)
        for index in self.list_view.selectedIndexes():
            setsel = self.data.sets[index.row()]
            members = self.data.members[setsel]
            existing = [x for x in members if cmds.objExists(x)]
            if existing:
                cmds.sets(*existing, name=setsel)
            else:
                cmds.warning(f"'{setsel}' not created, no members found in current scene.")
        cmds.select(sel)

    def add_members(self):
        selected = get_selected()
        indexes = [x.row() for x in self.list_view.selectedIndexes()]
        self.data.add_members(indexes, selected)

    def remove_members(self):
        selected = get_selected()
        indexes = [x.row() for x in self.list_view.selectedIndexes()]
        self.data.remove_members(indexes, selected)

    def replace_members(self):
        selected = get_selected()
        indexes = [x.row() for x in self.list_view.selectedIndexes()]
        self.data.replace_members(indexes, selected)


class TabBarWidget(QtWidgets.QTabBar):
    def __init__(self, ui):
        super(TabBarWidget, self).__init__()
        self.setMovable(True)
        self.ui = ui
        self.data = ui.data

        self.refresh_tabs()

        self.currentChanged.connect(self.tab_changed)
        self.tabMoved.connect(self.tab_moved)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(parent=self)
        menu.addAction('Add tab', self.add_tab)
        menu.addAction('Close tab', self.close_tab)
        menu.addAction('Rename tab', self.rename_tab)
        menu.exec_(event.globalPos())
        return menu

    def tab_changed(self, index):
        self.data.change_tab(index)
        self.ui.list_view.refresh()

    def refresh_tabs(self):
        current_tab = self.currentIndex()
        self.clear_tabs()
        for tab in self.data.tabs:
            self.addTab(tab)
        self.setCurrentIndex(current_tab)

    def add_tab(self):
        tab_name, do = QtWidgets.QInputDialog.getText(self, 'New tab', 'New tab name?')
        if not do or not tab_name:
            return
        tab_name = tab_name
        if tab_name in self.data.tabs:
            QtWidgets.QMessageBox.warning(self, 'Tab name already existing',
                                          'The given name already exists in the tabs list.')
            return
        self.data.add_tab(tab_name)
        self.addTab(tab_name)
        self.setCurrentIndex(self.count() - 1)

    def close_tab(self):
        index = self.currentIndex()
        answer = QtWidgets.QMessageBox.question(self, f'Closing {self.tabText(index)}',
                                                'Closing this tab will delete all of its data.\n'
                                                'Are you sure you want to continue ?')
        if answer != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        self.removeTab(index)
        self.data.remove_tab(index)
        if not self.count():
            self.data.reset()
        self.refresh_tabs()

    def rename_tab(self):
        current_index = self.currentIndex()
        old_name = self.tabText(current_index)
        new_name, do = QtWidgets.QInputDialog.getText(self, 'Rename tab', 'New name?', text=old_name)
        if not do or not new_name:
            return
        if new_name in self.data.tabs:
            QtWidgets.QMessageBox.warning(self, 'Tab name already existing',
                                          'The given name already exists in the tabs list.')
            return

        self.setTabText(current_index, new_name)
        self.data.rename_tab(new_name)

    def tab_moved(self, index):
        self.data.change_tabs_order([self.tabText(i) for i in range(self.count())])

    def clear_tabs(self):
        while self.count():
            self.removeTab(0)


class SetListView(QtWidgets.QListView):
    def __init__(self, data):
        super(SetListView, self).__init__()
        self.data = data
        self.setModel(ItemsListModel(data))
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def contextMenuEvent(self, event):
        selected_indexes = [index.row() for index in self.selectedIndexes()]
        if not selected_indexes:
            return
        menu = QtWidgets.QMenu(parent=self)

        # Move to tab menu
        move_menu = menu.addMenu('Move to tab...')
        for tab in self.data.tabs:
            if tab != self.data.tab:
                move_menu.addAction(tab, partial(self.data.move_sets_to_tab, selected_indexes, tab))

        # Print members action
        menu.addAction('Print members', self.print_elements)

        # Delete set action
        menu.addAction('Delete', self.delete_sets)

        menu.exec_(event.globalPos())

    def refresh(self):
        self.model().layoutChanged.emit()

    def print_elements(self):
        indexes = self.selectedIndexes()
        members = {}
        for index in indexes:
            sel_set = self.data.sets[index.row()]
            members[sel_set] = self.data.members[sel_set]
        pprint(members)

    def delete_sets(self):
        indexes = [x.row() for x in self.selectedIndexes()]
        self.data.delete_sets(indexes)
        self.refresh()

    def move_up(self):
        indexes = [x.row() for x in self.selectedIndexes()]
        self.data.move_sets_up(indexes)
        self.refresh()
        indexes = [x-1 for x in indexes]
        self.selectIndexes(indexes)

    def move_down(self):
        indexes = [x.row() for x in self.selectedIndexes()]
        self.data.move_sets_down(indexes)
        self.refresh()
        indexes = [x+1 for x in indexes]
        self.selectIndexes(indexes)

    def selectIndexes(self, indexes):
        self.selectionModel().clearSelection()
        model = self.model()
        for index in indexes:
            model_index = model.index(index)
            item_selection = QtCore.QItemSelection(model_index, model_index)
            self.selectionModel().select(item_selection, QtCore.QItemSelectionModel.Select)


class ItemsListModel(QtCore.QAbstractListModel):
    def __init__(self, data):
        super(ItemsListModel, self).__init__()
        self.sel_data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.sel_data.sets[index.row()]

    def rowCount(self, index):
        return len(self.sel_data.sets)

    def flags(self, index):
        return super(ItemsListModel, self).flags(index) | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if index.isValid() and role == QtCore.Qt.EditRole and value:
            if value in self.sel_data.sets:
                cmds.warning(f"'{value}' set already exists in the list")
                return False
            row = index.row()
            self.sel_data.rename_set(row, value)
            return True
        return False


class SelData:
    DEFAULT_TAB_NAME = 'Main'
    SETS_KEY = 'sets'
    MEMBERS_KEY = 'members'
    EMPTY_DATA = {SETS_KEY: [], MEMBERS_KEY: {}}

    def __init__(self):
        self.reset()

    def reset(self):
        sync_tabs_and_files()
        self.tabs = get_tabs_list() or [self.DEFAULT_TAB_NAME]
        self.tab = self.tabs[0]
        self.sets = []
        self.members = {}
        self.reload_data()

    # DATA stuff
    def get_data(self):
        return {self.SETS_KEY: self.sets, self.MEMBERS_KEY: self.members}

    def set_data(self, data):
        self.sets = data[self.SETS_KEY]
        self.members = data[self.MEMBERS_KEY]

    def save_data(self):
        save_tab_data(self.tab, self.get_data())
        save_tabs_file(self.tabs)

    def reload_data(self):
        sync_tabs_and_files()
        self.tabs = get_tabs_list()
        self.set_data(get_tab_data(self.tab) or self.EMPTY_DATA)
        self.save_data()

    # TAB Stuff
    def change_tab(self, index):
        tab = self.tabs[index]
        if not self.tab == tab:
            self.tab = tab
            self.set_data(get_tab_data(tab) or self.EMPTY_DATA)

    def change_tabs_order(self, new_order):
        self.tabs = new_order
        save_tabs_file(self.tabs)

    def add_tab(self, tab):
        self.tabs.append(tab)
        save_tab_data(tab, self.EMPTY_DATA)
        save_tabs_file(self.tabs)

    def remove_tab(self, index):
        tab = self.tabs.pop(index)
        delete_tab_file(tab)
        save_tabs_file(self.tabs)
        if not self.tabs:
            self.add_tab(self.DEFAULT_TAB_NAME)

    def rename_tab(self, name):
        old_name = self.tab
        index = self.tabs.index(old_name)
        self.tab = name
        self.tabs[index] = name
        rename_tab_file(self.tabs[index], name)
        save_tabs_file(self.tabs)

    # Set Stuff
    def add_set(self, name, members):
        self.sets.append(name)
        self.members[name] = members
        self.save_data()

    def add_members(self, indexes, members):
        sets = [self.sets[index] for index in indexes]
        for sel_set in sets:
            self.members[sel_set] = list(set(self.members[sel_set] + members))
        self.save_data()

    def remove_members(self, indexes, members):
        sets = [self.sets[index] for index in indexes]
        for sel_set in sets:
            # recreating the members list with a new list is faster than using list.remove()
            self.members[sel_set] = [member for member in self.members[sel_set] if member not in members]
        self.save_data()

    def replace_members(self, indexes, members):
        sets = [self.sets[index] for index in indexes]
        for sel_set in sets:
            self.members[sel_set] = members
        self.save_data()

    def move_sets_to_tab(self, indexes, tab):
        sets = [self.sets[index] for index in sorted(indexes)]
        tab_data = get_tab_data(tab) or self.EMPTY_DATA
        for sel_set in sets:
            if sel_set in tab_data[self.SETS_KEY]:
                cmds.warning(f"'{sel_set}' set already exists in '{tab}' tab")
                continue
            tab_data[self.SETS_KEY].append(sel_set)
            tab_data[self.MEMBERS_KEY][sel_set] = self.members[sel_set]
            self.sets.remove(sel_set)
            del self.members[sel_set]
        save_tab_data(tab, tab_data)
        self.save_data()

    def delete_sets(self, indexes):
        for index in indexes:
            sel_set = self.sets.pop(index)
            del self.members[sel_set]
        self.save_data()

    def rename_set(self, index, new_name):
        old_name = self.sets[index]
        self.sets[index] = new_name
        self.members[new_name] = self.members[old_name]
        del self.members[old_name]
        self.save_data()

    def move_sets_up(self, indexes):
        indexes = sorted(indexes)
        for index in indexes:
            if index == 0:
                continue
            sel_set = self.sets.pop(index)
            self.sets.insert(index-1, sel_set)
        self.save_data()

    def move_sets_down(self, indexes):
        indexes = sorted(indexes, reverse=True)
        for index in indexes:
            if index == len(self.sets):
                continue
            sel_set = self.sets.pop(index)
            self.sets.insert(index+1, sel_set)
        self.save_data()


def get_tabs_list() -> [str, ...]:
    """
    Returns the list of tabs from the tabs file.
    Returns an empty list if the tabs file does not exist.
    """
    if os.path.exists(TABS_FILE_PATH):
        with open(TABS_FILE_PATH, 'r') as f:
            return json.loads(f.read())
    return []


def save_tabs_file(data: [str, ...]) -> None:
    """Saves the given tabs list to the tabs file."""
    with open(TABS_FILE_PATH, 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))


def get_tab_data(tab: str) -> {}:
    """
    Returns the data from the file corresponding to the given tab.
    An empty dict is returned if the corresponding file does not exist.
    """
    file_path = get_file_path(tab)
    if os.path.exists(file_path):
        with open(file_path, 'r') as data:
            return json.loads(data.read())
    return {}


def save_tab_data(tab: str, data: {}) -> None:
    """Saves the given data to the file corresponding to the given tab."""
    file_path = get_file_path(tab)
    with open(file_path, 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))


def get_file_path(tab: str) -> Path:
    """
    Returns a Path to the file corresponding to the given tab.
    Creates the DATA_PATH folder if it does not already exist.
    """
    if not os.path.exists(DATA_PATH):
        DATA_PATH.mkdir()
    return DATA_PATH / f'{tab}.json'


def get_tab_files() -> [Path, ...]:
    """Returns a list of Path for each json file in the DATA_PATH."""
    files = [f for f in DATA_PATH.iterdir() if f.is_file() and f.suffix == '.json']
    return files


def sync_tabs_and_files() -> None:
    """
    Makes sure each .json files are listed in the tabs file and adds them if missing, then removes any tab from the tabs
    file if no corresponding .json file exist.
    Saves the new list of tabs in the tabs file.
    """
    # Adding tabs to tabs_list if they have a file but are not yet in the tabs_list
    tabs = get_tabs_list()
    for tab in get_tab_files():
        if tab.stem not in tabs:
            tabs.append(tab.stem)
    # Removing tabs from tabs_list if no corresponding file exist
    tab_names = [x.stem for x in get_tab_files()]
    for tab in tabs[:]:
        if tab not in tab_names:
            tabs.remove(tab)
    # Saving updated tabs_list
    save_tabs_file(tabs)


def clear_all_data() -> None:
    """Deletes all json tab files and the tabs file."""
    for tab_file in DATA_PATH.iterdir():
        if tab_file.is_file() and tab_file.suffix == '.json':
            tab_file.unlink()
    if TABS_FILE_PATH.exists():
        TABS_FILE_PATH.unlink()


def delete_tab_file(tab: str) -> None:
    """Deletes the file corresponding to the given tab."""
    tab_file = DATA_PATH / (tab+'.json')
    if tab_file.exists():
        tab_file.unlink()


def rename_tab_file(tab: str, name: str) -> None:
    """Renames the file corresponding to the given tab with the given name"""
    tab_file = DATA_PATH / (tab+'.json')
    if tab_file.exists():
        new_path = tab_file.with_name(name+'.json')  # replace with tab_file.with_stem when in python 3.9
        tab_file.rename(new_path)


def get_selected() -> [str, ...]:
    """Gets the current scene selection."""
    return cmds.ls(sl=True, fl=True)
