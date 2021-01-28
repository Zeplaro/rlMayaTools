import maya.cmds as mc


def quick_gym(angle=90, offset=20, handles_only=True, shift=True):
    sel = mc.ls(sl=True, type='transform')
    if handles_only:
        sel = [x for x in sel if x.endswith('hdl')]
    start_frame = mc.currentTime(q=True)
    frame = int(start_frame)
    done = 0
    for i in sel:
        try:
            set_rotate_key(i, frame, (0, 0, 0))
            set_rotate_key(i, frame + offset, (angle, 0, 0))
            set_rotate_key(i, frame + offset + 1, (angle / 4, 0, 0))
            set_rotate_key(i, frame + offset * 2, (-angle, 0, 0))

            set_rotate_key(i, frame + offset * 2 + 1, (0, 0, 0))
            set_rotate_key(i, frame + offset * 3, (0, 0, angle))
            set_rotate_key(i, frame + offset * 3 + 1, (0, 0, angle / 4))
            set_rotate_key(i, frame + offset * 4, (0, 0, -angle))

            set_rotate_key(i, frame + offset * 4 + 1, (0, 0, 0))
            set_rotate_key(i, frame + offset * 5, (0, angle, 0))
            set_rotate_key(i, frame + offset * 5 + 1, (0, angle / 4, 0))
            set_rotate_key(i, frame + offset * 6, (0, -angle, 0))

            set_rotate_key(i, frame + offset * 6 + 1, (0, 0, 0))

            mc.setAttr('{}.rx'.format(i), 0)
            mc.setAttr('{}.ry'.format(i), 0)
            mc.setAttr('{}.rz'.format(i), 0)
            if shift:
                frame += offset * 6 + 1
            done += 1
        except:
            pass

    if frame < start_frame + 121:
        frame = start_frame + 121
    mc.playbackOptions(ast=start_frame, aet=frame, min=start_frame, max=start_frame + 121)


def set_rotate_key(obj, frame, angle):
    mc.setAttr('{}.rx'.format(obj), angle[0])
    mc.setAttr('{}.ry'.format(obj), angle[1])
    mc.setAttr('{}.rz'.format(obj), angle[2])
    mc.setKeyframe('{}.rx'.format(obj), t=frame)
    mc.setKeyframe('{}.ry'.format(obj), t=frame)
    mc.setKeyframe('{}.rz'.format(obj), t=frame)
