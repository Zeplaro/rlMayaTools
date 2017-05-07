import maya.cmds as mc


def do_UI():

    winID = 'rollUI'
    if mc.window(winID, ex=True):
        mc.deleteUI(winID)
    mc.window(winID, t='Create roll pivot control')

    mc.columLayout()

    mc.showWindow()
    print('ok')
