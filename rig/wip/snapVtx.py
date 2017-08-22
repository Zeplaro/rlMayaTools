import maya.cmds as mc
from tbx import get_shape
from math import sqrt

# todo : do closest if sel is vtx
# todo : better stop button


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

    master = objs[-1]
    slaves = objs[:-1]

    mc.select(mc.polyListComponentConversion(master, tv=True))
    master_vtx = mc.ls(sl=True, fl=True)

    if closest:
        print('Starting comparision...')
        comp = 0

        def do_stop(*args):
            mc.button('stop', e=True, label='Stoped')

        if mc.window('snapVTX', exists=True):
            mc.deleteUI('snapVTX')
        mc.window('snapVTX', s=False, rtf=True)
        mc.columnLayout('columnMain')
        mc.text(label='Snaping in progress...', align='center')
        mc.button('stop', label='Stop', align='center', command=do_stop)
        mc.showWindow('snapVTX')

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
            slave_len = len(slave_vtx)

            for _i, vtx in enumerate(slave_vtx):
                if mc.button('stop', q=True, label=True) == 'Stoped':
                    break
                vtx_pos = mc.xform(vtx, q=True, ws=True, t=True)
                index = 0
                dist = get_dist(vtx_pos, master_vtx_pos[0])
                for mindex, mvtx in enumerate(master_vtx_pos):
                    new_dist = get_dist(vtx_pos, mvtx)
                    if dist > new_dist:
                        dist = new_dist
                        index = mindex
                    comp += 1
                mc.xform(vtx, ws=True, t=master_vtx_pos[index])
                mc.refresh(cv=True, f=True)
                print('{}/{}'.format(_i, slave_len))
    if closest:
        print('{} comparison done'.format(comp))
        mc.deleteUI('snapVTX')
    mc.select(sel)

