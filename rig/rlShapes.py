import maya.cmds as mc
from PySide import QtGui
from PySide import QtCore
import maya.OpenMayaUI as mui
import shiboken
from functools import partial
from math import sqrt, ceil
import shapeMirror
# reload(shapeMirror)
from tbx import get_shape


"""
todo: pokeball, half_circle, line, half_sphere, wobbly_circle, eye, foot,pin_sphere, pin_cube, pin_pyramide, pin_double_pyramide, pin_circle_crossed, star, circle_cross, double_pin_circle_crossed, u_turn_arrow, pin_arrow, cross_axis, sparkle

todo : refacto for >= maya 2017
        add : add selected custom shape to list
"""


def launch_ui():

    if mc.window('rlShapeCreator', exists=True):
        mc.deleteUI('rlShapeCreator')
    ui = RlShapes_ui()
    ui.show()


def getMayaWin():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(int(pointer), QtGui.QWidget)


class RlShapes_ui(QtGui.QDialog):

    maya_version = False
    if '2016 Extension 2' in mc.about(version=True) or int(mc.about(version=True)[:5]) > 2016:
        maya_version = True
    choosenColor = (255, 255, 0)
    shapesList = ['circle', 'sphere', 'square', 'cube', 'triangle', 'octogone', 'half\nsphere', 'arrow', 'quad\narrow', 'quad\nbent\narrow', 'octo\narrow', 'cross', 'double\narrow', 'double\nbent\narrow', 'pyramide', 'diamond', 'arrow\nhead', 'dome', 'flat\ndome', 'cylinder','half\narrow\nhead', 'eye', 'locator', 'quater\ncircle', 'fly']
    shapesDict = {'circleNormal': [(0, 1, 0)],
                  'square': [(0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5)],
                  'quad\narrow': [(0, 0, -0.5), (0.2, 0, -0.3), (0.1, 0, -0.3), (0.1, 0, -0.1), (0.3, 0, -0.1), (0.3, 0, -0.2), (0.5, 0, 0), (0.3, 0, 0.2), (0.3, 0, 0.1), (0.1, 0, 0.1), (0.1, 0, 0.3), (0.2, 0, 0.3), (0, 0, 0.5), (-0.2, 0, 0.3), (-0.1, 0, 0.3), (-0.1, 0, 0.1), (-0.3, 0, 0.1), (-0.3, 0, 0.2), (-0.5, 0, 0), (-0.3, 0, -0.2), (-0.3, 0, -0.1), (-0.1, 0, -0.1), (-0.1, 0, -0.3), (-0.2, 0, -0.3), (0, 0, -0.5)],
                  'cross': [(0.25, 0, -0.25), (0.5, 0, -0.25), (0.5, 0, 0.25), (0.25, 0, 0.25), (0.25, 0, 0.5), (-0.25, 0, 0.5), (-0.25, 0, 0.25), (-0.5, 0, 0.25), (-0.5, 0, -0.25), (-0.25, 0, -0.25), (-0.25, 0, -0.5), (0.25, 0, -0.5), (0.25, 0, -0.25)],
                  'arrow\nhead': [(0, 0, 0), (0, 1.5, 0.5), (0, 1.5, -0.5), (0, 0, 0), (-0.5, 1.5, 0), (0, 1.5, 0), (0.5, 1.5, 0), (0, 0, 0)],
                  'cube': [(0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)],
                  'sphere': [(-0.5, 0, 0), (-0.483, -0.1295, 0), (-0.433, -0.25, 0), (-0.3535, -0.3535, 0), (-0.25, -0.433, 0), (-0.1295, -0.483, 0), (0, -0.5, 0), (0.1295, -0.483, 0), (0.25, -0.433, 0), (0.3535, -0.3535, 0), (0.433, -0.25, 0), (0.483, -0.1295, 0), (0.5, 0, 0), (0.483, 0.1295, 0), (0.433, 0.25, 0), (0.3535, 0.3535, 0), (0.25, 0.433, 0), (0.1295, 0.483, 0), (0, 0.5, 0), (-0.1295, 0.483, 0), (-0.25, 0.433, 0), (-0.3535, 0.3535, 0), (-0.433, 0.25, 0), (-0.483, 0.1295, 0), (-0.5, 0, 0), (-0.483, 0, 0.1295), (-0.433, 0, 0.25), (-0.3535, 0, 0.3535), (-0.25, 0, 0.433), (-0.1295, 0, 0.483), (0, 0, 0.5), (0.1295, 0, 0.483), (0.25, 0, 0.433), (0.3535, 0, 0.3535), (0.433, 0, 0.25), (0.483, 0, 0.1295), (0.5, 0, 0), (0.483, 0, -0.1295), (0.433, 0, -0.25), (0.3535, 0, -0.3535), (0.25, 0, -0.433), (0.1295, 0, -0.483), (0, 0, -0.5), (-0.1295, 0, -0.483), (-0.25, 0, -0.433), (-0.3535, 0, -0.3535), (-0.433, 0, -0.25), (-0.483, 0, -0.1295), (-0.5, 0, 0), (-0.483, 0, 0.1295), (-0.433, 0, 0.25), (-0.3535, 0, 0.3535), (-0.25, 0, 0.433), (-0.1295, 0, 0.483), (0, 0, 0.5), (0, 0.1295, 0.483), (0, 0.25, 0.433), (0, 0.3535, 0.3535), (0, 0.433, 0.25), (0, 0.483, 0.1295), (0, 0.5, 0), (0, 0.483, -0.1295), (0, 0.433, -0.25), (0, 0.3535, -0.3535), (0, 0.25, -0.433), (0, 0.1295, -0.483), (0, 0, -0.5), (0, -0.1295, -0.483), (0, -0.25, -0.433), (0, -0.3535, -0.3535), (0, -0.433, -0.25), (0, -0.483, -0.1295), (0, -0.5, 0), (0, -0.483, 0.1295), (0, -0.433, 0.25), (0, -0.3535, 0.3535), (0, -0.25, 0.433), (0, -0.1295, 0.483), (0, 0, 0.5)],
                  'quater\ncircle': [(0, 0, -0.5), (0.129, 0, -0.483), (0.25, 0, -0.433), (0.354, 0, -0.354), (0.433, 0, -0.25), (0.483, 0, -0.129), (0.5, 0, 0)],
                  'cylinder': [(0, -0.75, -0.5), (0, 0.75, -0.5), (-0.129, 0.75, -0.483), (-0.25, 0.75, -0.433), (-0.354, 0.75, -0.354), (-0.433, 0.75, -0.25), (-0.483, 0.75, -0.129), (-0.5, 0.75, 0), (-0.5, -0.75, 0), (-0.483, -0.75, 0.129), (-0.433, -0.75, 0.25), (-0.354, -0.75, 0.354), (-0.25, -0.75, 0.433), (-0.129, -0.75, 0.483), (0, -0.75, 0.5), (0, 0.75, 0.5), (0.129, 0.75, 0.483), (0.25, 0.75, 0.433), (0.354, 0.75, 0.354), (0.433, 0.75, 0.25), (0.483, 0.75, 0.129), (0.5, 0.75, 0), (0.5, -0.75, 0), (0.483, -0.75, -0.129), (0.433, -0.75, -0.25), (0.354, -0.75, -0.354), (0.25, -0.75, -0.433), (0.129, -0.75, -0.483), (0, -0.75, -0.5), (-0.129, -0.75, -0.483), (-0.25, -0.75, -0.433), (-0.354, -0.75, -0.354), (-0.433, -0.75, -0.25), (-0.483, -0.75, -0.129), (-0.5, -0.75, 0), (-0.483, -0.75, 0.129), (-0.433, -0.75, 0.25), (-0.354, -0.75, 0.354), (-0.25, -0.75, 0.433), (-0.129, -0.75, 0.483), (0, -0.75, 0.5), (0.129, -0.75, 0.483), (0.25, -0.75, 0.433), (0.354, -0.75, 0.354), (0.433, -0.75, 0.25), (0.483, -0.75, 0.129), (0.5, -0.75, 0), (0.5, 0.75, 0), (0.483, 0.75, -0.129), (0.433, 0.75, -0.25), (0.354, 0.75, -0.354), (0.25, 0.75, -0.433), (0.129, 0.75, -0.483), (0, 0.75, -0.5), (-0.129, 0.75, -0.483), (-0.25, 0.75, -0.433), (-0.354, 0.75, -0.354), (-0.433, 0.75, -0.25), (-0.483, 0.75, -0.129), (-0.5, 0.75, 0), (-0.483, 0.75, 0.129), (-0.433, 0.75, 0.25), (-0.354, 0.75, 0.354), (-0.25, 0.75, 0.433), (-0.129, 0.75, 0.483), (0, 0.75, 0.5)],
                  'double\narrow': [(0, -0.5, 0), (-0.25, -0.25, 0), (-0.125, -0.25, 0), (-0.125, 0.25, 0), (-0.25, 0.25, 0), (0, 0.5, 0), (0.25, 0.25, 0), (0.125, 0.25, 0), (0.125, -0.25, 0), (0.25, -0.25, 0), (0, -0.5, 0)],
                  'locator': [(0, 0, 0.5), (0, 0, -0.5), (0, 0, 0), (-0.5, 0, 0), (0.5, 0, 0), (0, 0, 0), (0, 0.5, 0), (0, -0.5, 0)],
                  'half\narrow\nhead': [(0, 0, 0), (-0.5, 1.5, 0), (0.5, 1.5, 0), (0, 0, 0), (0, 1.5, 0.5), (0, 1.5, 0), (0, 0, 0)],
                  'pyramide': [(-0.5, 1.5, -0.5), (0.5, 1.5, -0.5), (0, 0, 0), (0.5, 1.5, 0.5), (-0.5, 1.5, 0.5), (0, 0, 0), (-0.5, 1.5, -0.5), (-0.5, 1.5, 0.5), (0.5, 1.5, 0.5), (0.5, 1.5, -0.5)],
                  'diamond': [(0, 1, 0), (-0.5, 0, 0.5), (0, -1, 0), (0.5, 0, 0.5), (0, 1, 0), (0.5, 0, -0.5), (0, -1, 0), (-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5), (-0.5, 0, -0.5), (0, 1, 0)],
                  'half\nsphere': [(-0.5, 0, 0), (-0.483, 0.129, 0), (-0.433, 0.25, 0), (-0.354, 0.354, 0), (-0.25, 0.433, 0), (-0.129, 0.483, 0), (0, 0.5, 0), (0.129, 0.483, 0), (0.25, 0.433, 0), (0.354, 0.354, 0), (0.433, 0.25, 0), (0.483, 0.129, 0), (0.5, 0, 0), (0.483, 0, 0.129), (0.433, 0, 0.25), (0.354, 0, 0.354), (0.25, 0, 0.433), (0.129, 0, 0.483), (0, 0, 0.5), (0, 0.129, 0.483), (0, 0.25, 0.433), (0, 0.354, 0.354), (0, 0.433, 0.25), (0, 0.483, 0.129), (0, 0.5, 0), (0, 0.483, -0.129), (0, 0.433, -0.25), (0, 0.354, -0.354), (0, 0.25, -0.433), (0, 0.129, -0.483), (0, 0, -0.5), (0.129, 0, -0.483), (0.25, 0, -0.433), (0.354, 0, -0.354), (0.433, 0, -0.25), (0.483, 0, -0.129), (0.5, 0, 0), (0.483, 0, 0.129), (0.433, 0, 0.25), (0.354, 0, 0.354), (0.25, 0, 0.433), (0.129, 0, 0.483), (0, 0, 0.5), (-0.129, 0, 0.483), (-0.25, 0, 0.433), (-0.354, 0, 0.354), (-0.433, 0, 0.25), (-0.483, 0, 0.129), (-0.5, 0, 0), (-0.483, 0, -0.129), (-0.433, 0, -0.25), (-0.354, 0, -0.354), (-0.25, 0, -0.433), (-0.129, 0, -0.483), (0, 0, -0.5)],
                  'dome': [(-0.354, 0, -0.354), (-0.342, 0.129, -0.342), (-0.306, 0.25, -0.306), (-0.25, 0.354, -0.25), (-0.177, 0.433, -0.177), (-0.091, 0.483, -0.091), (0, 0.5, 0), (0.091, 0.483, 0.091), (0.177, 0.433, 0.177), (0.25, 0.354, 0.25), (0.306, 0.25, 0.306), (0.342, 0.129, 0.342), (0.354, 0, 0.354), (0.433, 0, 0.25), (0.483, 0, 0.129), (0.5, 0, 0), (0.483, 0.129, 0), (0.433, 0.25, 0), (0.354, 0.354, 0), (0.25, 0.433, 0), (0.129, 0.483, 0), (0, 0.5, 0), (-0.129, 0.483, 0), (-0.25, 0.433, 0), (-0.354, 0.354, 0), (-0.433, 0.25, 0), (-0.483, 0.129, 0), (-0.501, 0, 0), (-0.483, 0, 0.129), (-0.433, 0, 0.25), (-0.354, 0, 0.354), (-0.342, 0.129, 0.342), (-0.306, 0.25, 0.306), (-0.25, 0.354, 0.25), (-0.177, 0.433, 0.177), (-0.091, 0.483, 0.091), (0, 0.5, 0), (0.091, 0.483, -0.091), (0.177, 0.433, -0.177), (0.25, 0.354, -0.25), (0.306, 0.25, -0.306), (0.342, 0.129, -0.342), (0.354, 0, -0.354), (0.25, 0, -0.433), (0.129, 0, -0.483), (0, 0, -0.5), (0, 0.129, -0.483), (0, 0.25, -0.433), (0, 0.354, -0.354), (0, 0.433, -0.25), (0, 0.483, -0.129), (0, 0.5, 0), (0, 0.483, 0.129), (0, 0.433, 0.25), (0, 0.354, 0.354), (0, 0.25, 0.433), (0, 0.129, 0.483), (0, 0, 0.501), (0.129, 0, 0.483), (0.25, 0, 0.433), (0.354, 0, 0.354), (0.433, 0, 0.25), (0.483, 0, 0.129), (0.5, 0, 0), (0.483, 0, -0.129), (0.433, 0, -0.25), (0.354, 0, -0.354), (0.25, 0, -0.433), (0.129, 0, -0.483), (0, 0, -0.5), (-0.129, 0, -0.483), (-0.25, 0, -0.433), (-0.354, 0, -0.354), (-0.433, 0, -0.25), (-0.483, 0, -0.129), (-0.501, 0, 0), (-0.483, 0, 0.129), (-0.433, 0, 0.25), (-0.354, 0, 0.354), (-0.25, 0, 0.433), (-0.129, 0, 0.483), (0, 0, 0.501)],
                  'flat\ndome': [(-0.354, 0, -0.354), (0.354, 0, 0.354), (0.433, 0, 0.25), (0.483, 0, 0.129), (0.5, 0, 0), (-0.501, 0, 0), (-0.483, 0, 0.129), (-0.433, 0, 0.25), (-0.354, 0, 0.354), (0.354, 0, -0.354), (0.25, 0, -0.433), (0.129, 0, -0.483), (0, 0, -0.5), (0, 0, 0.501), (0.129, 0, 0.483), (0.25, 0, 0.433), (0.354, 0, 0.354), (0.433, 0, 0.25), (0.483, 0, 0.129), (0.5, 0, 0), (0.483, 0, -0.129), (0.433, 0, -0.25), (0.354, 0, -0.354), (0.25, 0, -0.433), (0.129, 0, -0.483), (0, 0, -0.5), (-0.129, 0, -0.483), (-0.25, 0, -0.433), (-0.354, 0, -0.354), (-0.433, 0, -0.25), (-0.483, 0, -0.129), (-0.501, 0, 0), (-0.483, 0, 0.129), (-0.433, 0, 0.25), (-0.354, 0, 0.354), (-0.25, 0, 0.433), (-0.129, 0, 0.483), (0, 0, 0.501)],
                  'eye': [(0, 0, -0.25), (0.064, 0, -0.242), (0.125, 0, -0.216), (0.177, 0, -0.177), (0.216, 0, -0.125), (0.242, 0, -0.064), (0.25, 0, 0), (0.242, 0, 0.064), (0.216, 0, 0.125), (0.177, 0, 0.177), (0.125, 0, 0.216), (0.064, 0, 0.242), (0, 0, 0.25), (-0.129, 0, 0.242), (-0.25, 0, 0.216), (-0.354, 0, 0.177), (-0.433, 0, 0.125), (-0.483, 0, 0.064), (-0.5, 0, 0), (-0.483, 0, -0.064), (-0.433, 0, -0.125), (-0.354, 0, -0.177), (-0.25, 0, -0.216), (-0.129, 0, -0.242), (0, 0, -0.25), (0.129, 0, -0.242), (0.25, 0, -0.216), (0.354, 0, -0.177), (0.433, 0, -0.125), (0.483, 0, -0.064), (0.5, 0, 0), (0.483, 0, 0.064), (0.433, 0, 0.125), (0.354, 0, 0.177), (0.25, 0, 0.216), (0.129, 0, 0.242), (0, 0, 0.25), (-0.064, 0, 0.242), (-0.125, 0, 0.216), (-0.177, 0, 0.177), (-0.216, 0, 0.125), (-0.242, 0, 0.064), (-0.25, 0, 0), (-0.242, 0, -0.064), (-0.216, 0, -0.125), (-0.177, 0, -0.177), (-0.125, 0, -0.216), (-0.064, 0, -0.242), (0, 0, -0.25)],
                  'triangle': [(0.5, 0, 0.289), (-0.5, 0, 0.289), (0, 0, -0.577), (0.5, 0, 0.289)],
                  'octogone': [(0, 0, -0.5), (0.354, 0, -0.354), (0.5, 0, 0), (0.354, 0, 0.354), (0, 0, 0.5), (-0.354, 0, 0.354), (-0.5, 0, 0), (-0.354, 0, -0.354), (0, 0, -0.5)],
                  'double\nbent\narrow': [(0.5, 0, 0), (0.449, 0.047, 0.069), (0.393, 0.088, 0.139), (0.333, 0.124, 0.208), (0.271, 0.153, 0.278), (0.271, 0.153, 0.139), (0.205, 0.177, 0.139), (0.138, 0.194, 0.139), (0.069, 0.204, 0.139), (0, 0.207, 0.139), (-0.069, 0.204, 0.139), (-0.138, 0.194, 0.139), (-0.205, 0.177, 0.139), (-0.271, 0.153, 0.139), (-0.271, 0.153, 0.278), (-0.333, 0.124, 0.208), (-0.393, 0.088, 0.139), (-0.449, 0.047, 0.069), (-0.5, 0, 0), (-0.449, 0.047, -0.069), (-0.393, 0.088, -0.139), (-0.333, 0.124, -0.208), (-0.271, 0.153, -0.278), (-0.271, 0.153, -0.139), (-0.205, 0.177, -0.139), (-0.138, 0.194, -0.139), (-0.069, 0.204, -0.139), (0, 0.207, -0.139), (0.069, 0.204, -0.139), (0.138, 0.194, -0.139), (0.205, 0.177, -0.139), (0.271, 0.153, -0.139), (0.271, 0.153, -0.278), (0.333, 0.124, -0.208), (0.393, 0.088, -0.139), (0.449, 0.047, -0.069), (0.5, 0, 0)],
                  'quad\nbent\narrow': [(-0.1106, 0.1898, 0.1093), (-0.1106, 0.1746, 0.1808), (-0.1106, 0.152, 0.2503), (-0.1106, 0.1223, 0.3171), (-0.1651, 0.1126, 0.3122), (-0.2185, 0.0992, 0.3053), (-0.1651, 0.0862, 0.3593), (-0.1106, 0.065, 0.4105), (-0.0555, 0.036, 0.4578), (0, 0, 0.5), (0.0555, 0.036, 0.4578), (0.1106, 0.065, 0.4105), (0.1651, 0.0862, 0.3593), (0.2185, 0.0992, 0.3053), (0.1651, 0.1126, 0.3122), (0.1106, 0.1223, 0.3171), (0.1106, 0.152, 0.2503), (0.1106, 0.1746, 0.1808), (0.1106, 0.1898, 0.1093), (0.183, 0.1746, 0.1068), (0.2534, 0.152, 0.1033), (0.321, 0.1223, 0.0986), (0.321, 0.1126, 0.1471), (0.321, 0.0992, 0.1947), (0.3695, 0.0862, 0.1407), (0.4156, 0.065, 0.0895), (0.4592, 0.036, 0.0422), (0.5, 0, 0), (0.4592, 0.036, -0.0422), (0.4156, 0.065, -0.0895), (0.3695, 0.0862, -0.1407), (0.321, 0.0992, -0.1947), (0.321, 0.1126, -0.1471), (0.321, 0.1223, -0.0986), (0.2534, 0.152, -0.1033), (0.183, 0.1746, -0.1068), (0.1106, 0.1898, -0.1093), (0.1106, 0.1746, -0.1808), (0.1106, 0.152, -0.2503), (0.1106, 0.1223, -0.3171), (0.1651, 0.1126, -0.3122), (0.2185, 0.0992, -0.3053), (0.1651, 0.0862, -0.3593), (0.1106, 0.065, -0.4105), (0.0555, 0.036, -0.4578), (0, 0, -0.5), (-0.0555, 0.036, -0.4578), (-0.1106, 0.065, -0.4105), (-0.1651, 0.0862, -0.3593), (-0.2185, 0.0992, -0.3053), (-0.1651, 0.1126, -0.3122), (-0.1106, 0.1223, -0.3171), (-0.1106, 0.152, -0.2503), (-0.1106, 0.1746, -0.1808), (-0.1106, 0.1898, -0.1093), (-0.183, 0.1746, -0.1068), (-0.2534, 0.152, -0.1033), (-0.321, 0.1223, -0.0986), (-0.321, 0.1126, -0.1471), (-0.321, 0.0992, -0.1947), (-0.3695, 0.0862, -0.1407), (-0.4156, 0.065, -0.0895), (-0.4592, 0.036, -0.0422), (-0.5, 0, 0), (-0.4592, 0.036, 0.0422), (-0.4156, 0.065, 0.0895), (-0.3695, 0.0862, 0.1407), (-0.321, 0.0992, 0.1947), (-0.321, 0.1126, 0.1471), (-0.321, 0.1223, 0.0986), (-0.2534, 0.152, 0.1033), (-0.183, 0.1746, 0.1068), (-0.1106, 0.1898, 0.1093)],
                  'arrow': [(0.125, 0.625, 0), (0.125, 0.25, 0), (0.25, 0.25, 0), (0, 0, 0), (-0.25, 0.25, 0), (-0.125, 0.25, 0), (-0.125, 0.625, 0), (0.125, 0.625, 0)],
                  'octo\narrow': [(0.2357, 0, 0.3143), (0.0556, 0, 0.1341), (0.0556, 0, 0.3889), (0.1111, 0, 0.3889), (0, 0, 0.5), (-0.1111, 0, 0.3889), (-0.0556, 0, 0.3889), (-0.0556, 0, 0.1341), (-0.2357, 0, 0.3143), (-0.1964, 0, 0.3536), (-0.3536, 0, 0.3536), (-0.3536, 0, 0.1964), (-0.3143, 0, 0.2357), (-0.1341, 0, 0.0556), (-0.3889, 0, 0.0556), (-0.3889, 0, 0.1111), (-0.5, 0, 0), (-0.3889, 0, -0.1111), (-0.3889, 0, -0.0556), (-0.1341, 0, -0.0556), (-0.3143, 0, -0.2357), (-0.3536, 0, -0.1964), (-0.3536, 0, -0.3536), (-0.1964, 0, -0.3536), (-0.2357, 0, -0.3143), (-0.0556, 0, -0.1341), (-0.0556, 0, -0.3889), (-0.1111, 0, -0.3889), (0, 0, -0.5), (0.1111, 0, -0.3889), (0.0556, 0, -0.3889), (0.0556, 0, -0.1341), (0.2357, 0, -0.3143), (0.1964, 0, -0.3536), (0.3536, 0, -0.3536), (0.3536, 0, -0.1964), (0.3143, 0, -0.2357), (0.1341, 0, -0.0556), (0.3889, 0, -0.0556), (0.3889, 0, -0.1111), (0.5, 0, 0), (0.3889, 0, 0.1111), (0.3889, 0, 0.0556), (0.1341, 0, 0.0556), (0.3143, 0, 0.2357), (0.3536, 0, 0.1964), (0.3536, 0, 0.3536), (0.1964, 0, 0.3536), (0.2357, 0, 0.3143)],
                  'fly': [(0, 0.157, 0), (-0.078, 0.047, 0), (-0.005, 0.047, 0), (-0.009, -0.004, 0), (-0.049, -0.004, 0), (-0.095, -0.001, 0), (-0.144, 0.011, 0), (-0.185, 0.034, 0), (-0.215, 0.07, 0), (-0.232, 0.113, 0), (-0.237, 0.159, 0), (-0.237, 0.221, 0), (-0.5, 0.243, 0), (-0.451, 0.173, 0), (-0.264, 0.157, 0), (-0.262, 0.113, 0), (-0.455, 0.072, 0), (-0.404, 0.027, 0), (-0.25, 0.058, 0), (-0.24, 0.037, 0), (-0.229, 0.021, 0), (-0.349, -0.062, 0), (-0.284, -0.083, 0), (-0.186, -0.018, 0), (-0.167, -0.029, 0), (-0.149, -0.036, 0), (-0.195, -0.132, 0), (-0.127, -0.119, 0), (-0.09, -0.046, 0), (-0.016, -0.046, 0), (-0.022, -0.078, 0), (-0.038, -0.113, 0), (-0.067, -0.148, 0), (0, -0.243, 0), (0.067, -0.148, 0), (0.038, -0.113, 0), (0.022, -0.078, 0), (0.016, -0.046, 0), (0.09, -0.046, 0), (0.127, -0.119, 0), (0.195, -0.132, 0), (0.149, -0.036, 0), (0.167, -0.029, 0), (0.186, -0.018, 0), (0.284, -0.083, 0), (0.349, -0.062, 0), (0.229, 0.021, 0), (0.24, 0.037, 0), (0.25, 0.058, 0), (0.404, 0.027, 0), (0.455, 0.072, 0), (0.262, 0.113, 0), (0.264, 0.157, 0), (0.451, 0.173, 0), (0.5, 0.243, 0), (0.237, 0.221, 0), (0.237, 0.159, 0), (0.232, 0.113, 0), (0.215, 0.07, 0), (0.185, 0.034, 0), (0.144, 0.011, 0), (0.095, -0.001, 0), (0.049, -0.004, 0), (0.009, -0.004, 0), (0.005, 0.047, 0), (0.078, 0.047, 0), (0, 0.157, 0)],
                  }

    def __init__(self, parent=getMayaWin()):
        super(RlShapes_ui, self).__init__(parent)

        self.setWindowTitle('rlShape Creator')
        self.setObjectName('rlShapeCreator')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.ui_layout()
        self.ui_connection()
        if mc.ls(sl=1):
            self.get_curve_color()

    def ui_layout(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # Shapes menu layout
        self.shapesMenuLayout = QtGui.QHBoxLayout()
        self.shapesMenuLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.shapesMenuLayout.setSpacing(0)
        self.mainLayout.addLayout(self.shapesMenuLayout)
        # Shape Menu Button Font
        self.shapeMenuButtonFont = QtGui.QFont()
        self.shapeMenuButtonFont.setPointSize(6)
        self.shapeMenuButtonFont.setBold(True)
        # Shapes Menu Button
        self.shapeMenuButton = QtGui.QPushButton('V')
        self.shapeMenuButton.setFont(self.shapeMenuButtonFont)
        self.shapeMenuButton.setFixedSize(15, 20)
        self.shapeMenuButton.setFlat(True)
        self.shapesMenuLayout.addWidget(self.shapeMenuButton)
        # Shape Menu Label Font
        self.shapeMenuLabelFont = QtGui.QFont()
        self.shapeMenuLabelFont.setPointSize(7)
        self.shapeMenuLabelFont.setBold(True)
        # Shapes Menu Label
        self.shapeMenuLabelButton = QtGui.QPushButton('Shapes')
        self.shapeMenuLabelButton.setFixedSize(50, 20)
        self.shapeMenuLabelButton.setFlat(True)
        self.shapeMenuLabelButton.setFont(self.shapeMenuLabelFont)
        self.shapesMenuLayout.addWidget(self.shapeMenuLabelButton)

        # Shapes buttons Layout Widget
        self.shapeLayoutWidget = QtGui.QWidget()
        self.mainLayout.addWidget(self.shapeLayoutWidget)
        # Shapes buttons Layout
        self.shapeLayout = QtGui.QGridLayout()
        self.shapeLayoutWidget.setLayout(self.shapeLayout)
        row = 0
        column = 0.0
        shapeDone = 0
        while shapeDone < len(self.shapesList):
            if column < ceil(sqrt(len(self.shapesList))):
                self.shapeButton = QtGui.QPushButton(self.shapesList[shapeDone])
                self.shapeButton.setObjectName('btn_'+self.shapesList[shapeDone])
                self.shapeButton.setFixedSize(55, 55)
                self.shapeLayout.addWidget(self.shapeButton, row, column)
                column += 1
                shapeDone += 1
            else:
                column = 0
                row += 1

        # Shape Options
        self.replaceColorLayout = QtGui.QHBoxLayout()
        self.replaceColorLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addLayout(self.replaceColorLayout)
        # Replace checkbox
        self.replaceCheckBox = QtGui.QCheckBox('Replace')
        self.replaceCheckBox.setChecked(True)
        self.replaceColorLayout.addWidget(self.replaceCheckBox)
        # Separator
        self.vSeparator = QtGui.QLabel()
        self.vSeparator.setFrameStyle(QtGui.QFrame.VLine)
        self.replaceColorLayout.addWidget(self.vSeparator)
        # Color Picker
        self.colorLabel = QtGui.QLabel(' Color  :')
        self.replaceColorLayout.addWidget(self.colorLabel)
        self.colorButton = QtGui.QPushButton()
        self.colorButton.setStyleSheet('background-color: rgb' + str(self.choosenColor))
        self.colorButton.setFixedSize(50, 20)
        self.replaceColorLayout.addWidget(self.colorButton)
        # Apply Color button
        self.applyColorButton = QtGui.QPushButton('Apply Color')
        self.replaceColorLayout.addWidget(self.applyColorButton)
        # Get color button
        self.getColorButton = QtGui.QPushButton('Get')
        self.getColorButton.setFixedWidth(30)
        self.getColorButton.setToolTip('Get the color of the selected curve')
        self.replaceColorLayout.addWidget(self.getColorButton)

        # Size Layout
        self.sizeLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.sizeLayout)
        # Size Label
        self.sizeLabel = QtGui.QLabel(' Size :  ')
        self.sizeLayout.addWidget(self.sizeLabel)
        # Size Value
        self.sizeLineEdit = QtGui.QLineEdit('2')
        self.sizeLineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
        self.sizeLineEdit.setMaximumWidth(40)
        self.sizeLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.sizeLayout.addWidget(self.sizeLineEdit)
        # Size Slider
        self.sizeSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sizeSlider.setValue(2)
        self.sizeSlider.setMaximum(10)
        self.sizeSlider.setMinimum(1)
        self.sizeLayout.addWidget(self.sizeSlider)

        if self.maya_version:
            # Width Layout
            self.widthLayout = QtGui.QHBoxLayout()
            self.mainLayout.addLayout(self.widthLayout)
            # Width Label
            self.widthLabel = QtGui.QLabel(' Width :')
            self.widthLayout.addWidget(self.widthLabel)
            # Width Value
            self.widthLineEdit = QtGui.QLineEdit('1')
            self.widthLineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
            self.widthLineEdit.setMaximumWidth(40)
            self.widthLineEdit.setAlignment(QtCore.Qt.AlignCenter)
            self.widthLayout.addWidget(self.widthLineEdit)
            # Width Slider
            self.widthSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
            self.widthSlider.setValue(1)
            self.widthSlider.setMaximum(10)
            self.widthSlider.setMinimum(1)
            self.widthLayout.addWidget(self.widthSlider)
            # Width apply
            self.widthButton = QtGui.QPushButton('Apply')
            self.widthButton.setToolTip('Apply width on selected curves')
            self.widthButton.setFixedWidth(40)
            self.widthLayout.addWidget(self.widthButton)

        # Axis Twist layout
        self.axisTwistLayout = QtGui.QHBoxLayout()
        self.axisTwistLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addLayout(self.axisTwistLayout)
        # Axis Label
        self.axisLabel = QtGui.QLabel('Axis :')
        self.axisLabel.setFixedWidth(35)
        self.axisTwistLayout.addWidget(self.axisLabel)
        # radio Buttons
        self.axisButtonGroup = QtGui.QButtonGroup()
        for axis in 'xyz':
            self.radioButton = QtGui.QRadioButton(axis)
            self.radioButton.setFixedWidth(35)
            if axis == 'y':
                self.radioButton.setChecked(True)
            self.axisTwistLayout.addWidget(self.radioButton)
            self.axisButtonGroup.addButton(self.radioButton)
        # reverse checkbox
        self.reverseCheckBox = QtGui.QCheckBox('Reverse')
        self.reverseCheckBox.setFixedWidth(65)
        self.axisTwistLayout.addWidget(self.reverseCheckBox)
        # Separator
        self.vSeparator = QtGui.QFrame()
        self.vSeparator.setFrameStyle(QtGui.QFrame.VLine)
        self.vSeparator.setFixedWidth(10)
        self.axisTwistLayout.addWidget(self.vSeparator)
        # TwistLabel
        self.twistLabel = QtGui.QLabel('Twist ')
        self.twistLabel.setFixedWidth(30)
        self.axisTwistLayout.addWidget(self.twistLabel)
        # Twist Value
        self.twistLineEdit = QtGui.QLineEdit('0')
        self.twistLineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[\d]{1,3}[.][\d]{0,3}')))
        self.twistLineEdit.setMaximumWidth(40)
        self.twistLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.axisTwistLayout.addWidget(self.twistLineEdit)

        # Separator line
        self.hSeparator = QtGui.QFrame()
        self.hSeparator.setFrameStyle(QtGui.QFrame.HLine)
        self.mainLayout.addWidget(self.hSeparator)

        # Main Mirror Layout
        self.mainMirrorLayout = QtGui.QHBoxLayout()
        self.mainMirrorLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLayout.addLayout(self.mainMirrorLayout)
        # Mirror buttons layout
        self.mirrorButtonsLayout = QtGui.QVBoxLayout()
        self.mirrorButtonsLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mainMirrorLayout.addLayout(self.mirrorButtonsLayout)
        # Mirror solo button Layout
        self.mirrorSoloLayout = QtGui.QHBoxLayout()
        self.mirrorSoloLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.mirrorButtonsLayout.addLayout(self.mirrorSoloLayout)
        # Mirror Label
        self.mirrorLabel = QtGui.QLabel('Mirror :')
        self.mirrorSoloLayout.addWidget(self.mirrorLabel)
        # Mirror button
        for axe in 'XYZ':
            self.mirrorButton = QtGui.QPushButton(axe)
            self.mirrorButton.setObjectName('mirrorButton{}'.format(axe))
            self.mirrorButton.setFixedSize(25, 20)
            self.mirrorSoloLayout.addWidget(self.mirrorButton)
        # Mirror other side
        self.sideMirror = QtGui.QPushButton('Mirror other side')
        self.sideMirror.setFixedWidth(145)
        self.mirrorButtonsLayout.addWidget(self.sideMirror)
        # Copy shape button
        self.copyButton = QtGui.QPushButton('Copy Shapes')
        self.copyButton.setFixedWidth(145)
        self.mirrorButtonsLayout.addWidget(self.copyButton)
        # Separator Layout
        self.separatorLayout = QtGui.QVBoxLayout()
        self.mainMirrorLayout.addLayout(self.separatorLayout)
        # Separator line
        for sep in range(6):
            self.hSeparator = QtGui.QFrame()
            self.hSeparator.setFrameStyle(QtGui.QFrame.VLine)
            self.separatorLayout.addWidget(self.hSeparator)
        # Mirror Space
        self.spaceCheckBox = QtGui.QCheckBox('Object space')
        self.spaceCheckBox.setObjectName('objectSpace')
        self.spaceCheckBox.setChecked(True)
        self.spaceCheckBox.setFixedWidth(100)
        self.mainMirrorLayout.addWidget(self.spaceCheckBox)

        # Separator line
        self.hSeparator = QtGui.QFrame()
        self.hSeparator.setFrameStyle(QtGui.QFrame.HLine)
        self.mainLayout.addWidget(self.hSeparator)

        # Parent shape button
        self.parentButton = QtGui.QPushButton('Parent Shapes')
        self.mainLayout.addWidget(self.parentButton)

    def ui_connection(self):
        # Shapes
        self.shapeMenuButton.clicked.connect(self.shapes_hide)
        self.shapeMenuLabelButton.clicked.connect(self.shapes_hide)
        for buttonIndex in range(len(self.shapesList)):
            shape = self.shapesList[buttonIndex]
            self.shapeButton = self.findChild(QtGui.QPushButton, 'btn_'+shape)
            self.shapeButton.clicked.connect(partial(self.init_do_shape, shape))

        # Shape options
        self.colorButton.clicked.connect(self.get_picker_color)
        self.applyColorButton.clicked.connect(self.apply_color)
        self.getColorButton.clicked.connect(self.get_curve_color)
        # Size Slider
        self.sizeSlider.valueChanged.connect(self.sizeSlider_update)
        # Size LineEdit
        self.sizeLineEdit.textEdited.connect(self.sizeLineEdit_update)
        if self.maya_version:
            # Width Slider
            self.widthSlider.valueChanged.connect(self.widthSlider_update)
            # Width LineEdit
            self.widthLineEdit.textEdited.connect(self.widthLineEdit_update)
            # Width Button
            self.widthButton.clicked.connect(self.apply_width)

        # Mirror buttons
        self.mirbuttX = self.findChild(QtGui.QPushButton, 'mirrorButtonX')
        self.mirbuttX.clicked.connect(partial(self.mirror_signal, 'x'))
        self.mirbuttY = self.findChild(QtGui.QPushButton, 'mirrorButtonY')
        self.mirbuttY.clicked.connect(partial(self.mirror_signal, 'y'))
        self.mirbuttZ = self.findChild(QtGui.QPushButton, 'mirrorButtonZ')
        self.mirbuttZ.clicked.connect(partial(self.mirror_signal, 'z'))

        # Tools
        self.sideMirror.clicked.connect(self.sideMirror_signal)
        self.copyButton.clicked.connect(self.copy_signal)
        self.parentButton.clicked.connect(parent_shape)

    def shapes_hide(self):
        if self.shapeMenuButton.text() == 'V':
            self.shapeLayoutWidget.hide()
            self.shapeMenuButton.setText('>')
            self.shapeMenuButtonFont.setPointSize(9)
            self.shapeMenuButton.setFont(self.shapeMenuButtonFont)
            self.adjustSize()
        else:
            self.shapeMenuButton.setText('V')
            self.shapeMenuButtonFont.setPointSize(6)
            self.shapeMenuButton.setFont(self.shapeMenuButtonFont)
            self.shapeLayoutWidget.show()

    def sizeSlider_update(self):
        value = self.sizeSlider.value()
        self.sizeLineEdit.setText(str(value))

    def sizeLineEdit_update(self):
        value = self.sizeLineEdit.text()
        if float(value) > 10:
            if float(value) < 500:
                self.sizeSlider.setMaximum(float(value)*2)
            else:
                self.sizeSlider.setMaximum(1000)
        else:
            self.sizeSlider.setMaximum(10)
        self.sizeSlider.setValue(float(value))

    def widthSlider_update(self):
        value = self.widthSlider.value()
        self.widthLineEdit.setText(str(value))

    def widthLineEdit_update(self):
        value = self.widthLineEdit.text()
        if float(value) > 10:
            if float(value) < 500:
                self.widthSlider.setMaximum(float(value)*2)
            else:
                self.widthSlider.setMaximum(1000)
        else:
            self.widthSlider.setMaximum(10)
        self.widthSlider.setValue(float(value))

    def apply_width(self):
        crvs = [x for x in mc.ls(sl=True) if ('nurbsCurve' in mc.nodeType(x, i=True) or 'transform' in mc.nodeType(x, i=True)) and '.' not in x]
        width = float(self.widthLineEdit.text())
        for crv in crvs:
            if 'transform' in mc.nodeType(crv, i=True):
                shps = [x for x in get_shape(crv) if 'nurbsCurve' in mc.nodeType(x, i=True)]
                for shp in shps:
                    mc.setAttr(shp+'.lineWidth', width)
            else:
                mc.setAttr(crv+'.lineWidth', width)

    def mirror_signal(self, axis):
        mc.undoInfo(openChunk=True)
        space = self.findChild(QtGui.QCheckBox, 'objectSpace')
        ws = not space.isChecked()
        shapeMirror.do_shapeMirror(miraxis=axis, ws=ws, solo=True)
        mc.undoInfo(closeChunk=True)

    def sideMirror_signal(self):
        space = self.findChild(QtGui.QCheckBox, 'objectSpace')
        ws = not space.isChecked()
        shapeMirror.do_shapeMirror(ws=ws)

    def copy_signal(self):
        space = self.findChild(QtGui.QCheckBox, 'objectSpace')
        ws = not space.isChecked()
        shapeMirror.do_shapeMirror(ws=ws, copy=True)

    def get_picker_color(self):
        self.colorItem = QtGui.QColor()
        self.colorItem.setRgb(*self.choosenColor)
        self.colorPicker = QtGui.QColorDialog()
        self.colorItem = self.colorPicker.getColor(self.colorItem)
        if self.colorItem.isValid():
            RlShapes_ui.choosenColor = self.colorItem.getRgb()
            self.colorButton.setStyleSheet('background-color: rgb' + str(tuple(self.choosenColor)))

    def apply_color(self, crvs=None):
        def do_apply_color(shp, color):
            mc.setAttr(shp+'.overrideEnabled', True)
            mc.setAttr(shp+'.overrideRGBColors', True)
            mc.setAttr(shp+'.overrideColorRGB', *color)

        if not crvs:
            crvs = [x for x in mc.ls(sl=True) if ('geometryShape' in mc.nodeType(x, i=True) or 'transform' in mc.nodeType(x, i=True)) and '.' not in x]
        rgb_color = self.choosenColor
        rgb_color = [x/255.0 for x in rgb_color]
        for crv in crvs:
            if 'geometryShape' in mc.nodeType(crv, i=True):
                do_apply_color(crv, rgb_color)
            else:
                if get_shape(crv):
                    shapes = get_shape(crv)
                    for shape in shapes:
                        if 'geometryShape' in mc.nodeType(shape, i=True):
                            do_apply_color(shape, rgb_color[:3])

    def get_curve_color(self):

        def getColor(node):
            if mc.getAttr(node+'.overrideEnabled'):
                if mc.getAttr(node+'.overrideRGBColors'):
                    node_color = mc.getAttr(node+'.overrideColorRGB')[0]
                    node_color = [x*255 for x in node_color]
                    return node_color
                else:
                    color_index = mc.getAttr(node+'.overrideColor')
                    rgb_color = mc.colorIndex(color_index, q=True)
                    node_color = [x*255 for x in rgb_color]
                    return node_color
            else:
                parent = mc.listRelatives(node, parent=True, fullPath=True) or []
                if not parent:
                    return
                return getColor(parent[0])

        sel = [x for x in mc.ls(sl=True)
               if ('geometryShape' in mc.nodeType(x, i=True) or 'transform' in mc.nodeType(x, i=True)) and '.' not in x]
        if not sel:
            return
        obj = sel[0]
        if 'transform' in mc.nodeType(obj, i=True):
            if get_shape(obj):
                obj = get_shape(obj)[0]
        color = getColor(obj)
        if color:
            RlShapes_ui.choosenColor = color
            self.colorButton.setStyleSheet('background-color: rgb' + str(tuple(self.choosenColor)))

    def init_do_shape(self, shape):
        mc.undoInfo(openChunk=True)
        sel = [x for x in mc.ls(sl=True) if 'transform' in mc.nodeType(x, i=True)]
        if not sel:
            crv = self.do_shape(shape)
            mc.select(crv)
        else:
            replace = self.replaceCheckBox.isChecked()
            for i in sel:
                crv = self.do_shape(shape)
                crv_shape = get_shape(crv)
                if not replace:
                    parent_shape(i, crv_shape)
                    mc.delete(crv)
                else:
                    sel_shape = get_shape(i)
                    [mc.delete(x) for x in sel_shape if 'nurbsCurve' in mc.nodeType(x, i=True)]
                    parent_shape(i, crv_shape)
                    mc.delete(crv)
            mc.select(sel)
        mc.undoInfo(closeChunk=True)

    def do_shape(self, shape):
        size = float(self.sizeLineEdit.text())
        if shape == 'circle':
            nr = self.confo_axis('circleNormal')[0]
            crv = mc.circle(nr=nr, r=size/2.0, ch=False)[0]
        else:
            p = self.confo_axis(shape)
            p = [(x * size, y * size, z * size) for x, y, z in p]
            crv = mc.curve(d=1, p=p, n=shape+'#')
        if self.maya_version:
            width = float(self.widthLineEdit.text())
            mc.setAttr(crv+'.lineWidth', width)
        self.apply_color([crv])
        self.do_twist(crv)
        return crv

    def confo_axis(self, shape):
        axis = self.axisButtonGroup.checkedButton().text()
        p = self.shapesDict[shape]
        if self.reverseCheckBox.isChecked():
            p = [(x, -y, z) for x, y, z in p]
        if axis == 'x':
            p = [(y, z, x) for x, y, z in p]
        elif axis == 'z':
            p = [(z, x, y) for x, y, z in p]
        return p

    def do_twist(self, crv):
        twist_val = float(self.twistLineEdit.text())
        nb = mc.getAttr(crv+'.degree') + mc.getAttr(crv+'.spans')
        axis = self.axisButtonGroup.checkedButton().text()
        if axis == 'x':
            value = (twist_val, 0, 0)
        elif axis == 'z':
            value = (0, 0, twist_val)
        else:
            value = (0, twist_val, 0)
        mc.select(crv+'.cv[:'+str(nb)+']')
        mc.rotate(*value, os=True)


