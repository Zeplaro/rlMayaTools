import maya.cmds as mc


class Depend(object):
    def __init__(self, node):
        print('dpn')
        if not mc.objExists(node):
            raise Exception("{} does not exist in scene".format(node))
        self._name = node
        self._type_inheritance = mc.nodeType(node, i=True)

    def __repr__(self):
        return 'yama.{}({})'.format(self.__class__.__name__, self._name)

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name
