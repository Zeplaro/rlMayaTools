import maya.cmds as mc
import importlib
from rig.yama.nodes import depend as dpn

class_dict = {'skinCluster': ('skinCluster', 'SkinCluster'),
              'shape': ('shape', 'Shape'),
              'mesh': ('shape', 'Mesh'),
              'geometryFilter': ('geometryFilter', 'GeometryFilter'),
              'weightGeometryFilter': ('geometryFilter', 'WeightGeometryFilter'),
              'transform': ('transform', 'Transform'),
              'joint': ('transform', 'Joint'),
              }


def node_to_class(node):
    for node_type in mc.nodeType(node, i=True)[::-1]:
        if node_type in class_dict:
            lib = importlib.import_module('yama.' + class_dict[node_type][0])
            return lib.__getattribute__(class_dict[node_type][1])(node)
    return dpn.Depend(node)


nts = node_to_class


def nodes_to_classes(nodes):
    return [node_to_class(node) for node in nodes]
