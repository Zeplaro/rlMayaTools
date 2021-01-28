# encoding: utf8

import maya.cmds as mc
import maya.OpenMayaUI as mui
import maya.mel as mel
from functools import partial
from collections import OrderedDict
from Qt import QtGui, QtCore, QtWidgets, QtCompat
from PyQt5 import QtGui, QtCore, QtWidgets, QtCompat


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
        self.setMinimumSize(900, 600)
        self.ui_layout()
        self.ui_connections()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        loadObj_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(loadObj_layout)
        self.loadObj_button = QtWidgets.QPushButton('Load Mesh')
        main_layout.addWidget(self.loadObj_button)

        skincluster_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(skincluster_layout)



    def ui_connections(self):
        pass


def get_sel():
    obj = mc.ls(sl=True)
    if obj:
        return obj[0]


def get_skincluster(obj):
    skn = [x for x in mc.listHistory(obj) if 'skinCluster' in mc.nodeType(x, i=True)]
    if skn:
        return SkinCluster(skn[0])


class SkinCluster(object):
    def __init__(self, node):
        self.name = node

    @property
    def influences(self):
        return mc.skinCluster(self.name, q=True, influence=True)
