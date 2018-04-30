from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *
try:
    import shiboken
except:
    import shiboken2 as shiboken
import maya.cmds as mc
import maya.OpenMayaUI as mui


def launch_ui():

    if mc.window('attrManager', exists=True):
        mc.deleteUI('attrManager')
    ui = skin_ui()
    ui.show()


def getMayaWin():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(pointer), QWidget)


class skin_ui(QDialog):

    def __init__(self, parent=getMayaWin()):
        super(skin_ui, self).__init__(parent)

        self.ui_layout()

    def ui_layout

    def get_save(self):
        fname = QFileDialog.getSaveFileName(self, 'Save file')
        print(fname)
