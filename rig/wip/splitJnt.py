import maya.cmds as mc


def do_splitJnt(nb=1, jnts=False):

    if not jnts:
        jnts = mc.ls(sl=True, fl=True)
    if len(jnts) < 2:
        mc.warning('Not enough jnts selected')
        return
    start = jnts[0]
    end = jnts[1]
    rad = mc.joint(start, q=True, rad=True)[0]
    print(rad)
    mc.select(cl=True)
    splitdummy = mc.joint(n=start + '_splitdummy#')
    mc.parent(splitdummy, end, r=True)
    mc.parent(splitdummy, start)
    lastpos = mc.xform(splitdummy, q=True, t=True)
    splitpos = []
    for i in range(3):
        splitpos.append(lastpos[i]/(nb+1))
    mc.delete(splitdummy)

    splits = []
    for i in range(nb):
        mc.select(cl=True)
        split = mc.joint(n=start+'_split#', rad=rad)
        mc.parent(split, start, r=True)
        for j in range(3):
            splitpos[j] *= (i+1)
        mc.xform(split, r=True, t=splitpos)
        splits.append(split)

    for i in range(len(splits)-1):
            mc.parent(splits[i+1], splits[i])
    mc.parent(end, splits[-1])
    return splits
