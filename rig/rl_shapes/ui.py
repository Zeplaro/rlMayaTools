#!/usr/bin/env python

import os
import json
import maya.cmds as mc
import maya.OpenMayaUI as mui
from PySide2 import QtGui, QtCore, QtWidgets
import shiboken2 as QtCompat

__author__ = "Robin Lavigne"
__version__ = "0.1"
__email__ = "contact@robinlavigne.com"


def get_maya_version():
    version = mc.about(version=True)
    if '2016 Extension 2' in version or int(version[:5]) > 2016:
        return True
    return False


def launch_ui():
    if mc.window('shapes', exists=True):
        mc.deleteUI('shapes')
    ui = MainUI()
    ui.show()
    return ui


def get_maya_win():
    pointer = mui.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)


class MainUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_win()):
        super(MainUI, self).__init__(parent)
        self.setWindowTitle('rlShape Creator')
        self.setObjectName('shapes')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.shapes = load_shapes_library()
        self.shape_color = (255, 255, 0)

        self.setMinimumSize(350, 500)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs)
        self.main_tab = QtWidgets.QWidget()
        tabs.addTab(self.main_tab, 'Main')
        self.extra_tab = QtWidgets.QWidget()
        tabs.addTab(self.extra_tab, 'Extra')

        self.ui_layout()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.main_tab.setLayout(main_layout)
        shapes_group = QtWidgets.QGroupBox('Shapes')
        main_layout.addWidget(shapes_group)

        scroll_area = QtWidgets.QScrollArea()
        main_layout.addWidget(scroll_area)
        scroll_area.setWidgetResizable(True)

        shapes_container = QtWidgets.QWidget()
        scroll_area.setWidget(shapes_container)
        shapes_layout = QtWidgets.QGridLayout()
        shapes_container.setLayout(shapes_layout)

        row = 0
        collumn = 0
        for shape in self.shapes.keys():
            shape_button = QtWidgets.QToolButton()
            shape_button.setText(shape)
            shape_button.setStyleSheet('background-color: #55f')
            shape_button.setFixedSize(50, 50)
            shapes_layout.addWidget(shape_button, row, collumn)
            collumn += 1
            if collumn > 4:
                collumn = 0
                row += 1

        # Shape Options
        options_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(options_layout)
        # Replace checkbox
        self.replace_checkBox = QtWidgets.QCheckBox('Replace')
        self.replace_checkBox.setChecked(True)
        options_layout.addWidget(self.replace_checkBox)
        # Separator
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        options_layout.addWidget(sep)
        # Color Picker
        color_label = QtWidgets.QLabel('Color :')
        options_layout.addWidget(color_label)
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setStyleSheet('background-color: rgb{}'.format(self.shape_color))
        self.color_button.setFixedSize(40, 20)
        options_layout.addWidget(self.color_button)
        # Apply Color button
        self.apply_color_button = QtWidgets.QPushButton('Apply Color')
        options_layout.addWidget(self.apply_color_button)
        # Get color button
        self.get_color_button = QtWidgets.QPushButton('Get')
        self.get_color_button.setToolTip('Gets the color of the selected curve')
        options_layout.addWidget(self.get_color_button)

        # Size Layout
        size_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(size_layout)
        # Size Label
        size_label = QtWidgets.QLabel('Size :')
        size_layout.addWidget(size_label)
        # Size Value
        self.size_line_edit = QtWidgets.QLineEdit('2')
        self.size_line_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
        self.size_line_edit.setMaximumWidth(40)
        self.size_line_edit.setAlignment(QtCore.Qt.AlignCenter)
        size_layout.addWidget(self.size_line_edit)
        # Size Slider
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setValue(2)
        self.size_slider.setMaximum(10)
        self.size_slider.setMinimum(1)
        size_layout.addWidget(self.size_slider)

        if get_maya_version():
            # Width Layout
            width_layout = QtWidgets.QHBoxLayout()
            main_layout.addLayout(width_layout)
            # Width Label
            width_label = QtWidgets.QLabel('Width :')
            width_layout.addWidget(width_label)
            # Width Value
            self.width_lineEdit = QtWidgets.QLineEdit('1')
            self.width_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
            self.width_lineEdit.setMaximumWidth(40)
            self.width_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
            width_layout.addWidget(self.width_lineEdit)
            # Width Slider
            self.width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.width_slider.setValue(1)
            self.width_slider.setMaximum(10)
            self.width_slider.setMinimum(1)
            width_layout.addWidget(self.width_slider)
            # Width apply
            self.width_button = QtWidgets.QPushButton('Apply')
            self.width_button.setToolTip('Apply width on selected curves')
            self.width_button.setFixedWidth(40)
            width_layout.addWidget(self.width_button)

        # Axis Twist layout
        axis_layout = QtWidgets.QHBoxLayout()
        # axis_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addLayout(axis_layout)
        # Axis Label
        axis_label = QtWidgets.QLabel('Axis :')
        axis_label.setFixedWidth(35)
        axis_layout.addWidget(axis_label)
        # radio Buttons
        self.axis_button_group = QtWidgets.QButtonGroup()
        for xyz in 'xyz':
            radio_button = QtWidgets.QRadioButton(xyz)
            radio_button.setFixedWidth(35)
            if xyz == 'y':
                radio_button.setChecked(True)
            axis_layout.addWidget(radio_button)
            self.axis_button_group.addButton(radio_button)
        # reverse checkbox
        self.reverse_checkBox = QtWidgets.QCheckBox('Reverse')
        self.reverse_checkBox.setFixedWidth(65)
        axis_layout.addWidget(self.reverse_checkBox)
        # Separator
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        axis_layout.addWidget(sep)
        # TwistLabel
        twist_label = QtWidgets.QLabel('Twist')
        twist_label.setFixedWidth(30)
        axis_layout.addWidget(twist_label)
        # Twist Value
        self.twist_lineEdit = QtWidgets.QLineEdit('0')
        self.twist_lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('-?[\d]{1,3}[.][\d]{0,3}')))
        self.twist_lineEdit.setMaximumWidth(40)
        self.twist_lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        axis_layout.addWidget(self.twist_lineEdit)

        # Separator line
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        main_layout.addWidget(sep)

        # Mirror Layout
        mirror_layout = QtWidgets.QHBoxLayout()
        # mirror_layout.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addLayout(mirror_layout)
        # Mirror Label
        mirror_label = QtWidgets.QLabel('Mirror :')
        mirror_layout.addWidget(mirror_label)
        # Mirror button
        for xyz in 'XYZ':
            self.mirror_button = QtWidgets.QPushButton(xyz)
            # self.mirror_button.setObjectName('mirrorButton{}'.format(xyz))
            self.mirror_button.setFixedSize(25, 20)
            mirror_layout.addWidget(self.mirror_button)
        # Separator line
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.VLine)
        mirror_layout.addWidget(sep)
        # Mirror Space
        self.space_checkBox = QtWidgets.QCheckBox('Object space')
        self.space_checkBox.setObjectName('objectSpace')
        self.space_checkBox.setChecked(True)
        self.space_checkBox.setFixedWidth(100)
        mirror_layout.addWidget(self.space_checkBox)

        # Separator line
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        main_layout.addWidget(sep)

        # Parent shape button
        self.parent_button = QtWidgets.QPushButton('Parent Shapes')
        main_layout.addWidget(self.parent_button)


def load_shapes_library(custom=False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if custom:
        library_path = os.path.join(dir_path, 'shapes_library_custom.json')
    else:
        library_path = os.path.join(dir_path, 'shapes_library.json')
    try:
        with open(library_path, 'r') as library:
            data = json.load(library)
    except FileNotFoundError:
        data = {}
    return data


def save_shapes_library(data, custom=False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if custom:
        library_path = os.path.join(dir_path, 'shapes_library_custom.json')
    else:
        library_path = os.path.join(dir_path, 'shapes_library.json')
    try:
        with open(library_path, 'w') as library:
            json.dump(library, data)
    except FileNotFoundError:
        pass
