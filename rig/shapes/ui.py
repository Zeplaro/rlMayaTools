# encoding: utf8

import os
import json
from pathlib import Path
from functools import partial
from importlib import reload

import maya.OpenMayaUI as omui
from maya import cmds

from Qt import QtGui, QtCore, QtWidgets, QtCompat

from shapes import shapes
reload(shapes)


TITLE = "rl Shapes"
BASE_PATH = Path(__file__).parent


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
            title = ""
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
    close_existing(TITLE)
    ui = MainUI(parent=get_maya_window(), title=TITLE)
    ui.show()
    center_ui(ui.window())
    return ui


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None, title=TITLE):
        super().__init__(parent=parent)
        # Loading the .ui file
        self.ui = QtCompat.loadUi(str(BASE_PATH / "shapes.ui"), self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)

        # UI LAYOUT

        self.ui_connections()

    def ui_connections(self):
        for index in range(32):
            button = getattr(self, f"color{index}Button")
            button.clicked.connect(partial(shapes.indexColor, index, True))
        self.copyShapeButton.clicked.connect(self.copy)
        self.mirrorOtherSideButton.clicked.connect(shapes.Mirror.mirror_selected)

    def copy(self):
        shapes.copyShapes(self.copyShapeWorldRadioButton.isChecked())