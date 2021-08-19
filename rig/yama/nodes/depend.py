import maya.cmds as mc
import attribute as attr


class Depend(object):
    # todo : link to openMaya mObject instead of string
    def __init__(self, name):
        print('dpn')
        if not mc.objExists(name):
            raise Exception("{} does not exist in scene".format(name))
        self._name = name
        self._type_inheritance = mc.nodeType(name, i=True)

    def __repr__(self):
        return "yama.{}('{}')".format(self.__class__.__name__, self._name)

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
