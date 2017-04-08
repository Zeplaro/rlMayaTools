import maya.cmds as mc


def getSkinCluster(obj):

    hist = mc.listHistory(obj, ac=1, pdo=1)
    sknclust = mc.ls(hist, type='skinCluster')
    if sknclust:
        sknclust = sknclust[0]
    return sknclust


def do_skinAs():

    objs = mc.ls(sl=1, typ='transform')
    if len(objs)<2:
        print('Please select at least two objects')
        return
    master = objs[0]
    slaves = objs[1:]

    masterskn = getSkinCluster(master)
    if not masterskn:
        print('First selection as no skinCluster attached')
        return
    inf = mc.skinCluster(masterskn, q=1, inf=1)
    sm = mc.skinCluster(masterskn, q=1, sm=1)
    mi = mc.skinCluster(masterskn, q=1, mi=1)
    nw = mc.skinCluster(masterskn, q=1, nw=1)
    omi = mc.skinCluster(masterskn, q=1, omi=1)
    wd = mc.skinCluster(masterskn, q=1, wd=1)
    done = []
    for slave in slaves:
        if getSkinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        mc.select(inf, slave, r=1)
        mc.skinCluster(sm=sm, mi=mi, nw=nw, omi=omi, wd=wd)
        slaveskn = getSkinCluster(slave)
        mc.copySkinWeights(ss=masterskn, ds=slaveskn, nm=1, sa='closestPoint', ia=('oneToOne', 'label', 'closestJoint'))
        done.append(slave)
    return done
