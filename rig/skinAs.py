import maya.cmds as mc
import tbx


def do_skinAs():

    objs = mc.ls(sl=True, typ='transform', fl=True)
    if len(objs) < 2:
        mc.warning('Please select at least two objects')
        return
    master = objs[0]
    slaves = objs[1:]

    masterskn = tbx.getSkinCluster(master)
    if not masterskn:
        mc.warning('First selection as no skinCluster attached')
        return
    inf = mc.skinCluster(masterskn, q=True, inf=True)
    sm = mc.skinCluster(masterskn, q=True, sm=True)
    mi = mc.skinCluster(masterskn, q=True, mi=True)
    nw = mc.skinCluster(masterskn, q=True, nw=True)
    omi = mc.skinCluster(masterskn, q=True, omi=True)
    wd = mc.skinCluster(masterskn, q=True, wd=True)
    done = []
    for slave in slaves:
        if tbx.getSkinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        mc.select(inf, slave, r=True)
        mc.skinCluster(sm=sm, mi=mi, nw=nw, omi=omi, wd=wd)
        slaveskn = tbx.getSkinCluster(slave)
        mc.copySkinWeights(ss=masterskn, ds=slaveskn, nm=True, sa='closestPoint', ia=('oneToOne', 'label', 'closestJoint'))
        print(slave+' skinned')
        done.append(slave)
    return done
