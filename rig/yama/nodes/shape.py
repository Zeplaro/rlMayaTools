import maya.cmds as mc
import depend as dpn
reload(dpn)


class Shape(dpn.Depend):
    def __init__(self, node):
        super(Shape, self).__init__(node)
        if 'shape' not in self._type_inheritance:
            raise Exception("{} is not a shape".format(node))

    def get_components(self):
        raise NotImplementedError


class Mesh(Shape):
    def __init__(self, node):
        super(Mesh, self).__init__(node)
        if 'mesh' not in self._type_inheritance:
            raise Exception("{} is not a mesh".format(node))

    def get_components(self):
        return mc.ls(self.name + '.vtx[*]', fl=True)
