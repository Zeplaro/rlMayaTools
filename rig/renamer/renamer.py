# coding: utf-8

import os
import maya.OpenMayaUI as omui
try:
    from Qt import QtGui, QtCore, QtWidgets, QtCompat, uic
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets, QtUiTools
    import shiboken2 as QtCompat

from yama import nodes


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    parent = QtCompat.wrapInstance(long(ptr), QtWidgets.QMainWindow)
    return parent


def close_existing(target_title):
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
    ui_title = 'Renamer'
    close_existing(ui_title)
    ui = MainUI(parent=get_maya_window(), title=ui_title)
    ui.window.show()
    return ui


def loadUiWidget(uifilename, parent=None):
    """Properly Loads and returns UI files - by BarryPye on stackOverflow"""
    loader = QtUiTools.QUiLoader()
    uifile = QtCore.QFile(uifilename)
    uifile.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uifile, parent)
    uifile.close()
    return ui


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, title, parent=None):
        super(MainUI, self).__init__(parent)
        # main window load / settings
        self.window = loadUiWidget(os.path.split(__file__)[0] + "/renamer.ui", parent)
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.window.setWindowTitle(title)

        self.central_widget = self.window.findChild(QtWidgets.QWidget, 'centralwidget')
        self.main_layout = self.central_widget.layout()

        self.model = NameModel(self)

        self.name_view = QtWidgets.QTableView()
        self.name_view.setModel(self.model)
        self.main_layout.insertWidget(1, self.name_view)

        self.replace_line = self.window.findChild(QtWidgets.QLineEdit, 'replace_line')
        self.replacewith_line = self.window.findChild(QtWidgets.QLineEdit, 'replacewith_line')
        self.first_spin = self.window.findChild(QtWidgets.QSpinBox, 'first_spin')
        self.last_spin = self.window.findChild(QtWidgets.QSpinBox, 'last_spin')
        self.from_spin = self.window.findChild(QtWidgets.QSpinBox, 'from_spin')
        self.to_spin = self.window.findChild(QtWidgets.QSpinBox, 'to_spin')

        self.ui_connections()

        self.reload_selection()

    def ui_connections(self):
        self.reload_button = self.window.findChild(QtWidgets.QPushButton, 'reload_button')
        self.reload_button.clicked.connect(self.reload_selection)
        self.replace_line.textChanged.connect(self.refresh_newnames)
        self.replacewith_line.textChanged.connect(self.refresh_newnames)
        self.first_spin.valueChanged.connect(self.refresh_newnames)
        self.last_spin.valueChanged.connect(self.refresh_newnames)
        self.from_spin.valueChanged.connect(self.fromspin_changed)
        self.to_spin.valueChanged.connect(self.tospin_changed)

    def reload_selection(self):
        self.model.maya_objects = nodes.selected()
        self.refresh_newnames()

    def refresh_newnames(self):
        self.model.layoutChanged.emit()

    def get_new_name(self, name):
        old = name[:]
        name = self.replace(name)
        name = self.remove(name)
        name = self.add(name)
        name = self.numbering(name)
        return name

    def replace(self, name):
        name = name.replace(self.replace_line.text(), self.replacewith_line.text())
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
        # name = self.
        return name

    def numbering(self, name):
        return name

    def fromspin_changed(self):
        from_value = self.from_spin.value()
        to_value = self.to_spin.value()
        if to_value < from_value:
            self.to_spin.setValue(from_value)
        self.refresh_newnames()

    def tospin_changed(self):
        from_value = self.from_spin.value()
        to_value = self.to_spin.value()
        if from_value > to_value:
            self.from_spin.setValue(to_value)
        self.refresh_newnames()


class NameModel(QtCore.QAbstractTableModel):
    def __init__(self, main_ui):
        super(NameModel, self).__init__()
        self.main_ui = main_ui
        self.maya_objects = []

    def rowCount(self, index):
        return len(self.maya_objects)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            name = self.maya_objects[index.row()].name
            if index.column() == 0:
                return name
            else:
                return self.main_ui.get_new_name(name)

    def headerData(self, column, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if column == 0:
                    return "Current name"
                else:
                    return "New name"
