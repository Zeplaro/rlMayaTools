from maya import cmds
import tbx


def align(objs=None, t=True, r=True):
    if not objs:
        if cmds.selectPref(q=True, tso=True) == 0:  # Allows you to get components order of selection
            cmds.selectPref(tso=True)
        objs = cmds.ls(os=True, fl=True)
    assert objs and len(objs) > 2, 'Not enough object selected'
    poses = [cmds.xform(x, q=True, t=True, ws=True) for x in objs]
    if t:
        t_start, t_end = poses[0], poses[-1]
        t_steps = [(t_end[x] - t_start[x]) / (len(objs) - 1.0) for x in range(3)]
    if r:
        r_start, r_end = [cmds.xform(x, q=True, ws=True, ro=True) for x in (objs[0], objs[-1])]
        r_steps = [(r_end[x] - r_start[x]) / (len(objs) - 1.0) for x in range(3)]

    for i, j in enumerate(objs):
        if t:
            pos = [t_steps[x] * i + t_start[x] for x in range(3)]
            cmds.xform(j, ws=True, t=pos)
        if r:
            rot = [r_steps[x] * i + r_start[x] for x in range(3)]
            cmds.xform(j, ws=True, ro=rot)

    if r and not t:
        for obj, pos in zip(objs, poses):
            cmds.xform(obj, t=pos, ws=True)


@tbx.keepsel
def aim(objs=None, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType='scene', worldUpObject=None, worldUpVector=(0, 1, 0)):
    """
    (objs=None, aimVector=(0, 0, 1), upVector=(0, 1, 0), worldUpType='scene', worldUpObject=None, worldUpVector=(0, 1, 0))
    Args:
        objs: [str, ...]
        aimVector: [float, float, float]
        upVector: [float, float, float]
        worldUpType: str, One of 5 values : "scene", "object", "objectrotation", "vector", or "none"
        worldUpObject: str, Use for worldUpType "object" and "objectrotation"
        worldUpVector: [float, float, float], Use for worldUpType "scene" and "objectrotation"
    """
    if not objs:
        objs = cmds.ls(sl=True)
    assert objs and len(objs) > 1, 'Not enough object selected'
    poses = [cmds.xform(x, q=True, t=True, ws=True) for x in objs]
    nulls = [cmds.createNode('transform') for _ in objs]
    [cmds.xform(null, t=pos, ws=True) for null, pos in zip(nulls, poses)]
    world_null = cmds.createNode('transform', name='world_null')
    for obj, null, pos in zip(objs[:-1], nulls[1:], poses):
        cmds.xform(obj, t=pos, ws=True)
        if worldUpType == 'scene':
            cmds.delete(cmds.aimConstraint(null, obj, aimVector=aimVector, upVector=upVector,
                                           worldUpType='objectrotation', worldUpObject=world_null,
                                           worldUpVector=worldUpVector, mo=False))
        elif worldUpType == 'object':
            cmds.delete(cmds.aimConstraint(null, obj, aimVector=aimVector, upVector=upVector, worldUpType='object',
                                           worldUpObject=worldUpObject, mo=False))
        else:
            cmds.delet(nulls, world_null)
            raise NotImplementedError

    cmds.xform(objs[-1], t=poses[-1], ro=cmds.xform(objs[-2], q=True, ro=True, ws=True), ws=True)
    cmds.delete(world_null, nulls)


def match(objs=None, t=True, r=True, s=False):
    if not objs:
        objs = cmds.ls(sl=True, fl=True)
    assert objs > 1, 'Less than 2 objects selected'

    master, slaves = objs[0], objs[1:]
    pos = cmds.xform(master, q=True, t=True, ws=True)
    rot = cmds.xform(master, q=True, ro=True, ws=True)
    scale = cmds.xform(master, q=True, s=True, ws=True)
    for slave in slaves:
        if t:
            cmds.xform(slave, t=pos, ws=True)
        if r:
            cmds.xform(slave, ro=rot, ws=True)
        if s:
            cmds.xform(slave, s=scale, ws=True)
