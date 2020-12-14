# Print un message dans la command line
import maya.OpenMaya as om
om.MGlobal.displayInfo("my grey info message")

########################################################################################################################
# Add a message attribute
mc.addAttr(sel, at='message', ln='L_eye')

########################################################################################################################
# To append a python script path
# It can be written in a userSetup.py file in your script folder to be load when maya starts
import sys
sys.path.append(r'D:/Robin/Work/Python/rlMayaTools')

########################################################################################################################
# Hide node on the channelbox list
mc.setAttr('node.ihi', False)  #Ou node.isHistoricalyInteresting on ou off

########################################################################################################################
# Viewport command
mc.ogs(r=1) # reset/refresh le viewport
mc.ogs(p=1) # pause le viewport

########################################################################################################################
# Reset all Maya Windows placement
import maya.cmds as mc
do_not_remove = ['MayaWindow', 'nextFloatWindow']
for _w in mc.lsUI(windows=1):
    if _w not in do_not_remove:
        mc.deleteUI(_w)
        mc.windowPref(_w, remove=1)
        print('# cleanup ui ', _w)

########################################################################################################################
if ((((True == False) == False) == True) == False) == False:
    print('wut?')

########################################################################################################################
# focus une windows docké dans maya a l'ouverture
"""J'ai trouvé
my_dockable_win.raise_()
😑
Ou sinon
for dock_widget in mainWindow.findChildren(QtWidgets.QDockWidget):
mainWindow.tabifyDockWidget(dock_widget, dock_instance)
break"""

########################################################################################################################
# To force a Qt adjustSize() in maya
def adjustSize(self):
    mc.refresh()
    super(QtWidgets.QDialog, self).adjustSize()

########################################################################################################################
# Adds a separator to the active shelf
import maya.cmds as cmds
addSeparator_cmd = "import maya.cmds as cmds;import maya.mel as mel;cmds.separator(width=12, height = 35, style='shelf', hr=False, parent=mel.eval(\"tabLayout -q -selectTab $gShelfTopLevel\"))"
win_name = "Addshelf_win"
if cmds.window(win_name, ex=True):
    cmds.deleteUI(win_name)
win = cmds.window(win_name)
cmds.columnLayout(adj=True)
cmds.button(l="Add separator to this active self", command=addSeparator_cmd)
cmds.showWindow(win_name)
