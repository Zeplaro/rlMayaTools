import maya.cmds as mc
from tbx import get_shape

def do_snapVtx(objs=None, os=False, closest=False):

    if not objs:
        objs = [x for x in mc.ls(sl=True) if 'mesh' in mc.nodeType(get_shape(x), i=True) and '.' not in x]
    objs = [x for x in list(objs) if mc.objExists(x)]
    if len(objs) < 2:
        mc.warning("Select at least two mesh")
        return
