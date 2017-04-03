import maya.cmds as mc


def getskinCluster(obj):

    hist = mc.listHistory(obj, ac=1, pdo=1)
    sknclust = mc.ls(hist, type='skinCluster')
    return sknclust

def do_skinAs():

    objs = mc.ls(sl=1, typ='transform')
    try:
        master = objs[0]
    except:
        print('Please select at least two objects')
        return
    slaves = objs[1:] or []
    if not slaves:
        print('Please select at least two objects')
        return

    masterskn = getskinCluster(master)
    inf = mc.skinCluster(masterskn, q=1, inf=1)
    sm = mc.skinCluster(masterskn, q=1, sm=1)
    mi = mc.skinCluster(masterskn, q=1, mi=1)
    nw = mc.skinCluster(masterskn, q=1, nw=1)
    omi = mc.skinCluster(masterskn, q=1, omi=1)
    wd = mc.skinCluster(masterskn, q=1, wd=1)

    for slave in slaves:
        if getskinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        print(slave)
        mc.select(inf, slave, r=1)
        mc.skinCluster(sm=sm, mi=mi, nw=nw, omi=omi, wd=wd)


