#!/usr/bin/env python
# coding:utf-8
""":mod:`buildShapeRoll`
===================================
.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.10

"""
import createProjection as proj
import shapeFromGeo as sha
import maya.cmds as mc


def vector_from_shape(edges_sel, custom_curve_name, guide, main_control, bind_joint, max_geo_radius):
    vector = proj.create_projection_from_root(guide, max_geo_radius)
    curve = sha.build_shape(edges_sel, custom_curve_name)

    mc.createNode("nearestPointOnCurve", n=custom_curve_name + "nearestPointOncurve1")
    mc.spaceLocator(n=guide + 'pivot1')
    mc.parent(guide + 'pivot1', guide + '_orig1')
    mc.parent(curve[0], guide + '_orig1')

    mc.group(em=True, n=guide + '_bind_orig1')

    bind_translate = mc.xform(bind_joint, query=True, t=True, ws=True)
    bind_rotate = mc.xform(bind_joint, query=True, ro=True, ws=True)

    mc.xform(guide + '_bind_orig1', t=bind_translate, ws=True)
    mc.xform(guide + '_bind_orig1', ro=bind_rotate, ws=True)

    mc.parent(guide + '_bind_orig1', guide + '_orig1')

    mc.setAttr(guide + '_bind_orig1' + '.translateX', 0)
    mc.setAttr(guide + '_bind_orig1' + '.translateY', 0)
    mc.setAttr(guide + '_bind_orig1' + '.translateZ', 0)

    mc.parent(bind_joint, guide + '_bind_orig1')

    mc.connectAttr(curve[0] + '.local', custom_curve_name + "nearestPointOncurve1" + '.inputCurve')
    mc.connectAttr(vector + ".translate", custom_curve_name + "nearestPointOncurve1" + '.inPosition')
    mc.connectAttr(custom_curve_name + 'nearestPointOncurve1' + '.result.position.positionX',
                   guide + 'pivot1.translateX')
    mc.connectAttr(custom_curve_name + 'nearestPointOncurve1' + '.result.position.positionZ',
                   guide + 'pivot1.translateZ')
    mc.connectAttr(custom_curve_name + 'nearestPointOncurve1' + '.result.position.positionY',
                   guide + 'pivot1.translateY')

    mc.connectAttr(guide + '_ctrl1' + '.rotateX', guide + '_bind_orig1' + '.rotateX')
    mc.connectAttr(guide + '_ctrl1' + '.rotateZ', guide + '_bind_orig1' + '.rotateZ')

    mc.connectAttr(guide + 'pivot1' + '.translateX', guide + '_bind_orig1' + '.rotatePivotX')
    mc.connectAttr(guide + 'pivot1' + '.translateZ', guide + '_bind_orig1' + '.rotatePivotZ')
    mc.connectAttr(guide + 'pivot1' + '.translateY', guide + '_bind_orig1' + '.rotatePivotY')

    # mc.delete(guide)