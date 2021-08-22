# encoding: utf8

import importlib
import maya.cmds as mc
from yama import attribute

try:
    basestring
except NameError:
    basestring = str


"""
Lists the supported types of maya nodes. Any new node class should be added to this list to be able to get it from the 
node_to_class method.
When adding a new class follow this syntax ->   'mayaType': ('fileContainingTheClass', 'ClassName')
"""


def yam(node):
    """
    Handles all node class assignment to assign the proper class depending on the node type.
    todo : link class to openMaya mObject instead of string
    todo : make it works when an attribute is given.

    exemples :
    >> yam('skincluster42')
    SkinCluster('skincluster42')

    todo:
    >> yam('null0.translateX')
    Attribute('null0.translateX')
    """

    suported_class = {'skinCluster': ('skinCluster', 'SkinCluster'),
                      'shape': ('shape', 'Shape'),
                      'mesh': ('shape', 'Mesh'),
                      'nurbsCurve': ('shape', 'NurbsCurve'),
                      'geometryFilter': ('geometryFilter', 'GeometryFilter'),
                      'weightGeometryFilter': ('geometryFilter', 'WeightGeometryFilter'),
                      'blendShape': ('blendShape', 'BlendShape'),
                      'transform': ('transform', 'Transform'),
                      'joint': ('transform', 'Joint'),
                      }
    for node_type in mc.nodeType(node, i=True)[::-1]:
        if node_type in suported_class:
            lib = importlib.import_module(suported_class[node_type][0])
            return lib.__getattribute__(suported_class[node_type][1])(node)
    return DependNode(node)


def yams(nodes):
    return [yam(node) for node in nodes]


class YamNode(object):
    # TODO
    pass


class DependNode(YamNode):
    # todo : link to openMaya mObject instead of string
    def __init__(self, name):
        super(DependNode, self).__init__()
        if not mc.objExists(name):
            raise Exception("{} does not exist in scene".format(name))
        self._name = name
        self._type_inheritance = mc.nodeType(name, i=True)

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self._name)

    def __str__(self):
        return self._name

    def __getattr__(self, attr):
        return self.attr(attr)

    def __radd__(self, other):
        if isinstance(other, basestring):
            return other.__add__(self.name)
        else:
            raise TypeError("connot concatenate '{}' and '{}' objects".format(other.__class__.__name,
                                                                              self.__class__.__name__))

    def attr(self, attr):
        return attribute.Attr(self, attr)

    @property
    def name(self):
        return self._name

    def listRelatives(self, *args, **kwargs):
        return yams(mc.listRelatives(self, *args, **kwargs) or [])

    def type(self):
        return mc.getAttr(self, type=True)
