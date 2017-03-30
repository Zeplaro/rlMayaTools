#!/usr/bin/env python
# coding:utf-8
""":mod:`create_vector_oncurve`
===================================
.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.11

"""

import maya.cmds as mc
import shapeFromGeo as sha


def vector_on_curve(sel, curve_name, root_object, guide, bind_joint, max_geo_radius, parent_bind):
    mc.undoInfo(ock=True)
    curve = curve_name
    orig = create_projection(root_object, max_geo_radius)
    nodes = create_vector_graph(guide, max_geo_radius)

    mc.parent(curve, orig)
    mc.makeIdentity(curve, apply=True, translate=True, rotate=True, scale=True)

    bind_orig = mc.group(em=True, n=guide + '_bind_orig1')
    mc.parent(bind_orig, orig)
    mc.setAttr(bind_orig + '.translateX', 0)
    mc.setAttr(bind_orig + '.translateY', 0)
    mc.setAttr(bind_orig + '.translateZ', 0)

    pivot = mc.spaceLocator(n=guide + '_pivot1')
    mc.parent(pivot, orig)
    mc.setAttr(pivot[0] + '.translateX', 0)
    mc.setAttr(pivot[0] + '.translateY', 0)
    mc.setAttr(pivot[0] + '.translateZ', 0)

    create_connections(root_object, pivot[0], curve, bind_orig, nodes[0], nodes[1], nodes[2], nodes[3], nodes[4])

    mc.setAttr(curve + '.visibility', 0)
    if parent_bind == 1:
        mc.parent(bind_joint, bind_orig)
    mc.parent(orig, root_object)
    mc.undoInfo(cck=True)


def create_projection(root_object, max_geo_radius):
    mc.group(em=True, n=root_object + '_orig1')
    mc.circle(r=max_geo_radius, n=root_object + '_ctrl1', nr=[0, 1, 0])
    mc.delete(root_object + '_ctrl1', ch=True)
    mc.setAttr(root_object + '_ctrl1' + '.rotateOrder', 2)
    mc.setAttr(root_object + '_ctrl1' + '.rotateY', lock=True, keyable=False, channelBox=False)

    mc.group(em=True, n=root_object + '_offset1')
    mc.group(em=True, n=root_object + '_projection1')
    mc.group(em=True, n=root_object + '_vector1')

    translate = mc.xform(root_object, query=True, t=True, ws=True)
    rotate = mc.xform(root_object, query=True, ro=True, ws=True)

    mc.xform(root_object + '_orig1', t=translate, ws=True)
    mc.xform(root_object + '_orig1', ro=rotate, ws=True)

    mc.xform(root_object + '_ctrl1', t=translate, ws=True)
    mc.xform(root_object + '_ctrl1', ro=rotate, ws=True)
    mc.parent(root_object + '_ctrl1', root_object + '_orig1')

    mc.xform(root_object + '_offset1', t=translate, ws=True)
    mc.xform(root_object + '_offset1', ro=rotate, ws=True)
    mc.parent(root_object + '_offset1', root_object + '_ctrl1')
    mc.xform(root_object + '_offset1', t=[0, 1, 0], r=True, wd=True)
    mc.setAttr(root_object + '_offset1' + ".displayRotatePivot", 1)

    mc.xform(root_object + '_projection1', t=translate, ws=True)
    mc.xform(root_object + '_projection1', ro=rotate, ws=True)
    mc.parent(root_object + '_projection1', root_object + '_orig1')
    mc.setAttr(root_object + '_projection1' + '.displayScalePivot', 1)

    mc.xform(root_object + '_vector1', t=translate, ws=True)
    mc.xform(root_object + '_vector1', ro=rotate, ws=True)
    mc.parent(root_object + '_vector1', root_object + '_orig1')
    mc.setAttr(root_object + '_vector1' + ".displayRotatePivot", 1)

    mc.pointConstraint(root_object + '_offset1', root_object + '_projection1', sk='y', mo=True)

    return root_object + '_orig1'


def create_vector_graph(prefix, max_geo_radius):
    distance_between = mc.createNode('distanceBetween', n=prefix + 'distanceBetween1')
    vector_product = mc.createNode('vectorProduct', n=prefix + 'vectorProduct1')
    condition = mc.createNode('condition', n=prefix + 'condition1')
    multiply_divide = mc.createNode('multiplyDivide', n=prefix + 'vectorMultp1')
    nearest_point_on_curve = mc.createNode("nearestPointOnCurve", n=prefix + "nearestPointOncurve1")

    mc.setAttr(condition + '.colorIfTrueR', 0)
    mc.setAttr(condition + '.colorIfTrueG', 0)
    mc.setAttr(condition + '.colorIfTrueB', 1)

    mc.setAttr(vector_product + '.operation', 0)
    mc.setAttr(vector_product + '.normalizeOutput', 1)

    mc.setAttr(multiply_divide + '.input2X', max_geo_radius)
    mc.setAttr(multiply_divide + '.input2Y', max_geo_radius)
    mc.setAttr(multiply_divide + '.input2Z', max_geo_radius)

    return [distance_between, vector_product, condition, multiply_divide, nearest_point_on_curve]


def create_connections(root_object, out_pivot, custom_curve, bind_orig, distance_between, vector_product, condition,
                       multiply_divide, nearest_point_on_curve):
    mc.connectAttr(root_object + '_projection1' + '.translate', distance_between + '.point1')
    mc.connectAttr(root_object + '_ctrl1.translate', distance_between + '.point2')
    mc.connectAttr(distance_between + '.distance', condition + '.firstTerm')
    mc.connectAttr(root_object + '_projection1' + '.translate', condition + '.colorIfFalse')
    mc.connectAttr(condition + '.outColor', vector_product + '.input1')
    mc.connectAttr(vector_product + '.output.outputZ', multiply_divide + '.input1.input1Z')
    mc.connectAttr(vector_product + '.output.outputY', multiply_divide + '.input1.input1Y')
    mc.connectAttr(vector_product + '.output.outputX', multiply_divide + '.input1.input1X')
    mc.connectAttr(multiply_divide + '.output.outputX', root_object + '_vector1.translateX')
    mc.connectAttr(multiply_divide + '.output.outputZ', root_object + '_vector1.translateZ')

    mc.connectAttr(custom_curve + '.local', nearest_point_on_curve + '.inputCurve')
    mc.connectAttr(root_object + "_vector1.translate", nearest_point_on_curve + '.inPosition')

    mc.connectAttr(nearest_point_on_curve + '.result.position.positionX', out_pivot + '.translateX')
    mc.connectAttr(nearest_point_on_curve + '.result.position.positionY', out_pivot + '.translateY')
    mc.connectAttr(nearest_point_on_curve + '.result.position.positionZ', out_pivot + '.translateZ')

    mc.connectAttr(root_object + '_ctrl1.rotateX', bind_orig + '.rotateX')
    mc.connectAttr(root_object + '_ctrl1.rotateZ', bind_orig + '.rotateZ')

    mc.connectAttr(out_pivot + '.translateX', bind_orig + '.rotatePivotX')
    mc.connectAttr(out_pivot + '.translateZ', bind_orig + '.rotatePivotZ')
    mc.connectAttr(out_pivot + '.translateY', bind_orig + '.rotatePivotY')