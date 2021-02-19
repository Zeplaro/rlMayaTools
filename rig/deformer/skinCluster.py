import maya.cmds as mc
import maya.mel as mel


def get_skinCluster(obj):
    skn = mel.eval('findRelatedSkinCluster '+obj)
    return SkinCluster(skn) if skn else None


class SkinCluster(object):
    def __init__(self, node):
        if not mc.objExists(node):
            raise Exception("{} does not exist in scene".format(node))
        if not mc.nodeType(node) == 'skinCluster':
            raise Exception("{} is not a skinCluster".format(node))
        self._name = node

    def __repr__(self):
        return 'SkinCluster({})'.format(self._name)

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    def geometry(self):
        geo = mc.skinCLuster(self._name, q=True, geometry=True)
        return geo[0] if geo else None

    def influences(self):
        return mc.skinCluster(self.name, q=True, inf=True)

    def get_components(self):
        return mc.ls(self.geometry()+'.vtx[*]', fl=True)

    def weigths(self):
        pass

