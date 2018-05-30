import maya.cmds as mc
import node.shape as shp


class NurbsCurve(shp.Shape):
    def __init__(self, obj):
        super(NurbsCurve, self).__init__(obj)

    def __len__(self):
        return self['spans'] + self['degree']

    @property
    def arclen(self):
        return mc.arclen(self.name)
