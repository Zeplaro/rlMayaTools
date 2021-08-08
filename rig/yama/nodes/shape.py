import maya.cmds as mc
import depend as dpn
reload(dpn)


class Shape(dpn.Depend):
    def __init__(self, name):
        super(Shape, self).__init__(name)
        if 'shape' not in self._type_inheritance:
            raise Exception("{} is not a shape".format(name))

    def get_components(self):
        raise NotImplementedError

    def __len__(self):
        return len(self.get_components())


class Mesh(Shape):
    def __init__(self, name):
        super(Mesh, self).__init__(name)
        if 'mesh' not in self._type_inheritance:
            raise Exception("{} is not a mesh".format(name))

    def get_components(self):
        return mc.ls(self.name + '.vtx[*]', fl=True)

    def get_component_indexes(self):
        for i in range(len(self)):
            yield i
