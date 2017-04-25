import maya.cmds as mc


def getSkinCluster(obj):

    hist = mc.listHistory(obj, ac=True, pdo=True)
    sknclust = mc.ls(hist, type='skinCluster')
    if sknclust:
        sknclust = sknclust[0]
    return sknclust


def do_skinAs():

    objs = mc.ls(sl=True, typ='transform', fl=True)
    if len(objs)<2:
        return 'Please select at least two objects'
    master = objs[0]
    slaves = objs[1:]

    masterskn = getSkinCluster(master)
    if not masterskn:
        return 'First selection as no skinCluster attached'
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
        mc.skinCluster(sm=sm, mi=mi, nw=nw, omi=omi, wd=wd)
        slaveskn = getSkinCluster(slave)
        mc.copySkinWeights(ss=masterskn, ds=slaveskn, nm=True, sa='closestPoint', ia=('oneToOne', 'label', 'closestJoint'))
        print(slave+' skinned')
        done.append(slave)
    return done
