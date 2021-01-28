# encoding: utf-8
import maya.cmds as mc
from Qt import QtWidgets
import time


def snap_vtx(geos=None):
    if not geos:
        geos = mc.ls(sl=True, fl=True)
    if not len(geos) > 1:
        return
    source = geos[:-1]
    target = geos[-1]
    if '.vtx' not in source[0]:
        source = mc.ls(source[0] + '.vtx[*]', fl=True)
    size = len(source)

    mc.undoInfo(openChunk=True)
    prog = get_prog('Snap vtx', size)
    current_time = time.time()
    anim = get_anim()
    anim_index = 0
    for i, vertex in enumerate(source):
        if prog.wasCanceled():
            break
        if time.time() > current_time + 0.2:
            current_time = time.time()
            mc.refresh()
            if anim_index == len(anim) - 1:
                anim.reverse()
                anim_index = 0
            anim_index += 1
        prog.setValue(i)
        prog.setLabelText(u'Snapping vtx : {} / {}\n{}'.format(i, size, anim[anim_index]))
        # v Actual function v ###### ^ Visual garbage ^ ################################################################
        target_vtx = '{}.{}'.format(target, vertex.split('.')[-1])
        pos = mc.xform(vertex, q=True, ws=True, t=True)
        mc.xform(target_vtx, ws=True, t=pos)
    mc.undoInfo(closeChunk=True)

    print('Zoidberg processed {} vtx  (\\/)(o,,,o)(\\/)'.format(size))


def get_anim(lenght=30):
    emo = [u'(\\/)(°,,,°)(][)', u'(][)(°,,,°)(\\/)']
    # Generating animation sequence
    emo += emo[::-1]
    anim = [u' ' for _ in range(lenght)]
    anim = [list(anim) for _ in anim]
    [anim[i].insert(i, emo[i % len(emo)]) for i, _ in enumerate(anim)]
    anim = [u''.join(x) for x in anim]
    return anim


def get_prog(title, size):
    prog = QtWidgets.QProgressDialog(title, 'Stop', 0, size, parent=None)
    prog.setModal(True)
    prog.show()
    prog.raise_()
    prog.setWindowTitle(title)
    prog.setValue(0)
    return prog
