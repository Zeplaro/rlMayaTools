import maya.cmds as mc
import depend as dpn


class Transform(dpn.Depend):
    def __init__(self, name):
        super(Transform, self).__init__(name)
        if 'transform' not in self._type_inheritance:
            raise Exception("{} is not a transform".format(name))

    def get_shapes(self):
        return self.listRelatives(s=True)

    @property
    def shape(self):
        shapes = self.get_shapes()
        return shapes[0] if shapes else None


class Joint(Transform):
    def __init__(self, name):
        super(Transform, self).__init__(name)
        if 'joint' not in self._type_inheritance:
            raise Exception("{} is not a joint".format(name))
