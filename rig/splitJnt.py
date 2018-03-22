import maya.cmds as mc
# todo : ui


def do_splitJnt(nb=1, jnts=None):

    if not jnts:
        jnts = mc.ls(sl=True, fl=True, type='joint')
    if len(jnts) < 2:
        mc.warning('Not enough jnts selected')
        return

    start = jnts[0]
    end = jnts[1]
    rad = mc.joint(start, q=True, rad=True)[0]
    if end in (mc.listRelatives(start, ap=True) or []):
        mc.warning('Start joint is a child of the end joint')
        return
    if mc.listRelatives(end, p=True) != [start]:
        mc.parent(end, start)
    lastpos = mc.xform(end, q=True, t=True)
    splitpos = []
    for i in range(3):
        splitpos.append(lastpos[i]/(nb+1))

    splits = []
    pos = splitpos[:]
    for i in range(nb):
        mc.select(cl=True)
        split = mc.joint(n=start+'_split_#', rad=rad)
        mc.parent(split, start, r=True)
        mc.xform(split, r=True, t=pos)
        for j in range(3):
            pos[j] += splitpos[j]
        splits.append(split)

    for i in range(len(splits)-1):
            mc.parent(splits[i+1], splits[i])
    mc.parent(end, splits[-1])
    return splits
