import maya.cmds as mc
from tbx import get_shape
from math import sqrt

# todo : do closest if sel is vtx


def get_dist(a, b):
    dist = sqrt(pow((b[0]-a[0]), 2)+pow((b[1]-a[1]), 2)+pow((b[2]-a[2]), 2))
    return dist

def do_snapVtx(objs=None, os=False, closest=False):

    sel = mc.ls(sl=True)
    if not objs:
        objs = [x for x in sel if 'mesh' in (mc.nodeType(get_shape(x), i=True) or []) and '.' not in x]
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
            for i, vtx in enumerate(slave_vtx):
                print(vtx)
                dists = []
                for j in master_vtx_pos:
                    dist = get_dist(slave_vtx_pos[i], j)
                    dists.append(dist)
                index = 0
                val = dists[0]
                for k_, dist in enumerate(dists):
                    if val < dist:
                        index = k_
                        val = dist
                    else:
                        continue
                mc.xform(vtx, ws=True, t=master_vtx_pos[index])
    mc.select(sel)

