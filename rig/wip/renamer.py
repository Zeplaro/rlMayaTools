import maya.cmds as mc
import maya.cmds as mc
import maya.OpenMayaUI as mui
import maya.mel as mel
from functools import partial
from collections import OrderedDict
from Qt import QtGui, QtCore, QtWidgets, QtCompat


def launch_ui():
 if mc.window('renamer', exists=True):
 mc.deleteUI('renamer')
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

 self.setWindowTitle('Renamer')
 self.setObjectName('renamer')
 self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
 self.setMinimumSize(225, 300)

 self.ui_layout()
 self.ui_connections()

 def ui_layout(self):
 main_layout = QtWidgets.QVBoxLayout()
 self.setLayout(main_layout)

 prefix_layout = QtWidgets.QHBoxLayout()
 main_layout.addLayout(prefix_layout)


 def ui_connections(self):
 pass

 @staticmethod
 def get_sel():
 return mc.ls(sl=True, fl=True) or []

 @property
 def prefix(self):
 return ''

 @property
 def suffix(self):
 return ''

 def rename(self):
 for obj in self.get_sel():
 new_name = str(obj)
 new_name = self.prefix + new_name + self.suffix
 mc.rename(obj, new_name)