import maya.cmds as mc
import importlib
import depend as dpn


"""
Lists the supported types of maya nodes. Any new node class should be added to this list to be able to get it from the 
node_to_class method.
When adding a new class follow this syntax ->   'mayaType': ('fileContainingTheClass', 'ClassName')
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


def node_to_class(node):
    for node_type in mc.nodeType(node, i=True)[::-1]:
        if node_type in suported_class:
            lib = importlib.import_module(suported_class[node_type][0])
            return lib.__getattribute__(suported_class[node_type][1])(node)
    return dpn.Depend(node)


ntc = node_to_class


def nodes_to_classes(nodes):
    return [node_to_class(node) for node in nodes]
