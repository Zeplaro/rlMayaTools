import importlib
import maya.cmds as mc
import attribute as attr


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
    return Depend(node)


def nodes_to_classes(nodes):
    return [node_to_class(node) for node in nodes]


class Depend(object):
    # todo : link to openMaya mObject instead of string
    def __init__(self, name):
        if not mc.objExists(name):
            raise Exception("{} does not exist in scene".format(name))
        self._name = name
        self._type_inheritance = mc.nodeType(name, i=True)

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self._name)

    def __str__(self):
        return self._name

    @property
    def attr(self):
        return self.Attr(self)

    class Attr(object):
        def __init__(self, node):
            self.__dict__['_node'] = node

        def __getattr__(self, item):
            return attr.Attribute(self._node, item)

        def __setattr__(self, key, value):
            attr.Attribute(self._node, key).value = value


    @property
    def name(self):
        return self._name

    def listRelatives(self, *args, **kwargs):
        return nodes_to_classes(mc.listRelatives(self, *args, **kwargs) or [])
