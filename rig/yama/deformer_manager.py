# encoding: utf8

import deformer.skinCluster as skn
import maya.cmds as mc
import maya.OpenMayaUI as mui
from Qt import QtGui, QtCore, QtWidgets, QtCompat
try:
    from PyQt5 import QtGui, QtCore, QtWidgets, QtCompat
except:
    pass


def launch_ui():
    if mc.window('deformermanager', exists=True):
        mc.deleteUI('deformermanager')
    ui = MainUi()
    ui.show()
    return ui


def get_maya_win():
    pointer = mui.MQtUtil.mainWindow()
    return QtCompat.wrapInstance(int(pointer), QtWidgets.QWidget)


class MainUi(QtWidgets.QDialog, object):
    def __init__(self, parent=get_maya_win()):
        super(MainUi, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle('Deformer Manager')
        self.setObjectName('deformermanager')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(400, 600)
        self.mesh = None
        self.ui_layout()
        self.ui_connections()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        loadObj_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(loadObj_layout)
        self.loadObj_button = QtWidgets.QPushButton('Load Mesh')
        loadObj_layout.addWidget(self.loadObj_button)
        self.mesh_label = QtWidgets.QLabel('')
        loadObj_layout.addWidget(self.mesh_label)

        self.tabs = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tabs)

        # SkinCluster
        skinClusterContainer_widget = QtWidgets.QWidget()
        self.tabs.addTab(skinClusterContainer_widget, 'SkinCluster')

        skinCluster_layout = QtWidgets.QVBoxLayout()
        skinClusterContainer_widget.setLayout(skinCluster_layout)

        self.skn_label = QtWidgets.QLabel('SkinCluster : ')
        skinCluster_layout.addWidget(self.skn_label)

    def ui_connections(self):
        self.loadObj_button.clicked.connect(self.load_mesh)

    def load_mesh(self):
        mesh = get_sel()
        self.mesh_label.setText(mesh)
        self.mesh = mesh
        if mesh:
            skinCluster = skn.get_skinCluster(mesh)
            if skinCluster:
                self.skn_label.setText('SkinCluster : {}'.format(skinCluster))


def get_sel():
     obj = mc.ls(sl=True)
     if obj:
         return obj[0]
