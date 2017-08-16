import maya.cmds as mc
from tbx import get_shape


def do_snapVtx(objs=None, os=False, closest=False):

    if not objs:
        objs = [x for x in mc.ls(sl=True) if 'mesh' in mc.nodeType(get_shape(x), i=True) and '.' not in x]
    objs = [x for x in list(objs) if mc.objExists(x)]
    if len(objs) < 2:
        mc.warning("Select at least two mesh")
        return

    master = objs[0]
    slaves = objs[1:]

    mc.select(mc.polyListComponentConversion(master, tv=True))
    master_vtx = mc.ls(sl=True, fl=True)
    if closest or not os:
        master_vtx_pos = [mc.xform(x, q=True, ws=True, t=True) for x in master_vtx]
    else:
        master_vtx_pos = [mc.xform(x, q=True, os=True, t=True) for x in master_vtx]

    for slave in slaves:
        mc.select(mc.polyListComponentConversion(slave, tv=True))
        slave_vtx = mc.ls(sl=True, fl=True)

        if not closest:
            for i, vtx in enumerate(slave_vtx):
                if not os:
                    mc.xform(vtx, ws=True, t=master_vtx_pos[i])
                else:
                    mc.xform(vtx, os=True, t=master_vtx_pos[i])
        else:
            slave_vtx_pos = [mc.xform(x, q=True, ws=True, t=True) for x in slave_vtx]

