import maya.cmds as mc
import depend as dpn
reload(dpn)


class Transform(dpn.Depend):
    def __init__(self, node):
        super(Transform, self).__init__(node)
        if 'transform' not in self._type_inheritance:
            raise Exception("{} is not a transform".format(node))


class Joint(Transform):
    def __init__(self, node):
        super(Transform, self).__init__(node)
        if 'joint' not in self._type_inheritance:
            raise Exception("{} is not a joint".format(node))
