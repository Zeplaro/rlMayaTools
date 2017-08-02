#!/usr/bin/env python
# coding:utf-8
""":mod:`shapeFromGeo`
===================================
.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.10

"""

import maya.cmds as mc


def build_shape(edge_sel, custom_curve_name='custom1'):
    out_curve = mc.polyToCurve(edge_sel, n=custom_curve_name, form=2, degree=3)
    mc.delete(custom_curve_name, ch=True)
    mc.xform(out_curve[0], cp=True)
    return out_curve


def get_selection():
    sel = mc.ls(sl=True)
    return sel


def create_circle_test(radius, guide):
    if mc.objExists('cSr_circle_Test'):
        mc.delete('cSr_circle_Test')
    if type(radius) == int or str:
        mc.circle(n='cSr_circle_Test', r=radius, nr=[0, 1, 0])
    else:
        return

    translate = mc.xform(guide, query=True, t=True, ws=True)
    mc.xform('cSr_circle_Test', t=translate, ws=True)


def delete_circle_test():
    if mc.objExists('cSr_circle_Test'):
        mc.delete('cSr_circle_Test')