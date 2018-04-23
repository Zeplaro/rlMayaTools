import maya.cmds as mc
from functools import partial


def launch_ui():

    if mc.window('splitJntUI', exists=True):
        mc.deleteUI('splitJntUI')
    splitJnt_ui()


def splitJnt_ui():

        mc.window('splitJntUI', title='Split joint tool', s=False, rtf=True)

        mc.columnLayout('columnMain', w=400)
        mc.rowLayout('startRow', nc=3)
        mc.text('Start joint :', w=90)
        mc.textField('startJnt', w=250)
        mc.button('startUpdate', l='Update', command=partial(getSel, 'startJnt'))
        mc.setParent('..')
        mc.rowLayout('endRow', nc=3)
        mc.text('End joint :', w=90)
        mc.textField('endJnt', w=250)
        mc.button('endUpdate', l='Update', command=partial(getSel, 'endJnt'))
        mc.setParent('..')
        mc.intSliderGrp('nb', l='Number of split', cw=((1, 90), (2, 30)), cl3=('center', 'center', 'center'), value=1, min=1,
                        max=10, field=True, fieldMinValue=1, fieldMaxValue=1000, w=400)
        mc.rowLayout('suffixRow', nc=2)
        mc.text('Split suffix :', w=90)
        mc.textField('suffix', text='_split_', w=250)
        mc.setParent('..')
        mc.button('Split', w=400, command=launch_splitJnt)
        mc.showWindow('splitJntUI')


def getSel(btn, *args):

    sel = mc.ls(sl=True, type='joint')
    if not sel:
        mc.warning('No joint selected')
        return
    mc.textField(btn, e=True, text=sel[0])


def launch_splitJnt(*args):

        nb = mc.intSliderGrp('nb', q=True, value=True)
        jnts = [mc.textField('startJnt', q=True, text=True), mc.textField('endJnt', q=True, text=True)]
        suffix = mc.textField('suffix', q=True, text=True)
        if jnts[0] and jnts[1]:
            do_splitJnt(nb, jnts, suffix)
        else:
            do_splitJnt(nb=nb, jnts=None, suffix=suffix)


def do_splitJnt(nb=1, jnts=None, suffix='_split_'):

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
        split = mc.joint(n='{}{}#'.format(start, suffix), rad=rad)
        mc.parent(split, start, r=True)
        mc.xform(split, r=True, t=pos)
        for j in range(3):
            pos[j] += splitpos[j]
        splits.append(split)

    for i in range(len(splits)-1):
            mc.parent(splits[i+1], splits[i])
    mc.parent(end, splits[-1])
    return splits
