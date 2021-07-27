#!/usr/bin/env python

import maya.cmds as mc
import functools


def maya_undo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        data = func(*args, **kwargs)
        mc.undoInfo(closeChunk=True)
        return data
    return wrapper


def get_curves_data(curve=None):
    if not curve:
        curve = mc.ls(sl=True)
        if curve:
            curve = curve[0]
    shapes = mc.listRelatives(curve, s=True, pa=1, ni=True) or []
    data = {i: get_curve_data(shape) for i, shape in enumerate(shapes)}
    return data


def get_curve_data(curve_shape):
    name = curve_shape
    shape_type = mc.nodeType(name)
    spans = mc.getAttr('{}.spans'.format(name))
    form = mc.getAttr('{}.form'.format(name))
    degree = mc.getAttr('{}.degree'.format(name))
    cps = mc.ls('{}.cp[*]'.format(name), fl=True)
    cps_position = [mc.xform(cp, q=True, os=True, t=True) for cp in cps]
    info = mc.createNode('curveInfo')
    mc.connectAttr('{}.local'.format(name), '{}.inputCurve'.format(info))
    knots = mc.getAttr('{}.knots'.format(info))[0]
    mc.delete(info)
    data = {'shape_type': shape_type,
            'spans': spans,
            'form': form,
            'degree': degree,
            'cps': cps_position,
            'knots': knots,
            }
    return data


@maya_undo
def parent_shape(parent=None, childs=None):
    if not parent or not childs:
        sel = mc.ls(sl=True)
        if len(sel) < 2:
            return
        parent, childs = sel[-1], sel[:-1]
    for child in childs:
        mc.parent(child, parent, r=True, s=True)
