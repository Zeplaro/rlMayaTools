import maya.cmds as mc
import node.depend as dep


class Dag(dep.Depend):
    def __init__(self, obj):
        super(Dag, self).__init__(obj)

    @property
    def parent(self):
        return mc.listRelatives(self.name, p=True, fullPath=True)

    @parent.setter
    def parent(self, parent):
        if hasattr(parent, 'name'):
            parent = parent.name
        if parent:
            mc.parent(self.name, parent)
        else:
            mc.parent(self.name, w=True)

    @property
    def children(self):
        return mc.listRelatives(self.name, c=True, fullPath=True)
