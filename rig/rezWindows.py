import maya.cmds as mc
do_not_remove = ['MayaWindow', 'nextFloatWindow']
for _w in mc.lsUI(windows=1):
    if _w not in do_not_remove:
        mc.deleteUI(_w)
        mc.windowPref(_w, remove=1)
        print('# cleanup ui ', _w)
