import maya.cmds as mc
import node.shape as shp


class Mesh(shp.Shape):
    def __init__(self, mesh):
        super(Mesh, self).__init__(mesh)

    def __len__(self):
        return len(self.vtxs)

    @property
    def vtxs(self):
        return mc.ls('{}.vtx[:]'.format(self.name), long=True, fl=True)

    @property
    def faces(self):
        return mc.ls('{}.f[:]'.format(self.name), long=True, fl=True)

    @property
    def edges(self):
        return mc.ls('{}.f[:]'.format(self.name), long=True, fl=True)
