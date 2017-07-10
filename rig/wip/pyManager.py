import maya.cmds as mc
from functools import partial

def launchUI():
    winID = 'pyMUI'
    doc = 'docUI'
    if mc.window(winID, exists=True):
        mc.deleteUI(winID)
    mc.window(winID, title='pyManager')
    mc.columnLayout(w=400)






    # Put Win in dockControl
    if mc.dockControl(doc, exists=True):
        mc.deleteUI(doc, control=True)
    mc.dockControl(doc, area='right', content=winID, allowedArea=['right', 'left'], l='pyManager')


'''
import os
pypath = os.environ['MAYA_SCRIPT_PATH']
splitpath=pypath.split(';')
print path
for i in splitpath:
    print i
    print os.listdir(i)
'''