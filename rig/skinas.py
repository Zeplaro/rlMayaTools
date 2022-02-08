from maya import cmds, mel


def get_skinCluster(obj):
    sknclust = mel.eval('findRelatedSkinCluster '+obj)
    return sknclust if sknclust else None


def skinas(slave_namespace=None, master=None, *slaves):

    if not master or not slaves:
        objs = cmds.ls(sl=True, tr=True, fl=True)
        if len(objs) < 2:
            cmds.warning('Please select at least two objects')
            return
        master = objs[0]
        slaves = objs[1:]

    masterskn = get_skinCluster(master)
    if not masterskn:
        cmds.warning('First object as no skinCluster attached')
        return
    infs = cmds.skinCluster(masterskn, q=True, inf=True)
    if slave_namespace is not None:
        infs = ['{}{}'.format(slave_namespace, inf) for inf in infs]
    sm = cmds.skinCluster(masterskn, q=True, skinMethod=True)
    mi = cmds.skinCluster(masterskn, q=True, maximumInfluences=True)
    nw = cmds.skinCluster(masterskn, q=True, normalizeWeights=True)
    omi = cmds.skinCluster(masterskn, q=True, obeyMaxInfluences=True)
    wd = cmds.skinCluster(masterskn, q=True, weightDistribution=True)
    done = []
    for slave in slaves:
        if get_skinCluster(slave):
            print(slave+' already have a skin attached')
            continue
        cmds.select(infs, slave, r=True)
        cmds.skinCluster(name='skinCluster_{}_#'.format(slave), sm=sm, mi=mi, nw=nw, omi=omi, wd=wd, ihs=True, tsb=True)
        slaveskn = get_skinCluster(slave)
        cmds.copySkinWeights(ss=masterskn, ds=slaveskn, nm=True, sa='closestPoint',
                           ia=('oneToOne', 'label', 'closestJoint'))
        print(slave+' skinned')
        done.append(slave)
    return done
