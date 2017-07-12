import maya.cmds as mc
from tbx import getSkinCluster


def do_skinAs(master=None, *slaves):

    if not master or not slaves:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if len(objs) < 2:
            mc.warning('Please select at least two objects')
            return
        master = objs[0]
        slaves = objs[1:]

    masterskn = getSkinCluster(master)
    if not masterskn:
        mc.warning('First object as no skinCluster attached')
        return
    inf = mc.skinCluster(masterskn, q=True, inf=True)
    sm = mc.skinCluster(masterskn, q=True, sm=True)
    mi = mc.skinCluster(masterskn, q=True, mi=True)
    nw = mc.skinCluster(masterskn, q=True, nw=True)
    omi = mc.skinCluster(masterskn, q=True, omi=True)
    wd = mc.skinCluster(masterskn, q=True, wd=True)
    done = []
    for slave in slaves:
        if getSkinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        mc.select(inf, slave, r=True)
        mc.skinCluster(name='skinCluster_'+slave+'_#', sm=sm, mi=mi, nw=nw, omi=omi, wd=wd, ihs=True, tsb=True)
        slaveskn = getSkinCluster(slave)
        mc.copySkinWeights(ss=masterskn, ds=slaveskn, nm=True, sa='closestPoint', ia=('oneToOne', 'label', 'closestJoint'))
        print(slave+' skinned')
        done.append(slave)
    return done
