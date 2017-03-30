#!/usr/bin/env python
# coding:utf-8
""":mod:`createProjection`
===================================
.. module:: moduleName
   :platform: Unix
   :synopsis: module idea
   :author: viba
   :date: 2016.10

"""

import maya.cmds as mc


def create_projection_from_root(root_object='RooT', max_geo_radius=1):
    mc.group(em=True, n=root_object + '_orig1')
    mc.circle(r=max_geo_radius, n=root_object + '_ctrl1', nr=[0, 1, 0])
    mc.delete(root_object + '_ctrl1', ch=True)
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

    create_normalized_vector_graph(root_object, root_object + '_projection1', root_object + '_ctrl1', root_object +
                                   '_vector1', max_geo_radius)

    return root_object + '_vector1'


def create_normalized_vector_graph(prefix, projection_point_name, controller_name, out_vector_name, geo_diameter):
    distance_between = mc.createNode('distanceBetween', n=prefix + 'distanceBetween1')
    vector_product = mc.createNode('vectorProduct', n=prefix + 'vectorProduct1')
    condition = mc.createNode('condition', n=prefix + 'condition1')
    vector_multiplier = mc.createNode('multiplyDivide', n=prefix + 'vectorMultp1')

    mc.connectAttr(projection_point_name + '.translate', prefix + 'distanceBetween1' + '.point1')
    mc.connectAttr(controller_name + '.translate', prefix + 'distanceBetween1' + '.point2')
    mc.connectAttr(prefix + 'distanceBetween1' + '.distance', prefix + 'condition1' + '.firstTerm')

    mc.setAttr(prefix + 'condition1' + '.colorIfTrueR', 0)
    mc.setAttr(prefix + 'condition1' + '.colorIfTrueG', 0)
    mc.setAttr(prefix + 'condition1' + '.colorIfTrueB', 1)

    mc.connectAttr(projection_point_name + '.translate', prefix + 'condition1' + '.colorIfFalse')
    mc.connectAttr(prefix + 'condition1' + '.outColor', prefix + 'vectorProduct1' + '.input1')

    mc.setAttr(prefix + 'vectorProduct1' + '.operation', 0)
    mc.setAttr(prefix + 'vectorProduct1' + '.normalizeOutput', 1)

    mc.connectAttr(vector_product + '.output.outputZ', vector_multiplier + '.input1.input1Z')
    mc.connectAttr(vector_product + '.output.outputY', vector_multiplier + '.input1.input1Y')
    mc.connectAttr(vector_product + '.output.outputX', vector_multiplier + '.input1.input1X')

    mc.setAttr(vector_multiplier + '.input2X', geo_diameter)
    mc.setAttr(vector_multiplier + '.input2Y', geo_diameter)
    mc.setAttr(vector_multiplier + '.input2Z', geo_diameter)

    mc.connectAttr(vector_multiplier + '.output.outputX', out_vector_name + '.translateX')
    mc.connectAttr(vector_multiplier + '.output.outputZ', out_vector_name + '.translateZ')

    return [distance_between, condition, vector_product, vector_multiplier]