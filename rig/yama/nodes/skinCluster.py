import maya.cmds as mc
import maya.mel as mel
import geometryFilter as gof
import weightdict as wdt


def get_skinCluster(obj):
    skn = mel.eval('findRelatedSkinCluster ' + obj)
    return SkinCluster(skn) if skn else None


class SkinCluster(gof.GeometryFilter):
    def __init__(self, node):
        print('skn')
        super(SkinCluster, self).__init__(node)
        if 'skinCluster' not in self._type_inheritance:
            raise Exception("{} is not a skinCluster".format(node))

    def influences(self):
        return mc.skinCluster(self.name, q=True, inf=True) or []

    @property
    def weights(self):
        weights = {}
        for vtx, _ in enumerate(self.geometry.get_components()):
            weights[vtx] = wdt.WeightsDict()
            for jnt, _ in enumerate(self.influences()):
                weights[vtx][jnt] = mc.getAttr('{}.weightList[{}].weights[{}]'.format(self, vtx, jnt))
        return weights

    @weights.setter
    def weights(self, weights):
        for vtx in weights:
            for jnt in weights[vtx]:
                mc.setAttr('{}.weightList[{}].weights[{}]'.format(self, vtx, jnt), weights[vtx][jnt])
