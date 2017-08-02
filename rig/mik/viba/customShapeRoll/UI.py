#!/usr/bin/env python
# coding:utf-8
""":mod:`UI`
===================================

.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.11

"""

from PySide import QtGui
from PySide import QtCore
import maya.OpenMayaUI as omui
import shiboken
import shapeFromGeo
import create_vector_on_curve
import guide_creation


#####################################
# MAIN OBJECT
#####################################


class CustomShapeRollUi(QtGui.QDialog):
    def __init__(self, parent=None):
        super(CustomShapeRollUi, self).__init__(parent)

        self.setWindowTitle("Custom Shape Roll")

        self.setObjectName("CustomShapeRoll")

        self.resize(500, 200)

        self.create_layout()

        self.create_connections()

    def create_layout(self):
        self.customCurve_button = QtGui.QPushButton("Edges Selection ==> Custom Shape")
        self.edge_sel = QtGui.QLabel('edges selection')
        self.curve_name = QtGui.QLineEdit('curve_name')

        custom_shape_layout = QtGui.QHBoxLayout()
        custom_shape_layout.addWidget(self.edge_sel)
        custom_shape_layout.addWidget(self.customCurve_button)
        custom_shape_layout.addWidget(self.curve_name)

        self.root_button = QtGui.QPushButton('Create root controller')
        self.root_line_edit = QtGui.QLineEdit()

        root_layout = QtGui.QHBoxLayout()
        root_layout.addWidget(self.root_button)
        root_layout.addWidget(self.root_line_edit)

        self.guide_button = QtGui.QPushButton('Create guide')
        self.guide_line_edit = QtGui.QLineEdit()
        self.bind_label = QtGui.QLabel('Parent bind joint')
        self.bind_check = QtGui.QCheckBox()
        self.bind_line_edit = QtGui.QLineEdit('Joint name')
        self.radius_label = QtGui.QLabel('Radius')
        self.radius_line_edit = QtGui.QLineEdit('1')

        guide_layout = QtGui.QHBoxLayout()
        guide_layout.addWidget(self.guide_button)
        guide_layout.addWidget(self.guide_line_edit)
        guide_layout.addWidget(self.bind_label)
        guide_layout.addWidget(self.bind_check)
        guide_layout.addWidget(self.bind_line_edit)
        guide_layout.addWidget(self.radius_label)
        guide_layout.addWidget(self.radius_line_edit)

        self.build_button = QtGui.QPushButton("Build custom shape Roll !")

        build_layout = QtGui.QHBoxLayout()
        build_layout.addWidget(self.build_button)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(custom_shape_layout)
        main_layout.addLayout(root_layout)
        main_layout.addLayout(guide_layout)
        main_layout.addLayout(build_layout)

        self.setLayout(main_layout)

    def create_connections(self):
        self.connect(self.customCurve_button, QtCore.SIGNAL('clicked()'), self.edges_to_curve)
        self.connect(self.radius_line_edit, QtCore.SIGNAL('returnPressed()'), self.radius_test)
        self.connect(self.build_button, QtCore.SIGNAL('clicked()'), self.build_shape_roll)
        self.connect(self.root_button, QtCore.SIGNAL('clicked()'), self.create_root)
        self.connect(self.guide_button, QtCore.SIGNAL('clicked()'), self.create_guide)

    def create_root(self):
        guide_creation.create_guide_type(root=True, name=self.root_line_edit.text() + '_rootController01')
        self.root_line_edit.setText(self.root_line_edit.text() + '_rootController01')

    def create_guide(self):
        guide_creation.create_guide_type(locator=True, name=self.guide_line_edit.text() + '_vectorGuide01')
        self.guide_line_edit.setText(self.guide_line_edit.text() + '_vectorGuide01')

    def edges_to_curve(self):
        sel = shapeFromGeo.get_selection()
        shapeFromGeo.build_shape(sel, self.curve_name.text())
        self.edge_sel.setText(sel[0])
        self.edges_sel = sel
        print
        '###New custom shape created###'

    def radius_test(self):
        shapeFromGeo.create_circle_test(self.radius_line_edit.text(), self.guide_line_edit.text())

    def build_shape_roll(self):
        shapeFromGeo.delete_circle_test()
        create_vector_on_curve.vector_on_curve(self.curve_name.text(),
                                               self.curve_name.text(),
                                               self.root_line_edit.text(),
                                               self.guide_line_edit.text(),
                                               self.bind_line_edit.text(),
                                               float(self.radius_line_edit.text()),
                                               self.bind_check.isChecked())


#####################################
# LAUNCH UI
#####################################

def showUI():
    main = omui.MQtUtil.mainWindow()
    main = shiboken.wrapInstance(long(main), QtGui.QDialog)
    ui = main.findChild(CustomShapeRollUi, "CustomShapeRoll")
    if ui:
        print
        "delete"
        ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        ui.close()

    ui = CustomShapeRollUi(main)
    ui.show()