def parent_shape(parent=None, childs=None, freeze=False):

    mc.undoInfo(openChunk=True)
    if not parent or not childs:
        sel = mc.ls(sl=True)
        if len(sel) < 2:
            mc.warning('Select a shape and a parent transform')
            mc.undoInfo(closeChunk=True)
            return
        childs = sel[:-1]
        parent = sel[-1]
    for child in childs:
        if not (mc.nodeType(parent) == 'transform' or mc.nodeType(parent) == 'joint'):
            mc.warning('Select a shape and a parent transform')
            mc.undoInfo(closeChunk=True)
            return
        if parent in (mc.listRelatives(child, parent=True) or []):
            mc.warning(child+' is already a child of '+parent)
            mc.undoInfo(closeChunk=True)
            return
        if freeze:
            child_parent = mc.listRelatives(child, parent=True)[0]
            child_grd_parent = mc.listRelatives(child_parent, parent=True) or []
            child_parent_t = mc.xform(child_parent, q=True, ws=True, t=True)
            child_parent_ro = mc.xform(child_parent, q=True, ws=True, ro=True)
            child_parent_s = mc.xform(child_parent, q=True, ws=True, s=True)
            grp_freeze = mc.group(n='grpfreeze#', em=True, w=True)
            mc.parent(grp_freeze, parent, r=True)
            mc.parent(child_parent, grp_freeze)
            mc.parent(grp_freeze, w=True)
            for j in 'xyz':
                for i in 'tr':
                    mc.setAttr(grp_freeze+'.'+i+j, 0)
                mc.setAttr(grp_freeze+'.s'+j, 1)
            mc.makeIdentity(child_parent, a=True)

        mc.parent(child, parent, r=True, s=True)

        if freeze:
            if child_grd_parent:
                mc.parent(child_parent, child_grd_parent[0])
            else:
                mc.parent(child_parent, w=True)
            mc.delete(mc.parentConstraint(grp_freeze, child_parent, mo=False))
            mc.makeIdentity(child_parent, a=True)
            mc.xform(child_parent, ro=child_parent_ro, t=child_parent_t, s=child_parent_s, ws=True)
            mc.delete(grp_freeze)
    mc.undoInfo(closeChunk=True)
