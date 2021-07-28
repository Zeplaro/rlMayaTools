import maya.cmds as mc
import maya.mel as mel
import geometryFilter as gof
import weightsdict as wdt


def get_skinCluster(obj):
    skn = mel.eval('findRelatedSkinCluster ' + obj)
    return SkinCluster(skn) if skn else None


class SkinCluster(gof.GeometryFilter):
    def __init__(self, node):
        print('skn')
        super(SkinCluster, self).__init__(node)
        if 'skinCluster' not in self._type_inheritance:
            raise Exception("{} is not a skinCluster".format(node))
        self._weights_attr = None

    def influences(self):
        return mc.skinCluster(self.name, q=True, inf=True) or []

    @property
    def weights(self):
        weights = {}
        for i in self.geometry.get_component_indexes():
            weights[i] = wdt.WeightsDict()
            for jnt, _ in enumerate(self.influences()):
                weights[i][jnt] = mc.getAttr('{}.weightList[{}].weights[{}]'.format(self, i, jnt))
        return weights

    @weights.setter
    def weights(self, weights):
        for vtx in weights:
            for jnt in weights[vtx]:
                mc.setAttr('{}.weightList[{}].weights[{}]'.format(self, vtx, jnt), weights[vtx][jnt])

    def weights_attr(self, index):
        raise NotImplementedError
