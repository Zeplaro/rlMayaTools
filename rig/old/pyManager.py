import maya.cmds as mc
import os


def launch_ui():
    winID = 'pyMUI'
    doc = 'docUI'
    if mc.window(winID, exists=True):
        mc.deleteUI(winID)
    mc.window(winID, title='pyManager')
    mc.columnLayout(w=400)
    path = 'D:/Robin/Work/Python/rlMayaTools/rig'
    for script in get_scripts(path):
        mc.button(l=script, h=40, w=40, ann=node, command=partial(nodecreation, node))

    # Put Win in dockControl
    if mc.dockControl(doc, exists=True):
        mc.deleteUI(doc, control=True)
    mc.dockControl(doc, area='right', content=winID, allowedArea=['right', 'left'], l='pyManager')


def get_scripts(path):
    scritps = os.listdir(path)
    return scritps


def launchScript(script):
    exec(script+'.py')