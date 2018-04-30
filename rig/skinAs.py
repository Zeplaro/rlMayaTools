import maya.cmds as mc
from tbx import get_skinCluster


def do_skinAs(slaveNamespace=None, master=None, *slaves):

    if not master or not slaves:
        objs = mc.ls(sl=True, tr=True, fl=True)
        if len(objs) < 2:
            mc.warning('Please select at least two objects')
            return
        master = objs[0]
        slaves = objs[1:]

    masterskn = get_skinCluster(master)
    if not masterskn:
        mc.warning('First object as no skinCluster attached')
        return
    infs = mc.skinCluster(masterskn, q=True, inf=True)
    if slaveNamespace is not None:
        infs = ['{}{}'.format(slaveNamespace, inf) for inf in infs]
    sm = mc.skinCluster(masterskn, q=True, skinMethod=True)
    mi = mc.skinCluster(masterskn, q=True, maximumInfluences=True)
    nw = mc.skinCluster(masterskn, q=True, normalizeWeights=True)
    omi = mc.skinCluster(masterskn, q=True, obeyMaxInfluences=True)
    wd = mc.skinCluster(masterskn, q=True, weightDistribution=True)
    done = []
    for slave in slaves:
        if get_skinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        mc.select(infs, slave, r=True)
        mc.skinCluster(name='skinCluster_{}_#'.format(slave), sm=sm, mi=mi, nw=nw, omi=omi, wd=wd, ihs=True, tsb=True)
        slaveskn = get_skinCluster(slave)
        mc.copySkinWeights(ss=masterskn, ds=slaveskn, nm=True, sa='closestPoint', ia=('oneToOne', 'label', 'closestJoint'))
        print(slave+' skinned')
        done.append(slave)
    return done
