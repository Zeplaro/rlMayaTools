# encoding: utf8

import maya.cmds as mc
import maya.OpenMayaUI as mui
import maya.mel as mel
from functools import partial
from collections import OrderedDict
from Qt import QtGui, QtCore, QtWidgets, QtCompat


def launch_ui():
    if mc.window('compedit', exists=True):
        mc.deleteUI('compedit')
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

        self.setWindowTitle('Component Editor')
        self.setObjectName('compedit')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumSize(900, 600)
        self.obj = get_sel()
        print(self.obj)
        self.skn = None
        if self.obj:
            self.skn = get_skincluster(self.obj)
            print(self.skn)
        self.ui_layout()
        self.ui_connections()

    def ui_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        table_view = QtWidgets.QTableWidget()
        main_layout.addWidget(table_view)
        infs = self.skn.influences
        vtxs = mc.ls(self.obj+'.vtx[*]', fl=True)
        table_view.setColumnCount(len(infs))
        table_view.setRowCount(len(vtxs))
        table_view.setHorizontalHeaderLabels(infs)
        table_view.setVerticalHeaderLabels(vtxs)
        table_view.item(2, 5)

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
